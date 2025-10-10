from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import polars as pl

from kabukit.utils.config import get_cache_dir

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path
    from typing import Any, Self

    from polars import DataFrame
    from polars._typing import IntoExprColumn


class Base:
    data: DataFrame

    def __init__(self, data: DataFrame) -> None:
        self.data = data

    @classmethod
    def data_dir(cls) -> Path:
        clsname = cls.__name__.lower()
        return get_cache_dir() / clsname

    def write(self) -> Path:
        data_dir = self.data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        path = datetime.datetime.today().strftime("%Y%m%d")  # noqa: DTZ002
        filename = data_dir / f"{path}.parquet"
        self.data.write_parquet(filename)
        return filename

    @classmethod
    def read(cls, path: str | None = None) -> Self:
        data_dir = cls.data_dir()

        if path:
            filename = data_dir / path
        else:
            filenames = sorted(data_dir.glob("*.parquet"))
            if not filenames:
                msg = f"No data found in {data_dir}"
                raise FileNotFoundError(msg)

            filename = filenames[-1]

        data = pl.read_parquet(filename)
        return cls(data)

    def filter(
        self,
        *predicates: IntoExprColumn | Iterable[IntoExprColumn] | bool | list[bool],
        **constraints: Any,
    ) -> Self:
        """Filter the data with given predicates and constraints."""
        data = self.data.filter(*predicates, **constraints)
        return self.__class__(data)
