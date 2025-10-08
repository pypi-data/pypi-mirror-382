# Auto-generated Python type stubs for zignal
# Generated from Zig source code using compile-time reflection
# Do not modify manually - regenerate using: zig build generate-stubs

from __future__ import annotations

from enum import IntEnum
from typing import Literal, TypeAlias

import numpy as np
from numpy.typing import NDArray

# Type aliases for common patterns
Point: TypeAlias = tuple[float, float]
Size: TypeAlias = tuple[int, int]
RgbTuple: TypeAlias = tuple[int, int, int]
RgbaTuple: TypeAlias = tuple[int, int, int, int]


class PixelIterator:
    """
Iterator over image pixels yielding (row, col, pixel) in native format.

This iterator walks the image in row-major order (top-left to bottom-right).
For views, iteration respects the view bounds and the underlying stride, so
you only traverse the visible sub-rectangle without copying.

## Examples

```python
image = Image(2, 3, Rgb(255, 0, 0), format=zignal.Rgb)
for r, c, pixel in image:
    print(f"image[{r}, {c}] = {pixel}")
```

## Notes
- Returned by `iter(Image)` / `Image.__iter__()`\n
- Use `Image.to_numpy()` when you need bulk numeric processing for best performance.
    """
    def __iter__(self) -> PixelIterator:
        """Return self as an iterator."""
        ...
    def __next__(self) -> tuple[int, int, Color]:
        """Return the next (row, col, pixel) where pixel is native: int | Rgb | Rgba."""
        ...

class Rectangle:
    """A rectangle defined by its left, top, right, and bottom coordinates.
    """
    @classmethod
    def init_center(cls, x: float, y: float, width: float, height: float) -> Rectangle:
        """Create a Rectangle from center coordinates.

## Parameters
- `x` (float): Center x coordinate
- `y` (float): Center y coordinate
- `width` (float): Rectangle width
- `height` (float): Rectangle height

## Examples
```python
# Create a 100x50 rectangle centered at (50, 50)
rect = Rectangle.init_center(50, 50, 100, 50)
# This creates Rectangle(0, 25, 100, 75)
```"""
        ...
    def is_empty(self) -> bool:
        """Check if the rectangle is ill-formed (empty).

A rectangle is considered empty if its left >= right or top >= bottom.

## Examples
```python
rect1 = Rectangle(0, 0, 100, 100)
print(rect1.is_empty())  # False

rect2 = Rectangle(100, 100, 100, 100)
print(rect2.is_empty())  # True
```"""
        ...
    def area(self) -> float:
        """Calculate the area of the rectangle.

## Examples
```python
rect = Rectangle(0, 0, 100, 50)
print(rect.area())  # 5000.0
```"""
        ...
    def contains(self, x: float, y: float) -> bool:
        """Check if a point is inside the rectangle.

Uses exclusive bounds for right and bottom edges.

## Parameters
- `x` (float): X coordinate to check
- `y` (float): Y coordinate to check

## Examples
```python
rect = Rectangle(0, 0, 100, 100)
print(rect.contains(50, 50))   # True - inside
print(rect.contains(100, 50))  # False - on right edge (exclusive)
print(rect.contains(99.9, 99.9))  # True - just inside
print(rect.contains(150, 50))  # False - outside
```"""
        ...
    def grow(self, amount: float) -> Rectangle:
        """Create a new rectangle expanded by the given amount.

## Parameters
- `amount` (float): Amount to expand each border by

## Examples
```python
rect = Rectangle(50, 50, 100, 100)
grown = rect.grow(10)
# Creates Rectangle(40, 40, 110, 110)
```"""
        ...
    def shrink(self, amount: float) -> Rectangle:
        """Create a new rectangle shrunk by the given amount.

## Parameters
- `amount` (float): Amount to shrink each border by

## Examples
```python
rect = Rectangle(40, 40, 110, 110)
shrunk = rect.shrink(10)
# Creates Rectangle(50, 50, 100, 100)
```"""
        ...
    def intersect(self, other: Rectangle | tuple[float, float, float, float]) -> Rectangle | None:
        """Calculate the intersection of this rectangle with another.

## Parameters
- `other` (Rectangle | tuple[float, float, float, float]): The other rectangle to intersect with

## Examples
```python
rect1 = Rectangle(0, 0, 100, 100)
rect2 = Rectangle(50, 50, 150, 150)
intersection = rect1.intersect(rect2)
# Returns Rectangle(50, 50, 100, 100)

# Can also use a tuple
intersection = rect1.intersect((50, 50, 150, 150))
# Returns Rectangle(50, 50, 100, 100)

rect3 = Rectangle(200, 200, 250, 250)
result = rect1.intersect(rect3)  # Returns None (no overlap)
```"""
        ...
    def iou(self, other: Rectangle | tuple[float, float, float, float]) -> float:
        """Calculate the Intersection over Union (IoU) with another rectangle.

## Parameters
- `other` (Rectangle | tuple[float, float, float, float]): The other rectangle to calculate IoU with

## Returns
- `float`: IoU value between 0.0 (no overlap) and 1.0 (identical rectangles)

## Examples
```python
rect1 = Rectangle(0, 0, 100, 100)
rect2 = Rectangle(50, 50, 150, 150)
iou = rect1.iou(rect2)  # Returns ~0.143

# Can also use a tuple
iou = rect1.iou((0, 0, 100, 100))  # Returns 1.0 (identical)

# Non-overlapping rectangles
rect3 = Rectangle(200, 200, 250, 250)
iou = rect1.iou(rect3)  # Returns 0.0
```"""
        ...
    def overlaps(self, other: Rectangle | tuple[float, float, float, float], iou_thresh: float = 0.5, coverage_thresh: float = 1.0) -> bool:
        """Check if this rectangle overlaps with another based on IoU and coverage thresholds.

## Parameters
- `other` (Rectangle | tuple[float, float, float, float]): The other rectangle to check overlap with
- `iou_thresh` (float, optional): IoU threshold for considering overlap. Default: 0.5
- `coverage_thresh` (float, optional): Coverage threshold for considering overlap. Default: 1.0

## Returns
- `bool`: True if rectangles overlap enough based on the thresholds

## Description
Returns True if any of these conditions are met:
- IoU > iou_thresh
- intersection.area / self.area > coverage_thresh
- intersection.area / other.area > coverage_thresh

## Examples
```python
rect1 = Rectangle(0, 0, 100, 100)
rect2 = Rectangle(50, 50, 150, 150)

# Default thresholds
overlaps = rect1.overlaps(rect2)  # Uses IoU > 0.5

# Custom IoU threshold
overlaps = rect1.overlaps(rect2, iou_thresh=0.1)  # True

# Coverage threshold (useful for small rectangle inside large)
small = Rectangle(25, 25, 75, 75)
overlaps = rect1.overlaps(small, coverage_thresh=0.9)  # True (small is 100% covered)

# Can use tuple
overlaps = rect1.overlaps((50, 50, 150, 150), iou_thresh=0.1)
```"""
        ...
    @property
    def left(self) -> float: ...
    @property
    def top(self) -> float: ...
    @property
    def right(self) -> float: ...
    @property
    def bottom(self) -> float: ...
    @property
    def width(self) -> float: ...
    @property
    def height(self) -> float: ...
    def __init__(self, left: float, top: float, right: float, bottom: float) -> None:
        """Initialize a Rectangle with specified coordinates.

Creates a rectangle from its bounding coordinates. The rectangle is defined
by four values: left (x-min), top (y-min), right (x-max), and bottom (y-max).
The right and bottom bounds are exclusive.

## Parameters
- `left` (float): Left edge x-coordinate (inclusive)
- `top` (float): Top edge y-coordinate (inclusive)
- `right` (float): Right edge x-coordinate (exclusive)
- `bottom` (float): Bottom edge y-coordinate (exclusive)

## Examples
```python
# Create a rectangle from (10, 20) to (110, 70)
rect = Rectangle(10, 20, 110, 70)
print(rect.width)  # 100.0 (110 - 10)
print(rect.height)  # 50.0 (70 - 20)
print(rect.contains(109.9, 69.9))  # True
print(rect.contains(110, 70))  # False

# Create a square
square = Rectangle(0, 0, 50, 50)
print(square.width)  # 50.0
```

## Notes
- The constructor validates that right >= left and bottom >= top
- Use Rectangle.init_center() for center-based construction
- Coordinates follow image convention: origin at top-left, y increases downward
- Right and bottom bounds are exclusive"""
        ...

class BitmapFont:
    """Bitmap font for text rendering. Supports BDF/PCF formats, including optional gzip-compressed files (.bdf.gz, .pcf.gz).
    """
    @classmethod
    def load(cls, path: str) -> BitmapFont:
        """Load a bitmap font from file.

Supports BDF (Bitmap Distribution Format) and PCF (Portable Compiled Format) files, including
optionally gzip-compressed variants (e.g., `.bdf.gz`, `.pcf.gz`).

## Parameters
- `path` (str): Path to the font file

## Examples
```python
font = BitmapFont.load("unifont.bdf")
canvas.draw_text("Hello", (10, 10), font, (255, 255, 255))
```"""
        ...
    @classmethod
    def font8x8(cls) -> BitmapFont:
        """Get the built-in default 8x8 bitmap font with all available characters.

This font includes ASCII, extended ASCII, Greek, and box drawing characters.

## Examples
```python
font = BitmapFont.font8x8()
canvas.draw_text("Hello World!", (10, 10), font, (255, 255, 255))
```"""
        ...

class Interpolation(IntEnum):
    """Interpolation methods for image resizing.

Performance and quality comparison:

| Method            | Quality | Speed | Best Use Case       | Overshoot |
|-------------------|---------|-------|---------------------|-----------|
| NEAREST_NEIGHBOR  | ★☆☆☆☆   | ★★★★★ | Pixel art, masks    | No        |
| BILINEAR          | ★★☆☆☆   | ★★★★☆ | Real-time, preview  | No        |
| BICUBIC           | ★★★☆☆   | ★★★☆☆ | General purpose     | Yes       |
| CATMULL_ROM       | ★★★★☆   | ★★★☆☆ | Natural images      | No        |
| MITCHELL          | ★★★★☆   | ★★☆☆☆ | Balanced quality    | Yes       |
| LANCZOS           | ★★★★★   | ★☆☆☆☆ | High-quality resize | Yes       |

Note: "Overshoot" means the filter can create values outside the input range,
which can cause ringing artifacts but may also enhance sharpness."""
    NEAREST_NEIGHBOR = 0
    """Fastest, pixelated, good for pixel art"""
    BILINEAR = 1
    """Fast, smooth, good for real-time"""
    BICUBIC = 2
    """Balanced quality/speed, general purpose"""
    CATMULL_ROM = 3
    """Sharp, good for natural images"""
    MITCHELL = 4
    """High quality, reduces ringing"""
    LANCZOS = 5
    """Highest quality, slowest, for final output"""

class Blending(IntEnum):
    """Blending modes for color composition.

## Overview
These modes determine how colors are combined when blending. Each mode produces
different visual effects useful for various image compositing operations.

## Blend Modes

| Mode        | Description                                            | Best Use Case     |
|-------------|--------------------------------------------------------|-------------------|
| NONE        | No blending; overlay replaces base pixel               | Direct copy       |
| NORMAL      | Standard alpha blending with transparency              | Layering images   |
| MULTIPLY    | Darkens by multiplying colors (white has no effect)    | Shadows, darkening|
| SCREEN      | Lightens by inverting, multiplying, then inverting     | Highlights, glow  |
| OVERLAY     | Combines multiply and screen based on base color       | Contrast enhance  |
| SOFT_LIGHT  | Gentle contrast adjustment                             | Subtle lighting   |
| HARD_LIGHT  | Like overlay but uses overlay color to determine blend | Strong contrast   |
| COLOR_DODGE | Brightens base color based on overlay                  | Bright highlights |
| COLOR_BURN  | Darkens base color based on overlay                    | Deep shadows      |
| DARKEN      | Selects darker color per channel                       | Remove white      |
| LIGHTEN     | Selects lighter color per channel                      | Remove black      |
| DIFFERENCE  | Subtracts darker from lighter color                    | Invert/compare    |
| EXCLUSION   | Similar to difference but with lower contrast          | Soft inversion    |

## Examples
```python
base = zignal.Rgb(100, 100, 100)
overlay = zignal.Rgba(200, 50, 150, 128)

# Apply different blend modes
normal = base.blend(overlay, zignal.Blending.NORMAL)
multiply = base.blend(overlay, zignal.Blending.MULTIPLY)
screen = base.blend(overlay, zignal.Blending.SCREEN)
```

## Notes
- `NONE` performs a direct copy and is the default for APIs that accept blending
- All other blend modes respect alpha channel for proper compositing
- Result color type matches the base color type
- Overlay must be RGBA or convertible to RGBA"""
    NONE = 0
    """No blending; overlay replaces base pixel"""
    NORMAL = 1
    """Standard alpha blending with transparency"""
    MULTIPLY = 2
    """Darkens by multiplying colors"""
    SCREEN = 3
    """Lightens by inverting, multiplying, inverting"""
    OVERLAY = 4
    """Combines multiply and screen for contrast"""
    SOFT_LIGHT = 5
    """Gentle contrast adjustment"""
    HARD_LIGHT = 6
    """Strong contrast, like overlay but reversed"""
    COLOR_DODGE = 7
    """Brightens base color, creates glow effects"""
    COLOR_BURN = 8
    """Darkens base color, creates deep shadows"""
    DARKEN = 9
    """Selects darker color per channel"""
    LIGHTEN = 10
    """Selects lighter color per channel"""
    DIFFERENCE = 11
    """Subtracts colors for inversion effect"""
    EXCLUSION = 12
    """Like difference but with lower contrast"""

