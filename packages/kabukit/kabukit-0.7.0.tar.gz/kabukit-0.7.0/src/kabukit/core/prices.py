from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

from .base import Base

if TYPE_CHECKING:
    from datetime import timedelta
    from typing import Self

    from polars import DataFrame, Expr

    from .statements import Statements


class Prices(Base):
    def truncate(self, every: str | timedelta | Expr) -> Self:
        """時系列データを指定された頻度で集計し、切り詰める。

        このメソッドは、日次などの時系列データを指定された頻度（例: 月次、週次）で
        集計し、新しい時間軸に切り詰めます。集計方法は以下の通りです。

        *   `Open`: 各期間の最初の`Open`値
        *   `High`: 各期間の最大`High`値
        *   `Low`: 各期間の最小`Low`値
        *   `Close`: 各期間の最後の`Close`値
        *   `Volume`: 各期間の`Volume`の合計
        *   `TurnoverValue`: 各期間の`TurnoverValue`の合計

        Args:
            every (str | timedelta | Expr): 切り詰める頻度を指定します。
                例: "1d" (日次), "1mo" (月次), `timedelta`オブジェクト,
                または Polars の `Expr` オブジェクト。

        Returns:
            Self: 指定された頻度で切り詰められた新しいPricesオブジェクト。
        """
        data = (
            self.data.group_by(pl.col("Date").dt.truncate(every), "Code")
            .agg(
                pl.col("Open").drop_nulls().first(),
                pl.col("High").max(),
                pl.col("Low").min(),
                pl.col("Close").drop_nulls().last(),
                pl.col("Volume").sum(),
                pl.col("TurnoverValue").sum(),
            )
            .sort("Code", "Date")
        )

        return self.__class__(data)

    def with_adjusted_shares(self, statements: Statements) -> Self:
        """日次の調整済み株式数を計算し、列として追加する。

        決算短信で報告される株式数（例：発行済株式総数）は、四半期ごとなど
        特定の日付のデータです。一方で、株式分割や併合は日々発生し、株式数を
        変動させます。
        このメソッドは、直近の決算で報告された株式数を、日々の調整係数
        (`AdjustmentFactor`) を用いて補正し、日次ベースの時系列データとして
        提供します。これにより、日々の時価総額計算などが正確に行えるようになります。

        具体的には、`statements`から`IssuedShares`（発行済株式総数）と
        `TreasuryShares`（自己株式数）を取得し、それぞれを調整します。
        計算結果は、元の列名との混同を避けるため、接頭辞`Adjusted`を付与した
        新しい列（`AdjustedIssuedShares`, `AdjustedTreasuryShares`）として
        追加されます。

        Args:
            statements (Statements): 財務データを提供する`Statements`オブジェクト。

        Returns:
            Self: `AdjustedIssuedShares`および`AdjustedTreasuryShares`列が
            追加された、新しいPricesオブジェクト。

        Note:
            この計算は、決算発表間の株式数の変動が、株式分割・併合
            （`AdjustmentFactor`）にのみ起因すると仮定しています。
            期中に行われる増資や自己株式取得など、`AdjustmentFactor`に
            反映されないイベントによる株式数の変動は考慮されません。
        """
        if "AdjustedIssuedShares" in self.data.columns:
            return self

        shares = statements.shares().rename({"Date": "ReportDate"})

        adjusted = (
            self.data.join_asof(
                shares,
                left_on="Date",
                right_on="ReportDate",
                by="Code",
                check_sortedness=False,
            )
            .with_columns(
                (1.0 / pl.col("AdjustmentFactor"))
                .cum_prod()
                .over("Code", "ReportDate")
                .alias("CumulativeRatio"),
            )
            .with_columns(
                (pl.col("IssuedShares", "TreasuryShares") * pl.col("CumulativeRatio"))
                .round(0)
                .cast(pl.Int64)
                .name.prefix("Adjusted"),
            )
            .select(
                "Date",
                "Code",
                "ReportDate",
                "AdjustedIssuedShares",
                "AdjustedTreasuryShares",
            )
        )

        data = self.data.join(adjusted, on=["Date", "Code"], how="left")

        return self.__class__(data)

    @property
    def _outstanding_shares_expr(self) -> pl.Expr:
        """調整済み発行済株式数を計算する Polars 式を返す。

        Raises:
            KeyError: 必要な列が存在しない場合は KeyError を送出する。
        """
        required_cols = {"AdjustedIssuedShares", "AdjustedTreasuryShares"}

        if not required_cols.issubset(self.data.columns):
            missing = required_cols - set(self.data.columns)
            msg = f"必要な列が存在しません: {missing}。"
            msg += "事前に .with_adjusted_shares() を呼び出してください。"
            raise KeyError(msg)

        return pl.col("AdjustedIssuedShares") - pl.col("AdjustedTreasuryShares")

    def with_market_cap(self) -> Self:
        """時価総額を計算し、列として追加する。

        このメソッドは、日々の調整前終値 (`RawClose`) と、調整済みの発行済株式数
        (`AdjustedIssuedShares`) および自己株式数 (`AdjustedTreasuryShares`)
        を基に、日次ベースの時価総額を計算します。

        計算式:
            時価総額 = 調整前終値 * (調整済み発行済株式数 - 調整済み自己株式数)

        Returns:
            Self: `MarketCap` 列が追加された、新しいPricesオブジェクト。

        Note:
            このメソッドを呼び出す前に、`with_adjusted_shares()` あるいは
            `with_yields()` を実行して、調整済みの株式数列を事前に計算して
            おく必要があります。
        """
        data = self.data.with_columns(
            (pl.col("RawClose") * self._outstanding_shares_expr).alias("MarketCap"),
        )

        return self.__class__(data)

    def with_equity(self, statements: Statements) -> Self:
        """時系列の純資産を列として追加する。

        Args:
            statements (Statements): 財務データを提供する`Statements`オブジェクト。

        Returns:
            Self: `Equity` 列が追加された、新しいPricesオブジェクト。
        """
        if "Equity" in self.data.columns:
            return self

        data = self.data.join_asof(
            statements.equity(),
            on="Date",
            by="Code",
            check_sortedness=False,
        )

        return self.__class__(data)

    def with_book_value_yield(self) -> Self:
        """時系列の一株あたり純資産と純資産利回りを列として追加する。

        計算式:
            一株あたり純資産 = 純資産 / (調整済み発行済株式数 - 調整済み自己株式数)
            純資産利回り = 一株あたり純資産 / 調整前終値

        Returns:
            Self: `BookValuePerShare`, `BookValueYield` 列が追加された、
            新しいPricesオブジェクト。

        Note:
            このメソッドを呼び出す前に、`with_equity()` および
            `with_adjusted_shares()` を実行して、純資産および調整済み株式数
            列を事前に計算しておく必要があります。
        """
        data = self.data.with_columns(
            (pl.col("Equity") / self._outstanding_shares_expr).alias(
                "BookValuePerShare",
            ),
        ).with_columns(
            (pl.col("BookValuePerShare") / pl.col("RawClose")).alias(
                "BookValueYield",
            ),
        )

        return self.__class__(data)

    def with_forecast_profit(self, statements: Statements) -> Self:
        """時系列の予想純利益を列として追加する。

        Args:
            statements (Statements): 財務データを提供する`Statements`オブジェクト。

        Returns:
            Self: `ForecastProfit` 列が追加された、新しいPricesオブジェクト。
        """
        if "ForecastProfit" in self.data.columns:
            return self

        data = self.data.join_asof(
            statements.forecast_profit(),
            on="Date",
            by="Code",
            check_sortedness=False,
        )

        return self.__class__(data)

    def with_earnings_yield(self) -> Self:
        """時系列の一株あたり純利益と収益利回り(純利益利回り)を列として追加する。

        計算式:
            一株あたり純利益 = 予想純利益 / (調整済み発行済株式数 - 調整済み自己株式数)
            収益利回り = 一株あたり純利益 / 調整前終値

        Returns:
            Self: `EarningsPerShare`, `EarningsYield` 列が追加された、
            新しいPricesオブジェクト。

        Note:
            このメソッドを呼び出す前に、`with_forecast_profit()` および
            `with_adjusted_shares()` を実行して、予想純利益および調整済み株式数
            列を事前に計算しておく必要があります。
        """
        data = self.data.with_columns(
            (pl.col("ForecastProfit") / self._outstanding_shares_expr).alias(
                "EarningsPerShare",
            ),
        ).with_columns(
            (pl.col("EarningsPerShare") / pl.col("RawClose")).alias("EarningsYield"),
        )

        return self.__class__(data)

    def with_forecast_dividend(self, statements: Statements) -> Self:
        """時系列の予想年間配当総額を列として追加する。

        Args:
            statements (Statements): 財務データを提供する`Statements`オブジェクト。

        Returns:
            Self: `ForecastDividend` 列が追加された、新しいPricesオブジェクト。
        """
        if "ForecastDividend" in self.data.columns:
            return self

        data = self.data.join_asof(
            statements.forecast_dividend(),
            on="Date",
            by="Code",
            check_sortedness=False,
        )

        return self.__class__(data)

    def with_dividend_yield(self) -> Self:
        """時系列の一株あたり配当金と配当利回りを列として追加する。

        計算式:
            一株あたり配当金 = 予想年間配当総額 / (調整済み発行済株式数 - 調整済み自己株式数)
            配当利回り = 一株あたり配当金 / 調整前終値

        Returns:
            Self: `DividendPerShare`, `DividendYield` 列が追加された、
            新しいPricesオブジェクト。

        Note:
            このメソッドを呼び出す前に、`with_forecast_dividend()` および
            `with_adjusted_shares()` を実行して、予想年間配当総額および調整済み株式数
            列を事前に計算しておく必要があります。
        """  # noqa: E501
        data = self.data.with_columns(
            (pl.col("ForecastDividend") / self._outstanding_shares_expr).alias(
                "DividendPerShare",
            ),
        ).with_columns(
            (pl.col("DividendPerShare") / pl.col("RawClose")).alias("DividendYield"),
        )

        return self.__class__(data)

    def with_yields(self, statements: Statements) -> Self:
        """すべての利回り関連指標を計算し、列として追加する。

        このメソッドは、以下の利回り関連指標をまとめて計算し、DataFrameに
        追加するコンビニエンスメソッドです。

        *   純資産利回り (`BookValueYield`)
        *   収益利回り (`EarningsYield`)
        *   配当利回り (`DividendYield`)

        内部で `with_adjusted_shares()`, `with_equity()`,
        `with_book_value_yield()`, `with_forecast_profit()`,
        `with_earnings_yield()`, `with_forecast_dividend()`,
        `with_dividend_yield()` を呼び出します。
        これらのメソッドはべき等であるため、重複して呼び出されても
        無駄な計算は行われません。

        Args:
            statements (Statements): 財務データを提供する`Statements`オブジェクト。

        Returns:
            Self: `BookValuePerShare`, `BookValueYield`, `EarningsPerShare`,
            `EarningsYield`, `DividendPerShare`, `DividendYield` 列が追加された、
            新しいPricesオブジェクト。
        """
        return (
            self.with_adjusted_shares(statements)
            .with_equity(statements)
            .with_book_value_yield()
            .with_forecast_profit(statements)
            .with_earnings_yield()
            .with_forecast_dividend(statements)
            .with_dividend_yield()
        )

    def period_stats(self) -> DataFrame:
        """各期ごとの各種利回りおよび調整済み終値の統計量を計算し、DataFrameを返す。

        このメソッドは、`Code`と`ReportDate`で定義される各期（決算期間）ごとに、
        以下の指標の統計量（始値、高値、安値、終値、平均値）を計算し、新しいDataFrameを
        返します。

        対象指標:
        *   `BookValueYield` (純資産利回り)
        *   `EarningsYield` (収益利回り)
        *   `DividendYield` (配当利回り)
        *   `Close` (調整済み終値)

        統計量の種類:
        *   `_PeriodOpen`: 各期の最初の値
        *   `_PeriodHigh`: 各期の最大値
        *   `_PeriodLow`: 各期の最小値
        *   `_PeriodClose`: 各期の最後の値
        *   `_PeriodMean`: 各期の平均値

        Note:
            このメソッドを呼び出す前に、対象となる利回りカラムと`Close`、
            そして`ReportDate`が`self.data`に存在している必要があります。
            通常、`with_yields()` メソッドを呼び出すことで、これらの前提条件が
            満たされます。

        Returns:
            DataFrame: 統計量カラムが追加された、新しいDataFrameオブジェクト。
        """
        # 必要なカラムが存在するかチェック
        required_cols = {
            "BookValueYield",
            "EarningsYield",
            "DividendYield",
            "Close",
            "ReportDate",
        }
        if not required_cols.issubset(self.data.columns):
            missing = required_cols - set(self.data.columns)
            msg = f"必要な列が存在しません: {missing}。"
            msg += "事前に `with_yields()` メソッドなどを呼び出してください。"
            raise KeyError(msg)

        # 統計量を計算するカラムのリスト
        target_cols = ["BookValueYield", "EarningsYield", "DividendYield", "Close"]

        # 各カラムに対して統計量を計算する式を生成
        aggs: list[pl.Expr] = []
        for col in target_cols:
            aggs.extend(
                [
                    pl.col(col).drop_nulls().first().alias(f"{col}_PeriodOpen"),
                    pl.col(col).max().alias(f"{col}_PeriodHigh"),
                    pl.col(col).min().alias(f"{col}_PeriodLow"),
                    pl.col(col).drop_nulls().last().alias(f"{col}_PeriodClose"),
                    pl.col(col).mean().alias(f"{col}_PeriodMean"),
                ],
            )

        # CodeとReportDateでグループ化し、統計量を計算
        return self.data.group_by("Code", "ReportDate", maintain_order=True).agg(aggs)

    def with_period_stats(self) -> Self:
        """各期ごとの各種利回りおよび調整済み終値の統計量を計算し、列として追加する。

        このメソッドは、`Code`と`ReportDate`で定義される各期（決算期間）ごとに、
        以下の指標の統計量（始値、高値、安値、終値、平均値）を計算し、新しい列として追加します。

        対象指標:
        *   `BookValueYield` (純資産利回り)
        *   `EarningsYield` (収益利回り)
        *   `DividendYield` (配当利回り)
        *   `Close` (調整済み終値)

        統計量の種類:
        *   `_PeriodOpen`: 各期の最初の値
        *   `_PeriodHigh`: 各期の最大値
        *   `_PeriodLow`: 各期の最小値
        *   `_PeriodClose`: 各期の最後の値
        *   `_PeriodMean`: 各期の平均値

        Note:
            このメソッドを呼び出す前に、対象となる利回りカラムと`Close`、
            そして`ReportDate`が`self.data`に存在している必要があります。
            通常、`with_yields()` メソッドを呼び出すことで、これらの前提条件が
            満たされます。

        Returns:
            Self: 統計量カラムが追加された、新しいPricesオブジェクト。
        """
        stats = self.period_stats()
        data = self.data.join(stats, on=["Code", "ReportDate"], how="left")

        return self.__class__(data)
