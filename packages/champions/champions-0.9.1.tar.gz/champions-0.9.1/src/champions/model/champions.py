import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Spore(BaseModel):
    cut: list[str]
    score: float
    depth: str


class Champion(BaseModel):
    spore: list[Spore]
    target: str | int

    def get_sql(self, res_name: str) -> str:
        sql_ref = "CASE \n"
        for spore in self.spore:
            sql_ref += (
                f"  WHEN {' AND '.join(spore.cut)} THEN CAST({spore.score} AS DOUBLE)\n"
            )
        sql_ref += f"END AS {res_name}"
        return sql_ref


class Champions(BaseModel):
    champions: dict[str, Champion]
    target: str

    def get_sql(self) -> dict[str, str]:
        return {
            f"res_{name}": champion.get_sql(f"res_{name}")
            for name, champion in self.champions.items()
        }