class BorderMode(IntEnum):
    """Border handling strategies used by convolution and order-statistic filters.

- `ZERO`: Pad with zeros outside the source image.
- `REPLICATE`: Repeat the nearest edge pixel.
- `MIRROR`: Reflect pixels at the border (default).
- `WRAP`: Wrap around to the opposite edge."""
    ZERO = 0
    """Pad with zeros outside the image"""
    REPLICATE = 1
    """Repeat the nearest edge pixel"""
    MIRROR = 2
    """Reflect pixels across the border"""
    WRAP = 3
    """Wrap around to the opposite edge"""

class DrawMode(IntEnum):
    """Rendering quality mode for drawing operations.

## Attributes
- `FAST` (int): Fast rendering without antialiasing (value: 0)
- `SOFT` (int): High-quality rendering with antialiasing (value: 1)

## Notes
- FAST mode provides pixel-perfect rendering with sharp edges
- SOFT mode provides smooth, antialiased edges for better visual quality
- Default mode is FAST for performance"""
    FAST = 0
    """Fast rendering with hard edges"""
    SOFT = 1
    """Antialiased rendering with smooth edges"""

class OptimizationPolicy(IntEnum):
    """Optimization policy for assignment problems.

Determines whether to minimize or maximize the total cost."""
    MIN = 0
    """Minimize total cost"""
    MAX = 1
    """Maximize total cost (profit)"""

class MotionBlur:
    """Motion blur effect configuration.

Use the static factory methods to create motion blur configurations:
- `MotionBlur.linear(angle, distance)` - Linear motion blur
- `MotionBlur.radial_zoom(center, strength)` - Radial zoom blur
- `MotionBlur.radial_spin(center, strength)` - Radial spin blur

## Examples
```python
import math
from zignal import Image, MotionBlur

img = Image.load("photo.jpg")

# Linear motion blur
horizontal = img.motion_blur(MotionBlur.linear(angle=0, distance=30))
vertical = img.motion_blur(MotionBlur.linear(angle=math.pi/2, distance=20))

# Radial zoom blur
zoom = img.motion_blur(MotionBlur.radial_zoom(center=(0.5, 0.5), strength=0.7))
zoom_default = img.motion_blur(MotionBlur.radial_zoom())  # Uses defaults

# Radial spin blur
spin = img.motion_blur(MotionBlur.radial_spin(center=(0.3, 0.7), strength=0.5))
```
    """
    def linear(angle: float, distance: int) -> MotionBlur:
        """Create linear motion blur configuration."""
        ...
    def radial_zoom(center: tuple[float, float] = (0.5, 0.5), strength: float = 0.5) -> MotionBlur:
        """Create radial zoom blur configuration."""
        ...
    def radial_spin(center: tuple[float, float] = (0.5, 0.5), strength: float = 0.5) -> MotionBlur:
        """Create radial spin blur configuration."""
        ...
    @property
    def type(self) -> Literal['linear', 'radial_zoom', 'radial_spin']: ...
    @property
    def angle(self) -> float | None: ...
    @property
    def distance(self) -> int | None: ...
    @property
    def center(self) -> tuple[float, float] | None: ...
    @property
    def strength(self) -> float | None: ...
    def __repr__(self) -> str: ...

