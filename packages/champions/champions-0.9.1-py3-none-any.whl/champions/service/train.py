import itertools
import math
import sys
import time
from typing import Optional
from pydantic import BaseModel
from champions.model.datacard import DataCard, Feature
from champions.model.dataframes import (
    CombinedCategorizedFeature,
    ContCats,
    TrainDataframes,
    CategorizedFeature,
)
from champions.model.filter import CombineFilter, Filter, SingleFilter
from champions.model.settings import TrainSettings
from champions.model.champions import Champion, Spore
import polars as pl


import logging

from champions.service.darkwing import Darkwing

logger = logging.getLogger(__name__)


class Train(BaseModel):
    dc: DataCard
    settings: TrainSettings
    darkwing: Optional[Darkwing] = None

    def model_post_init(self, __context) -> None:
        self.darkwing = Darkwing(dc=self.dc)
        super().model_post_init(__context)

    def run(self):
        logger.info("start training")
        for n in range(self.settings.n):
            for cat in self.dc.target.values:
                if self.settings.champion_exists(target=cat, n=n):
                    logger.info(f"tree {n} for label {cat} already exists")
                    continue

                logger.info(f"train tree {n} for label {cat}")

                train_res = Champion(
                    spore=self.train_champion(
                        target_filter=self.gen_target_filter(cat=cat),
                        path_filter=[],
                    ),
                    target=cat,
                )
                self.settings.save_champion(champion=train_res, n=n)

    def gen_target_filter(self, cat) -> Filter:
        return Filter(
            combine=[
                CombineFilter(
                    combine=[
                        SingleFilter(
                            feat_name=self.dc.target.feature_name,
                            operator="=",
                            value=cat,
                        )
                    ]
                )
            ],
            invert=False,
        )

    def train_champion(
        self, target_filter: Filter, path_filter: list[Filter], depth: str = ""
    ) -> list[Spore]:
        train_df = self.darkwing.read_akt_train(
            targer_filter=target_filter,
            train_settings=self.settings,
            akt_filters=path_filter,
        )

        if train_df.is_final_size() or len(depth) >= self.settings.max_depth:
            score = train_df.score()
            logging.info(
                f"final spore depth: {depth}, {score} non target {train_df.non_target_df_size} target: {train_df.target_df_size}"
            )
            return [
                Spore(
                    cut=[fil.sql() for fil in path_filter],
                    score=score,
                    depth=depth,
                )
            ]

        self.cater(train_df=train_df)
        left_filter, right_filter = self.counter(train_df=train_df)
        left_spores = self.train_champion(
            target_filter=target_filter,
            path_filter=path_filter + [left_filter],
            depth=depth + "l",
        )
        right_spores = self.train_champion(
            target_filter=target_filter,
            path_filter=path_filter + [right_filter],
            depth=depth + "r",
        )
        return left_spores + right_spores

    def counter(self, train_df: TrainDataframes) -> tuple[Filter, Filter]:
        sorted_train_feats = sorted(
            train_df.train_features,
            key=lambda x: x.calc_diff(),
            reverse=True,
        )
        best_feat = sorted_train_feats[0]
        best_feat_diff = best_feat.calc_diff()

        for dim in range(2, self.settings.n_dims + 1):
            counter = 0
            for comb in itertools.combinations(sorted_train_feats, r=dim):
                counter += 1
                akt_feature = CombinedCategorizedFeature(
                    comb,
                    non_target_size=train_df.n_count_non_target,
                    target_size=train_df.n_count_target,
                )
                if akt_feature.calc_diff() > best_feat_diff:
                    best_feat = akt_feature
                    best_feat_diff = akt_feature.calc_diff()

                if (
                    self.settings.calcs_per_dim
                    and counter > self.settings.calcs_per_dim
                ):
                    break

        # with pl.Config(tbl_rows=100, tbl_cols=100):
        #    print(best_feat.diff_df)

        # print(best_feat_diff, train_df.n_count_non_target)
        # print(best_feat_diff, train_df.n_count_target)

        return best_feat.get_left_right_filter()

    def cater(self, train_df: TrainDataframes):
        for feat in self.dc.train_cat_feature:
            self.cat_cater(feat=feat, train_df=train_df)
        for feat in self.dc.train_con_feature:
            self.cont_cater(feat=feat, train_df=train_df)

    def cat_cater(self, feat: Feature, train_df: TrainDataframes):
        raise NotImplementedError("gibt noch net")
        df = train_df.non_target_df_cat
        print(df.select(pl.col(feat.name).value_counts()))

    def get_n_quantiles(self, series: pl.Series, n: int) -> ContCats:
        res = []
        label = ["0"]
        idx = 0
        for i in range(1, n):
            quantile = series.quantile(quantile=i / n, interpolation="lower")
            if quantile in res:
                continue
            idx += 1
            label.append(f"{idx}")
            res.append(quantile)
        return ContCats(cuts=res, labels=label, feat_name=series.name)

    def cont_cater(self, feat: Feature, train_df: TrainDataframes):
        categorized_feature = self.cont_cater_impl(feat=feat, train_df=train_df, n=2)

        for n in range(3,self.settings.n_cat+1):
            cat_feature = self.cont_cater_impl(feat=feat, train_df=train_df, n=n)
            if cat_feature.calc_diff() > categorized_feature.calc_diff():
                categorized_feature = cat_feature

        if not categorized_feature.is_diff_to_low():
            train_df.train_features.append(categorized_feature)


    def cont_cater_impl(
        self, feat: Feature, train_df: TrainDataframes, n: int
    ) -> CategorizedFeature:
        

        df_sorted = train_df.df_group[[feat.name,'weight']].sort(feat.name)
        cumulative_weights = df_sorted['weight'].cum_sum()

        res = []
        label = ["0"]
        idx = 0
        for i in range(1, n):
            quantile = i /n 
            index = (cumulative_weights >= quantile).arg_true()[0]

            
            if index > 0:
                weight_below = cumulative_weights[index - 1]
                value_below = df_sorted[feat.name][index - 1]
                value_at_index = df_sorted[feat.name][index]
                fraction = (quantile - weight_below) / (cumulative_weights[index] - weight_below)
                value =  value_below + fraction * (value_at_index - value_below)
            else:
                value = df_sorted[feat.name][0]
            if value in res:
                continue
            idx += 1
            label.append(f"{idx}")
            res.append(value)


        return train_df.create_categorized_features(
            feat=feat,
            cuts=ContCats(cuts=res, labels=label, feat_name=feat.name),
        )
