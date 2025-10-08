import logging
import sys
from typing import Any
import duckdb
from pydantic import BaseModel
import polars as pl

from champions.model.champions import Champions
from champions.model.datacard import DataCard
from champions.model.dataframes import EvalDataframe, TrainDataframes
from champions.model.filter import Filter, SingleFilter
from champions.model.settings import TrainSettings


logger = logging.getLogger(__name__)


class Darkwing(BaseModel):
    dc: DataCard
    df_train_cach: Any | None = None
    df_test_cache: Any | None = None

    def read_akt_train(
        self,
        targer_filter: Filter,
        train_settings: TrainSettings,
        akt_filters: list[Filter] = [],
    ) -> TrainDataframes:
        """
        Reads a list of CSV files into a DuckDB relation.

        Args:
            filepaths: A list of filepaths to CSV files.

        Returns:
            A DuckDB relation containing the data from all CSV files.
        """

        full_filters_target = [targer_filter.sql()] + [f.sql() for f in akt_filters]
        target_df = self._get_pl_train_df(
            full_filters=full_filters_target,
            max_eval_fit=train_settings.max_eval_fit,
        )
        full_filters_non_target = [targer_filter.sql(do_invert=True)] + [
            f.sql() for f in akt_filters
        ]
        non_target_df = self._get_pl_train_df(
            full_filters=full_filters_non_target,
            max_eval_fit=train_settings.max_eval_fit,
        )

        return TrainDataframes(
            target_df=target_df,
            non_target_df=non_target_df,
            frac_eval_cat=train_settings.frac_eval_cat,
            min_size=train_settings.min_eval_fit,
        )

    def _get_pl_train_df(self, full_filters: list[str], max_eval_fit) -> pl.DataFrame:
        df = self.get_cached_train_df()
        sql = f"""
                SELECT {", ".join(self.dc.feature_names)}
                FROM df
                WHERE {" AND ".join(full_filters)}
                LIMIT {max_eval_fit}; 
              """
        return duckdb.sql(sql).pl().sample(fraction=1, shuffle=True)

    def get_cached_train_df(self) -> pl.DataFrame:
        if self.df_train_cach is None:
            self.df_train_cach = pl.read_csv(",".join(self.dc.train_files))
        return self.df_train_cach

    def get_eval_sr(self, champions: Champions) -> EvalDataframe:
        df_sum = None

        for name, champion in champions.champions.items():
            case_sql = champion.get_sql(name)
            df = self._get_pl_eval_df(col_sql=case_sql)
            df_sum = df_sum.hstack(df) if df_sum is not None else df


        #return df_sum.transpose().median().transpose().to_series().alias(champions.target)

        return (df_sum.mean_horizontal()).alias(champions.target)

        # for feat_name, case_sql in champions.get_sql().items():
        #    df = self._get_pl_eval_df(case_sql=case_sql)
        #    logger.info(f"Evaluate {df}")
        #    logger.info(f"{case_sql}")

    def _get_pl_eval_df(self, col_sql: str) -> pl.DataFrame:
        df = self.get_cached_eval_df()
        sql = f"""
                SELECT {col_sql}\n
                FROM df; 
              """
        return duckdb.sql(sql).pl()


    def get_cached_eval_df(self) -> pl.DataFrame:
        if self.df_test_cache is None:
            self.df_test_cache = pl.read_csv(",".join(self.dc.test_files))
        return self.df_test_cache
