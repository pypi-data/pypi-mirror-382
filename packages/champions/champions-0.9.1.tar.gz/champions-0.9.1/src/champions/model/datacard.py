import logging
from typing import Literal
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Feature(BaseModel):
    name: str
    statistical: Literal["category", "continus"]
    type: str


class Target(BaseModel):
    feature_name: str
    values: list[int | str]


class DataCard(BaseModel):
    features: list[Feature]
    infos: dict
    target: Target
    test_files: list[str]
    train_files: list[str]

    @property
    def feature_names(self) -> list[str]:
        return [f'"{feat.name}"' for feat in self.features]

    @property
    def train_feature(self) -> list[Feature]:
        return [feat for feat in self.features if feat.name != self.target.feature_name]

    @property
    def train_cat_feature(self) -> list[Feature]:
        return [
            feat
            for feat in self.features
            if feat.name != self.target.feature_name and feat.statistical == "category"
        ]

    @property
    def train_con_feature(self) -> list[Feature]:
        return [
            feat
            for feat in self.features
            if feat.name != self.target.feature_name and feat.statistical == "continus"
        ]
