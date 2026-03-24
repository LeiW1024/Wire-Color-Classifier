import numpy as np

from app.pipeline import analyze_image


def test_pipeline_returns_colors_and_counts(sample_color_image: np.ndarray):
    result = analyze_image(sample_color_image)
    assert len(result["colors_found"]) > 0
    assert result["total_wires"] > 0
    assert isinstance(result["wire_counts"], dict)
    assert isinstance(result["bounding_boxes"], list)
    assert isinstance(result["annotated_image"], str)


def test_pipeline_handles_blank_image(blank_image: np.ndarray):
    result = analyze_image(blank_image)
    assert result["total_wires"] == 0
    assert len(result["colors_found"]) == 0
    assert result["bounding_boxes"] == []


def test_pipeline_bounding_boxes_match_counts(sample_color_image: np.ndarray):
    result = analyze_image(sample_color_image)
    total_from_boxes = len(result["bounding_boxes"])
    total_from_counts = sum(result["wire_counts"].values())
    assert total_from_boxes == total_from_counts == result["total_wires"]
