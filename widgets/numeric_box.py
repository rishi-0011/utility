import tkinter as tk
from widgets.assets import get_pill_stepper_image

class LabVIEWNumericBox(tk.Frame):
    """
    1:1 Authentic LabVIEW Sunken Entry Box.
    Features:
    - Left-attached authentic LabVIEW pill stepper
    - 2px 3D Sunken border (#202020 bevel, pure white background #ffffff)
    - Bold, centered text
    """
    def __init__(self, parent, initial_val="0.0", width=62, height=26, font=("Arial", 10, "bold"),
                 has_stepper=True, pill_img=None, on_step=None, on_change=None, justify="center",
                 bg="#8c97a8", entry_bg="#ffffff", entry_fg="#000000"):
        super().__init__(parent, bg=bg)
        self.on_step = on_step
        self.on_change = on_change
        self.font = font

        # 1. Pill Stepper on Left
        if has_stepper:
            img = pill_img or get_pill_stepper_image(18, height)
            if img:
                self.lbl_pill = tk.Label(self, image=img, bg=bg, bd=0, cursor="hand2")
                self.lbl_pill.pack(side=tk.LEFT, padx=(0, 2))
                self.lbl_pill.bind("<Button-1>", self._handle_step)
            else:
                self.c_pill = tk.Canvas(self, width=18, height=height, bg=bg, highlightthickness=0, cursor="hand2")
                self.c_pill.pack(side=tk.LEFT, padx=(0, 2))
                r = 8
                self.c_pill.create_oval(1, 1, 17, 1 + 2*r, fill="#cfd8e6", outline="#5c6877")
                self.c_pill.create_oval(1, height - 1 - 2*r, 17, height - 1, fill="#cfd8e6", outline="#5c6877")
                self.c_pill.create_rectangle(1, 1 + r, 17, height - 1 - r, fill="#cfd8e6", outline="#cfd8e6")
                self.c_pill.create_line(1, 1 + r, 1, height - 1 - r, fill="#5c6877")
                self.c_pill.create_line(17, 1 + r, 17, height - 1 - r, fill="#5c6877")
                self.c_pill.create_polygon(5, 9, 13, 9, 9, 4, fill="#000000")
                self.c_pill.create_polygon(5, height - 9, 13, height - 9, 9, height - 4, fill="#000000")
                self.c_pill.bind("<Button-1>", self._handle_step)

        # 2. Outer Frame (fixed size container matching parent background)
        self.outer_frame = tk.Frame(self, bg=bg, width=width, height=height)
        self.outer_frame.pack(side=tk.LEFT)
        self.outer_frame.pack_propagate(False)

        # 3. Inner Entry Box with clean sunken border (no black outer frame border)
        self.entry = tk.Entry(
            self.outer_frame, font=font, bg=entry_bg, fg=entry_fg,
            bd=1, relief=tk.SUNKEN, justify=justify, highlightthickness=0
        )
        self.entry.insert(0, str(initial_val))
        self.entry.pack(fill=tk.BOTH, expand=True)

        if on_change:
            self.entry.bind("<KeyRelease>", lambda e: on_change())

    def _handle_step(self, event):
        if self.on_step:
            is_up = event.y < (self.outer_frame.winfo_height() // 2 or 13)
            self.on_step(1 if is_up else -1)

    def get(self):
        return self.entry.get()

    def set(self, val):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(val))

    def delete(self, first, last=None):
        self.entry.delete(first, last)

    def insert(self, index, string):
        self.entry.insert(index, string)

    def bind(self, sequence=None, func=None, add=None):
        return self.entry.bind(sequence, func, add)

    def focus_set(self):
        return self.entry.focus_set()