class Rgb:
    """RGB color in sRGB colorspace with components in range 0-255"""
    def __init__(self, r: int, g: int, b: int) -> None: ...
    @property
    def r(self) -> int: ...
    @r.setter
    def r(self, value: int) -> None: ...
    @property
    def g(self) -> int: ...
    @g.setter
    def g(self, value: int) -> None: ...
    @property
    def b(self) -> int: ...
    @b.setter
    def b(self, value: int) -> None: ...
    def to_rgba(self, alpha: int = 255) -> Rgba:
        """Convert to RGBA color space with the given alpha value (0-255, default: 255)"""
        ...
    def to_hsl(self) -> Hsl:
        """Convert to `Hsl` color space."""
        ...
    def to_hsv(self) -> Hsv:
        """Convert to `Hsv` color space."""
        ...
    def to_lab(self) -> Lab:
        """Convert to `Lab` color space."""
        ...
    def to_lch(self) -> Lch:
        """Convert to `Lch` color space."""
        ...
    def to_lms(self) -> Lms:
        """Convert to `Lms` color space."""
        ...
    def to_oklab(self) -> Oklab:
        """Convert to `Oklab` color space."""
        ...
    def to_oklch(self) -> Oklch:
        """Convert to `Oklch` color space."""
        ...
    def to_xyb(self) -> Xyb:
        """Convert to `Xyb` color space."""
        ...
    def to_xyz(self) -> Xyz:
        """Convert to `Xyz` color space."""
        ...
    def to_ycbcr(self) -> Ycbcr:
        """Convert to `Ycbcr` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def blend(self, overlay: Rgba | tuple[int, int, int, int], mode: Blending = Blending.NORMAL) -> Rgb: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Rgba:
    """RGBA color with alpha channel, components in range 0-255"""
    def __init__(self, r: int, g: int, b: int, a: int) -> None: ...
    @property
    def r(self) -> int: ...
    @r.setter
    def r(self, value: int) -> None: ...
    @property
    def g(self) -> int: ...
    @g.setter
    def g(self, value: int) -> None: ...
    @property
    def b(self) -> int: ...
    @b.setter
    def b(self, value: int) -> None: ...
    @property
    def a(self) -> int: ...
    @a.setter
    def a(self, value: int) -> None: ...
    def to_rgb(self) -> Rgb:
        """Convert to `Rgb` color space."""
        ...
    def to_hsl(self) -> Hsl:
        """Convert to `Hsl` color space."""
        ...
    def to_hsv(self) -> Hsv:
        """Convert to `Hsv` color space."""
        ...
    def to_lab(self) -> Lab:
        """Convert to `Lab` color space."""
        ...
    def to_lch(self) -> Lch:
        """Convert to `Lch` color space."""
        ...
    def to_lms(self) -> Lms:
        """Convert to `Lms` color space."""
        ...
    def to_oklab(self) -> Oklab:
        """Convert to `Oklab` color space."""
        ...
    def to_oklch(self) -> Oklch:
        """Convert to `Oklch` color space."""
        ...
    def to_xyb(self) -> Xyb:
        """Convert to `Xyb` color space."""
        ...
    def to_xyz(self) -> Xyz:
        """Convert to `Xyz` color space."""
        ...
    def to_ycbcr(self) -> Ycbcr:
        """Convert to `Ycbcr` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def blend(self, overlay: Rgba | tuple[int, int, int, int], mode: Blending = Blending.NORMAL) -> Rgba: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Hsl:
    """HSL (Hue-Saturation-Lightness) color representation"""
    def __init__(self, h: float, s: float, l: float) -> None: ...
    @property
    def h(self) -> float: ...
    @h.setter
    def h(self, value: float) -> None: ...
    @property
    def s(self) -> float: ...
    @s.setter
    def s(self, value: float) -> None: ...
    @property
    def l(self) -> float: ...
    @l.setter
    def l(self, value: float) -> None: ...
    def to_rgb(self) -> Rgb:
        """Convert to `Rgb` color space."""
        ...
    def to_rgba(self, alpha: int = 255) -> Rgba:
        """Convert to RGBA color space with the given alpha value (0-255, default: 255)"""
        ...
    def to_hsv(self) -> Hsv:
        """Convert to `Hsv` color space."""
        ...
    def to_lab(self) -> Lab:
        """Convert to `Lab` color space."""
        ...
    def to_lch(self) -> Lch:
        """Convert to `Lch` color space."""
        ...
    def to_lms(self) -> Lms:
        """Convert to `Lms` color space."""
        ...
    def to_oklab(self) -> Oklab:
        """Convert to `Oklab` color space."""
        ...
    def to_oklch(self) -> Oklch:
        """Convert to `Oklch` color space."""
        ...
    def to_xyb(self) -> Xyb:
        """Convert to `Xyb` color space."""
        ...
    def to_xyz(self) -> Xyz:
        """Convert to `Xyz` color space."""
        ...
    def to_ycbcr(self) -> Ycbcr:
        """Convert to `Ycbcr` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def blend(self, overlay: Rgba | tuple[int, int, int, int], mode: Blending = Blending.NORMAL) -> Hsl: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Hsv:
    """HSV (Hue-Saturation-Value) color representation"""
    def __init__(self, h: float, s: float, v: float) -> None: ...
    @property
    def h(self) -> float: ...
    @h.setter
    def h(self, value: float) -> None: ...
    @property
    def s(self) -> float: ...
    @s.setter
    def s(self, value: float) -> None: ...
    @property
    def v(self) -> float: ...
    @v.setter
    def v(self, value: float) -> None: ...
    def to_rgb(self) -> Rgb:
        """Convert to `Rgb` color space."""
        ...
    def to_rgba(self, alpha: int = 255) -> Rgba:
        """Convert to RGBA color space with the given alpha value (0-255, default: 255)"""
        ...
    def to_hsl(self) -> Hsl:
        """Convert to `Hsl` color space."""
        ...
    def to_lab(self) -> Lab:
        """Convert to `Lab` color space."""
        ...
    def to_lch(self) -> Lch:
        """Convert to `Lch` color space."""
        ...
    def to_lms(self) -> Lms:
        """Convert to `Lms` color space."""
        ...
    def to_oklab(self) -> Oklab:
        """Convert to `Oklab` color space."""
        ...
    def to_oklch(self) -> Oklch:
        """Convert to `Oklch` color space."""
        ...
    def to_xyb(self) -> Xyb:
        """Convert to `Xyb` color space."""
        ...
    def to_xyz(self) -> Xyz:
        """Convert to `Xyz` color space."""
        ...
    def to_ycbcr(self) -> Ycbcr:
        """Convert to `Ycbcr` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def blend(self, overlay: Rgba | tuple[int, int, int, int], mode: Blending = Blending.NORMAL) -> Hsv: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Lab:
    """CIELAB color space representation"""
    def __init__(self, l: float, a: float, b: float) -> None: ...
    @property
    def l(self) -> float: ...
    @l.setter
    def l(self, value: float) -> None: ...
    @property
    def a(self) -> float: ...
    @a.setter
    def a(self, value: float) -> None: ...
    @property
    def b(self) -> float: ...
    @b.setter
    def b(self, value: float) -> None: ...
    def to_rgb(self) -> Rgb:
        """Convert to `Rgb` color space."""
        ...
    def to_rgba(self, alpha: int = 255) -> Rgba:
        """Convert to RGBA color space with the given alpha value (0-255, default: 255)"""
        ...
    def to_hsl(self) -> Hsl:
        """Convert to `Hsl` color space."""
        ...
    def to_hsv(self) -> Hsv:
        """Convert to `Hsv` color space."""
        ...
    def to_lch(self) -> Lch:
        """Convert to `Lch` color space."""
        ...
    def to_lms(self) -> Lms:
        """Convert to `Lms` color space."""
        ...
    def to_oklab(self) -> Oklab:
        """Convert to `Oklab` color space."""
        ...
    def to_oklch(self) -> Oklch:
        """Convert to `Oklch` color space."""
        ...
    def to_xyb(self) -> Xyb:
        """Convert to `Xyb` color space."""
        ...
    def to_xyz(self) -> Xyz:
        """Convert to `Xyz` color space."""
        ...
    def to_ycbcr(self) -> Ycbcr:
        """Convert to `Ycbcr` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def blend(self, overlay: Rgba | tuple[int, int, int, int], mode: Blending = Blending.NORMAL) -> Lab: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Lch:
    """CIE LCH color space representation (cylindrical Lab)"""
    def __init__(self, l: float, c: float, h: float) -> None: ...
    @property
    def l(self) -> float: ...
    @l.setter
    def l(self, value: float) -> None: ...
    @property
    def c(self) -> float: ...
    @c.setter
    def c(self, value: float) -> None: ...
    @property
    def h(self) -> float: ...
    @h.setter
    def h(self, value: float) -> None: ...
    def to_rgb(self) -> Rgb:
        """Convert to `Rgb` color space."""
        ...
    def to_rgba(self, alpha: int = 255) -> Rgba:
        """Convert to RGBA color space with the given alpha value (0-255, default: 255)"""
        ...
    def to_hsl(self) -> Hsl:
        """Convert to `Hsl` color space."""
        ...
    def to_hsv(self) -> Hsv:
        """Convert to `Hsv` color space."""
        ...
    def to_lab(self) -> Lab:
        """Convert to `Lab` color space."""
        ...
    def to_lms(self) -> Lms:
        """Convert to `Lms` color space."""
        ...
    def to_oklab(self) -> Oklab:
        """Convert to `Oklab` color space."""
        ...
    def to_oklch(self) -> Oklch:
        """Convert to `Oklch` color space."""
        ...
    def to_xyb(self) -> Xyb:
        """Convert to `Xyb` color space."""
        ...
    def to_xyz(self) -> Xyz:
        """Convert to `Xyz` color space."""
        ...
    def to_ycbcr(self) -> Ycbcr:
        """Convert to `Ycbcr` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def blend(self, overlay: Rgba | tuple[int, int, int, int], mode: Blending = Blending.NORMAL) -> Lch: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Lms:
    """LMS color space representing Long, Medium, Short wavelength cone responses"""
    def __init__(self, l: float, m: float, s: float) -> None: ...
    @property
    def l(self) -> float: ...
    @l.setter
    def l(self, value: float) -> None: ...
    @property
    def m(self) -> float: ...
    @m.setter
    def m(self, value: float) -> None: ...
    @property
    def s(self) -> float: ...
    @s.setter
    def s(self, value: float) -> None: ...
    def to_rgb(self) -> Rgb:
        """Convert to `Rgb` color space."""
        ...
    def to_rgba(self, alpha: int = 255) -> Rgba:
        """Convert to RGBA color space with the given alpha value (0-255, default: 255)"""
        ...
    def to_hsl(self) -> Hsl:
        """Convert to `Hsl` color space."""
        ...
    def to_hsv(self) -> Hsv:
        """Convert to `Hsv` color space."""
        ...
    def to_lab(self) -> Lab:
        """Convert to `Lab` color space."""
        ...
    def to_lch(self) -> Lch:
        """Convert to `Lch` color space."""
        ...
    def to_oklab(self) -> Oklab:
        """Convert to `Oklab` color space."""
        ...
    def to_oklch(self) -> Oklch:
        """Convert to `Oklch` color space."""
        ...
    def to_xyb(self) -> Xyb:
        """Convert to `Xyb` color space."""
        ...
    def to_xyz(self) -> Xyz:
        """Convert to `Xyz` color space."""
        ...
    def to_ycbcr(self) -> Ycbcr:
        """Convert to `Ycbcr` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def blend(self, overlay: Rgba | tuple[int, int, int, int], mode: Blending = Blending.NORMAL) -> Lms: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Oklab:
    """Oklab perceptual color space representation"""
    def __init__(self, l: float, a: float, b: float) -> None: ...
    @property
    def l(self) -> float: ...
    @l.setter
    def l(self, value: float) -> None: ...
    @property
    def a(self) -> float: ...
    @a.setter
    def a(self, value: float) -> None: ...
    @property
    def b(self) -> float: ...
    @b.setter
    def b(self, value: float) -> None: ...
    def to_rgb(self) -> Rgb:
        """Convert to `Rgb` color space."""
        ...
    def to_rgba(self, alpha: int = 255) -> Rgba:
        """Convert to RGBA color space with the given alpha value (0-255, default: 255)"""
        ...
    def to_hsl(self) -> Hsl:
        """Convert to `Hsl` color space."""
        ...
    def to_hsv(self) -> Hsv:
        """Convert to `Hsv` color space."""
        ...
    def to_lab(self) -> Lab:
        """Convert to `Lab` color space."""
        ...
    def to_lch(self) -> Lch:
        """Convert to `Lch` color space."""
        ...
    def to_lms(self) -> Lms:
        """Convert to `Lms` color space."""
        ...
    def to_oklch(self) -> Oklch:
        """Convert to `Oklch` color space."""
        ...
    def to_xyb(self) -> Xyb:
        """Convert to `Xyb` color space."""
        ...
    def to_xyz(self) -> Xyz:
        """Convert to `Xyz` color space."""
        ...
    def to_ycbcr(self) -> Ycbcr:
        """Convert to `Ycbcr` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def blend(self, overlay: Rgba | tuple[int, int, int, int], mode: Blending = Blending.NORMAL) -> Oklab: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Oklch:
    """Oklch perceptual color space in cylindrical coordinates"""
    def __init__(self, l: float, c: float, h: float) -> None: ...
    @property
    def l(self) -> float: ...
    @l.setter
    def l(self, value: float) -> None: ...
    @property
    def c(self) -> float: ...
    @c.setter
    def c(self, value: float) -> None: ...
    @property
    def h(self) -> float: ...
    @h.setter
    def h(self, value: float) -> None: ...
    def to_rgb(self) -> Rgb:
        """Convert to `Rgb` color space."""
        ...
    def to_rgba(self, alpha: int = 255) -> Rgba:
        """Convert to RGBA color space with the given alpha value (0-255, default: 255)"""
        ...
    def to_hsl(self) -> Hsl:
        """Convert to `Hsl` color space."""
        ...
    def to_hsv(self) -> Hsv:
        """Convert to `Hsv` color space."""
        ...
    def to_lab(self) -> Lab:
        """Convert to `Lab` color space."""
        ...
    def to_lch(self) -> Lch:
        """Convert to `Lch` color space."""
        ...
    def to_lms(self) -> Lms:
        """Convert to `Lms` color space."""
        ...
    def to_oklab(self) -> Oklab:
        """Convert to `Oklab` color space."""
        ...
    def to_xyb(self) -> Xyb:
        """Convert to `Xyb` color space."""
        ...
    def to_xyz(self) -> Xyz:
        """Convert to `Xyz` color space."""
        ...
    def to_ycbcr(self) -> Ycbcr:
        """Convert to `Ycbcr` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def blend(self, overlay: Rgba | tuple[int, int, int, int], mode: Blending = Blending.NORMAL) -> Oklch: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Xyb:
    """XYB color space used in JPEG XL image compression"""
    def __init__(self, x: float, y: float, b: float) -> None: ...
    @property
    def x(self) -> float: ...
    @x.setter
    def x(self, value: float) -> None: ...
    @property
    def y(self) -> float: ...
    @y.setter
    def y(self, value: float) -> None: ...
    @property
    def b(self) -> float: ...
    @b.setter
    def b(self, value: float) -> None: ...
    def to_rgb(self) -> Rgb:
        """Convert to `Rgb` color space."""
        ...
    def to_rgba(self, alpha: int = 255) -> Rgba:
        """Convert to RGBA color space with the given alpha value (0-255, default: 255)"""
        ...
    def to_hsl(self) -> Hsl:
        """Convert to `Hsl` color space."""
        ...
    def to_hsv(self) -> Hsv:
        """Convert to `Hsv` color space."""
        ...
    def to_lab(self) -> Lab:
        """Convert to `Lab` color space."""
        ...
    def to_lch(self) -> Lch:
        """Convert to `Lch` color space."""
        ...
    def to_lms(self) -> Lms:
        """Convert to `Lms` color space."""
        ...
    def to_oklab(self) -> Oklab:
        """Convert to `Oklab` color space."""
        ...
    def to_oklch(self) -> Oklch:
        """Convert to `Oklch` color space."""
        ...
    def to_xyz(self) -> Xyz:
        """Convert to `Xyz` color space."""
        ...
    def to_ycbcr(self) -> Ycbcr:
        """Convert to `Ycbcr` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def blend(self, overlay: Rgba | tuple[int, int, int, int], mode: Blending = Blending.NORMAL) -> Xyb: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Xyz:
    """CIE 1931 XYZ color space representation"""
    def __init__(self, x: float, y: float, z: float) -> None: ...
    @property
    def x(self) -> float: ...
    @x.setter
    def x(self, value: float) -> None: ...
    @property
    def y(self) -> float: ...
    @y.setter
    def y(self, value: float) -> None: ...
    @property
    def z(self) -> float: ...
    @z.setter
    def z(self, value: float) -> None: ...
    def to_rgb(self) -> Rgb:
        """Convert to `Rgb` color space."""
        ...
    def to_rgba(self, alpha: int = 255) -> Rgba:
        """Convert to RGBA color space with the given alpha value (0-255, default: 255)"""
        ...
    def to_hsl(self) -> Hsl:
        """Convert to `Hsl` color space."""
        ...
    def to_hsv(self) -> Hsv:
        """Convert to `Hsv` color space."""
        ...
    def to_lab(self) -> Lab:
        """Convert to `Lab` color space."""
        ...
    def to_lch(self) -> Lch:
        """Convert to `Lch` color space."""
        ...
    def to_lms(self) -> Lms:
        """Convert to `Lms` color space."""
        ...
    def to_oklab(self) -> Oklab:
        """Convert to `Oklab` color space."""
        ...
    def to_oklch(self) -> Oklch:
        """Convert to `Oklch` color space."""
        ...
    def to_xyb(self) -> Xyb:
        """Convert to `Xyb` color space."""
        ...
    def to_ycbcr(self) -> Ycbcr:
        """Convert to `Ycbcr` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Ycbcr:
    """YCbCr color space used in JPEG and video encoding"""
    def __init__(self, y: int, cb: int, cr: int) -> None: ...
    @property
    def y(self) -> int: ...
    @y.setter
    def y(self, value: int) -> None: ...
    @property
    def cb(self) -> int: ...
    @cb.setter
    def cb(self, value: int) -> None: ...
    @property
    def cr(self) -> int: ...
    @cr.setter
    def cr(self, value: int) -> None: ...
    def to_rgb(self) -> Rgb:
        """Convert to `Rgb` color space."""
        ...
    def to_rgba(self, alpha: int = 255) -> Rgba:
        """Convert to RGBA color space with the given alpha value (0-255, default: 255)"""
        ...
    def to_hsl(self) -> Hsl:
        """Convert to `Hsl` color space."""
        ...
    def to_hsv(self) -> Hsv:
        """Convert to `Hsv` color space."""
        ...
    def to_lab(self) -> Lab:
        """Convert to `Lab` color space."""
        ...
    def to_lch(self) -> Lch:
        """Convert to `Lch` color space."""
        ...
    def to_lms(self) -> Lms:
        """Convert to `Lms` color space."""
        ...
    def to_oklab(self) -> Oklab:
        """Convert to `Oklab` color space."""
        ...
    def to_oklch(self) -> Oklch:
        """Convert to `Oklch` color space."""
        ...
    def to_xyb(self) -> Xyb:
        """Convert to `Xyb` color space."""
        ...
    def to_xyz(self) -> Xyz:
        """Convert to `Xyz` color space."""
        ...
    def to_gray(self) -> int:
        """Convert to a grayscale value representing the luminance/lightness as an integer between 0 and 255."""
    ...
    def blend(self, overlay: Rgba | tuple[int, int, int, int], mode: Blending = Blending.NORMAL) -> Ycbcr: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

# Union type for any color value
Color: TypeAlias = int | RgbTuple | RgbaTuple | Rgb | Rgba | Hsl | Hsv | Lab | Lch | Lms | Oklab | Oklch | Xyb | Xyz | Ycbcr

class Grayscale:
    """Grayscale image format (single channel, u8)"""
    ...

class Assignment:
    """Result of solving an assignment problem.

Contains the optimal assignments and total cost.

## Attributes
- `assignments`: List of column indices for each row (None if unassigned)
- `total_cost`: Total cost of the assignment
    """
    @property
    def assignments(self) -> list[int|None]: ...
    @property
    def total_cost(self) -> float: ...

class Image:
    """Image for processing and manipulation.

Pixel access via indexing returns a proxy object that allows in-place
modification. Use `.item()` on the proxy to extract the color value:
```python
  pixel = img[row, col]  # Returns pixel proxy
  color = pixel.item()   # Extracts color object (Rgb/Rgba/int)
```
This object is iterable: iterating yields (row, col, pixel) in native
dtype in row-major order. For bulk numeric work, prefer `to_numpy()`.
    """
    @classmethod
    def load(cls, path: str) -> Image:
        """Load an image from file (PNG or JPEG).

The pixel format (Grayscale, Rgb, or Rgba) is automatically determined from the
file metadata. For PNGs, the format matches the file's color type. For JPEGs,
grayscale images load as Grayscale, color images as Rgb.

## Parameters
- `path` (str): Path to the PNG or JPEG file to load

## Returns
Image: A new Image object with pixels in the format matching the file

## Raises
- `FileNotFoundError`: If the file does not exist
- `ValueError`: If the file format is unsupported
- `MemoryError`: If allocation fails during loading
- `PermissionError`: If read permission is denied

## Examples
```python
# Load images with automatic format detection
img = Image.load("photo.png")     # May be Rgba
img2 = Image.load("grayscale.jpg") # Will be Grayscale
img3 = Image.load("rgb.png")       # Will be Rgb

# Check format after loading
print(img.dtype)  # e.g., Rgba, Rgb, or Grayscale
```"""
        ...
    def save(self, path: str) -> None:
        """Save the image to a file (PNG or JPEG format).

The format is determined by the file extension (.png, .jpg, or .jpeg).

## Parameters
- `path` (str): Path where the image file will be saved.
  Must have .png, .jpg, or .jpeg extension.

## Raises
- `ValueError`: If the file has an unsupported extension
- `MemoryError`: If allocation fails during save
- `PermissionError`: If write permission is denied
- `FileNotFoundError`: If the directory does not exist

## Examples
```python
img = Image.load("input.png")
img.save("output.png")   # Save as PNG
img.save("output.jpg")   # Save as JPEG
```"""
        ...
    def copy(self) -> Image:
        """Create a deep copy of the image.

Returns a new Image with the same dimensions and pixel data,
but with its own allocated memory.

