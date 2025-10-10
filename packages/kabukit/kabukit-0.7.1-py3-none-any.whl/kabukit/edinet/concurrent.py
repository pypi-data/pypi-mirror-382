from __future__ import annotations

from typing import TYPE_CHECKING

from kabukit.utils import concurrent
from kabukit.utils.date import get_dates

from .client import EdinetClient

if TYPE_CHECKING:
    import datetime
    from collections.abc import Iterable

    from polars import DataFrame

    from kabukit.utils.concurrent import Callback, Progress


async def fetch(
    resource: str,
    args: Iterable[str | datetime.date],
    /,
    max_concurrency: int | None = None,
    progress: Progress | None = None,
    callback: Callback | None = None,
) -> DataFrame:
    """引数に対応する各種データを取得し、単一のDataFrameにまとめて返す。

    Args:
        resource (str): 取得するデータの種類。EdinetClientのメソッド名から"get_"を
            除いたものを指定する。
        args (Iterable[str | datetime.date]): 取得対象の引数のリスト。
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
    return await concurrent.fetch(
        EdinetClient,
        resource,
        args,
        max_concurrency=max_concurrency,
        progress=progress,
        callback=callback,
    )


async def fetch_list(
    days: int | None = None,
    years: int | None = None,
    limit: int | None = None,
    max_concurrency: int | None = None,
    progress: Progress | None = None,
    callback: Callback | None = None,
) -> DataFrame:
    """過去days日またはyears年の文書一覧を取得し、単一のDataFrameにまとめて返す。

    Args:
        days (int | None): 過去days日の日付リストを取得する。
        years (int | None): 過去years年の日付リストを取得する。
            daysが指定されている場合は無視される。
        max_concurrency (int | None, optional): 同時に実行するリクエストの最大数。
            指定しないときはデフォルト値が使用される。
        progress (Progress | None, optional): 進捗表示のための関数。
            tqdm, marimoなどのライブラリを使用できる。
            指定しないときは進捗表示は行われない。
        callback (Callback | None, optional): 各DataFrameに対して適用する
            コールバック関数。指定しないときはそのままのDataFrameが使用される。

    Returns:
        DataFrame:
            文書一覧を含む単一のDataFrame。
    """
    dates = get_dates(days=days, years=years)

    if limit is not None:
        dates = dates[:limit]

    df = await fetch(
        "list",
        dates,
        max_concurrency=max_concurrency,
        progress=progress,
        callback=callback,
    )
    return df.sort("Date")


async def fetch_csv(
    doc_ids: Iterable[str],
    /,
    limit: int | None = None,
    max_concurrency: int | None = None,
    progress: Progress | None = None,
    callback: Callback | None = None,
) -> DataFrame:
    """文書をCSV形式で取得し、単一のDataFrameにまとめて返す。

    Args:
        doc_ids (Iterable[str]): 取得対象の文書IDのリスト。
        max_concurrency (int | None, optional): 同時に実行するリクエストの最大数。
            指定しないときはデフォルト値が使用される。
        progress (Progress | None, optional): 進捗表示のための関数。
            tqdm, marimoなどのライブラリを使用できる。
            指定しないときは進捗表示は行われない。
        callback (Callback | None, optional): 各DataFrameに対して適用する
            コールバック関数。指定しないときはそのままのDataFrameが使用される。

    Returns:
        DataFrame:
            文書含む単一のDataFrame。
    """
    doc_ids = list(doc_ids)

    if limit is not None:
        doc_ids = doc_ids[:limit]

    df = await fetch(
        "csv",
        doc_ids,
        max_concurrency=max_concurrency,
        progress=progress,
        callback=callback,
    )
    return df.sort("docID")
