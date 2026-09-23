import tkinter as tk
import tkinter.font as tkfont
import math
import os
from widgets import (
    LabVIEWNumericBox,
    get_carona_logo,
    get_pill_stepper_image,
)

# ==============================================================================
# Authentic Datasets for MSG Curves (from LabVIEW reference screenshot)
# ==============================================================================
MSG_250_DATA = [
    [0.00, 0.0],
    [10.00, 31.7],
    [12.00, 37.4],
    [14.00, 42.9],
    [15.00, 45.5],
    [16.00, 48.1],
    [18.00, 54.0],
    [20.00, 59.0],
    [22.00, 64.5],
    [24.00, 70.0],
    [26.00, 75.5],
    [28.00, 81.0],
    [30.00, 86.0],
    [35.00, 99.0],
    [40.00, 112.0],
    [45.00, 125.0],
    [50.00, 138.0],
    [55.00, 151.0],
    [60.00, 163.0],
    [65.00, 175.0],
    [70.00, 187.0],
    [75.00, 198.0],
    [80.00, 210.0],
    [90.00, 231.0],
    [100.00, 252.0],
    [120.00, 288.0],
    [140.00, 318.0],
    [160.00, 336.0],
    [180.00, 348.0],
    [200.00, 355.0],
]

MSG_500_DATA = [
    [0.00, 0.0],
    [20.00, 61.0],
    [25.00, 75.0],
    [30.00, 89.0],
    [40.00, 117.0],
    [50.00, 144.0],
    [60.00, 170.0],
    [70.00, 195.0],
    [80.00, 219.0],
    [90.00, 242.0],
    [100.00, 265.0],
    [120.00, 308.0],
    [140.00, 348.0],
    [160.00, 385.0],
    [180.00, 419.0],
    [200.00, 450.0],
    [220.00, 478.0],
    [240.00, 504.0],
    [260.00, 528.0],
    [280.00, 550.0],
    [300.00, 570.0],
    [320.00, 588.0],
    [340.00, 604.0],
    [360.00, 618.0],
    [380.00, 630.0],
    [400.00, 640.0],
]