## Examples
```python
img = Image.load("photo.png")
copy = img.copy()
# Modifying copy doesn't affect original
copy[0, 0] = (255, 0, 0)
```"""
        ...
    def fill(self, color: Color) -> None:
        """Fill the entire image with a solid color.

## Parameters
- `color`: Fill color. Can be:
  - Integer (0-255) for grayscale images
  - RGB tuple (r, g, b) with values 0-255
  - RGBA tuple (r, g, b, a) with values 0-255
  - Any color object (Rgb, Hsl, Hsv, etc.)

## Examples
```python
img = Image(100, 100)
img.fill((255, 0, 0))  # Fill with red
```"""
        ...
    def view(self, rect: Rectangle | tuple[float, float, float, float] | None = None) -> Image:
        """Create a view of the image or a sub-region (zero-copy).

Creates a new Image that shares the same underlying pixel data. Changes
to the view affect the original image and vice versa.

## Parameters
- `rect` (Rectangle | tuple[float, float, float, float] | None): Optional rectangle
  defining the sub-region to view. If None, creates a view of the entire image.
  When providing a tuple, it should be (left, top, right, bottom).

## Returns
Image: A view of the image that shares the same pixel data

## Examples
```python
img = Image.load("photo.png")
# View entire image
view = img.view()
# View sub-region
rect = Rectangle(10, 10, 100, 100)
sub = img.view(rect)
# Modifications to view affect original
sub.fill((255, 0, 0))  # Fills region in original image
```"""
        ...
    def set_border(self, rect: Rectangle | tuple[float, float, float, float], color: Color | None = None) -> None:
        """Set the image border outside a rectangle to a value.

Sets pixels outside the given rectangle to the provided color/value,
leaving the interior untouched. The rectangle may be provided as a
Rectangle or a tuple (left, top, right, bottom). It is clipped to the
image bounds.

## Parameters
- `rect` (Rectangle | tuple[float, float, float, float]): Inner rectangle to preserve.
- `color` (optional): Fill value for border. Accepts the same types as `fill`.
   If omitted, uses zeros for the current dtype (0, Rgb(0,0,0), or Rgba(0,0,0,0)).

## Examples
```python
img = Image(100, 100)
rect = Rectangle(10, 10, 90, 90)
img.set_border(rect)               # zero border
img.set_border(rect, (255, 0, 0))  # red border

# Common pattern: set a uniform 16px border using shrink()
img.set_border(img.get_rectangle().shrink(16))
```"""
        ...
    def is_contiguous(self) -> bool:
        """Check if the image data is stored contiguously in memory.

Returns True if pixels are stored without gaps (stride == cols),
False for views or images with custom strides.

## Examples
```python
img = Image(100, 100)
print(img.is_contiguous())  # True
view = img.view(Rectangle(10, 10, 50, 50))
print(view.is_contiguous())  # False
```"""
        ...
    def get_rectangle(self) -> Rectangle:
        """Get the full image bounds as a Rectangle(left=0, top=0, right=cols, bottom=rows)."""
        ...
    def convert(self, dtype: Grayscale | Rgb | Rgba) -> Image:
        """
Convert the image to a different pixel data type.

Supported targets: Grayscale, Rgb, Rgba.

Returns a new Image with the requested format."""
        ...
    def canvas(self) -> Canvas:
        """Get a Canvas object for drawing on this image.

Returns a Canvas that can be used to draw shapes, lines, and text
directly onto the image pixels.

## Examples
```python
img = Image(200, 200)
cv = img.canvas()
cv.draw_circle(100, 100, 50, (255, 0, 0))
cv.fill_rect(10, 10, 50, 50, (0, 255, 0))
```"""
        ...
    def psnr(self, other: Image) -> float:
        """Calculate Peak Signal-to-Noise Ratio between two images.

PSNR is a quality metric where higher values indicate greater similarity.
Typical values: 30-50 dB (higher is better). Returns infinity for identical images.

## Parameters
- `other` (Image): The image to compare against. Must have same dimensions and dtype.

## Returns
float: PSNR value in decibels (dB), or inf for identical images

## Raises
- `ValueError`: If images have different dimensions or dtypes

## Examples
```python
original = Image.load("original.png")
compressed = Image.load("compressed.png")
quality = original.psnr(compressed)
print(f"PSNR: {quality:.2f} dB")
```"""
        ...
    def ssim(self, other: Image) -> float:
        """Calculate Structural Similarity Index between two images.

SSIM is a perceptual metric in the range [0, 1] where higher values indicate
greater structural similarity.

## Parameters
- `other` (Image): The image to compare against. Must have same dimensions and dtype.

## Returns
float: SSIM value between 0 and 1 (inclusive)

## Raises
- `ValueError`: If images have different dimensions or dtypes, or are smaller than 11x11

## Examples
```python
original = Image.load("frame.png")
processed = pipeline(original)
score = original.ssim(processed)
print(f"SSIM: {score:.4f}")
```"""
        ...
    @classmethod
    def from_numpy(cls, array: NDArray[np.uint8]) -> Image:
        """Create Image from a NumPy array with dtype uint8.

Zero-copy is used for arrays with these shapes:
- Grayscale: (rows, cols, 1) → Image(Grayscale)
- RGB: (rows, cols, 3) → Image(Rgb)
- RGBA: (rows, cols, 4) → Image(Rgba)

The array can have row strides (e.g., from views or slicing) as long as pixels
within each row are contiguous. For arrays with incompatible strides (e.g., transposed),
use `numpy.ascontiguousarray()` first.

## Parameters
- `array` (NDArray[np.uint8]): NumPy array with shape (rows, cols, 1), (rows, cols, 3) or (rows, cols, 4) and dtype uint8.
  Pixels within rows must be contiguous.

## Raises
- `TypeError`: If array is None or has wrong dtype
- `ValueError`: If array has wrong shape or incompatible strides

## Notes
The array can have row strides (padding between rows) but pixels within
each row must be contiguous. For incompatible layouts (e.g., transposed
arrays), use np.ascontiguousarray() first:

```python
arr = np.ascontiguousarray(arr)
img = Image.from_numpy(arr)
```

## Examples
```python
arr = np.zeros((100, 200, 3), dtype=np.uint8)
img = Image.from_numpy(arr)
print(img.rows, img.cols)
# Output: 100 200
```"""
        ...
    def to_numpy(self) -> NDArray[np.uint8]:
        """Convert the image to a NumPy array (zero-copy when possible).

Returns an array in the image's native dtype:\n
- Grayscale → shape (rows, cols, 1)\n
- Rgb → shape (rows, cols, 3)\n
- Rgba → shape (rows, cols, 4)

## Examples
```python
img = Image.load("photo.png")
arr = img.to_numpy()
print(arr.shape, arr.dtype)
# Example: (H, W, C) uint8 where C is 1, 3, or 4
```"""
        ...
    def resize(self, size: float | tuple[int, int], method: Interpolation = Interpolation.BILINEAR) -> Image:
        """Resize the image to the specified size.

## Parameters
- `size` (float or tuple[int, int]):
  - If float: scale factor (e.g., 0.5 for half size, 2.0 for double size)
  - If tuple: target dimensions as (rows, cols)
- `method` (`Interpolation`, optional): Interpolation method to use. Default is `Interpolation.BILINEAR`."""
        ...
    def letterbox(self, size: int | tuple[int, int], method: Interpolation = Interpolation.BILINEAR) -> Image:
        """Resize image to fit within the specified size while preserving aspect ratio.

The image is scaled to fit within the target dimensions and centered with
black borders (letterboxing) to maintain the original aspect ratio.

## Parameters
- `size` (int or tuple[int, int]):
  - If int: creates a square output of size x size
  - If tuple: target dimensions as (rows, cols)
- `method` (`Interpolation`, optional): Interpolation method to use. Default is `Interpolation.BILINEAR`."""
        ...
    def rotate(self, angle: float, method: Interpolation = Interpolation.BILINEAR) -> Image:
        """Rotate the image by the specified angle around its center.

The output image is automatically sized to fit the entire rotated image without clipping.

## Parameters
- `angle` (float): Rotation angle in radians counter-clockwise.
- `method` (`Interpolation`, optional): Interpolation method to use. Default is `Interpolation.BILINEAR`.

## Examples
```python
import math
img = Image.load("photo.png")

# Rotate 45 degrees with default bilinear interpolation
rotated = img.rotate(math.radians(45))

# Rotate 90 degrees with nearest neighbor (faster, lower quality)
rotated = img.rotate(math.radians(90), Interpolation.NEAREST_NEIGHBOR)

# Rotate -30 degrees with Lanczos (slower, higher quality)
rotated = img.rotate(math.radians(-30), Interpolation.LANCZOS)
```"""
        ...
    def warp(self, transform: SimilarityTransform | AffineTransform | ProjectiveTransform, shape: tuple[int, int] | None = None, method: Interpolation = Interpolation.BILINEAR) -> Image:
        """Apply a geometric transform to the image.

This method warps an image using a geometric transform (Similarity, Affine, or Projective).
For each pixel in the output image, it applies the transform to find the corresponding
location in the source image and samples using the specified interpolation method.

## Parameters
- `transform`: A geometric transform object (SimilarityTransform, AffineTransform, or ProjectiveTransform)
- `shape` (optional): Output image shape as (rows, cols) tuple. Defaults to input image shape.
- `method` (optional): Interpolation method. Defaults to Interpolation.BILINEAR.

## Examples
```python
# Apply similarity transform
from_points = [(0, 0), (100, 0), (100, 100)]
to_points = [(10, 10), (110, 20), (105, 115)]
transform = SimilarityTransform(from_points, to_points)
warped = img.warp(transform)

# Apply with custom output size and interpolation
warped = img.warp(transform, shape=(512, 512), method=Interpolation.BICUBIC)
```"""
        ...
    def flip_left_right(self) -> Image:
        """Flip image left-to-right (horizontal mirror).

Returns a new image that is a horizontal mirror of the original.
```python
flipped = img.flip_left_right()
```"""
        ...
    def flip_top_bottom(self) -> Image:
        """Flip image top-to-bottom (vertical mirror).

Returns a new image that is a vertical mirror of the original.
```python
flipped = img.flip_top_bottom()
```"""
        ...
    def crop(self, rect: Rectangle | tuple[float, float, float, float]) -> Image:
        """Extract a rectangular region from the image.

Returns a new Image containing the cropped region. Pixels outside the original
image bounds are filled with transparent black (0, 0, 0, 0).

## Parameters
- `rect` (Rectangle): The rectangular region to extract

## Examples
```python
img = Image.load("photo.png")
rect = Rectangle(10, 10, 110, 110)  # 100x100 region starting at (10, 10)
cropped = img.crop(rect)
print(cropped.rows, cropped.cols)  # 100 100
```"""
        ...
    def extract(self, rect: Rectangle | tuple[float, float, float, float], angle: float = 0.0, size: int | tuple[int, int] | None = None, method: Interpolation = Interpolation.BILINEAR) -> Image:
        """Extract a rotated rectangular region from the image and resample it.

Returns a new Image containing the extracted and resampled region.

## Parameters
- `rect` (Rectangle): The rectangular region to extract (before rotation)
- `angle` (float, optional): Rotation angle in radians (counter-clockwise). Default: 0.0
- `size` (int or tuple[int, int], optional). If not specified, uses the rectangle's dimensions.
  - If int: output is a square of side `size`
  - If tuple: output size as (rows, cols)
- `method` (Interpolation, optional): Interpolation method. Default: BILINEAR

## Examples
```python
import math
img = Image.load("photo.png")
rect = Rectangle(10, 10, 110, 110)

# Extract without rotation
extracted = img.extract(rect)

# Extract with 45-degree rotation
rotated = img.extract(rect, angle=math.radians(45))

# Extract and resize to specific dimensions
resized = img.extract(rect, size=(50, 75))

# Extract to a 64x64 square
square = img.extract(rect, size=64)
```"""
        ...
    def insert(self, source: Image, rect: Rectangle | tuple[float, float, float, float], angle: float = 0.0, method: Interpolation = Interpolation.BILINEAR, blend_mode: Blending = Blending.NONE) -> None:
        """Insert a source image into this image at a specified rectangle with optional rotation.

This method modifies the image in-place.

## Parameters
- `source` (Image): The image to insert
- `rect` (Rectangle): Destination rectangle where the source will be placed
- `angle` (float, optional): Rotation angle in radians (counter-clockwise). Default: 0.0
- `method` (Interpolation, optional): Interpolation method. Default: BILINEAR
- `blend_mode` (Blending, optional): Compositing mode for RGBA images. Default: NONE

## Examples
```python
import math
canvas = Image(500, 500)
logo = Image.load("logo.png")

# Insert at top-left
rect = Rectangle(10, 10, 110, 110)
canvas.insert(logo, rect)

# Insert with rotation
rect2 = Rectangle(200, 200, 300, 300)
canvas.insert(logo, rect2, angle=math.radians(45))
```"""
        ...
    def box_blur(self, radius: int) -> Image:
        """Apply a box blur to the image.

## Parameters
- `radius` (int): Non-negative blur radius in pixels. `0` returns an unmodified copy.

