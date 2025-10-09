from typing import Any, Dict, Optional, List

from pydantic import BaseModel, RootModel


class FilterConditionsV0(BaseModel):
    eq: Optional[Any] = None
    ne: Optional[Any] = None
    lt: Optional[Any] = None
    lte: Optional[Any] = None
    gt: Optional[Any] = None
    gte: Optional[Any] = None
    like: Optional[str] = None
    in_: Optional[List[Any]] = None
    is_null: Optional[bool] = None


class FiltersV0(RootModel):
    root: Dict[str, FilterConditionsV0]
