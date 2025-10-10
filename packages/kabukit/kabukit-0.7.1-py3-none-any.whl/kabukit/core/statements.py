from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

from .base import Base

if TYPE_CHECKING:
    from polars import DataFrame


class Statements(Base):
    def shares(self) -> DataFrame:
        """発行済株式数および自己株式数を取得する。"""
        return self.data.filter(
            pl.col("IssuedShares").is_not_null(),
        ).select(
            "Date",
            "Code",
            "IssuedShares",
            "TreasuryShares",
        )

    def equity(self) -> DataFrame:
        """Statementsデータから純資産を抽出する。

        Returns:
            DataFrame: Date, Code, Equity を含むDataFrame
        """
        return self.data.filter(
            pl.col("Equity").is_not_null(),
        ).select("Date", "Code", "Equity")

    def forecast_profit(self) -> DataFrame:
        """Statementsデータから予想純利益を抽出する。

        Returns:
            DataFrame: Date, Code, ForecastProfit を含むDataFrame
        """
        return (
            self.data.with_columns(
                pl.when(pl.col("TypeOfDocument").str.starts_with("FY"))
                .then(pl.col("NextYearForecastProfit"))
                .otherwise(pl.col("ForecastProfit"))
                .alias("ForecastProfit"),
            )
            .filter(pl.col("ForecastProfit").is_not_null())
            .select("Date", "Code", "ForecastProfit")
        )

    def forecast_dividend(self) -> DataFrame:
        """予想年間配当総額を抽出する。

        Returns:
            DataFrame: Date, Code, ForecastDividend を含むDataFrame
        """
        # 予想株式数を計算
        forecast_shares = (
            pl.when(pl.col("TypeOfDocument").str.starts_with("FY"))
            .then(
                pl.col("NextYearForecastProfit")
                / pl.col("NextYearForecastEarningsPerShare"),
            )
            .otherwise(pl.col("ForecastProfit") / pl.col("ForecastEarningsPerShare"))
            .alias("ForecastShares")
        )

        # 年間配当総額を計算
        annual_forecast_dividend = (
            pl.when(pl.col("TypeOfDocument").str.starts_with("FY"))
            .then(
                pl.col("NextYearForecastDividendPerShareAnnual")
                * pl.col("ForecastShares"),
            )
            .otherwise(
                pl.col("ForecastDividendPerShareAnnual") * pl.col("ForecastShares"),
            )
            .round(0)
            .alias("ForecastDividend")
        )

        return (
            self.data.with_columns(forecast_shares)
            .with_columns(annual_forecast_dividend)
            .filter(pl.col("ForecastDividend").is_not_null())
            .select("Date", "Code", "ForecastDividend")
        )
