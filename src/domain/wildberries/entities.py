from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class ProductDetails(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    imt_id: int | None = Field(default=None, alias="imtId")
    nm_id: int | None = Field(default=None, alias="nmId")
    product_name: str | None = Field(default=None, alias="productName")
    supplier_article: str | None = Field(default=None, alias="supplierArticle")
    supplier_name: str | None = Field(default=None, alias="supplierName")
    brand_name: str | None = Field(default=None, alias="brandName")
    size: str | None = None


class PhotoLink(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    full_size: str | None = Field(default=None, alias="fullSize")
    mini_size: str | None = Field(default=None, alias="miniSize")


class VideoInfo(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    preview_image: str | None = Field(default=None, alias="previewImage")
    link: str = ""
    duration_sec: int | None = Field(default=None, alias="durationSec")


class WildberriesReview(BaseModel):
    """Customer review data from Wildberries."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    product_id: str | None = Field(default=None, alias="productId")
    author: str | None = Field(default=None, alias="userName")
    rating: int | None = Field(default=None, alias="productValuation")
    text: str | None = Field(default=None, alias="text")
    pros: str | None = Field(default=None, alias="pros")
    cons: str | None = Field(default=None, alias="cons")
    created_at: datetime | None = Field(default=None, alias="createdDate")
    language: str | None = Field(default=None, alias="language")
    product_details: ProductDetails | None = Field(default=None, alias="productDetails")
    photo_links: List[PhotoLink] | None = Field(default=None, alias="photoLinks")
    video: VideoInfo | None = Field(default=None, alias="video")
    matching_size: str | None = Field(default=None, alias="matchingSize")
    color: str | None = Field(default=None, alias="color")
    state: str | None = Field(default=None, alias="state")

    @property
    def summary(self) -> str:
        return "\n".join(filter(None, [self.text, self.pros, self.cons]))
