"""
Visual effects that can be applied to camera frames.
Each effect is a function: frame_rgb -> frame_rgb
"""

import cv2
import numpy as np
import random


def apply_effect(frame, effect_key):
    """Apply a named effect to an RGB frame."""
    effects = {
        "none": lambda f: f,
        "noir": effect_noir,
        "thermal": effect_thermal,
        "glitch": effect_glitch,
        "pixel": effect_pixel,
        "vaporwave": effect_vaporwave,
    }
    fn = effects.get(effect_key, lambda f: f)
    return fn(frame.copy())


def effect_noir(frame):
    """Classic film noir — high contrast B&W with vignette."""
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    # Boost contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Add subtle vignette
    h, w = gray.shape
    X = cv2.getGaussianKernel(w, w * 0.5)
    Y = cv2.getGaussianKernel(h, h * 0.5)
    mask = Y * X.T
    mask = mask / mask.max()
    gray = (gray * mask).astype(np.uint8)

    # Add film grain
    noise = np.random.normal(0, 12, gray.shape).astype(np.int16)
    gray = np.clip(gray.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)


def effect_thermal(frame):
    """Thermal / infrared camera look."""
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    # Apply colormap (COLORMAP_JET for thermal look)
    thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    return cv2.cvtColor(thermal, cv2.COLOR_BGR2RGB)


def effect_glitch(frame):
    """Digital glitch — RGB channel shift + scanlines."""
    h, w = frame.shape[:2]
    result = frame.copy()

    # Channel offset
    shift = random.randint(3, 12)
    result[:, shift:, 0] = frame[:, :-shift, 0]  # Red shift right
    result[:, :-shift, 2] = frame[:, shift:, 2]   # Blue shift left

    # Random horizontal slice displacement
    for _ in range(random.randint(2, 6)):
        y = random.randint(0, h - 10)
        slice_h = random.randint(2, 15)
        offset = random.randint(-20, 20)
        if 0 <= y + slice_h < h:
            slc = result[y:y+slice_h].copy()
            result[y:y+slice_h] = np.roll(slc, offset, axis=1)

    # Scanlines
    result[::2] = (result[::2] * 0.7).astype(np.uint8)

    return result


def effect_pixel(frame):
    """Pixelation / mosaic effect."""
    h, w = frame.shape[:2]
    pixel_size = 12

    # Downscale then upscale
    small = cv2.resize(frame, (w // pixel_size, h // pixel_size),
                       interpolation=cv2.INTER_LINEAR)
    pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    return pixelated


def effect_vaporwave(frame):
    """Vaporwave aesthetic — pink/cyan tint + chromatic aberration."""
    h, w = frame.shape[:2]
    result = frame.copy().astype(np.float32)

    # Pink/cyan color wash
    result[:, :, 0] = np.clip(result[:, :, 0] * 1.1 + 30, 0, 255)  # Red boost
    result[:, :, 1] = np.clip(result[:, :, 1] * 0.7, 0, 255)       # Green reduce
    result[:, :, 2] = np.clip(result[:, :, 2] * 1.2 + 40, 0, 255)  # Blue boost

    result = result.astype(np.uint8)

    # Slight chromatic aberration
    shift = 3
    output = result.copy()
    output[:, shift:, 0] = result[:, :-shift, 0]
    output[:, :-shift, 2] = result[:, shift:, 2]

    # Horizontal scanline overlay
    output[::3] = (output[::3].astype(np.float32) * 0.85).astype(np.uint8)

    return output