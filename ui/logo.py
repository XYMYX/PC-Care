import sys
from pathlib import Path

SYMBOL_WIDTH = 340
SYMBOL_HEIGHT = 464
STROKE_WIDTH = 22
STROKES = (
    ((0, 0), (0, 464)),
    ((340, 0), (340, 464)),
    ((0, 0), (340, 464)),
    ((340, 0), (0, 464)),
    ((170, 232), (170, 464)),
)


def icon_path():
    base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)
    return str(Path(base) / "assets" / "xymyx.ico")