## Examples
```python
img = Image.load("photo.png")
soft = img.box_blur(2)
identity = img.box_blur(0)  # no-op copy
```"""
        ...
    def median_blur(self, radius: int) -> Image:
        """Apply a median blur (order-statistic filter) to the image.

## Parameters
- `radius` (int): Non-negative blur radius in pixels. `0` returns an unmodified copy.

## Notes
- Uses `BorderMode.MIRROR` at the image edges to avoid introducing artificial borders.

## Examples
```python
img = Image.load("noisy.png")
denoised = img.median_blur(2)
```"""
        ...
    def min_blur(self, radius: int, border: BorderMode = BorderMode.MIRROR) -> Image:
        """Apply a minimum filter (rank 0 percentile) to the image.

## Parameters
- `radius` (int): Non-negative blur radius in pixels. `0` returns an unmodified copy.
- `border` (BorderMode, optional): Border handling strategy. Defaults to `BorderMode.MIRROR`.

## Use case
- Morphological erosion to remove "salt" noise or shrink bright speckles."""
        ...
    def max_blur(self, radius: int, border: BorderMode = BorderMode.MIRROR) -> Image:
        """Apply a maximum filter (rank 1 percentile) to the image.

## Parameters
- `radius` (int): Non-negative blur radius in pixels.
- `border` (BorderMode, optional): Border handling strategy. Defaults to `BorderMode.MIRROR`.

## Use case
- Morphological dilation to expand highlights or fill gaps in masks."""
        ...
    def midpoint_blur(self, radius: int, border: BorderMode = BorderMode.MIRROR) -> Image:
        """Apply a midpoint filter (average of min and max) to the image.

## Parameters
- `radius` (int): Non-negative blur radius.
- `border` (BorderMode, optional): Border handling strategy. Defaults to `BorderMode.MIRROR`.

## Use case
- Softens impulse noise while preserving thin edges (midpoint between min/max)."""
        ...
    def percentile_blur(self, radius: int, percentile: float, border: BorderMode = BorderMode.MIRROR) -> Image:
        """Apply a percentile blur (order-statistic filter) to the image.

## Parameters
- `radius` (int): Non-negative blur radius defining the neighborhood window.
- `percentile` (float): Value in the range [0.0, 1.0] selecting which ordered pixel to keep.
- `border` (BorderMode, optional): Border handling strategy. Defaults to `BorderMode.MIRROR`.

## Use case
- Fine control over ordered statistics (e.g., `percentile=0.1` suppresses bright outliers).

## Examples
```python
img = Image.load("noisy.png")
median = img.percentile_blur(2, 0.5)
max_filter = img.percentile_blur(1, 1.0, border=zignal.BorderMode.ZERO)
```"""
        ...
    def alpha_trimmed_mean_blur(self, radius: int, trim_fraction: float, border: BorderMode = BorderMode.MIRROR) -> Image:
        """Apply an alpha-trimmed mean blur, discarding a fraction of low/high pixels.

## Parameters
- `radius` (int): Non-negative blur radius.
- `trim_fraction` (float): Fraction in [0, 0.5) removed from both tails.
- `border` (BorderMode, optional): Border handling strategy. Defaults to `BorderMode.MIRROR`.

## Use case
- Robust alternative to averaging that discards extremes (hot pixels, specular highlights)."""
        ...
    def gaussian_blur(self, sigma: float) -> Image:
        """Apply Gaussian blur to the image.

## Parameters
- `sigma` (float): Standard deviation of the Gaussian kernel. Must be > 0.

## Examples
```python
img = Image.load("photo.png")
blurred = img.gaussian_blur(2.0)
blurred_soft = img.gaussian_blur(5.0)  # More blur
```"""
        ...
    def sharpen(self, radius: int) -> Image:
        """Sharpen the image using unsharp masking (2 * self - blur_box).

## Parameters
- `radius` (int): Non-negative blur radius used to compute the unsharp mask. `0` returns an unmodified copy.

## Examples
```python
img = Image.load("photo.png")
crisp = img.sharpen(2)
identity = img.sharpen(0)  # no-op copy
```"""
        ...
    def invert(self) -> Image:
        """Invert the colors of the image.

Creates a negative/inverted version of the image where:
- Grayscale pixels: 255 - value
- RGB pixels: inverts each channel (255 - r, 255 - g, 255 - b)
- RGBA pixels: inverts RGB channels while preserving alpha

## Examples
```python
img = Image.load("photo.png")
inverted = img.invert()

# Works with all image types
gray = Image(100, 100, 128, dtype=zignal.Grayscale)
gray_inv = gray.invert()  # pixels become 127
```"""
        ...
    def autocontrast(self, cutoff: float = 0.0) -> Image:
        """Automatically adjust image contrast by stretching the intensity range.

Analyzes the histogram and remaps pixel values so the darkest pixels
become black (0) and brightest become white (255).

## Parameters
- `cutoff` (float, optional): Rate of pixels to ignore at extremes (0-0.5).
  Default: 0. For example, 0.02 ignores the darkest and brightest 2% of pixels,
  helping to remove outliers.

## Returns
A new image with adjusted contrast.

## Examples
```python
img = Image.load("photo.png")

# Basic auto-contrast
enhanced = img.autocontrast()

# Ignore 2% outliers on each end
enhanced = img.autocontrast(cutoff=0.02)
```"""
        ...
    def equalize(self) -> Image:
        """Equalize the histogram of the image to improve contrast.

Redistributes pixel intensities to achieve a more uniform histogram,
which typically enhances contrast in images with poor contrast or
uneven lighting conditions. The technique maps the cumulative
distribution function (CDF) of pixel values to create a more even
spread of intensities across the full range.

For color images (RGB/RGBA), each channel is equalized independently.

## Returns
Image: New image with equalized histogram

## Example
```python
import zignal

# Load an image with poor contrast
img = zignal.Image.load("low_contrast.jpg")

# Apply histogram equalization
equalized = img.equalize()

# Save the result
equalized.save("equalized.jpg")

# Compare with autocontrast
auto = img.autocontrast(cutoff=0.02)
```"""
        ...
    def motion_blur(self, config: MotionBlur) -> Image:
        """Apply motion blur effect to the image.

Motion blur simulates camera or object movement during exposure.
Three types of motion blur are supported:
- `MotionBlur.linear()` - Linear motion blur
- `MotionBlur.radial_zoom()` - Radial zoom blur
- `MotionBlur.radial_spin()` - Radial spin blur

## Examples
```python
from zignal import Image, MotionBlur
import math

img = Image.load("photo.png")

# Linear motion blur examples
horizontal_blur = img.motion_blur(MotionBlur.linear(angle=0, distance=30))  # Camera panning
vertical_blur = img.motion_blur(MotionBlur.linear(angle=math.pi/2, distance=20))  # Camera shake
diagonal_blur = img.motion_blur(MotionBlur.linear(angle=math.pi/4, distance=25))  # Diagonal motion

# Radial zoom blur examples
center_zoom = img.motion_blur(MotionBlur.radial_zoom(center=(0.5, 0.5), strength=0.7))  # Center zoom burst
off_center_zoom = img.motion_blur(MotionBlur.radial_zoom(center=(0.33, 0.67), strength=0.5))  # Rule of thirds
subtle_zoom = img.motion_blur(MotionBlur.radial_zoom(strength=0.3))  # Subtle effect with defaults

# Radial spin blur examples
center_spin = img.motion_blur(MotionBlur.radial_spin(center=(0.5, 0.5), strength=0.5))  # Center rotation
swirl_effect = img.motion_blur(MotionBlur.radial_spin(center=(0.3, 0.3), strength=0.6))  # Off-center swirl
strong_spin = img.motion_blur(MotionBlur.radial_spin(strength=0.8))  # Strong spin with defaults
```

## Notes
- Linear blur preserves image dimensions
- Radial effects use bilinear interpolation for smooth results
- Strength values closer to 1.0 produce stronger blur effects"""
        ...
    def threshold_otsu(self) -> tuple[Image, int]:
        """Binarize the image using Otsu's method.

The input is converted to grayscale if needed. Returns a tuple containing the
binary image (0 or 255 values) and the threshold chosen by the algorithm.

## Returns
- `tuple[Image, int]`: (binary image, threshold)

## Examples
```python
binary, threshold = img.threshold_otsu()
print(threshold)
```"""
        ...
    def threshold_adaptive_mean(self, radius: int = 6, c: float = 5.0) -> Image:
        """Adaptive mean thresholding producing a binary image.

Pixels are compared to the mean of a local window (square of size `2*radius+1`).
Values greater than `mean - c` become 255, others become 0.

## Parameters
- `radius` (int, optional): Neighborhood radius. Must be > 0. Default: 6.
- `c` (float, optional): Subtracted constant. Default: 5.0.

## Returns
- `Image`: Binary image with values 0 or 255."""
        ...
    def sobel(self) -> Image:
        """Apply Sobel edge detection and return the gradient magnitude.

The result is a new grayscale image (`dtype=zignal.Grayscale`) where
each pixel encodes the edge strength at that location.

## Examples
```python
img = Image.load("photo.png")
edges = img.sobel()
```"""
        ...
    def shen_castan(self, smooth: float = 0.9, window_size: int = 7, high_ratio: float = 0.99, low_rel: float = 0.5, hysteresis: bool = True, use_nms: bool = False) -> Image:
        """Apply Shen-Castan edge detection to the image.

The Shen-Castan algorithm uses ISEF (Infinite Symmetric Exponential Filter)
for edge detection with adaptive gradient computation and hysteresis thresholding.
Returns a binary edge map where edges are 255 (white) and non-edges are 0 (black).

## Parameters
- `smooth` (float, optional): ISEF smoothing factor (0 < smooth < 1). Higher values preserve more detail. Default: 0.9
- `window_size` (int, optional): Odd window size for local gradient statistics (>= 3). Default: 7
- `high_ratio` (float, optional): Percentile for high threshold selection (0 < high_ratio < 1). Default: 0.99
- `low_rel` (float, optional): Low threshold as fraction of high threshold (0 < low_rel < 1). Default: 0.5
- `hysteresis` (bool, optional): Enable hysteresis edge linking. When True, weak edges connected to strong edges are preserved. Default: True
- `use_nms` (bool, optional): Use non-maximum suppression for single-pixel edges. When True, produces thinner edges. Default: False

## Returns
- `Image`: Binary edge map (Grayscale image with values 0 or 255)

## Examples
```python
from zignal import Image

img = Image.load("photo.jpg")

# Use default settings
edges = img.shen_castan()

# Low-noise settings for clean images
clean_edges = img.shen_castan(smooth=0.95, high_ratio=0.98)

# High-noise settings for noisy images
denoised_edges = img.shen_castan(smooth=0.7, window_size=11)

# Single-pixel edges with NMS
thin_edges = img.shen_castan(use_nms=True)
```"""
        ...
    def canny(self, sigma: float = 1.4, low: float = 50, high: float = 150) -> Image:
        """Apply Canny edge detection to the image.

The Canny algorithm is a classic multi-stage edge detector that produces thin,
well-localized edges with good noise suppression. It consists of five main steps:
1. Gaussian smoothing to reduce noise
2. Gradient computation using Sobel operators
3. Non-maximum suppression to thin edges
4. Double thresholding to classify strong and weak edges
5. Edge tracking by hysteresis to link edges

Returns a binary edge map where edges are 255 (white) and non-edges are 0 (black).

## Parameters
- `sigma` (float, optional): Standard deviation for Gaussian blur. Default: 1.4.
                             Typical values: 1.0-2.0. Higher values = more smoothing, fewer edges.
- `low` (float, optional): Lower threshold for hysteresis. Default: 50.
- `high` (float, optional): Upper threshold for hysteresis. Default: 150.
                            Should be 2-3x larger than `low`.

## Returns
A new grayscale image (`dtype=zignal.Grayscale`) with binary edge map.

## Raises
- `ValueError`: If sigma < 0, thresholds are negative, or low >= high

## Examples
```python
img = Image.load("photo.png")

# Use defaults (sigma=1.4, low=50, high=150)
edges = img.canny()

# Custom parameters - more aggressive edge detection (lower thresholds)
edges_sensitive = img.canny(sigma=1.0, low=30, high=90)

# Conservative edge detection (higher thresholds)
edges_conservative = img.canny(sigma=2.0, low=100, high=200)
```"""
        ...
    def blend(self, overlay: Image, mode: Blending = Blending.NORMAL) -> None:
        """Blend an overlay image onto this image using the specified blend mode.

Modifies this image in-place. Both images must have the same dimensions.
The overlay image must have an alpha channel for proper blending.

## Parameters
- `overlay` (Image): Image to blend onto this image
- `mode` (Blending, optional): Blending mode (default: NORMAL)

## Raises
- `ValueError`: If images have different dimensions
- `TypeError`: If overlay is not an Image object

## Examples
```python
# Basic alpha blending
base = Image(100, 100, (255, 0, 0))
overlay = Image(100, 100, (0, 0, 255, 128))  # Semi-transparent blue
base.blend(overlay)  # Default NORMAL mode

# Using different blend modes
base.blend(overlay, zignal.Blending.MULTIPLY)
base.blend(overlay, zignal.Blending.SCREEN)
base.blend(overlay, zignal.Blending.OVERLAY)
```"""
        ...
    def dilate_binary(self, kernel_size: int = 3, iterations: int = 1) -> Image:
        """Dilate a binary image using a square structuring element.

