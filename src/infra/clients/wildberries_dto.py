from __future__ import annotations

import json
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, computed_field

from src.domain.entities import Review


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

    _SOURCE_PAYLOAD_INCLUDE = {
        "id",
        "text",
        "pros",
        "cons",
        "product_valuation",
        "product_details",
        "user_name",
        "matching_size",
        "bables",
        "color",
        "subject_name",
        "has_photos",
        "has_video",
    }

    id: str
    product_id: str | None = Field(default=None, alias="productId")
    user_name: str | None = Field(default=None, alias="userName")
    product_valuation: int | None = Field(default=None, alias="productValuation")
    text: str | None = Field(default=None, alias="text")
    pros: str | None = Field(default=None, alias="pros")
    cons: str | None = Field(default=None, alias="cons")
    created_date: datetime | None = Field(default=None, alias="createdDate")
    language: str | None = Field(default=None, alias="language")
    product_details: ProductDetails | None = Field(default=None, alias="productDetails")
    photo_links: List[PhotoLink] | None = Field(default=None, alias="photoLinks")
    video: VideoInfo | None = Field(default=None, alias="video")
    matching_size: str | None = Field(default=None, alias="matchingSize")
    bables: List[str] | None = None
    color: str | None = Field(default=None, alias="color")
    state: str | None = Field(default=None, alias="state")
    subject_name: str | None = Field(default=None, alias="subjectName")

    @property
    def summary(self) -> str:
        return "\n".join(filter(None, [self.text, self.pros, self.cons]))

    @computed_field
    def has_photos(self) -> bool:
        return bool(self.photo_links)

    @computed_field
    def has_video(self) -> bool:
        if not self.video:
            return False
        return bool(self.video.link or self.video.preview_image or self.video.duration_sec is not None)

    def to_source_payload(self) -> str:
        payload = self.model_dump(by_alias=True, include=self._SOURCE_PAYLOAD_INCLUDE)
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str)

    def to_review(self) -> Review:
        return Review(id=self.id, text=self.to_source_payload(), summary=self.summary)
