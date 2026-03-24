import cv2
import numpy as np

from app.pipeline import analyze_image


def _create_ground_truth_image():
    """Create a synthetic image with known wire colors and counts."""
    img = np.ones((400, 400, 3), dtype=np.uint8) * 200  # Gray background

    # Draw red wires (3 lines)
    for y in [50, 100, 150]:
        cv2.line(img, (20, y), (380, y), (0, 0, 255), 4)

    # Draw blue wires (2 lines)
    for y in [220, 270]:
        cv2.line(img, (20, y), (380, y), (255, 0, 0), 4)

    # Draw green wires (2 lines)
    for y in [330, 370]:
        cv2.line(img, (20, y), (380, y), (0, 255, 0), 4)

    expected = {"red": 3, "blue": 2, "green": 2}
    return img, expected


def test_accuracy_above_80_percent():
    """Fails the build if wire detection accuracy drops below 80%."""
    image, expected = _create_ground_truth_image()
    result = analyze_image(image)

    total_expected = sum(expected.values())
    total_detected = result["total_wires"]

    if total_expected > 0:
        accuracy = min(total_detected, total_expected) / total_expected
    else:
        accuracy = 1.0

    assert accuracy >= 0.80, (
        f"Accuracy {accuracy:.1%} is below 80% threshold. "
        f"Expected {total_expected} wires, detected {total_detected}."
    )


def test_no_phantom_colors_on_blank():
    """Ensure no colors are detected on a blank image."""
    blank = np.ones((200, 200, 3), dtype=np.uint8) * 255
    result = analyze_image(blank)
    assert result["total_wires"] == 0, (
        f"Detected {result['total_wires']} phantom wires on blank image"
    )
