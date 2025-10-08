from typing import Literal
from pydantic import BaseModel


class SingleFilter(BaseModel):
    feat_name: str
    operator: Literal["=", "<", "<=", ">", ">=", "in", "between"]
    value: str | int | float | list[str] | list[int] | list[float]

    def sql(self) -> str:
        if self.operator == "between":
            return f'( "{self.feat_name}" > {self.value[0]} AND "{self.feat_name}" <= {self.value[1]} )'
        if isinstance(self.value, list):
            return f"{self.feat_name} {self.operator} ( {', '.join(self.value)})"
        return f'"{self.feat_name}"{self.operator}{self.value}'


class CombineFilter(BaseModel):
    combine: list[SingleFilter]
    invert: bool = False

    def sql(self, do_invert: bool = False) -> str:
        prefix = "not" if self.invert ^ do_invert else ""  # python xor
        if len(self.combine) == 1:
            return f" {prefix} {self.combine[0].sql()} "
        return f" {prefix} ( {' AND '.join([sf.sql() for sf in self.combine])} )"


class Filter(BaseModel):
    combine: list[CombineFilter]
    invert: bool

    def sql(self, do_invert: bool = False) -> str:
        prefix = "not" if self.invert ^ do_invert else ""  # python xor
        if len(self.combine) == 1:
            return f" {prefix} {self.combine[0].sql()} "
        return f" {prefix} ( {' OR '.join([sf.sql() for sf in self.combine])} )"
