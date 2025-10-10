"""class Effect: OpenCV advanced image effects operations:
  ** neon glow, hdr, blur **
Copyright © 2025 John Liu
"""

from pathlib import Path

import cv2
import numpy as np

EFFECTS = {
    "neon": {"glow_intensity": 2.0, "edge_thickness": 2},
    "hdr": {"gamma": 1.2, "saturation": 1.0},
    "blur": {"ksize": (29, 29), "sigmaX": 0},
}


class Effect:
    @staticmethod
    def neon_glow_effect(img, glow_intensity=2.0, edge_thickness=2):
        """
        Creates neon glow effect using edge detection and Gaussian blur
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Edge detection with Canny
        edges = cv2.Canny(gray, 100, 200)

        # Dilate edges to make them thicker
        kernel = np.ones((edge_thickness, edge_thickness), np.uint8)
        thick_edges = cv2.dilate(edges, kernel, iterations=1)

        glow = cv2.GaussianBlur(thick_edges, (15, 15), 0)

        # Normalize and apply color
        glow_normalized = glow.astype(np.float32) / 255.0
        glow_colored = np.zeros_like(img, dtype=np.float32)

        # Apply neon colors (cyan, magenta, yellow)
        glow_colored[:, :, 0] = glow_normalized * 255  # Blue
        glow_colored[:, :, 1] = glow_normalized * 0  # Green
        glow_colored[:, :, 2] = glow_normalized * 255  # Red

        # Combine with original image
        result = cv2.addWeighted(
            img.astype(np.float32), 0.7, glow_colored, glow_intensity, 0
        )
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def hdr_effect(img, gamma=1.2, saturation=1.1):
        """
        Creates HDR-like effect with tone mapping and color enhancement
        """
        hdr = img.astype(np.float32) / 255.0  # convert to float

        # Reinhard tone mapping
        luminance = (
            0.2126 * hdr[:, :, 2] + 0.7152 * hdr[:, :, 1] + 0.0722 * hdr[:, :, 0]
        )
        # Prevent division by zero
        luminance += 1e-6

        tonemapped = hdr / luminance[:, :, np.newaxis]
        tonemapped = np.power(tonemapped, gamma)

        # Adjust saturation
        hsv = cv2.cvtColor((tonemapped * 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Local contrast enhancement using CLAHE
        lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_channel = clahe.apply(l_channel)
        lab = cv2.merge([l_channel, a_channel, b_channel])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        return result

    def apply_effects(self, img, in_path: Path, effect_name: str) -> tuple:
        """Apply image effects

        Args:
            img: Pillow image data
            in_path: image file path
            effect_name: "neon", "hdr", etc. string

        Returns:
            tuple: rgb image data, output file path
        """
        opencv_img = np.array(img)
        if opencv_img is None:
            raise ValueError(f"Failed to get opencv_img from {in_path}")
        if effect_name not in EFFECTS:
            raise ValueError(f"Bad {effect_name=}")
        key = effect_name
        val = EFFECTS[key]
        out_file = Path(f"{in_path.parent}/{in_path.stem}_{key}{in_path.suffix}")
        new_img = None
        rgb_img = None
        if effect_name == "neon":
            new_img = self.neon_glow_effect(opencv_img, **val)
        elif effect_name == "hdr":
            new_img = self.hdr_effect(opencv_img, **val)
        elif effect_name == "blur":
            tmp = cv2.cvtColor(opencv_img, cv2.COLOR_RGB2BGR)
            new_img = cv2.GaussianBlur(tmp, **val)
        if new_img is not None:
            rgb_img = cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB)
        return rgb_img, out_file
