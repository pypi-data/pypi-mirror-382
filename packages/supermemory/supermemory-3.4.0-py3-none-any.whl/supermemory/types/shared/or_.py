# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Or"]


class Or(BaseModel):
    or_: List[object] = FieldInfo(alias="OR")
