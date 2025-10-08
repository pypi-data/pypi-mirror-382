from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

import typer
from async_typer import AsyncTyper  # pyright: ignore[reportMissingTypeStubs]
from typer import Argument

if TYPE_CHECKING:
    from kabukit.core.base import Base

app = AsyncTyper(
    add_completion=False,
    help="J-Quantsからデータを取得します。",
)

Code = Annotated[
    str | None,
    Argument(help="銘柄コード。指定しない場合は全銘柄の情報を取得します。"),
]


@app.async_command()  # pyright: ignore[reportUnknownMemberType]
async def info(code: Code = None) -> None:
    """上場銘柄一覧を取得します。"""
    from kabukit.core.info import Info
    from kabukit.jquants.client import JQuantsClient

    async with JQuantsClient() as client:
        df = await client.get_info(code)

    typer.echo(df)

    if code is None:
        path = Info(df).write()
        typer.echo(f"全銘柄の情報を '{path}' に保存しました。")


async def _fetch(
    code: str | None,
    target: str,
    cls: type[Base],
    fetch_func_name: str,
    message: str,
    **kwargs: Any,
) -> None:
    """財務情報・株価情報を取得するための共通処理"""
    from kabukit.jquants.client import JQuantsClient

    if code is not None:
        async with JQuantsClient() as client:
            df = await getattr(client, fetch_func_name)(code)
        typer.echo(df)
        return

    import tqdm.asyncio

    from kabukit.jquants.concurrent import fetch_all

    try:
        df = await fetch_all(target, progress=tqdm.asyncio.tqdm, **kwargs)
    except KeyboardInterrupt:
        typer.echo("中断しました。")
        raise typer.Exit(1) from None

    typer.echo(df)
    path = cls(df).write()
    typer.echo(f"全銘柄の{message}を '{path}' に保存しました。")


@app.async_command()  # pyright: ignore[reportUnknownMemberType]
async def statements(code: Code = None) -> None:
    """財務情報を取得します。"""
    from kabukit.core.statements import Statements

    await _fetch(
        code=code,
        target="statements",
        cls=Statements,
        fetch_func_name="get_statements",
        message="財務情報",
    )


@app.async_command()  # pyright: ignore[reportUnknownMemberType]
async def prices(code: Code = None) -> None:
    """株価を取得します。"""
    from kabukit.core.prices import Prices

    await _fetch(
        code=code,
        target="prices",
        cls=Prices,
        fetch_func_name="get_prices",
        message="株価情報",
        max_concurrency=8,
    )


@app.async_command(name="list")  # pyright: ignore[reportUnknownMemberType]
async def list_() -> None:
    """報告書一覧を取得します。"""
    import tqdm.asyncio

    from kabukit.core.list import List
    from kabukit.edinet.concurrent import fetch_list

    try:
        df = await fetch_list(years=10, progress=tqdm.asyncio.tqdm)
    except (KeyboardInterrupt, RuntimeError):
        typer.echo("中断しました。")
        raise typer.Exit(1) from None

    typer.echo(df)
    path = List(df).write()
    typer.echo(f"報告書一覧を '{path}' に保存しました。")


@app.async_command()  # pyright: ignore[reportUnknownMemberType]
async def reports() -> None:
    """報告書を取得します。"""
    import polars as pl
    import tqdm.asyncio

    from kabukit.core.list import List
    from kabukit.core.reports import Reports
    from kabukit.edinet.concurrent import fetch_csv

    try:
        df = List.read().data
    except FileNotFoundError:
        await list_()
        df = List.read().data

    lst = df.filter(pl.col("csvFlag"), pl.col("secCode").is_not_null())
    doc_ids = lst["docID"].unique()

    try:
        df = await fetch_csv(doc_ids, limit=1000, progress=tqdm.asyncio.tqdm)
    except (KeyboardInterrupt, RuntimeError):
        typer.echo("中断しました。")
        raise typer.Exit(1) from None

    typer.echo(df)
    path = Reports(df).write()
    typer.echo(f"報告書を '{path}' に保存しました。")


@app.async_command(name="all")  # pyright: ignore[reportUnknownMemberType]
async def all_(code: Code = None) -> None:
    """上場銘柄一覧、財務情報、株価、報告書を連続して取得します。"""
    typer.echo("上場銘柄一覧を取得します。")
    await info(code)

    typer.echo("---")
    typer.echo("財務情報を取得します。")
    await statements(code)

    typer.echo("---")
    typer.echo("株価を取得します。")
    await prices(code)

    if code is None:
        typer.echo("---")
        typer.echo("報告書一覧を取得します。")
        await list_()
        typer.echo("---")
        typer.echo("報告書を取得します。")
        await reports()
