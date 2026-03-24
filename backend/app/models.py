# backend/app/models.py
from pydantic import BaseModel


class BoundingBoxResponse(BaseModel):
    color: str
    x: int
    y: int
    w: int
    h: int


class AnalyzeResponse(BaseModel):
    colors_found: list[str]
    wire_counts: dict[str, int]
    total_wires: int
    bounding_boxes: list[BoundingBoxResponse]
    annotated_image: str  # base64 encoded


class ColorRangeResponse(BaseModel):
    name: str
    lower: tuple[int, int, int]
    upper: tuple[int, int, int]


class ColorsResponse(BaseModel):
    colors: list[ColorRangeResponse]