class MSGCurveWindow(tk.Toplevel):
    """
    Dedicated 1:1 LabVIEW Window for MSG Curves (Definition MSG Voltage-Distance Curves).
    Matches user reference screenshot media_1790166325853.png perfectly:
      - 2-tone header title with 3D drop-shadow
      - Uniform Carona Power branding on far left, Yellow Exit button on right
      - 0-400mm X-axis, 0-800kV Y-axis Black XY graph with smooth red curve
      - 250 / 500 sphere preset buttons
      - Scrollable data table with yellow selected row highlight and p/q buttons
      - Numeric inputs with pill steppers
      - Add / Del orange buttons
      - Default Modify Ratio [%] digital display (10.0) with mini stepper
    """
    def __init__(self, parent, polarity="Positive", app_ref=None):
        super().__init__(parent)
        self.parent = parent
        self.app_ref = app_ref
        pol_str = str(polarity).strip().lower()
        self.polarity = "Negative" if "neg" in pol_str else "Positive"
        self.state_key = f"msg_curve_{self.polarity.lower()}"

        self.title("Gap Distance Setting")
        self.resizable(True, True)
        self.minsize(780, 580)

        # Uniform steel-slate palette sampled from LabVIEW reference
        self.COLOR_BG = "#8c97a8"          # Outer window background
        self.COLOR_PANEL = "#8c97a8"       # Panel background
        self.COLOR_BORDER = "#5c6877"      # Recessed groove border
        self.COLOR_GRAPH_BG = "#000000"    # Black graph background
        self.COLOR_GRID = "#282828"        # Subtle grid lines
        self.COLOR_CURVE = "#ff0000"       # Red curve line
        self.COLOR_EXIT = "#ffff00"        # Yellow exit button
        self.COLOR_ORANGE = "#fca834"      # Orange for Add, Del, p, q
        self.COLOR_SEL = "#ffff00"         # Yellow selected row highlight
        self.COLOR_PRESET_ACTIVE = "#33cc33"   # Bright green active preset
        self.COLOR_PRESET_INACTIVE = "#cad2db" # Slate grey inactive preset

        self.configure(bg=self.COLOR_BG)

        self.font_title = ("Arial", 15, "bold")
        self.font_header = ("Arial", 8, "bold")
        self.font_label = ("Arial", 8)
        self.font_btn = ("Arial", 8, "bold")
        self.font_axis = ("Arial", 7)
        self.font_digital = ("Arial", 10, "bold")

        # Active sphere preset: 250 or 500
        self.active_preset = 250

        # Initial curve data
        saved = getattr(self.app_ref, self.state_key, None) if self.app_ref else None
        if saved and isinstance(saved, list) and len(saved) > 0:
            self.curve_data_250 = [list(pt) for pt in saved]
        else:
            self.curve_data_250 = [list(pt) for pt in MSG_250_DATA]
        self.curve_data_500 = [list(pt) for pt in MSG_500_DATA]

        self.curve_data = self.curve_data_250
        self.selected_index = 0
        self.ratio = 10.0
        self.logo_img = None
        self.table_row_widgets = []

        self.setup_ui()
        self.center_on_parent(840, 620)

    def center_on_parent(self, width=840, height=620):
        self.parent.update_idletasks()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()
        if pw < 100 or ph < 100:
            pw = self.winfo_screenwidth()
            ph = self.winfo_screenheight()
            px = 0
            py = 0
        x = px + max(0, (pw - width) // 2)
        y = py + max(0, (ph - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        main_container = tk.Frame(self, bg=self.COLOR_BORDER, bd=2, relief=tk.SUNKEN)
        main_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # ----------------------------------------------------------------------
        # Top Header Bar: Carona Logo, 3D Drop-Shadow Two-Tone Title, Exit Button
        # ----------------------------------------------------------------------
        header_frame = tk.Frame(main_container, bg=self.COLOR_PANEL, height=44)
        header_frame.pack(fill=tk.X, padx=4, pady=(4, 0))
        header_frame.pack_propagate(False)

        # Exit Button on Far Right
        exit_btn = tk.Button(
            header_frame, text="Exit", bg=self.COLOR_EXIT, fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=14, pady=1,
            cursor="hand2", command=self.on_exit
        )
        exit_btn.pack(side=tk.RIGHT, padx=6, pady=4)

        # Uniform Carona Power Logo on Far Left
        self.logo_img = get_carona_logo(height=28)
        if self.logo_img:
            self.lbl_logo = tk.Label(header_frame, image=self.logo_img, bg=self.COLOR_PANEL, bd=0)
            self.lbl_logo.pack(side=tk.LEFT, padx=(6, 8), pady=4)

        # Two-Tone Title Canvas with 3D Drop Shadow
        self.title_canvas = tk.Canvas(header_frame, bg=self.COLOR_PANEL, highlightthickness=0)
        self.title_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        prefix = "Definition MSG "
        hi = self.polarity
        hi_col = "#ff0000" if self.polarity == "Positive" else "#2b66ff"
        suffix = " Voltage-Distance Curves"

        f_font = ("Arial", 15, "bold")
        font_obj = tkfont.Font(family="Arial", size=15, weight="bold")

        def draw_title(event=None):
            self.title_canvas.delete("all")
            w = self.title_canvas.winfo_width()
            cx = w // 2 or 380

            w_pre = font_obj.measure(prefix)
            w_hi = font_obj.measure(hi)
            w_suf = font_obj.measure(suffix)
            total_w = w_pre + w_hi + w_suf
            x_start = cx - total_w // 2

            # 1. 3D Drop-Shadow (+1, +1 for each segment identically)
            self.title_canvas.create_text(x_start + 1, 21, text=prefix, fill="#000000", font=f_font, anchor="w")
            self.title_canvas.create_text(x_start + w_pre + 1, 21, text=hi, fill="#000000", font=f_font, anchor="w")
            self.title_canvas.create_text(x_start + w_pre + w_hi + 1, 21, text=suffix, fill="#000000", font=f_font, anchor="w")

            # 2. Foreground Two-Tone Text
            self.title_canvas.create_text(x_start, 20, text=prefix, fill="#ffffff", font=f_font, anchor="w")
            self.title_canvas.create_text(x_start + w_pre, 20, text=hi, fill=hi_col, font=f_font, anchor="w")
            self.title_canvas.create_text(x_start + w_pre + w_hi, 20, text=suffix, fill="#ffffff", font=f_font, anchor="w")

        self.title_canvas.bind("<Configure>", draw_title)

        # ----------------------------------------------------------------------
        # Middle Area: Left Graph (XY) + Right Control Panel
        # ----------------------------------------------------------------------
        content_split = tk.Frame(main_container, bg=self.COLOR_PANEL)
        content_split.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # LEFT: Black XY Graph Area (0-400mm, 0-800kV)
        graph_box = tk.Frame(content_split, bg=self.COLOR_PANEL)
        graph_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 6), pady=4)

        g_border = tk.Frame(graph_box, bg="#3c444c", bd=2, relief=tk.SUNKEN)
        g_border.pack(fill=tk.BOTH, expand=True)

        self.graph_canvas = tk.Canvas(g_border, bg=self.COLOR_GRAPH_BG, highlightthickness=0)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        self.graph_canvas.bind("<Configure>", lambda e: self.draw_graph())

        # RIGHT: Controls Panel (Presets, Table, Inputs, Buttons, Modify Ratio)
        right_panel = tk.Frame(content_split, bg=self.COLOR_PANEL, width=285)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(2, 4), pady=4)
        right_panel.pack_propagate(False)

        # 1. Preset Selector Buttons (250 / 500)
        preset_f = tk.Frame(right_panel, bg=self.COLOR_PANEL)
        preset_f.pack(fill=tk.X, pady=(2, 4))

        self.btn_250 = tk.Button(
            preset_f, text="250", bg=self.COLOR_PRESET_ACTIVE, fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, width=6,
            cursor="hand2", command=lambda: self.set_preset(250)
        )
        self.btn_250.pack(side=tk.LEFT, padx=(2, 0))

        self.btn_500 = tk.Button(
            preset_f, text="500", bg=self.COLOR_PRESET_INACTIVE, fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, width=6,
            cursor="hand2", command=lambda: self.set_preset(500)
        )
        self.btn_500.pack(side=tk.RIGHT, padx=(0, 20))

        # 2. Table + Side Navigation Buttons (p / q)
        tbl_container = tk.Frame(right_panel, bg=self.COLOR_PANEL)
        tbl_container.pack(fill=tk.BOTH, expand=True, pady=(2, 4))

        # Side Buttons (p / q) on Far Right
        btn_pq_frame = tk.Frame(tbl_container, bg=self.COLOR_PANEL)
        btn_pq_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 0))

        btn_p = tk.Button(
            btn_pq_frame, text="p", bg=self.COLOR_ORANGE, fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, width=2, height=1,
            cursor="hand2", command=self.on_nav_up
        )
        btn_p.pack(pady=(60, 10))

        btn_q = tk.Button(
            btn_pq_frame, text="q", bg=self.COLOR_ORANGE, fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, width=2, height=1,
            cursor="hand2", command=self.on_nav_down
        )
        btn_q.pack(pady=(10, 0))

        # Table Outer Frame
        tbl_outer = tk.Frame(tbl_container, bg="#5c6877", bd=1, relief=tk.SUNKEN)
        tbl_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Table Header
        tbl_header = tk.Frame(tbl_outer, bg="#c0c8d4", bd=1, relief=tk.RAISED)
        tbl_header.pack(fill=tk.X)
        tk.Label(
            tbl_header, text="Distance [mm.]", bg="#c0c8d4", fg="#0a1018",
            font=self.font_header, width=13, bd=1, relief=tk.GROOVE
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            tbl_header, text="Voltage [kV]", bg="#c0c8d4", fg="#0a1018",
            font=self.font_header, width=12, bd=1, relief=tk.GROOVE
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Table Scrollable Area
        self.tbl_canvas = tk.Canvas(tbl_outer, bg="#ffffff", bd=0, highlightthickness=0)
        self.tbl_scroll = tk.Scrollbar(tbl_outer, orient=tk.VERTICAL, command=self.tbl_canvas.yview)
        self.tbl_canvas.configure(yscrollcommand=self.tbl_scroll.set)

        self.tbl_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tbl_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tbl_inner = tk.Frame(self.tbl_canvas, bg="#ffffff")
        self.tbl_canvas_window = self.tbl_canvas.create_window((0, 0), window=self.tbl_inner, anchor="nw")

        self.tbl_inner.bind("<Configure>", lambda e: self.tbl_canvas.configure(scrollregion=self.tbl_canvas.bbox("all")))
        self.tbl_canvas.bind("<Configure>", lambda e: self.tbl_canvas.itemconfig(self.tbl_canvas_window, width=e.width))

        # Enable mouse wheel scrolling on table
        def on_mousewheel(event):
            self.tbl_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.tbl_canvas.bind_all("<MouseWheel>", on_mousewheel)

        # 3. Numeric Inputs & Action Buttons (Distance/Add in Col 1, Voltage/Del in Col 2)
        inputs_box = tk.Frame(right_panel, bg=self.COLOR_PANEL)
        inputs_box.pack(fill=tk.X, pady=(4, 4))
        inputs_box.columnconfigure(0, weight=1, uniform="ctrl_col")
        inputs_box.columnconfigure(1, weight=1, uniform="ctrl_col")

        col_d = tk.Frame(inputs_box, bg=self.COLOR_PANEL)
        col_d.grid(row=0, column=0, sticky="nsew", padx=(2, 6))

        tk.Label(col_d, text="Distance [mm]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(anchor="center", pady=(0, 2))
        self.spin_d, self.entry_d = self.make_numeric_box(col_d, "0.00", precision=2, step=1.0)
        self.spin_d.pack(anchor="center", pady=(0, 6))
        btn_add = tk.Button(
            col_d, text="Add", bg=self.COLOR_ORANGE, fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, width=10, pady=1,
            cursor="hand2", command=self.on_add_point
        )
        btn_add.pack(anchor="center")

        col_v = tk.Frame(inputs_box, bg=self.COLOR_PANEL)
        col_v.grid(row=0, column=1, sticky="nsew", padx=(6, 2))

        tk.Label(col_v, text="Voltage [KV]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(anchor="center", pady=(0, 2))
        self.spin_v, self.entry_v = self.make_numeric_box(col_v, "0.0", precision=1, step=1.0)
        self.spin_v.pack(anchor="center", pady=(0, 6))
        btn_del = tk.Button(
            col_v, text="Del", bg=self.COLOR_ORANGE, fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, width=10, pady=1,
            cursor="hand2", command=self.on_del_point
        )
        btn_del.pack(anchor="center")

        # 4. Default Modify Ratio [%] Digital Readout
        r_ratio = tk.Frame(right_panel, bg=self.COLOR_PANEL)
        r_ratio.pack(fill=tk.X, pady=(4, 6))

        tk.Label(r_ratio, text="Default Modify Ratio [%]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(anchor="center")

        ratio_sub = tk.Frame(r_ratio, bg=self.COLOR_PANEL)
        ratio_sub.pack(anchor="center", pady=(3, 0))

        # Mini up/down stepper buttons
        sp_f = tk.Frame(ratio_sub, bg="#d0d8e8", bd=1, relief=tk.RAISED)
        sp_f.pack(side=tk.LEFT, padx=(0, 3))

        btn_ratio_up = tk.Label(sp_f, text="▲", bg="#d0d8e8", fg="#1a2030", font=("Arial", 6, "bold"), cursor="hand2")
        btn_ratio_up.pack(padx=2, pady=(1, 0))
        btn_ratio_up.bind("<Button-1>", lambda e: self.on_ratio_change(1.0))

        btn_ratio_down = tk.Label(sp_f, text="▼", bg="#d0d8e8", fg="#1a2030", font=("Arial", 6, "bold"), cursor="hand2")
        btn_ratio_down.pack(padx=2, pady=(0, 1))
        btn_ratio_down.bind("<Button-1>", lambda e: self.on_ratio_change(-1.0))

        read_f = tk.Frame(ratio_sub, bg="#000000", bd=2, relief=tk.SUNKEN)
        read_f.pack(side=tk.LEFT)
        self.lbl_ratio = tk.Label(
            read_f, text=f"{self.ratio:.1f}", bg="#000000", fg="#00ff00",
            font=self.font_digital, width=8, anchor="center"
        )
        self.lbl_ratio.pack(padx=4, pady=1)

        # Initial table and graph render
        self.refresh_table()

    def set_preset(self, preset):
        self.active_preset = preset
        if preset == 250:
            self.btn_250.config(bg=self.COLOR_PRESET_ACTIVE)
            self.btn_500.config(bg=self.COLOR_PRESET_INACTIVE)
            self.curve_data = self.curve_data_250
        else:
            self.btn_250.config(bg=self.COLOR_PRESET_INACTIVE)
            self.btn_500.config(bg=self.COLOR_PRESET_ACTIVE)
            self.curve_data = self.curve_data_500

        self.selected_index = 0
        self.refresh_table()
        self.draw_graph()

    def make_numeric_box(self, parent, default_val, precision=1, step=1.0):
        def on_step(d):
            try:
                v = float(num_box.get().replace(",", "."))
            except ValueError:
                v = 0.0
            v = max(0.0, v + d * step)
            num_box.set(f"{v:.{precision}f}")

        num_box = LabVIEWNumericBox(
            parent, initial_val=default_val, width=62, height=26,
            font=("Arial", 10, "bold"), on_step=on_step, bg=self.COLOR_PANEL
        )
        return num_box, num_box

    def refresh_table(self):
        for w in self.tbl_inner.winfo_children():
            w.destroy()
        self.table_row_widgets = []

        for idx, (dist, volt) in enumerate(self.curve_data):
            is_sel = (idx == self.selected_index)
            row_bg = self.COLOR_SEL if is_sel else "#ffffff"
            row_fg = "#000000"

            row = tk.Frame(self.tbl_inner, bg=row_bg, bd=1, relief=tk.GROOVE, cursor="hand2")
            row.pack(fill=tk.X, expand=True)

            l1 = tk.Label(row, text=f"{dist:.2f}", bg=row_bg, fg=row_fg, font=self.font_label, width=13, anchor="center")
            l1.pack(side=tk.LEFT, fill=tk.X, expand=True)

            l2 = tk.Label(row, text=f"{volt:.1f}", bg=row_bg, fg=row_fg, font=self.font_label, width=12, anchor="center")
            l2.pack(side=tk.LEFT, fill=tk.X, expand=True)

            def make_click_handler(i=idx):
                return lambda e: self.select_row(i)

            row.bind("<Button-1>", make_click_handler(idx))
            l1.bind("<Button-1>", make_click_handler(idx))
            l2.bind("<Button-1>", make_click_handler(idx))
            self.table_row_widgets.append((row, l1, l2))

        # Update input boxes to selected item
        if 0 <= self.selected_index < len(self.curve_data):
            sel_d, sel_v = self.curve_data[self.selected_index]
            self.entry_d.delete(0, tk.END)
            self.entry_d.insert(0, f"{sel_d:.2f}")
            self.entry_v.delete(0, tk.END)
            self.entry_v.insert(0, f"{sel_v:.1f}")

    def select_row(self, idx):
        if 0 <= idx < len(self.curve_data):
            self.selected_index = idx
            self.refresh_table()
            self.draw_graph()

            # Scroll table to ensure selected row is visible
            total_rows = len(self.curve_data)
            if total_rows > 0:
                fraction = max(0.0, min(1.0, (idx - 3) / total_rows))
                self.tbl_canvas.yview_moveto(fraction)

    def on_nav_up(self):
        if self.selected_index > 0:
            self.select_row(self.selected_index - 1)

    def on_nav_down(self):
        if self.selected_index < len(self.curve_data) - 1:
            self.select_row(self.selected_index + 1)

    def on_add_point(self):
        try:
            d = float(self.entry_d.get().replace(",", "."))
            v = float(self.entry_v.get().replace(",", "."))
            replaced = False
            for i, item in enumerate(self.curve_data):
                if abs(item[0] - d) < 1e-4:
                    self.curve_data[i] = [d, v]
                    self.selected_index = i
                    replaced = True
                    break
            if not replaced:
                self.curve_data.append([d, v])
                self.curve_data.sort(key=lambda x: x[0])
                for i, item in enumerate(self.curve_data):
                    if abs(item[0] - d) < 1e-4:
                        self.selected_index = i
                        break
            self.refresh_table()
            self.draw_graph()
        except ValueError:
            pass

    def on_del_point(self):
        if len(self.curve_data) > 1 and 0 <= self.selected_index < len(self.curve_data):
            del self.curve_data[self.selected_index]
            self.selected_index = max(0, min(self.selected_index, len(self.curve_data) - 1))
            self.refresh_table()
            self.draw_graph()

    def on_ratio_change(self, delta):
        self.ratio = max(0.0, self.ratio + delta)
        self.lbl_ratio.config(text=f"{self.ratio:.1f}")

    def draw_graph(self):
        c = self.graph_canvas
        c.delete("all")

        cw = c.winfo_width()
        ch = c.winfo_height()
        if cw < 50 or ch < 50:
            cw, ch = 480, 480

        gx1 = 62
        gy1 = 20
        gx2 = max(gx1 + 100, cw - 18)
        gy2 = max(gy1 + 100, ch - 42)
        gw = gx2 - gx1
        gh = gy2 - gy1

        # Solid black inner graph canvas
        c.create_rectangle(gx1, gy1, gx2, gy2, fill="#000000", outline="#3c444c", width=1.5)

        # Y-Axis Ticks & Grid (0.0 to 800.0, step 50.0 matching screenshot)
        for v in range(0, 850, 50):
            y = gy2 - (v / 800.0) * gh
            c.create_line(gx1, y, gx2, y, fill=self.COLOR_GRID, width=1)
            c.create_line(gx1 - 4, y, gx1, y, fill="#ffffff", width=1)
            c.create_text(gx1 - 6, y, text=f"{v:.1f}", fill="#ffffff", font=self.font_axis, anchor="e")

        # X-Axis Ticks & Grid (0.0 to 400.0, step 50.0 matching screenshot)
        for d in range(0, 450, 50):
            x = gx1 + (d / 400.0) * gw
            c.create_line(x, gy1, x, gy2, fill=self.COLOR_GRID, width=1)
            c.create_line(x, gy2, x, gy2 + 4, fill="#ffffff", width=1)
            c.create_text(x, gy2 + 9, text=f"{d:.1f}", fill="#ffffff", font=self.font_axis, anchor="center")

        # Labels exactly as in screenshot
        c.create_text(16, (gy1 + gy2) // 2, text="Charging Voltage [KV]", fill="#ffffff", font=self.font_header, angle=90)
        c.create_text((gx1 + gx2) // 2, gy2 + 25, text="Distance [mm]", fill="#ffffff", font=self.font_header)

        # Plot Red Smooth Curve connecting points
        sorted_pts = sorted(self.curve_data, key=lambda x: x[0])
        coords = []
        for d, v in sorted_pts:
            px = gx1 + (min(400.0, max(0.0, d)) / 400.0) * gw
            py = gy2 - (min(800.0, max(0.0, v)) / 800.0) * gh
            coords.extend([px, py])

        if len(coords) >= 4:
            # Smooth cubic spline line matching screenshot
            c.create_line(coords, fill=self.COLOR_CURVE, width=2, smooth=True)

        # Highlight currently selected point on curve
        if 0 <= self.selected_index < len(self.curve_data):
            sd, sv = self.curve_data[self.selected_index]
            spx = gx1 + (min(400.0, max(0.0, sd)) / 400.0) * gw
            spy = gy2 - (min(800.0, max(0.0, sv)) / 800.0) * gh
            c.create_oval(spx - 4, spy - 4, spx + 4, spy + 4, fill="#ffff00", outline="#ffffff", width=1.5)

    def on_exit(self):
        if self.app_ref:
            setattr(self.app_ref, self.state_key, self.curve_data_250)
        self.destroy()


class MSGCurvePositivePolarityWindow(MSGCurveWindow):
    """
    Dedicated MSG Curve Positive Polarity Window.
    Matches 'MSG Curve - Positive polarity' button on Utility Settings view.
    """
    def __init__(self, parent, app_ref=None):
        super().__init__(parent, polarity="Positive", app_ref=app_ref)
