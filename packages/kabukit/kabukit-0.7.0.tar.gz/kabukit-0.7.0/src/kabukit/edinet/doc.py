from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import polars as pl

if TYPE_CHECKING:
    from polars import DataFrame


def clean_list(df: DataFrame, date: str | datetime.date) -> DataFrame:
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()  # noqa: DTZ007

    null_columns = [c for c in df.columns if df[c].dtype == pl.Null]

    return (
        df.with_columns(
            pl.col(null_columns).cast(pl.String),
        )
        .with_columns(
            pl.lit(date).alias("Date"),
            pl.col("^.+DateTime$").str.to_datetime("%Y-%m-%d %H:%M", strict=False),
            pl.col("^period.+$").str.to_date("%Y-%m-%d", strict=False),
            pl.col("^.+Flag$").cast(pl.Int8).cast(pl.Boolean),
            pl.col("^.+Code$").cast(pl.String),
        )
        .select("Date", pl.exclude("Date"))
    )


def read_csv(data: bytes) -> DataFrame:
    return pl.read_csv(
        data,
        separator="\t",
        encoding="utf-16-le",
        infer_schema_length=None,
    )


def clean_csv(df: DataFrame, doc_id: str) -> DataFrame:
    return df.select(
        pl.lit(doc_id).alias("docID"),
        pl.all(),
    )
