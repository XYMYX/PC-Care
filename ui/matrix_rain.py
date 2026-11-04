import random
import tkinter
from dataclasses import dataclass

import customtkinter as ctk

from ui import theme

GLYPHS = "0123456789XYMアイウエオカキクケコサシスセソタチツテトナニヌネノ"
SHADES = ("#8C8C8C", "#6A6A6A", "#565656", "#464646", "#383838", "#2C2C2C", "#222222", "#1A1A1A")
CELL_SIZE = 22
ACTIVE_SHARE = 0.6
TICK_MILLISECONDS = 110
REBUILD_DELAY_MILLISECONDS = 150
MAX_START_DELAY = 30
SPEEDS = (1, 2, 2, 3)


@dataclass
class Drop:
    column: int
    items: list
    speed: int
    row: int
    newest: int = 0


class MatrixRain(tkinter.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.BACKGROUND, highlightthickness=0, takefocus=0)
        self.drops = []
        self.ticks = 0
        self.tick_id = None
        self.rebuild_id = None
        self.bind("<Configure>", self.schedule_rebuild, add="+")

    def schedule_rebuild(self, _event):
        if self.rebuild_id:
            self.after_cancel(self.rebuild_id)
        self.rebuild_id = self.after(REBUILD_DELAY_MILLISECONDS, self.rebuild)

    def rebuild(self):
        self.rebuild_id = None
        self.delete("rain")
        self.cell_size = round(CELL_SIZE * ctk.ScalingTracker.get_widget_scaling(self))
        self.rows = self.winfo_height() // self.cell_size + 1
        columns = self.winfo_width() // self.cell_size
        rain_font = theme.canvas_font(self, 15)
        self.drops = [
            self.create_drop(column, rain_font)
            for column in range(columns)
            if random.random() < ACTIVE_SHARE
        ]
        self.tag_lower("rain")
        if self.tick_id is None:
            self.tick()

    def create_drop(self, column, rain_font):
        items = [
            self.create_text(-100, -100, text="", font=rain_font, tags="rain") for _shade in SHADES
        ]
        start = random.randint(-MAX_START_DELAY, self.rows)
        return Drop(column, items, random.choice(SPEEDS), start)

    def advance(self, drop):
        drop.row += 1
        if drop.row - len(SHADES) > self.rows:
            drop.row = -random.randint(1, MAX_START_DELAY)
        drop.newest = (drop.newest + 1) % len(drop.items)
        head = drop.items[drop.newest]
        x = drop.column * self.cell_size + self.cell_size // 2
        self.coords(head, x, drop.row * self.cell_size)
        self.itemconfigure(head, text=random.choice(GLYPHS))
        for age, shade in enumerate(SHADES):
            self.itemconfigure(drop.items[drop.newest - age], fill=shade)

    def tick(self):
        self.ticks += 1
        if self.winfo_toplevel().state() != "iconic":
            for drop in self.drops:
                if self.ticks % drop.speed == 0:
                    self.advance(drop)
        self.tick_id = self.after(TICK_MILLISECONDS, self.tick)

    def destroy(self):
        for pending in (self.tick_id, self.rebuild_id):
            if pending:
                self.after_cancel(pending)
        super().destroy()