## Parameters
- `kernel_size` (int, optional): Side length of the square element (odd, >= 1). Default: 3.
- `iterations` (int, optional): Number of passes. Default: 1.

## Returns
- `Image`: Dilated binary image."""
        ...
    def erode_binary(self, kernel_size: int = 3, iterations: int = 1) -> Image:
        """Erode a binary image using a square structuring element.

Same parameters as `dilate_binary`."""
        ...
    def open_binary(self, kernel_size: int = 3, iterations: int = 1) -> Image:
        """Perform binary opening (erosion followed by dilation).

Useful for removing isolated noise while preserving overall shapes."""
        ...
    def close_binary(self, kernel_size: int = 3, iterations: int = 1) -> Image:
        """Perform binary closing (dilation followed by erosion).

Useful for filling small holes and connecting nearby components."""
        ...
    def __format__(self, format_spec: str) -> str:
        """Format image for display using various terminal graphics protocols.

## Parameters
- `format_spec` (str): Format specifier with optional size constraints

  **Pattern:** `format` or `format:WIDTHxHEIGHT` or `format:WIDTHx` or `format:xHEIGHT`

  **Formats:**
  - `''` (empty): Text representation (e.g., 'Image(800x600)')
  - `'auto'`: Auto-detect best format (kitty → sixel → sgr)
  - `'sgr'`: Unicode half-blocks with 24-bit color
  - `'braille'`: Braille patterns (monochrome, 2x4 resolution per character)
  - `'sixel'`: Sixel graphics protocol (up to 256 colors)
  - `'kitty'`: Kitty graphics protocol (full 24-bit color)

  **Size constraints (optional):**
  All size parameters maintain the original aspect ratio:
  - `:WIDTHxHEIGHT` - Scale to fit within WIDTH×HEIGHT box
  - `:WIDTHx` - Constrain width to WIDTH pixels
  - `:xHEIGHT` - Constrain height to HEIGHT pixels

## Examples
```python
img = Image.load("photo.png")  # e.g., 1920x1080

# Basic display formats
print(f"{img}")           # Text: Image(1920x1080)
print(f"{img:sgr}")       # Display with unicode half-blocks
print(f"{img:braille}")   # Display with braille patterns
print(f"{img:sixel}")     # Display with sixel graphics
print(f"{img:kitty}")     # Display with kitty graphics
print(f"{img:auto}")      # Auto-detect best format

# With size constraints (aspect ratio always preserved)
print(f"{img:sgr:400x300}")     # Fit within 400x300 (actual: 400x225)
print(f"{img:braille:200x}")    # Width=200, height auto-calculated
print(f"{img:sixel:x150}")      # Height=150, width auto-calculated
print(f"{img:auto:500x500}")    # Fit within 500x500 box
```"""
        ...
    @property
    def rows(self) -> int: ...
    @property
    def cols(self) -> int: ...
    @property
    def dtype(self) -> Grayscale | Rgb | Rgba: ...
    def __init__(self, rows: int, cols: int, color: Color | None = None, dtype = Grayscale | Rgb | Rgba) -> None:
        """Create a new Image with the specified dimensions and optional fill color.

## Parameters
- `rows` (int): Number of rows (height) of the image
- `cols` (int): Number of columns (width) of the image
- `color` (optional): Fill color. Can be:
  - Integer (0-255) for grayscale
  - RGB tuple (r, g, b) with values 0-255
  - RGBA tuple (r, g, b, a) with values 0-255
  - Any color object (Rgb, Hsl, Hsv, etc.)
  - Defaults to transparent (0, 0, 0, 0)
- `dtype` (type, optional): Pixel data type specifying storage type.
  - `zignal.Grayscale` → single-channel u8 (NumPy shape (H, W, 1))
  - `zignal.Rgb` (default) → 3-channel RGB (NumPy shape (H, W, 3))
  - `zignal.Rgba` → 4-channel RGBA (NumPy shape (H, W, 4))

## Examples
```python
# Create a 100x200 black image (default RGB)
img = Image(100, 200)

# Create a 100x200 red image (RGBA)
img = Image(100, 200, (255, 0, 0, 255))

# Create a 100x200 grayscale image with mid-gray fill
img = Image(100, 200, 128, dtype=zignal.Grayscale)

# Create a 100x200 RGB image (dtype overrides the color value)
img = Image(100, 200, (0, 255, 0, 255), dtype=zignal.Rgb)

# Create an image from numpy array dimensions
img = Image(*arr.shape[:2])

# Create with semi-transparent blue (requires RGBA)
img = Image(100, 100, (0, 0, 255, 128), dtype=zignal.Rgba)
```"""
        ...
    def __len__(self) -> int: ...
    def __iter__(self) -> PixelIterator:
        """Iterate over pixels in row-major order, yielding (row, col, pixel) in native dtype (int|Rgb|Rgba)."""
        ...
    def __getitem__(self, key: tuple[int, int]) -> int | Rgb | Rgba: ...
    def __setitem__(self, key: tuple[int, int] | slice, value: Color | Image) -> None: ...
    def __format__(self, format_spec: str) -> str:
        """Format image for display using various terminal graphics protocols.

## Parameters
- `format_spec` (str): Format specifier with optional size constraints

  **Pattern:** `format` or `format:WIDTHxHEIGHT` or `format:WIDTHx` or `format:xHEIGHT`

  **Formats:**
  - `''` (empty): Text representation (e.g., 'Image(800x600)')
  - `'auto'`: Auto-detect best format (kitty → sixel → sgr)
  - `'sgr'`: Unicode half-blocks with 24-bit color
  - `'braille'`: Braille patterns (monochrome, 2x4 resolution per character)
  - `'sixel'`: Sixel graphics protocol (up to 256 colors)
  - `'kitty'`: Kitty graphics protocol (full 24-bit color)

  **Size constraints (optional):**
  All size parameters maintain the original aspect ratio:
  - `:WIDTHxHEIGHT` - Scale to fit within WIDTH×HEIGHT box
  - `:WIDTHx` - Constrain width to WIDTH pixels
  - `:xHEIGHT` - Constrain height to HEIGHT pixels

## Examples
```python
img = Image.load("photo.png")  # e.g., 1920x1080

# Basic display formats
print(f"{img}")           # Text: Image(1920x1080)
print(f"{img:sgr}")       # Display with unicode half-blocks
print(f"{img:braille}")   # Display with braille patterns
print(f"{img:sixel}")     # Display with sixel graphics
print(f"{img:kitty}")     # Display with kitty graphics
print(f"{img:auto}")      # Auto-detect best format

# With size constraints (aspect ratio always preserved)
print(f"{img:sgr:400x300}")     # Fit within 400x300 (actual: 400x225)
print(f"{img:braille:200x}")    # Width=200, height auto-calculated
print(f"{img:sixel:x150}")      # Height=150, width auto-calculated
print(f"{img:auto:500x500}")    # Fit within 500x500 box
```"""
        ...
    def __eq__(self, other: object) -> bool:
        """Check equality with another Image by comparing dimensions and pixel data."""
        ...
    def __ne__(self, other: object) -> bool:
        """Check inequality with another Image."""
        ...

class Matrix:
    """Matrix for numerical computations with f64 (float64) values.

This class provides a bridge between zignal's Matrix type and NumPy arrays,
with zero-copy operations when possible.

## Examples
```python
import zignal
import numpy as np

# Create from list of lists
m = zignal.Matrix([[1, 2, 3], [4, 5, 6]])

# Create with dimensions using full()
m = zignal.Matrix.full(3, 4)  # 3x4 matrix of zeros
m = zignal.Matrix.full(3, 4, fill_value=1.0)  # filled with 1.0

# From numpy (zero-copy for float64 contiguous arrays)
arr = np.random.randn(10, 5)
m = zignal.Matrix.from_numpy(arr)

# To numpy (zero-copy)
arr = m.to_numpy()
```
    """
    @classmethod
    def full(cls, rows: int, cols: int, fill_value: float = 0.0) -> Matrix:
        """Create a Matrix filled with a specified value.

## Parameters
- `rows` (int): Number of rows
- `cols` (int): Number of columns
- `fill_value` (float, optional): Value to fill the matrix with (default: 0.0)

## Returns
Matrix: A new Matrix of the specified dimensions filled with fill_value

## Examples
```python
# Create 3x4 matrix of zeros
m = Matrix.full(3, 4)

# Create 3x4 matrix of ones
m = Matrix.full(3, 4, 1.0)

# Create 5x5 matrix filled with 3.14
m = Matrix.full(5, 5, 3.14)
```"""
        ...
    @classmethod
    def from_numpy(cls, array: NDArray[np.float64]) -> Matrix:
        """Create a Matrix from a NumPy array (zero-copy when possible).

The array must be 2D with dtype float64 and be C-contiguous.
If the array is not contiguous or not float64, an error is raised.

## Parameters
- `array` (NDArray[np.float64]): A 2D NumPy array with dtype float64

## Returns
Matrix: A new Matrix that shares memory with the NumPy array

## Examples
```python
import numpy as np
arr = np.random.randn(10, 5)  # float64 by default
m = Matrix.from_numpy(arr)
# Modifying arr will modify m and vice versa
```"""
        ...
    @classmethod
    def identity(cls, rows: int, cols: int) -> Matrix:
        """Create an identity matrix.

## Parameters
- `rows` (int): Number of rows
- `cols` (int): Number of columns

## Returns
Matrix: Identity matrix with ones on diagonal"""
        ...
    @classmethod
    def zeros(cls, rows: int, cols: int) -> Matrix:
        """Create a matrix filled with zeros.

## Parameters
- `rows` (int): Number of rows
- `cols` (int): Number of columns

## Returns
Matrix: Matrix filled with zeros"""
        ...
    @classmethod
    def ones(cls, rows: int, cols: int) -> Matrix:
        """Create a matrix filled with ones.

## Parameters
- `rows` (int): Number of rows
- `cols` (int): Number of columns

## Returns
Matrix: Matrix filled with ones"""
        ...
    def to_numpy(self) -> NDArray[np.float64]:
        """Convert the matrix to a NumPy array (zero-copy).

Returns a float64 NumPy array that shares memory with the Matrix.
Modifying the array will modify the Matrix.

## Returns
NDArray[np.float64]: A 2D NumPy array with shape (rows, cols)

## Examples
```python
m = Matrix(3, 4, fill_value=1.0)
arr = m.to_numpy()  # shape (3, 4), dtype float64
```"""
        ...
    def transpose(self) -> Matrix:
        """Transpose the matrix.

## Returns
Matrix: A new transposed matrix where rows and columns are swapped

## Examples
```python
m = Matrix([[1, 2, 3], [4, 5, 6]])
t = m.transpose()  # shape (3, 2)
```"""
        ...
    def inverse(self) -> Matrix:
        """Compute the matrix inverse.

## Returns
Matrix: The inverse matrix such that A @ A.inverse() ≈ I

## Raises
ValueError: If matrix is not square or is singular

## Examples
```python
m = Matrix([[2, 0], [0, 2]])
inv = m.inverse()  # [[0.5, 0], [0, 0.5]]
```"""
        ...
    def dot(self, other: Matrix) -> Matrix:
        """Matrix multiplication (dot product).

## Parameters
- `other` (Matrix): Matrix to multiply with

## Returns
Matrix: Result of matrix multiplication

## Examples
```python
a = Matrix([[1, 2], [3, 4]])
b = Matrix([[5, 6], [7, 8]])
c = a.dot(b)  # or a @ b
```"""
        ...
    def sum(self) -> float:
        """Sum of all matrix elements.

## Returns
float: The sum of all elements

## Examples
```python
m = Matrix([[1, 2], [3, 4]])
s = m.sum()  # 10.0
```"""
        ...
    def mean(self) -> float:
        """Mean (average) of all matrix elements.

## Returns
float: The mean of all elements"""
        ...
    def min(self) -> float:
        """Minimum element in the matrix.

## Returns
float: The minimum value"""
        ...
    def max(self) -> float:
        """Maximum element in the matrix.

## Returns
float: The maximum value"""
        ...
    def trace(self) -> float:
        """Sum of diagonal elements (trace).

## Returns
float: The trace of the matrix

## Raises
ValueError: If matrix is not square"""
        ...
    def copy(self) -> Matrix:
        """Create a copy of the matrix.

## Returns
Matrix: A new matrix with the same values"""
        ...
    def determinant(self) -> float:
        """Compute the determinant of the matrix.

## Returns
float: The determinant value

## Raises
ValueError: If matrix is not square"""
        ...
    def det(self) -> float:
        """Compute the determinant of the matrix.

## Returns
float: The determinant value

## Raises
ValueError: If matrix is not square"""
        ...
    def gram(self) -> Matrix:
        """Compute Gram matrix (X × X^T).

## Returns
Matrix: The Gram matrix (rows × rows)"""
        ...
    def covariance(self) -> Matrix:
        """Compute covariance matrix (X^T × X).

## Returns
Matrix: The covariance matrix (cols × cols)"""
        ...
    def cov(self) -> Matrix:
        """Compute covariance matrix (X^T × X).

