from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class AdUnitsFetchModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: Annotated[str, Field(min_length=2)]
    use_fingerprint_filtering: Annotated[bool, Field(default=False)]


class AdUnitsIntegrateModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ad_unit_ids: list[str]
    base_content: Annotated[str, Field(min_length=10)]
