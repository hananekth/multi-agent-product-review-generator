from typing import Optional

from pydantic import BaseModel, Field


class ProductInfo(BaseModel):
    title: str = Field(..., description="Title of the product information source.")
    url: str = Field(..., description="Link to the source.")
    summary: Optional[str] = Field(None, description="Summary of the information if available.")


class SearchResults(BaseModel):
    product_sources: list[ProductInfo]


class ScrapedContent(BaseModel):
    title: str = Field(..., description="Title of the source.")
    url: str = Field(..., description="Link to the source.")
    summary: Optional[str] = Field(None, description="Summary of the content if available.")
    content: Optional[str] = Field(
        None,
        description="Full content in markdown format. None if content is unavailable.",
    )

