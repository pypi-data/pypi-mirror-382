from __future__ import annotations

import datetime
import os
from enum import StrEnum
from typing import TYPE_CHECKING

import polars as pl
from polars import DataFrame

from kabukit.core.client import Client
from kabukit.utils.config import load_dotenv, set_key
from kabukit.utils.params import get_params

from . import info, prices, statements, topix

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from typing import Any, Self

    from httpx import HTTPStatusError  # noqa: F401
    from httpx._types import QueryParamTypes

API_VERSION = "v1"
BASE_URL = f"https://api.jquants.com/{API_VERSION}"


class AuthKey(StrEnum):
    """J-Quants認証のための環境変数キー。"""

    REFRESH_TOKEN = "JQUANTS_REFRESH_TOKEN"  # noqa: S105
    ID_TOKEN = "JQUANTS_ID_TOKEN"  # noqa: S105


class JQuantsClient(Client):
    """J-Quants APIと対話するためのクライアント。

    API認証トークン（リフレッシュトークンおよびIDトークン）を管理し、
    各種J-Quants APIエンドポイントへアクセスするメソッドを提供する。
    トークンは設定ファイルから読み込まれ、またファイルに保存される。

    Attributes:
        client: APIリクエストを行うための `AsyncClient` インスタンス。
    """

    def __init__(self, id_token: str | None = None) -> None:
        super().__init__(BASE_URL)
        self.set_id_token(id_token)

    def set_id_token(self, id_token: str | None = None) -> None:
        """IDトークンをヘッダーに設定する。

        Args:
            id_token (str | None, optional): 設定するIDトークン。
                Noneの場合、環境変数から読み込む。
        """

        if id_token is None:
            load_dotenv()
            id_token = os.environ.get(AuthKey.ID_TOKEN)

        if id_token:
            self.client.headers["Authorization"] = f"Bearer {id_token}"

    async def post(self, url: str, json: Any | None = None) -> Any:
        """指定されたURLにPOSTリクエストを送信する。

        Args:
            url: POSTリクエストのURLパス。
            json: リクエストボディのJSONペイロード。

        Returns:
            APIからのJSONレスポンス。

        Raises:
            HTTPStatusError: APIリクエストが失敗した場合。
        """
        resp = await self.client.post(url, json=json)
        resp.raise_for_status()
        return resp.json()

    async def get(self, url: str, params: QueryParamTypes | None = None) -> Any:
        """指定されたURLにGETリクエストを送信する。

        Args:
            url (str): GETリクエストのURLパス。
            params (QueryParamTypes | None, optional): リクエストのクエリパラメータ。

        Returns:
            APIからのJSONレスポンス。

        Raises:
            HTTPStatusError: APIリクエストが失敗した場合。
        """
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def auth(
        self,
        mailaddress: str,
        password: str,
        *,
        save: bool = False,
    ) -> Self:
        """認証を行い、トークンを保存する。

        Args:
            mailaddress (str): J-Quantsに登録したメールアドレス。
            password (str): J-Quantsのパスワード。
            save (bool, optional): トークンを環境変数に保存するかどうか。

        Raises:
            HTTPStatusError: APIリクエストが失敗した場合。
        """
        json_data = {"mailaddress": mailaddress, "password": password}
        data = await self.post("/token/auth_user", json=json_data)
        refresh_token = data["refreshToken"]

        url = f"/token/auth_refresh?refreshtoken={refresh_token}"
        data = await self.post(url)
        id_token = data["idToken"]

        if save:
            set_key(AuthKey.REFRESH_TOKEN, refresh_token)
            set_key(AuthKey.ID_TOKEN, id_token)

        self.set_id_token(id_token)
        return self

    async def get_info(
        self,
        code: str | None = None,
        date: str | datetime.date | None = None,
        *,
        clean: bool = True,
    ) -> DataFrame:
        """銘柄情報を取得する。

        Args:
            code (str, optional): 情報を取得する銘柄のコード。
            date (str | datetime.date, optional): 情報を取得する日付。
            clean (bool, optional): 取得したデータをクリーンアップするかどうか。

        Returns:
            銘柄情報を含むDataFrame。

        Raises:
            HTTPStatusError: APIリクエストが失敗した場合。
        """
        params = get_params(code=code, date=date)
        url = "/listed/info"
        data = await self.get(url, params)
        df = DataFrame(data["info"])
        return info.clean(df) if clean else df

    async def iter_pages(
        self,
        url: str,
        params: dict[str, Any] | None,
        name: str,
    ) -> AsyncIterator[DataFrame]:
        """ページ分割されたAPIレスポンスを反復処理する。

        Args:
            url (str): APIエンドポイントのベースURL。
            params (dict[str, Any]): クエリパラメータの辞書。
            name (str): アイテムのリストを含むJSONレスポンスのキー。

        Yields:
            データの各ページに対応するDataFrame。

        Raises:
            HTTPStatusError: APIリクエストが失敗した場合。
        """
        params = params or {}

        while True:
            data = await self.get(url, params)
            yield DataFrame(data[name])
            if "pagination_key" in data:
                params["pagination_key"] = data["pagination_key"]
            else:
                break

    async def get_prices(
        self,
        code: str | None = None,
        date: str | datetime.date | None = None,
        from_: str | datetime.date | None = None,
        to: str | datetime.date | None = None,
        *,
        clean: bool = True,
    ) -> DataFrame:
        """日々の株価四本値を取得する。

        株価は分割・併合を考慮した調整済み株価（小数点第２位四捨五入）と調整前の株価を取得できる。

        Args:
            code (str, optional): 株価を取得する銘柄のコード。
            date (str | datetime.date, optional): 株価を取得する日付。
                `from_`または`to`とは併用不可。
            from_ (str | datetime.date, optional): 取得期間の開始日。
                `date`とは併用不可。
            to (str | datetime.date, optional): 取得期間の終了日。
                `date`とは併用不可。
            clean (bool, optional): 取得したデータをクリーンアップするかどうか。

        Returns:
            日々の株価四本値を含むDataFrame。

        Raises:
            ValueError: `date`と`from_`/`to`の両方が指定された場合。
            HTTPStatusError: APIリクエストが失敗した場合。
        """
        if not date and not code:
            return await self.get_latest_available_prices(clean=clean)

        if date and (from_ or to):
            msg = "dateとfrom/toの両方を指定することはできません。"
            raise ValueError(msg)

        params = get_params(code=code, date=date, from_=from_, to=to)

        url = "/prices/daily_quotes"
        name = "daily_quotes"

        dfs = [df async for df in self.iter_pages(url, params, name)]
        df = pl.concat(dfs)

        if df.is_empty():
            return df

        return prices.clean(df) if clean else df

    async def get_latest_available_prices(
        self,
        num_days: int = 30,
        *,
        clean: bool = True,
    ) -> DataFrame:
        """直近利用可能な日付の株価を取得する。"""
        today = datetime.date.today()  # noqa: DTZ011

        for days in range(num_days):
            date = today - datetime.timedelta(days)
            df = await self.get_prices(date=date, clean=clean)

            if not df.is_empty():
                return df

        return DataFrame()

    async def get_statements(
        self,
        code: str | None = None,
        date: str | datetime.date | None = None,
        *,
        clean: bool = True,
        with_date: bool = True,
    ) -> DataFrame:
        """四半期毎の決算短信サマリーおよび業績・配当の修正に関する開示情報を取得する。

        Args:
            code (str, optional): 財務情報を取得する銘柄のコード。
            date (str | datetime.date, optional): 財務情報を取得する日付。
            clean (bool, optional): 取得したデータをクリーンアップするかどうか。
            with_date (bool, optional): クリーンアップ後に営業日ベースで開示日の翌日を
                計算して`Date`列を追加するかどうか。

        Returns:
            財務情報を含むDataFrame。

        Raises:
            ValueError: `code`と`date`が両方とも指定されない場合。
            HTTPStatusError: APIリクエストが失敗した場合。
        """
        if not code and not date:
            msg = "codeまたはdateのどちらかを指定する必要があります。"
            raise ValueError(msg)

        params = get_params(code=code, date=date)
        url = "/fins/statements"
        name = "statements"

        dfs = [df async for df in self.iter_pages(url, params, name)]
        df = pl.concat(dfs)

        if df.is_empty() or not clean:
            return df

        df = statements.clean(df)

        return statements.with_date(df) if with_date else df

    async def get_announcement(self) -> DataFrame:
        """翌日発表予定の決算情報を取得する。

        Returns:
            開示情報を含むPolars DataFrame。

        Raises:
            HTTPStatusError: APIリクエストが失敗した場合。
        """
        url = "fins/announcement"
        name = "announcement"

        dfs = [df async for df in self.iter_pages(url, {}, name)]
        df = pl.concat(dfs)
        if df.is_empty():
            return df

        return df.with_columns(pl.col("Date").str.to_date("%Y-%m-%d", strict=False))

    async def get_trades_spec(
        self,
        section: str | None = None,
        from_: str | datetime.date | None = None,
        to: str | datetime.date | None = None,
    ) -> DataFrame:
        """投資部門別の情報を取得する。

        Args:
            section: 絞り込み対象のセクション。
            from_: 取得期間の開始日。
            to: 取得期間の終了日。

        Returns:
            投資部門別の情報を含むPolars DataFrame。

        Raises:
            HTTPStatusError: APIリクエストが失敗した場合。
        """
        params = get_params(section=section, from_=from_, to=to)

        url = "/markets/trades_spec"
        name = "trades_spec"

        dfs = [df async for df in self.iter_pages(url, params, name)]
        df = pl.concat(dfs)
        if df.is_empty():
            return df

        return df.with_columns(pl.col("^.*Date$").str.to_date("%Y-%m-%d", strict=False))

    async def get_topix(
        self,
        from_: str | datetime.date | None = None,
        to: str | datetime.date | None = None,
    ) -> DataFrame:
        """日次のTOPIX指数データを取得する。

        Args:
            from_: 取得期間の開始日。
            to: 取得期間の終了日。

        Returns:
            日次のTOPIX指数データを含むPolars DataFrame。

        Raises:
            HTTPStatusError: APIリクエストが失敗した場合。
        """
        params = get_params(from_=from_, to=to)

        url = "/indices/topix"
        name = "topix"

        dfs = [df async for df in self.iter_pages(url, params, name)]
        df = pl.concat(dfs)
        if df.is_empty():
            return df

        return topix.clean(df)
