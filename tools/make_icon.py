import math
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ui.logo import STROKE_WIDTH, STROKES, SYMBOL_HEIGHT, SYMBOL_WIDTH

OUTPUT = Path(__file__).resolve().parent.parent / "assets" / "xymyx.ico"
SIZES = (16, 24, 32, 48, 64, 128, 256)
SYMBOL_SHARE = 0.86
MINIMUM_STROKE_PIXELS = 1.5
PNG_FROM_SIZE = 256


def segment_distance(x, y, start, end):
    delta_x, delta_y = end[0] - start[0], end[1] - start[1]
    length = delta_x * delta_x + delta_y * delta_y
    position = max(0.0, min(1.0, ((x - start[0]) * delta_x + (y - start[1]) * delta_y) / length))
    return math.hypot(x - start[0] - position * delta_x, y - start[1] - position * delta_y)


def render(size):
    scale = size * SYMBOL_SHARE / SYMBOL_HEIGHT
    left = (size - SYMBOL_WIDTH * scale) / 2
    top = (size - SYMBOL_HEIGHT * scale) / 2
    strokes = [
        ((left + a * scale, top + b * scale), (left + c * scale, top + d * scale))
        for (a, b), (c, d) in STROKES
    ]
    radius = max(STROKE_WIDTH * scale, MINIMUM_STROKE_PIXELS) / 2
    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            distance = min(segment_distance(x + 0.5, y + 0.5, *stroke) for stroke in strokes)
            level = round(255 * max(0.0, min(1.0, radius - distance + 0.5)))
            row += bytes((level, level, level, 255))
        rows.append(bytes(row))
    return rows


def png_chunk(name, data):
    return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data))


def encode_png(rows, size):
    raw = b"".join(b"\x00" + row for row in rows)
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(raw, 9))
        + png_chunk(b"IEND", b"")
    )


def encode_bitmap(rows, size):
    header = struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    pixels = b"".join(bytes(row) for row in reversed(rows))
    mask = bytes(((size + 31) // 32 * 4) * size)
    return header + pixels + mask


def write_icon():
    images = []
    for size in SIZES:
        rows = render(size)
        images.append((size, encode_png(rows, size) if size >= PNG_FROM_SIZE else encode_bitmap(rows, size)))
    offset = 6 + 16 * len(images)
    directory = struct.pack("<HHH", 0, 1, len(images))
    for size, data in images:
        side = 0 if size >= 256 else size
        directory += struct.pack("<BBBBHHII", side, side, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_bytes(directory + b"".join(data for _size, data in images))


if __name__ == "__main__":
    write_icon()
