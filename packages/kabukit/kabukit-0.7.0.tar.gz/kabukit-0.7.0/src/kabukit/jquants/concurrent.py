from __future__ import annotations

from typing import TYPE_CHECKING

from kabukit.utils import concurrent

from .client import JQuantsClient
from .info import get_target_codes

if TYPE_CHECKING:
    from collections.abc import Iterable

    from polars import DataFrame

    from kabukit.utils.concurrent import Callback, Progress


async def fetch(
    resource: str,
    codes: Iterable[str],
    /,
    max_concurrency: int | None = None,
    progress: Progress | None = None,
    callback: Callback | None = None,
) -> DataFrame:
    """複数の銘柄の各種データを取得し、単一のDataFrameにまとめて返す。

    Args:
        resource (str): 取得するデータの種類。JQuantsClientのメソッド名から"get_"を
            除いたものを指定する。
        codes (Iterable[str]): 取得対象の銘柄コードのリスト。
        max_concurrency (int | None, optional): 同時に実行するリクエストの最大数。
            指定しないときはデフォルト値が使用される。
        progress (Progress | None, optional): 進捗表示のための関数。
            tqdm, marimoなどのライブラリを使用できる。
            指定しないときは進捗表示は行われない。
        callback (Callback | None, optional): 各DataFrameに対して適用する
            コールバック関数。指定しないときはそのままのDataFrameが使用される。

    Returns:
        DataFrame:
            すべての銘柄の財務情報を含む単一のDataFrame。
    """
    data = await concurrent.fetch(
        JQuantsClient,
        resource,
        codes,
        max_concurrency=max_concurrency,
        progress=progress,
        callback=callback,
    )
    return data.sort("Code", "Date")


async def fetch_all(
    resource: str,
    /,
    limit: int | None = None,
    max_concurrency: int | None = None,
    progress: Progress | None = None,
    callback: Callback | None = None,
) -> DataFrame:
    """全銘柄の各種データを取得し、単一のDataFrameにまとめて返す。

    Args:
        resource (str): 取得するデータの種類。JQuantsClientのメソッド名から"get_"を
            除いたものを指定する。
        limit (int | None, optional): 取得する銘柄数の上限。
            指定しないときはすべての銘柄が対象となる。
        max_concurrency (int | None, optional): 同時に実行するリクエストの最大数。
            指定しないときはデフォルト値が使用される。
        progress (Progress | None, optional): 進捗表示のための関数。
            tqdm, marimoなどのライブラリを使用できる。
            指定しないときは進捗表示は行われない。
        callback (Callback | None, optional): 各DataFrameに対して適用する
            コールバック関数。指定しないときはそのままのDataFrameが使用される。

    Returns:
        DataFrame:
            すべての銘柄の財務情報を含む単一のDataFrame。
    """

    codes = await get_target_codes()
    codes = codes[:limit]

    return await fetch(
        resource,
        codes,
        max_concurrency=max_concurrency,
        progress=progress,
        callback=callback,
    )