## Returns
Matrix: The covariance matrix (cols × cols)"""
        ...
    def norm(self, kind: str = 'fro') -> float:
        """Compute matrix norm.

## Parameters
- `kind` (str, optional): Norm type - 'fro' (Frobenius, default), 'l1', 'max'

## Returns
float: The norm value"""
        ...
    def variance(self) -> float:
        """Compute variance of all matrix elements.

## Returns
float: The variance"""
        ...
    def std(self) -> float:
        """Compute standard deviation of all matrix elements.

## Returns
float: The standard deviation"""
        ...
    def pow(self, n: float) -> Matrix:
        """Raise all elements to power n (element-wise).

## Parameters
- `n` (float): The exponent

## Returns
Matrix: Matrix with elements raised to power n"""
        ...
    def row(self, idx: int) -> Matrix:
        """Extract a row as a column vector.

## Parameters
- `idx` (int): Row index

## Returns
Matrix: Column vector containing the row"""
        ...
    def col(self, idx: int) -> Matrix:
        """Extract a column as a column vector.

## Parameters
- `idx` (int): Column index

## Returns
Matrix: Column vector"""
        ...
    def submatrix(self, row_start: int, col_start: int, row_count: int, col_count: int) -> Matrix:
        """Extract a submatrix.

## Parameters
- `row_start` (int): Starting row index
- `col_start` (int): Starting column index
- `row_count` (int): Number of rows
- `col_count` (int): Number of columns

## Returns
Matrix: Submatrix"""
        ...
    @classmethod
    def random(cls, rows: int, cols: int, seed: int | None = None) -> Matrix:
        """Create a matrix filled with random values in [0, 1).

## Parameters
- `rows` (int): Number of rows
- `cols` (int): Number of columns
- `seed` (int, optional): Random seed for reproducibility

## Returns
Matrix: Matrix filled with random float64 values

## Examples
```python
m = Matrix.random(10, 5)  # Random 10x5 matrix
m = Matrix.random(10, 5, seed=42)  # Reproducible random matrix
```"""
        ...
    def rank(self) -> int:
        """Compute the numerical rank of the matrix.

Uses QR decomposition with column pivoting to determine the rank.

## Returns
int: The numerical rank"""
        ...
    def pinv(self, tolerance: float | None = None) -> Matrix:
        """Compute the Moore-Penrose pseudoinverse.

Works for rectangular matrices and gracefully handles rank deficiency.
Uses SVD-based algorithm.

## Parameters
- `tolerance` (float, optional): Threshold for small singular values

## Returns
Matrix: The pseudoinverse matrix

## Examples
```python
# For rectangular matrix
m = Matrix([[1, 2], [3, 4], [5, 6]])
pinv = m.pinv()
# With custom tolerance
pinv = m.pinv(tolerance=1e-10)
```"""
        ...
    def lu(self) -> dict:
        """Compute LU decomposition with partial pivoting.

Returns L, U matrices and permutation vector such that PA = LU.

## Returns
dict: Dictionary with keys:
  - 'l': Lower triangular matrix
  - 'u': Upper triangular matrix
  - 'p': Permutation vector (as Matrix)
  - 'sign': Determinant sign (+1.0 or -1.0)

## Raises
ValueError: If matrix is not square"""
        ...
    def qr(self) -> dict:
        """Compute QR decomposition with column pivoting.

Returns Q, R matrices and additional information about the decomposition.

## Returns
dict: Dictionary with keys:
  - 'q': Orthogonal matrix (m×n)
  - 'r': Upper triangular matrix (n×n)
  - 'rank': Numerical rank (int)
  - 'perm': Column permutation indices (list of int)
  - 'col_norms': Final column norms (list of float)"""
        ...
    def svd(self, full_matrices: bool = True, compute_uv: bool = True) -> dict:
        """Compute Singular Value Decomposition (SVD).

Computes A = U × Σ × V^T where U and V are orthogonal matrices
and Σ is a diagonal matrix of singular values.

## Parameters
- `full_matrices` (bool, optional): If True, U is m×m; if False, U is m×n (default: True)
- `compute_uv` (bool, optional): If True, compute U and V; if False, only compute singular values (default: True)

## Returns
dict: Dictionary with keys:
  - 'u': Left singular vectors (Matrix or None)
  - 's': Singular values as column vector (Matrix)
  - 'v': Right singular vectors (Matrix or None)
  - 'converged': Convergence status (0 = success, k = failed at k-th value)

## Raises
ValueError: If rows < cols (matrix must be tall or square)"""
        ...
    @property
    def rows(self) -> int: ...
    @property
    def cols(self) -> int: ...
    @property
    def shape(self) -> tuple[int, int]: ...
    @property
    def dtype(self) -> str: ...
    @property
    def T(self) -> Matrix: ...
    def __init__(self, data: list[list[float]]) -> None:
        """Create a new Matrix from a list of lists.

## Parameters
- `data` (List[List[float]]): List of lists containing matrix data

## Examples
```python
# Create from list of lists
m = Matrix([[1, 2, 3], [4, 5, 6]])  # 2x3 matrix
m = Matrix([[1.0, 2.5], [3.7, 4.2]])  # 2x2 matrix
```"""
        ...
    def __getitem__(self, key: tuple[int, int]) -> float:
        """Get matrix element at (row, col)"""
        ...
    def __setitem__(self, key: tuple[int, int], value: float) -> None:
        """Set matrix element at (row, col)"""
        ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __add__(self, other: Matrix | float) -> Matrix:
        """Element-wise addition or scalar offset"""
        ...
    def __radd__(self, other: float) -> Matrix:
        """Reverse addition (scalar + matrix)"""
        ...
    def __sub__(self, other: Matrix | float) -> Matrix:
        """Element-wise subtraction or scalar offset"""
        ...
    def __rsub__(self, other: float) -> Matrix:
        """Reverse subtraction (scalar - matrix)"""
        ...
    def __mul__(self, other: Matrix | float) -> Matrix:
        """Element-wise multiplication or scalar multiplication"""
        ...
    def __rmul__(self, other: float) -> Matrix:
        """Reverse multiplication (scalar * matrix)"""
        ...
    def __truediv__(self, other: float) -> Matrix:
        """Scalar division"""
        ...
    def __matmul__(self, other: Matrix) -> Matrix:
        """Matrix multiplication"""
        ...
    def __neg__(self) -> Matrix:
        """Unary negation"""
        ...

class Canvas:
    """Canvas for drawing operations on images.
    """
    def fill(self, color: Color) -> None:
        """Fill the entire canvas with a color.

## Parameters
- `color` (int, tuple or color object): Color to fill the canvas with. Can be:
  - Integer: grayscale value 0-255 (0=black, 255=white)
  - RGB tuple: `(r, g, b)` with values 0-255
  - RGBA tuple: `(r, g, b, a)` with values 0-255
  - Any color object: `Rgb`, `Rgba`, `Hsl`, `Hsv`, `Lab`, `Lch`, `Lms`, `Oklab`, `Oklch`, `Xyb`, `Xyz`, `Ycbcr`

## Examples
```python
img = Image.load("photo.png")
canvas = img.canvas()
canvas.fill(128)  # Fill with gray
canvas.fill((255, 0, 0))  # Fill with red
canvas.fill(Rgb(0, 255, 0))  # Fill with green using Rgb object
```"""
        ...
    def draw_line(self, p1: tuple[float, float], p2: tuple[float, float], color: Color, width: int = 1, mode: DrawMode = DrawMode.FAST) -> None:
        """Draw a line between two points.

## Parameters
- `p1` (tuple[float, float]): Starting point coordinates (x, y)
- `p2` (tuple[float, float]): Ending point coordinates (x, y)
- `color` (int, tuple or color object): Color of the line.
- `width` (int, optional): Line width in pixels (default: 1)
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    def draw_rectangle(self, rect: Rectangle | tuple[float, float, float, float], color: Color, width: int = 1, mode: DrawMode = DrawMode.FAST) -> None:
        """Draw a rectangle outline.

## Parameters
- `rect` (Rectangle | tuple[float, float, float, float]): Rectangle object defining the bounds
- `color` (int, tuple or color object): Color of the rectangle.
- `width` (int, optional): Line width in pixels (default: 1)
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    def fill_rectangle(self, rect: Rectangle | tuple[float, float, float, float], color: Color, mode: DrawMode = DrawMode.FAST) -> None:
        """Fill a rectangle area.

## Parameters
- `rect` (Rectangle | tuple[float, float, float, float]): Rectangle object defining the bounds
- `color` (int, tuple or color object): Fill color.
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    def draw_polygon(self, points: list[tuple[float, float]], color: Color, width: int = 1, mode: DrawMode = DrawMode.FAST) -> None:
        """Draw a polygon outline.

## Parameters
- `points` (list[tuple[float, float]]): List of (x, y) coordinates forming the polygon
- `color` (int, tuple or color object): Color of the polygon.
- `width` (int, optional): Line width in pixels (default: 1)
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    def fill_polygon(self, points: list[tuple[float, float]], color: Color, mode: DrawMode = DrawMode.FAST) -> None:
        """Fill a polygon area.

## Parameters
- `points` (list[tuple[float, float]]): List of (x, y) coordinates forming the polygon
- `color` (int, tuple or color object): Fill color.
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    def draw_image(self, image: Image, position: tuple[float, float], source_rect: Rectangle | tuple[float, float, float, float] | None = None, blend_mode: Blending | None = Blending.NORMAL) -> None:
        """Composite another image onto this canvas.

## Parameters
- `image` (Image): Source image to draw.
- `position` (tuple[float, float]): Top-left destination position `(x, y)`.
- `source_rect` (Rectangle | tuple[float, float, float, float] | None, optional): Optional source rectangle in
  source image coordinates. When omitted or `None`, the entire image is used.
- `blend_mode` (Blending | None, optional): Blending mode applied when drawing RGBA sources. Defaults to `Blending.NORMAL`; use `None` or `Blending.NONE` for direct copy.

## Notes
- Alpha blending is handled automatically based on the source image dtype; non-RGBA images always copy pixels directly.
- Drawing is clipped to the canvas bounds."""
        ...
    def draw_circle(self, center: tuple[float, float], radius: float, color: Color, width: int = 1, mode: DrawMode = DrawMode.FAST) -> None:
        """Draw a circle outline.

## Parameters
- `center` (tuple[float, float]): Center coordinates (x, y)
- `radius` (float): Circle radius
- `color` (int, tuple or color object): Color of the circle.
- `width` (int, optional): Line width in pixels (default: 1)
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    def fill_circle(self, center: tuple[float, float], radius: float, color: Color, mode: DrawMode = DrawMode.FAST) -> None:
        """Fill a circle area.

## Parameters
- `center` (tuple[float, float]): Center coordinates (x, y)
- `radius` (float): Circle radius
- `color` (int, tuple or color object): Fill color.
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    def draw_arc(self, center: tuple[float, float], radius: float, start_angle: float, end_angle: float, color: Color, width: int = 1, mode: DrawMode = DrawMode.FAST) -> None:
        """Draw an arc outline.

## Parameters
- `center` (tuple[float, float]): Center coordinates (x, y)
- `radius` (float): Arc radius in pixels
- `start_angle` (float): Starting angle in radians (0 = right, π/2 = down, π = left, 3π/2 = up)
- `end_angle` (float): Ending angle in radians
- `color` (int, tuple or color object): Color of the arc.
- `width` (int, optional): Line width in pixels (default: 1)
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)

## Notes
- Angles are measured in radians, with 0 pointing right and increasing clockwise
- For a full circle, use start_angle=0 and end_angle=2π
- The arc is drawn from start_angle to end_angle in the positive angular direction"""
        ...
    def fill_arc(self, center: tuple[float, float], radius: float, start_angle: float, end_angle: float, color: Color, mode: DrawMode = DrawMode.FAST) -> None:
        """Fill an arc (pie slice) area.

## Parameters
- `center` (tuple[float, float]): Center coordinates (x, y)
- `radius` (float): Arc radius in pixels
- `start_angle` (float): Starting angle in radians (0 = right, π/2 = down, π = left, 3π/2 = up)
- `end_angle` (float): Ending angle in radians
- `color` (int, tuple or color object): Fill color.
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)

## Notes
- Creates a filled pie slice from the center to the arc edge
- Angles are measured in radians, with 0 pointing right and increasing clockwise
- For a full circle, use start_angle=0 and end_angle=2π"""
        ...
    def draw_quadratic_bezier(self, p0: tuple[float, float], p1: tuple[float, float], p2: tuple[float, float], color: Color, width: int = 1, mode: DrawMode = DrawMode.FAST) -> None:
        """Draw a quadratic Bézier curve.

## Parameters
- `p0` (tuple[float, float]): Start point (x, y)
- `p1` (tuple[float, float]): Control point (x, y)
- `p2` (tuple[float, float]): End point (x, y)
- `color` (int, tuple or color object): Color of the curve.
- `width` (int, optional): Line width in pixels (default: 1)
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    def draw_cubic_bezier(self, p0: tuple[float, float], p1: tuple[float, float], p2: tuple[float, float], p3: tuple[float, float], color: Color, width: int = 1, mode: DrawMode = DrawMode.FAST) -> None:
        """Draw a cubic Bézier curve.

