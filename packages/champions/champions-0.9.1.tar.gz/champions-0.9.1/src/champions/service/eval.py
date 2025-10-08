import os
import sys
from typing import Optional
import duckdb
from pydantic import BaseModel
import yaml
from sklearn.metrics import roc_curve
import altair as alt

from champions.model.champions import Champion, Champions
from champions.model.datacard import DataCard
from champions.model.settings import EvalSettings
from champions.service.darkwing import Darkwing
import polars as pl
import logging

logger = logging.getLogger(__name__)


class Eval(BaseModel):
    dc: DataCard
    settings: EvalSettings
    darkwing: Optional[Darkwing] = None

    def model_post_init(self, __context) -> None:
        self.darkwing = Darkwing(dc=self.dc)
        os.makedirs(self.settings.out_folder, exist_ok=True)
        super().model_post_init(__context)

    def run(self):
        logger.info("Start Eval")

        df_res = self.darkwing._get_pl_eval_df(col_sql=self.dc.target.feature_name)
        # df_res = pl.read_parquet("test.parquet")
        plots = None

        for target in self.dc.target.values:
            logger.info(f"Evaluate target {target}")
            target_champions = self.load_champions(target=f"{target}")
            sr = self.darkwing.get_eval_sr(champions=target_champions)
            df_res = df_res.with_columns(sr)
            new_plot = self.plot_roc(df=df_res, target_label=target)
            new_plot.save(self.settings.out_folder / f"{target}_roc.html")
            if plots is None:
                plots = new_plot
            else:
                plots = plots + new_plot

        plots.save(self.settings.out_folder / "all_roc.html")

        if len(self.dc.target.values) > 1:
            df_multi_res = self.add_multi_class_result(
                df=df_res, target_values=self.dc.target.values
            )
            df_res = pl.concat(
                [df_res, df_multi_res],
                how="horizontal",
            )

            multi_res_plot = (
                df_res.group_by("label")
                .agg(pl.col("correct").sum() / pl.count())
                .sort("label")
                .plot.bar(x="label", y="correct")
            )
            prec = df_res["correct"].sum() / df_res["correct"].count()
            all_pred_labels = (
                alt.Chart(pl.DataFrame({"correct": [prec]}))
                .mark_rule()
                .encode(y="correct")
            )
            (multi_res_plot + all_pred_labels).save(
                self.settings.out_folder / "multi_class_result.html"
            )
        logger.info(f"{df_res}")

    def add_multi_class_result(self, df: pl.DataFrame, target_values: list[str | int]):
        greates = ", ".join([f'"{value}"' for value in target_values])
        cases = [
            f'WHEN "{value}" = GREATEST({greates}) THEN {value}'
            for value in target_values
        ]
        return (
            duckdb.sql(f"""
            SELECT
                label,
                CASE
                    {" \n ".join(cases)}
                END AS predicted_label
            FROM df
        """)
            .pl()
            .with_columns(
                (pl.col("label") == pl.col("predicted_label"))
                .cast(pl.Int64)
                .alias("correct")
            )
            .select("predicted_label", "correct")
        )

    def load_champions(self, target: str) -> Champions:
        data = {}
        for folder in self.settings.in_folders:
            target_folder = folder / target
            if not target_folder.exists():
                logger.error(f'folder {target_folder} does not exist. ')
                break
            for file in target_folder.glob("*.yaml"):
                f_name = str(file).strip('.yaml').replace('/','_')

                with open(file, "r") as f:
                    logger.debug(f"Load Champion from {file}")
                    data[f_name] = Champion(**yaml.safe_load(f))
        return Champions(champions=data, target=target)

    def plot_roc(self, df: pl.DataFrame, target_label: str | int):
        score_feat = f"{target_label}"
        df_plot = (
            duckdb.sql(f"""
            SELECT fp,tp
            FROM (
                SELECT
                    ROUND(SUM(CASE WHEN label == '{target_label}' THEN 1 ELSE 0 END) OVER (ORDER BY "{score_feat}" DESC) / SUM(CASE WHEN label == '{target_label}' THEN 1 ELSE 0 END) OVER (), 3)  AS tp,
                    ROUND(SUM(CASE WHEN label == '{target_label}' THEN 0 ELSE 1 END) OVER (ORDER BY "{score_feat}" DESC) / SUM(CASE WHEN label == '{target_label}' THEN 0 ELSE 1 END) OVER (), 3)  AS fp
                FROM df
                )
            GROUP BY fp,tp
            ORDER BY fp,tp
        """)
            .pl(
                # ).vstack(pl.DataFrame({'fp': 0.0, 'tp': 0.0})
            )
            .with_columns(pl.lit(score_feat).alias("target"))
        )
        plot = df_plot.plot.line(x="fp", y="tp", color="target").interactive()
        return plot
