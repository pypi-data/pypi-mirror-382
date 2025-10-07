# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ProjectListResponse", "ProjectListResponseItem"]


class ProjectListResponseItem(BaseModel):
    id: str

    concurrency: int
    """The maximum number of sessions that this project can run concurrently."""

    created_at: datetime = FieldInfo(alias="createdAt")

    default_timeout: int = FieldInfo(alias="defaultTimeout")

    name: str

    owner_id: str = FieldInfo(alias="ownerId")

    updated_at: datetime = FieldInfo(alias="updatedAt")


ProjectListResponse: TypeAlias = List[ProjectListResponseItem]
