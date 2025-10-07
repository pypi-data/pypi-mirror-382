"""
All API Schemas go here.
"""

from typing import List, Optional

from datadict_cli.lib.types import CatalogType, ItemType
from pydantic import BaseModel, ConfigDict, Field


# Output schemas for JSON serialization
class ItemRef(BaseModel):
    """Basic reference to an item for lineage metadata."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    type: ItemType
    key: Optional[str] = None
    catalog_id: str


class LineageOut(BaseModel):
    """Lineage relationship describing upstream/downstream items."""

    model_config = ConfigDict(extra="forbid")

    upstream: ItemRef
    downstream: ItemRef


class ItemOut(BaseModel):
    """
    Output schema for core item JSON serialization (without children)
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    type: ItemType
    name: str
    description: Optional[str] = None
    notes: Optional[str] = None
    properties: Optional[dict] = None
    lineage: Optional[List["LineageOut"]] = None


class ItemChildrenOut(BaseModel):
    """
    Output schema for item children list
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    children: List["ItemOut"] = Field(default_factory=list)


class TocItem(BaseModel):
    """
    Item for table of contents for catalog
    """

    children: List["TocItem"] = Field(default_factory=list)
    name: str
    id: str
    url: Optional[str] = (
        None  # Frontend URL for any resource is /<item.type>/<item.id>. not all toc items have url some are just for children
    )


class CatalogOut(BaseModel):
    """
    Output schema for catalog JSON serialization
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    type: CatalogType
    path: str
    toc: List[TocItem] = Field(default_factory=list)


class ProjectOut(BaseModel):
    """
    Output schema for project JSON serialization
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    version: str
    catalogs: list[str] = Field(default_factory=list)
