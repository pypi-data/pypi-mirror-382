import itertools
import math
import time
import polars as pl
from pydantic import BaseModel
from dataclasses import dataclass

from champions.model.datacard import Feature
from champions.model.filter import CombineFilter, Filter, SingleFilter
import sys


class ContCats(BaseModel):
    cuts: list[float]
    labels: list[str]
    feat_name: str

    def cut(self, series: pl.Series) -> pl.Series:
        # return series.cut(self.cuts)
        return series.cut(self.cuts, labels=self.labels)

    def get_single_filter(self, i: int) -> SingleFilter:
        if i == 2 and len(self.cuts) == 1:
            sys.exit()

        if i == 0:
            return SingleFilter(
                feat_name=self.feat_name,
                operator="<=",
                value=self.cuts[i],
            )

        if i == len(self.labels) - 1:
            return SingleFilter(
                feat_name=self.feat_name,
                operator=">",
                value=self.cuts[i - 1],
            )
        return SingleFilter(
            feat_name=self.feat_name,
            operator="between",
            value=[self.cuts[i - 1], self.cuts[i]],
        )


class CategorizedFeatureMixin:
    diff_df: pl.DataFrame
    cut_list: list[ContCats]
    feature_list: list[str]

    def calc_diff(
        self,
    ) -> float:
        # self.diff_sr.entropy()
        return self.diff_df["diff"].abs().sum()

    def set_diff_df(
        self,
        df_count_target: pl.DataFrame,
        df_count_non_target: pl.DataFrame,
        join_on: list[str] | str,
    ):
        self.diff_df = (
            df_count_non_target.join(df_count_target, on=join_on, how="outer")
            .fill_null(0)
            .with_columns(
                (pl.col("proportion_right") - pl.col("proportion")).alias("diff"),
                pl.max_horizontal(
                    pl.col("proportion"), pl.col("proportion_right")
                ).alias("max_proportion"),
            )
        )

    def get_left_right_filter(self) -> tuple[Filter, Filter]:
        # for fea_name, cut in zip(self.feature_list, self.cut_list):

        target_res_df = self.diff_df.filter(pl.col("diff") > 0)[
            [f"{cut.feat_name}_right" for cut in self.cut_list]
        ]
        target_lists = [
            target_res_df[f"{cut.feat_name}_right"].to_list() for cut in self.cut_list
        ]
        target_list_tupels = [akt_tuple for akt_tuple in zip(*target_lists)]

        all_labels = [cut.labels for cut in self.cut_list]
        target_filter = []
        non_targer_filter = []

        for possible_combs in itertools.product(*all_labels):
            single_filter_list = [
                cut.get_single_filter(int(index))
                for index, cut in zip(possible_combs, self.cut_list)
            ]
            comb_filter = CombineFilter(combine=single_filter_list)
            if possible_combs in target_list_tupels:
                target_filter.append(comb_filter)
            else:
                non_targer_filter.append(comb_filter)

        return Filter(combine=non_targer_filter, invert=False), Filter(
            combine=target_filter, invert=False
        )


@dataclass
class CategorizedFeature(CategorizedFeatureMixin):
    feature: Feature
    cuts: ContCats
    target_sr: pl.Series
    non_target_sr: pl.Series

    def __post_init__(self):
        df_count_target = self.target_sr.value_counts(normalize=True)
        df_count_non_target = self.non_target_sr.value_counts(normalize=True)
        self.set_diff_df(
            df_count_target=df_count_target,
            df_count_non_target=df_count_non_target,
            join_on=self.feature.name,
        )


    @property
    def cut_list(self) -> list[ContCats]:
        return [self.cuts]

    def is_diff_to_low(self, threshold: float = 0.90) -> bool:
        max_wert = self.diff_df["max_proportion"].max()
        min_prop_of_max = self.diff_df.filter(pl.col("max_proportion") == max_wert)[
            "proportion", "proportion_right"
        ].min_horizontal()[0]
        return min_prop_of_max > threshold


class CombinedCategorizedFeature(CategorizedFeatureMixin):
    def __init__(
        self,
        train_features: tuple[CategorizedFeature],
        non_target_size: int,
        target_size: int,
    ):
        groub_by = [train.feature.name for train in train_features]
        non_target_df = pl.DataFrame([train.non_target_sr for train in train_features])

        df_count_non_target = (
            non_target_df.group_by(groub_by)
            .len(name="proportion")
            .with_columns(pl.col("proportion") / non_target_size)
        )
        target_df = pl.DataFrame([train.target_sr for train in train_features])
        df_count_target = (
            target_df.group_by(groub_by)
            .len(name="proportion")
            .with_columns(pl.col("proportion") / target_size)
        )
        self.set_diff_df(
            df_count_target=df_count_target,
            df_count_non_target=df_count_non_target,
            join_on=groub_by,
        )
        self.cut_list = [train.cuts for train in train_features]


class TrainDataframes:
    def __init__(
        self,
        target_df: pl.DataFrame,
        non_target_df: pl.DataFrame,
        frac_eval_cat: float,
        min_size: int,
    ):
        self.target_df_size = target_df.height
        self.non_target_df_size = non_target_df.height

        self.min_size = min_size

        self.n_count_target, n_group_target = self._calc_split(target_df.height, frac_eval_cat)
        self.target_df_count = target_df.head(self.n_count_target)
        target_df_group = target_df.tail(-self.n_count_target)
        #target_df_group['weight'] = 0.5 /  len(target_df_group)
 
        self.n_count_non_target, n_group_non_target = self._calc_split(non_target_df.height, frac_eval_cat)
        self.non_target_df_count = non_target_df.head(self.n_count_non_target)
        non_target_df_group = non_target_df.tail(-self.n_count_non_target)

        if n_group_non_target > 0 and n_group_target > 0:       

            self.df_group = pl.concat([target_df_group.with_columns(pl.lit(0.5 /n_group_target).alias('weight')),
                              non_target_df_group.with_columns(pl.lit(0.5 /n_group_non_target).alias('weight'))
                              ])
        self.train_features: list[CategorizedFeature] = []

    def create_categorized_features(
        self, feat: Feature, cuts: ContCats
    ) -> CategorizedFeature:
        target_sr = cuts.cut(series=self.target_df_count[feat.name])
        non_target_sr = cuts.cut(series=self.non_target_df_count[feat.name])
        return CategorizedFeature(
            feature=feat, cuts=cuts, target_sr=target_sr, non_target_sr=non_target_sr
        )

    def _calc_split(self, n: int, frac: float):
        split = round(n * frac)
        if split < 1:
            return 1 ,0
        if split >= n:
            return n - 1 , 1
        return split, n- split

    def score(self) -> float:
        if self.non_target_df_size + self.target_df_size == 0:
            return 0.0
        return (self.target_df_size - self.non_target_df_size) / (
            self.non_target_df_size + self.target_df_size
        )

    def is_final_size(self) -> bool:
        return (
            self.target_df_size < self.min_size
            or self.non_target_df_size < self.min_size
        )


class EvalDataframe:
    def __init__(self, df: pl.DataFrame, target: str | int) -> None:
        self.df = df
