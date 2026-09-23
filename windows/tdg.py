import os
import math
import tkinter as tk
from PIL import Image, ImageTk
from widgets import LabVIEWNumericBox, LabVIEWDropdown, get_carona_logo, get_asset_file

class TDGWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("TDG")
        self.resizable(True, True)
        self.configure(bg="#8c97a8")

        self.setup_ui()
        self.center_on_parent(960, 560)
        self.minsize(860, 500)

    def center_on_parent(self, width=960, height=560):
        self.parent.update_idletasks()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()
        if pw < 100 or ph < 100:
            pw = self.winfo_screenwidth()
            ph = self.winfo_screenheight()
            px, py = 0, 0
        x = px + max(0, (pw - width) // 2)
        y = py + max(0, (ph - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        # 1. Top Header Area (Exit Button on Right, Centered Title)
        header_f = tk.Frame(self, bg="#8c97a8", height=44)
        header_f.pack(fill=tk.X, padx=12, pady=(8, 2))
        header_f.pack_propagate(False)

        # Exit Button at Top-Right
        exit_btn = tk.Button(
            header_f, text="Exit", bg="#ffff00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=16, pady=1,
            cursor="hand2", command=self.destroy
        )
        exit_btn.pack(side=tk.RIGHT, pady=4)

        # Carona Power Logo on Far Left
        self.logo_img = get_carona_logo(height=28)
        if self.logo_img:
            self.lbl_logo = tk.Label(header_f, image=self.logo_img, bg="#8c97a8", bd=0)
            self.lbl_logo.pack(side=tk.LEFT, padx=(4, 8), pady=4)

        # Centered Title "TDG vs New WinSDAC"
        title_c = tk.Canvas(header_f, bg="#8c97a8", highlightthickness=0)
        title_c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def draw_title(e=None):
            title_c.delete("all")
            w = title_c.winfo_width()
            cx = w // 2 or 380
            title_c.create_text(cx + 1, 21, text="TDG vs New WinSDAC", fill="#000000", font=("Arial", 16, "bold"))
            title_c.create_text(cx, 20, text="TDG vs New WinSDAC", fill="#ffffff", font=("Arial", 16, "bold"))

        title_c.bind("<Configure>", draw_title)

        # 2. Main Content Frame
        content_f = tk.Frame(self, bg="#8c97a8")
        content_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 10))

        # --- LEFT PANEL: Graph and Status Bar ---
        left_f = tk.Frame(content_f, bg="#8c97a8")
        left_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 6))

        # Graph Container with 3D Sunken Border
        graph_border = tk.Frame(left_f, bg="#3c444c", bd=2, relief=tk.SUNKEN)
        graph_border.pack(fill=tk.BOTH, expand=True)

        self.graph_canvas = tk.Canvas(graph_border, bg="#9ba5b5", highlightthickness=0)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        self.graph_canvas.bind("<Configure>", self.draw_graph)

        # Bottom Range Bar (Blue Outline Box)
        bar_f = tk.Frame(left_f, bg="#8c97a8", height=18)
        bar_f.pack(fill=tk.X, pady=(8, 2))
        bar_f.pack_propagate(False)

        self.bar_c = tk.Canvas(bar_f, bg="#8c97a8", height=18, highlightthickness=0)
        self.bar_c.pack(fill=tk.BOTH, expand=True)
        self.bar_c.bind("<Configure>", self.draw_bottom_bar)

        # Vertical Divider
        sep = tk.Frame(content_f, bg="#5c6877", width=2, bd=1, relief=tk.SUNKEN)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=4, pady=4)

        # --- RIGHT PANEL: Controls ---
        right_f = tk.Frame(content_f, bg="#8c97a8", width=240)
        right_f.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 4))
        right_f.pack_propagate(False)

        # Action Buttons
        btn_cfg = tk.Button(
            right_f, text="Configure Test Path", bg="#e0e4ec", fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, pady=3, cursor="hand2"
        )
        btn_cfg.pack(fill=tk.X, padx=12, pady=(0, 6))

        btn_open = tk.Button(
            right_f, text="Open", bg="#00c0ff", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, pady=3, cursor="hand2"
        )
        btn_open.pack(fill=tk.X, padx=12, pady=(0, 6))

        btn_save = tk.Button(
            right_f, text="Save", bg="#ffff99", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, pady=3, cursor="hand2"
        )
        btn_save.pack(fill=tk.X, padx=12, pady=(0, 10))

        # Graph Toolbar Palette [ + | 🔍 | ✋ | X | Y | MK ]
        pal_outer = tk.Frame(right_f, bg="#c8d0dc", bd=1, relief=tk.SUNKEN)
        pal_outer.pack(pady=(0, 12), padx=12)

        tools = [("+", False), ("🔍", True), ("✋", False), ("X", False), ("Y", False), ("MK", False)]
        for sym, active in tools:
            btn_tool = tk.Canvas(pal_outer, width=28, height=22, bg="#a0abbc" if active else "#d9e0ea", highlightthickness=0, cursor="hand2")
            btn_tool.pack(side=tk.LEFT, padx=1, pady=1)
            if active:
                btn_tool.create_rectangle(0, 0, 27, 21, outline="#5c6877")
                btn_tool.create_rectangle(3, 3, 7, 7, fill="#00ff00", outline="#00aa00")
            else:
                btn_tool.create_rectangle(0, 0, 27, 21, outline="#ffffff")
                btn_tool.create_rectangle(1, 1, 26, 20, outline="#8c97a8")
            btn_tool.create_text(15, 11, text=sym, fill="#000000", font=("Arial", 8, "bold"))

        # Dropdowns Table Frame
        grid_f = tk.Frame(right_f, bg="#8c97a8")
        grid_f.pack(fill=tk.X, padx=10, pady=(0, 10))

        def make_dropdown_row(parent, row, label_text, default_val, options):
            tk.Label(
                parent, text=label_text, bg="#8c97a8", fg="#000000",
                font=("Arial", 9, "bold"), anchor="w"
            ).grid(row=row, column=0, sticky="w", pady=4)

            drop_outer = tk.Frame(parent, bg="#5c6877", bd=1, relief=tk.SUNKEN)
            drop_outer.grid(row=row, column=1, sticky="e", pady=4, padx=(6, 0))

            drop_inner = tk.Frame(drop_outer, bg="#eef2f8")
            drop_inner.pack(fill=tk.BOTH, expand=True)

            lbl_val = tk.Label(
                drop_inner, text=default_val, bg="#eef2f8", fg="#000000",
                font=("Arial", 9, "bold"), width=10, anchor="w", padx=4
            )
            lbl_val.pack(side=tk.LEFT)

            btn_arrow = tk.Label(
                drop_inner, text="▼", bg="#d0d8e4", fg="#000000",
                font=("Arial", 7), relief=tk.RAISED, bd=1, padx=4, cursor="hand2"
            )
            btn_arrow.pack(side=tk.RIGHT, fill=tk.Y)

            menu = tk.Menu(self, tearoff=0)
            for opt in options:
                menu.add_command(label=opt, command=lambda o=opt, l=lbl_val: l.config(text=o))

            def popup(event):
                try:
                    menu.tk_popup(event.x_root, event.y_root)
                finally:
                    menu.grab_release()

            btn_arrow.bind("<Button-1>", popup)
            lbl_val.bind("<Button-1>", popup)

        make_dropdown_row(grid_f, 0, "Type", "Voltage", ["Voltage", "Current"])
        make_dropdown_row(grid_f, 1, "Polarity", "Positive", ["Positive", "Negative"])
        make_dropdown_row(grid_f, 2, "Impulse Type", "Lightning", ["Lightning", "Switching", "Chopped"])

        # Checkboxes
        cb_f = tk.Frame(right_f, bg="#8c97a8")
        cb_f.pack(fill=tk.X, padx=10, pady=(4, 0))

        def make_checkbox_row(parent, text_label):
            row_f = tk.Frame(parent, bg="#8c97a8")
            row_f.pack(fill=tk.X, pady=3)

            tk.Label(
                row_f, text=text_label, bg="#8c97a8", fg="#000000",
                font=("Arial", 9, "bold"), anchor="w"
            ).pack(side=tk.LEFT)

            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(
                row_f, variable=var, bg="#8c97a8", activebackground="#8c97a8",
                relief=tk.SUNKEN, bd=1, selectcolor="#ffffff", highlightthickness=0
            )
            cb.pack(side=tk.RIGHT)
            return var

        self.var_resample = make_checkbox_row(cb_f, "Resample 50k points")
        self.var_iec = make_checkbox_row(cb_f, "Enable IEC 60-1")

    def draw_graph(self, event=None):
        c = self.graph_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 100 or h < 100:
            return

        pad_left = 60
        pad_right = 20
        pad_top = 20
        pad_bottom = 40

        plot_w = w - pad_left - pad_right
        plot_h = h - pad_top - pad_bottom

        # Plot background
        c.create_rectangle(pad_left, pad_top, pad_left + plot_w, pad_top + plot_h, fill="#9ba5b5", outline="#7c8798", width=1.5)

        # Y Axis Ticks: -11 to 2 (14 tick marks)
        y_min, y_max = -11, 2
        total_y_steps = y_max - y_min

        for val in range(y_min, y_max + 1):
            ratio = (val - y_min) / float(total_y_steps)
            py = pad_top + plot_h - ratio * plot_h

            grid_color = "#6c7788" if val == 0 else "#7c8798"
            grid_width = 1.5 if val == 0 else 1.0
            c.create_line(pad_left, py, pad_left + plot_w, py, fill=grid_color, width=grid_width)
            c.create_text(pad_left - 8, py, text=str(val), fill="#000000", font=("Arial", 9, "bold"), anchor="e")

        # X Axis Ticks: 0 to 40u in steps of 4u (11 tick marks)
        x_ticks = [(0, "0"), (4, "4u"), (8, "8u"), (12, "12u"), (16, "16u"),
                   (20, "20u"), (24, "24u"), (28, "28u"), (32, "32u"), (36, "36u"), (40, "40u")]

        for val, label in x_ticks:
            ratio = val / 40.0
            px = pad_left + ratio * plot_w

            c.create_line(px, pad_top, px, pad_top + plot_h, fill="#7c8798", width=1)
            c.create_text(px, pad_top + plot_h + 10, text=label, fill="#000000", font=("Arial", 9, "bold"), anchor="n")

        # Y Axis Label: "Current[A]"
        c.create_text(16, pad_top + plot_h // 2, text="Current[A]", fill="#000000", font=("Arial", 10, "bold"), angle=90)

        # X Axis Label: "Time"
        c.create_text(pad_left + plot_w // 2, pad_top + plot_h + 26, text="Time", fill="#000000", font=("Arial", 10, "bold"))

    def draw_bottom_bar(self, event=None):
        c = self.bar_c
        c.delete("all")
        w = c.winfo_width()
        if w < 50:
            return
        pad_left = 60
        pad_right = 20
        c.create_rectangle(pad_left, 3, w - pad_right, 15, outline="#2b78e4", width=2, fill="#8c97a8")

# ==============================================================================