## Parameters
- `p0` (tuple[float, float]): Start point (x, y)
- `p1` (tuple[float, float]): First control point (x, y)
- `p2` (tuple[float, float]): Second control point (x, y)
- `p3` (tuple[float, float]): End point (x, y)
- `color` (int, tuple or color object): Color of the curve.
- `width` (int, optional): Line width in pixels (default: 1)
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    def draw_spline_polygon(self, points: list[tuple[float, float]], color: Color, width: int = 1, tension: float = 0.5, mode: DrawMode = DrawMode.FAST) -> None:
        """Draw a smooth spline through polygon points.

## Parameters
- `points` (list[tuple[float, float]]): List of (x, y) coordinates to interpolate through
- `color` (int, tuple or color object): Color of the spline.
- `width` (int, optional): Line width in pixels (default: 1)
- `tension` (float, optional): Spline tension (0.0 = angular, 0.5 = smooth, default: 0.5)
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    def fill_spline_polygon(self, points: list[tuple[float, float]], color: Color, tension: float = 0.5, mode: DrawMode = DrawMode.FAST) -> None:
        """Fill a smooth spline area through polygon points.

## Parameters
- `points` (list[tuple[float, float]]): List of (x, y) coordinates to interpolate through
- `color` (int, tuple or color object): Fill color.
- `tension` (float, optional): Spline tension (0.0 = angular, 0.5 = smooth, default: 0.5)
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    def draw_text(self, text: str, position: tuple[float, float], color: Color, font: BitmapFont = BitmapFont.font8x8(), scale: float = 1.0, mode: DrawMode = DrawMode.FAST) -> None:
        """Draw text on the canvas.

## Parameters
- `text` (str): Text to draw
- `position` (tuple[float, float]): Position coordinates (x, y)
- `color` (int, tuple or color object): Text color.
- `font` (BitmapFont, optional): Font object to use for rendering. If `None`, uses BitmapFont.font8x8()
- `scale` (float, optional): Text scale factor (default: 1.0)
- `mode` (`DrawMode`, optional): Drawing mode (default: `DrawMode.FAST`)"""
        ...
    @property
    def rows(self) -> int: ...
    @property
    def cols(self) -> int: ...
    @property
    def image(self) -> Image: ...
    def __init__(self, image: Image) -> None:
        """Create a Canvas for drawing operations on an Image.

A Canvas provides drawing methods to modify the pixels of an Image. The Canvas
maintains a reference to the parent Image to prevent it from being garbage collected
while drawing operations are in progress.

## Parameters
- `image` (Image): The Image object to draw on. Must be initialized with dimensions.

## Examples
```python
# Create an image and get its canvas
img = Image(100, 100, Rgb(255, 255, 255))
canvas = Canvas(img)

# Draw on the canvas
canvas.fill(Rgb(0, 0, 0))
canvas.draw_circle((50, 50), 20, Rgb(255, 0, 0))
```

## Notes
- The Canvas holds a reference to the parent Image
- All drawing operations modify the original Image pixels
- Use Image.canvas() method as a convenient way to create a Canvas"""
        ...

class FeatureDistributionMatching:
    """Feature Distribution Matching for image style transfer.
    """
    def set_target(self, image: Image) -> None:
        """Set the target image whose distribution will be matched.

This method computes and stores the target distribution statistics (mean and covariance)
for reuse across multiple source images. This is more efficient than recomputing
the statistics for each image when applying the same style to multiple images.

## Parameters
- `image` (`Image`): Target image providing the color distribution to match. Must be RGB.

## Examples
```python
fdm = FeatureDistributionMatching()
target = Image.load("sunset.png")
fdm.set_target(target)
```"""
        ...
    def set_source(self, image: Image) -> None:
        """Set the source image to be transformed.

The source image will be modified in-place when update() is called.

## Parameters
- `image` (`Image`): Source image to be modified. Must be RGB.

## Examples
```python
fdm = FeatureDistributionMatching()
source = Image.load("portrait.png")
fdm.set_source(source)
```"""
        ...
    def match(self, source: Image, target: Image) -> None:
        """Set both source and target images and apply the transformation.

This is a convenience method that combines set_source(), set_target(), and update()
into a single call. The source image is modified in-place.

## Parameters
- `source` (`Image`): Source image to be modified (RGB)
- `target` (`Image`): Target image providing the color distribution to match (RGB)

## Examples
```python
fdm = FeatureDistributionMatching()
source = Image.load("portrait.png")
target = Image.load("sunset.png")
fdm.match(source, target)  # source is now modified
source.save("portrait_sunset.png")
```"""
        ...
    def update(self) -> None:
        """Apply the feature distribution matching transformation.

This method modifies the source image in-place to match the target distribution.
Both source and target must be set before calling this method.

## Raises
- `RuntimeError`: If source or target has not been set

## Examples
```python
fdm = FeatureDistributionMatching()
fdm.set_target(target)
fdm.set_source(source)
fdm.update()  # source is now modified
```

### Batch processing
```python
fdm.set_target(style_image)
for img in images:
    fdm.set_source(img)
    fdm.update()  # Each img is modified in-place
```"""
        ...
    def __init__(self) -> None:
        """Initialize a new FeatureDistributionMatching instance.

Creates a new FDM instance that can be used to transfer color distributions
between images. The instance maintains internal state for efficient batch
processing of multiple images with the same target distribution.

## Examples
```python
# Create an FDM instance
fdm = FeatureDistributionMatching()

# Single image transformation
source = Image.load("portrait.png")
target = Image.load("sunset.png")
fdm.match(source, target)  # source is modified in-place
source.save("portrait_sunset.png")

# Batch processing with same style
style = Image.load("style_reference.png")
fdm.set_target(style)
for filename in image_files:
    img = Image.load(filename)
    fdm.set_source(img)
    fdm.update()
    img.save(f"styled_{filename}")
```

## Notes
- The algorithm matches mean and covariance of pixel distributions
- Target statistics are computed once and can be reused for multiple sources
- See: https://facebookresearch.github.io/dino/blog/"""
        ...

class PCA:
    """Principal Component Analysis (PCA) for dimensionality reduction.

PCA is a statistical technique that transforms data to a new coordinate system
where the greatest variance lies on the first coordinate (first principal component),
the second greatest variance on the second coordinate, and so on.

## Examples
```python
import zignal
import numpy as np

# Create PCA instance
pca = zignal.PCA()

# Prepare data using Matrix
data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
matrix = zignal.Matrix.from_numpy(data)

# Fit PCA, keeping 2 components
pca.fit(matrix, num_components=2)

# Project a single vector
coeffs = pca.project([2, 3, 4])

# Transform batch of data
transformed = pca.transform(matrix)

# Reconstruct from coefficients
reconstructed = pca.reconstruct(coeffs)
```
    """
    def fit(self, data: Matrix, num_components: int|None = None) -> None:
        """Fit the PCA model on training data.

## Parameters
- `data` (Matrix): Training samples matrix (n_samples × n_features)
- `num_components` (int, optional): Number of components to keep. If None, keeps min(n_samples-1, n_features)

## Raises
- ValueError: If data has insufficient samples (< 2)
- ValueError: If num_components is 0

## Examples
```python
matrix = zignal.Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
pca.fit(matrix)  # Keep all possible components
pca.fit(matrix, num_components=2)  # Keep only 2 components
```"""
        ...
    def project(self, vector: list[float]) -> list[float]:
        """Project a single vector onto the PCA space.

## Parameters
- `vector` (list[float]): Input vector to project

## Returns
list[float]: Coefficients in PCA space

## Raises
- RuntimeError: If PCA has not been fitted
- ValueError: If vector dimension doesn't match fitted data

## Examples
```python
coeffs = pca.project([1.0, 2.0, 3.0])
```"""
        ...
    def transform(self, data: Matrix) -> Matrix:
        """Transform data matrix to PCA space.

## Parameters
- `data` (Matrix): Data matrix (n_samples × n_features)

## Returns
Matrix: Transformed data (n_samples × n_components)

## Raises
- RuntimeError: If PCA has not been fitted
- ValueError: If data dimensions don't match fitted data

## Examples
```python
transformed = pca.transform(matrix)
```"""
        ...
    def reconstruct(self, coefficients: list[float]) -> list[float]:
        """Reconstruct a vector from PCA coefficients.

## Parameters
- `coefficients` (List[float]): Coefficients in PCA space

## Returns
List[float]: Reconstructed vector in original space

## Raises
- RuntimeError: If PCA has not been fitted
- ValueError: If number of coefficients doesn't match number of components

## Examples
```python
reconstructed = pca.reconstruct([1.0, 2.0])
```"""
        ...
    @property
    def mean(self) -> list[float]: ...
    @property
    def components(self) -> Matrix: ...
    @property
    def eigenvalues(self) -> list[float]: ...
    @property
    def num_components(self) -> int: ...
    @property
    def dim(self) -> int: ...

class ConvexHull:
    """Convex hull computation using Graham's scan algorithm.
    """
    def find(self, points: list[tuple[float, float]]) -> list[tuple[float, float]] | None:
        """Find the convex hull of a set of 2D points.

Returns the vertices of the convex hull in clockwise order as a list of
(x, y) tuples, or None if the hull is degenerate (e.g., all points are
collinear).

## Parameters
- `points` (list[tuple[float, float]]): List of (x, y) coordinate pairs.
  At least 3 points are required.

## Examples
```python
hull = ConvexHull()
points = [(0, 0), (1, 1), (2, 2), (3, 1), (4, 0), (2, 4), (1, 3)]
result = hull.find(points)
# Returns: [(0.0, 0.0), (1.0, 3.0), (2.0, 4.0), (4.0, 0.0)]
```"""
        ...
    def __init__(self) -> None:
        """Initialize a new ConvexHull instance.

Creates a new ConvexHull instance that can compute the convex hull of
2D point sets using Graham's scan algorithm. The algorithm has O(n log n)
time complexity where n is the number of input points.

## Examples
```python
# Create a ConvexHull instance
hull = ConvexHull()

# Find convex hull of points
points = [(0, 0), (1, 1), (2, 2), (3, 1), (4, 0), (2, 4), (1, 3)]
result = hull.find(points)
# Returns: [(0.0, 0.0), (1.0, 3.0), (2.0, 4.0), (4.0, 0.0)]
```

## Notes
- Returns vertices in clockwise order
- Returns None for degenerate cases (e.g., all points collinear)
- Requires at least 3 points for a valid hull"""
        ...

class SimilarityTransform:
    """Similarity transform (rotation + uniform scale + translation)
    """
    def __init__(self, from_points: list[tuple[float, float]], to_points: list[tuple[float, float]]) -> None:
        """Create similarity transform from point correspondences."""
        ...
    def project(self, points: tuple[float, float] | list[tuple[float, float]]) -> tuple[float, float] | list[tuple[float, float]]:
        """Transform point(s). Returns same type as input."""
        ...
    @property
    def matrix(self) -> list[list[float]]: ...
    @property
    def bias(self) -> tuple[float, float]: ...

class AffineTransform:
    """Affine transform (general 2D linear transform)
    """
    def __init__(self, from_points: list[tuple[float, float]], to_points: list[tuple[float, float]]) -> None:
        """Create affine transform from point correspondences."""
        ...
    def project(self, points: tuple[float, float] | list[tuple[float, float]]) -> tuple[float, float] | list[tuple[float, float]]:
        """Transform point(s). Returns same type as input."""
        ...
    @property
    def matrix(self) -> list[list[float]]: ...
    @property
    def bias(self) -> tuple[float, float]: ...

class ProjectiveTransform:
    """Projective transform (homography/perspective transform)
    """
    def __init__(self, from_points: list[tuple[float, float]], to_points: list[tuple[float, float]]) -> None:
        """Create projective transform from point correspondences."""
        ...
    def project(self, points: tuple[float, float] | list[tuple[float, float]]) -> tuple[float, float] | list[tuple[float, float]]:
        """Transform point(s). Returns same type as input."""
        ...
    def inverse(self) -> ProjectiveTransform | None:
        """Get inverse transform, or None if not invertible."""
        ...
    @property
    def matrix(self) -> list[list[float]]: ...

def solve_assignment_problem(cost_matrix: Matrix, policy: OptimizationPolicy = OptimizationPolicy.MIN) -> Assignment:
    """Solve the assignment problem using the Hungarian algorithm.

Finds the optimal one-to-one assignment that minimizes or maximizes
the total cost in O(n³) time. Handles both square and rectangular matrices.

## Parameters
- `cost_matrix` (`Matrix`): Cost matrix where element (i,j) is the cost of assigning row i to column j
- `policy` (`OptimizationPolicy`): Whether to minimize or maximize total cost (default: MIN)

## Returns
`Assignment`: Object containing the optimal assignments and total cost

## Examples
```python
from zignal import Matrix, OptimizationPolicy, solve_assignment_problem

matrix = Matrix([[1, 2, 6], [5, 3, 6], [4, 5, 0]])

for p in [OptimizationPolicy.MIN, OptimizationPolicy.MAX]:
    result = solve_assignment_problem(matrix, p)
    print("minimum cost") if p == OptimizationPolicy.MIN else print("maximum profit")
    print(f"  - Total cost:  {result.total_cost}")
    print(f"  - Assignments: {result.assignments}")
```"""
    ...

__version__: str
__all__: list[str]
