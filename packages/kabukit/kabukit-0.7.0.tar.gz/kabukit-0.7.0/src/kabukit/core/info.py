from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from polars import DataFrame


class Info(Base):
    pass
