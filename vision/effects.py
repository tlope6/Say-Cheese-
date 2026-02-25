"""
Visual effects that can be applied to camera frames.
Each effect is a function: frame_rgb -> frame_rgb
Now includes retro arcade effects: CRT and Neon Edge.
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
        "crt": effect_crt,
        "neon_edge": effect_neon_edge,
    }
    fn = effects.get(effect_key, lambda f: f)
    return fn(frame.copy())


def effect_noir(frame):
    """Classic film noir — high contrast B&W with vignette."""
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    h, w = gray.shape
    X = cv2.getGaussianKernel(w, w * 0.5)
    Y = cv2.getGaussianKernel(h, h * 0.5)
    mask = Y * X.T
    mask = mask / mask.max()
    gray = (gray * mask).astype(np.uint8)

    noise = np.random.normal(0, 12, gray.shape).astype(np.int16)
    gray = np.clip(gray.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)


def effect_thermal(frame):
    """Thermal / infrared camera look."""
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    return cv2.cvtColor(thermal, cv2.COLOR_BGR2RGB)


def effect_glitch(frame):
    """Digital glitch — RGB channel shift + scanlines."""
    h, w = frame.shape[:2]
    result = frame.copy()

    shift = random.randint(3, 12)
    result[:, shift:, 0] = frame[:, :-shift, 0]
    result[:, :-shift, 2] = frame[:, shift:, 2]

    for _ in range(random.randint(2, 6)):
        y = random.randint(0, h - 10)
        slice_h = random.randint(2, 15)
        offset = random.randint(-20, 20)
        if 0 <= y + slice_h < h:
            slc = result[y:y+slice_h].copy()
            result[y:y+slice_h] = np.roll(slc, offset, axis=1)

    result[::2] = (result[::2] * 0.7).astype(np.uint8)

    return result


def effect_pixel(frame):
    """Pixelation / mosaic — extra chunky for retro feel."""
    h, w = frame.shape[:2]
    pixel_size = 8

    small = cv2.resize(frame, (w // pixel_size, h // pixel_size),
                       interpolation=cv2.INTER_LINEAR)
    pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    return pixelated


def effect_vaporwave(frame):
    """Vaporwave aesthetic — pink/cyan tint + chromatic aberration."""
    h, w = frame.shape[:2]
    result = frame.copy().astype(np.float32)

    result[:, :, 0] = np.clip(result[:, :, 0] * 1.1 + 30, 0, 255)
    result[:, :, 1] = np.clip(result[:, :, 1] * 0.7, 0, 255)
    result[:, :, 2] = np.clip(result[:, :, 2] * 1.2 + 40, 0, 255)

    result = result.astype(np.uint8)

    shift = 3
    output = result.copy()
    output[:, shift:, 0] = result[:, :-shift, 0]
    output[:, :-shift, 2] = result[:, shift:, 2]

    output[::3] = (output[::3].astype(np.float32) * 0.85).astype(np.uint8)

    return output


def effect_crt(frame):
    """
    CRT monitor effect — scanlines, slight barrel distortion,
    green phosphor tint, screen flicker.
    """
    h, w = frame.shape[:2]
    result = frame.copy().astype(np.float32)

    # Green phosphor tint
    result[:, :, 0] *= 0.6   # reduce red
    result[:, :, 1] *= 1.1   # boost green
    result[:, :, 2] *= 0.5   # reduce blue

    result = np.clip(result, 0, 255).astype(np.uint8)

    # Heavy scanlines (every other row darkened)
    result[::2] = (result[::2].astype(np.float32) * 0.55).astype(np.uint8)

    # Thinner bright lines between scanlines
    result[1::4] = np.clip(
        result[1::4].astype(np.int16) + 15, 0, 255
    ).astype(np.uint8)

    # Random flicker (subtle brightness variation)
    flicker = random.uniform(0.92, 1.0)
    result = (result.astype(np.float32) * flicker).astype(np.uint8)

    # Vignette (CRT screens darken at edges)
    X = cv2.getGaussianKernel(w, w * 0.6)
    Y = cv2.getGaussianKernel(h, h * 0.6)
    mask = Y * X.T
    mask = mask / mask.max()
    mask = np.stack([mask] * 3, axis=-1)
    result = (result.astype(np.float32) * mask).astype(np.uint8)

    # Slight noise (static)
    noise = np.random.randint(0, 8, result.shape, dtype=np.uint8)
    result = cv2.add(result, noise)

    return result


def effect_neon_edge(frame):
    """
    Neon edge detection — black background with glowing colored edges.
    Looks like a neon sign / wireframe version of you.
    """
    h, w = frame.shape[:2]

    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Canny edge detection
    edges = cv2.Canny(gray, 50, 150)

    # Dilate edges slightly for glow base
    kernel = np.ones((2, 2), np.uint8)
    edges_thick = cv2.dilate(edges, kernel, iterations=1)

    # Create color channels from edges with different offsets for chromatic look
    result = np.zeros((h, w, 3), dtype=np.uint8)

    # Cyan edges (shifted slightly)
    result[:, 2:, 2] = edges_thick[:, :-2]  # blue channel, shifted right
    result[:, :, 1] = edges_thick             # green channel, centered

    # Pink/magenta edges from a second pass
    edges2 = cv2.Canny(gray, 80, 200)
    result[:, :-2, 0] = edges2[:, 2:]        # red channel, shifted left

    # Add glow by blurring and adding back
    glow = cv2.GaussianBlur(result, (7, 7), 0)
    result = cv2.addWeighted(result, 1.0, glow, 0.8, 0)

    # Boost brightness
    result = np.clip(result.astype(np.int16) * 2, 0, 255).astype(np.uint8)

    return result