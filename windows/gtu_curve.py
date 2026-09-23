import tkinter as tk
import math
import os
import base64
from PIL import Image, ImageTk
from widgets import LabVIEWNumericBox, get_carona_logo, get_pill_stepper_image, CARONA_LOGO_B64, PILL_STEPPER_B64

class GTUCurveWindow(tk.Toplevel):
    def __init__(self, parent, app_ref=None, state_key="gtu_curve"):
        super().__init__(parent)
        self.parent = parent
        self.app_ref = app_ref
        self.state_key = state_key
        if not hasattr(self, "display_title"):
            self.display_title = "Voltage vs Sphere Distance"
        self.title("Gap Distance Setting")
        self.resizable(True, True)
        self.minsize(740, 560)

        # Exact sampled uniform color theme
        self.COLOR_BG = "#8c97a8"          # Steel-slate window background
        self.COLOR_PANEL = "#8c97a8"       # Panel background
        self.COLOR_BORDER = "#5c6877"      # Recessed groove border
        self.COLOR_GRAPH_BG = "#000000"    # Black graph background
        self.COLOR_GRID = "#262626"        # Subtle grid lines
        self.COLOR_CURVE = "#ff0000"       # Red curve line
        self.COLOR_EXIT = "#facc15"        # Yellow exit button
        self.COLOR_ORANGE = "#f3a812"      # Orange for selected row, Add, Del, p, q
        self.COLOR_TEXT_LIGHT = "#ffffff"  # White text

        self.configure(bg=self.COLOR_BG)

        self.font_title = ("Arial", 14, "bold")
        self.font_header = ("Arial", 8, "bold")
        self.font_label = ("Arial", 8)
        self.font_btn = ("Arial", 8, "bold")
        self.font_axis = ("Arial", 7)
        self.font_digital = ("Arial", 10, "bold")

        # Initial curve data matching screenshot
        if self.app_ref and getattr(self.app_ref, self.state_key, None):
            self.curve_data = [list(pt) for pt in getattr(self.app_ref, self.state_key)]
        else:
            self.curve_data = [
                [0.00, 0.0],
                [3.10, 10.0],
                [5.00, 15.0],
                [6.70, 20.0],
                [10.50, 30.0],
                [20.20, 50.0],
                [30.00, 70.0],
                [40.00, 90.0],
                [45.50, 100.0]
            ]
        self.selected_index = 0
        self.logo_img = None
        self.table_row_widgets = []

        self.setup_ui()
        self.center_on_parent(740, 580)

    def center_on_parent(self, width=740, height=580):
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
        # Top Header Bar: Title & Exit Button
        # ----------------------------------------------------------------------
        header_frame = tk.Frame(main_container, bg=self.COLOR_PANEL, height=44)
        header_frame.pack(fill=tk.X, padx=4, pady=(4, 0))
        header_frame.pack_propagate(False)

        # Exit Button on Far Right
        exit_btn = tk.Button(
            header_frame, text="Exit", bg=self.COLOR_EXIT, fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=14, pady=1,
            cursor="hand2", command=self.destroy
        )
        exit_btn.pack(side=tk.RIGHT, padx=6, pady=6)

        # Carona Power Logo on Far Left
        self.logo_img = get_carona_logo(height=28)
        if self.logo_img:
            self.lbl_logo = tk.Label(header_frame, image=self.logo_img, bg=self.COLOR_PANEL, bd=0)
            self.lbl_logo.pack(side=tk.LEFT, padx=(6, 8), pady=4)

        # Centered White Title with dark drop shadow
        self.title_canvas = tk.Canvas(header_frame, bg=self.COLOR_PANEL, highlightthickness=0)
        self.title_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def update_title(event=None):
            self.title_canvas.delete("all")
            w = self.title_canvas.winfo_width()
            h = self.title_canvas.winfo_height()
            if w < 10:
                w = 600
            cx = w // 2
            cy = h // 2 if h > 10 else 22
            d_title = getattr(self, "display_title", "Voltage vs Sphere Distance")
            self.title_canvas.create_text(cx + 1, cy + 1, text=d_title, fill="#1a2030", font=self.font_title)
            self.title_canvas.create_text(cx, cy, text=d_title, fill="#ffffff", font=self.font_title)

        self.title_canvas.bind("<Configure>", update_title)

        # Content Body
        body = tk.Frame(main_container, bg=self.COLOR_PANEL)
        body.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        content_split = tk.Frame(body, bg=self.COLOR_PANEL)
        content_split.pack(fill=tk.BOTH, expand=True)

        # ----------------------------------------------------------------------
        # LEFT: Black XY Graph Area
        # ----------------------------------------------------------------------
        graph_box = tk.Frame(content_split, bg=self.COLOR_PANEL)
        graph_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 8), pady=4)

        self.graph_canvas = tk.Canvas(graph_box, bg=self.COLOR_GRAPH_BG, highlightthickness=1, highlightbackground="#3c444c")
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        self.graph_canvas.bind("<Configure>", lambda e: self.draw_graph())

        # ----------------------------------------------------------------------
        # RIGHT: Data Table, Inputs, Ratio
        # ----------------------------------------------------------------------
        right_panel = tk.Frame(content_split, bg=self.COLOR_PANEL, width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 4), pady=4)
        right_panel.pack_propagate(False)

        # 1. Table + Side Buttons (p / q) Container
        tbl_container = tk.Frame(right_panel, bg=self.COLOR_PANEL)
        tbl_container.pack(fill=tk.X, pady=(0, 6))

        # Side Buttons (p / q) on the right of table
        btn_pq_frame = tk.Frame(tbl_container, bg=self.COLOR_PANEL)
        btn_pq_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 0))

        btn_p = tk.Button(
            btn_pq_frame, text="p", bg=self.COLOR_ORANGE, fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, width=2, height=1,
            cursor="hand2", command=self.on_nav_up
        )
        btn_p.pack(pady=(18, 4))

        btn_q = tk.Button(
            btn_pq_frame, text="q", bg=self.COLOR_ORANGE, fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, width=2, height=1,
            cursor="hand2", command=self.on_nav_down
        )
        btn_q.pack(pady=(4, 0))

        # Table outer frame
        tbl_outer = tk.Frame(tbl_container, bg="#5c6877", bd=1, relief=tk.SUNKEN)
        tbl_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Table Header
        tbl_header = tk.Frame(tbl_outer, bg="#c0c8d4", bd=1, relief=tk.RAISED)
        tbl_header.pack(fill=tk.X)
        tk.Label(tbl_header, text="Distance [mm.]", bg="#c0c8d4", fg="#0a1018", font=self.font_header, width=13, bd=1, relief=tk.GROOVE).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(tbl_header, text="Voltage [kV]", bg="#c0c8d4", fg="#0a1018", font=self.font_header, width=12, bd=1, relief=tk.GROOVE).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Table Canvas (with scrollbar)
        self.tbl_canvas = tk.Canvas(tbl_outer, bg="#ffffff", bd=0, highlightthickness=0, height=185)
        self.tbl_scroll = tk.Scrollbar(tbl_outer, orient=tk.VERTICAL, command=self.tbl_canvas.yview)
        self.tbl_canvas.configure(yscrollcommand=self.tbl_scroll.set)

        self.tbl_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tbl_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tbl_inner = tk.Frame(self.tbl_canvas, bg="#ffffff")
        self.tbl_canvas_window = self.tbl_canvas.create_window((0, 0), window=self.tbl_inner, anchor="nw")

        self.tbl_inner.bind("<Configure>", lambda e: self.tbl_canvas.configure(scrollregion=self.tbl_canvas.bbox("all")))
        self.tbl_canvas.bind("<Configure>", lambda e: self.tbl_canvas.itemconfig(self.tbl_canvas_window, width=e.width))

        # 3. Inputs Section (Distance, Voltage, Add, Del)
        inputs_box = tk.Frame(right_panel, bg=self.COLOR_PANEL)
        inputs_box.pack(fill=tk.X, pady=(4, 6))

        r_inputs = tk.Frame(inputs_box, bg=self.COLOR_PANEL)
        r_inputs.pack(fill=tk.X)

        # Distance input
        col_d = tk.Frame(r_inputs, bg=self.COLOR_PANEL)
        col_d.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        tk.Label(col_d, text="Distance [mm]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(anchor="center")
        self.spin_d, self.entry_d = self.make_numeric_box(col_d, "0.00")
        self.spin_d.pack(anchor="center")

        # Voltage input
        col_v = tk.Frame(r_inputs, bg=self.COLOR_PANEL)
        col_v.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))
        tk.Label(col_v, text="Voltage [KV]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(anchor="center")
        self.spin_v, self.entry_v = self.make_numeric_box(col_v, "0.0")
        self.spin_v.pack(anchor="center")

        # Buttons: Add & Del
        r_btns = tk.Frame(inputs_box, bg=self.COLOR_PANEL)
        r_btns.pack(fill=tk.X, pady=(6, 0))

        btn_add = tk.Button(
            r_btns, text="Add", bg=self.COLOR_ORANGE, fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, width=8,
            cursor="hand2", command=self.on_add_point
        )
        btn_add.pack(side=tk.LEFT, expand=True, padx=(0, 4))

        btn_del = tk.Button(
            r_btns, text="Del", bg=self.COLOR_ORANGE, fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, width=8,
            cursor="hand2", command=self.on_del_point
        )
        btn_del.pack(side=tk.LEFT, expand=True, padx=(4, 0))

        # 4. Default Modify Ratio [%] Digital Readout
        r_ratio = tk.Frame(right_panel, bg=self.COLOR_PANEL)
        r_ratio.pack(fill=tk.X, pady=(8, 0))

        tk.Label(r_ratio, text="Default Modify Ratio [%]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(anchor="center")

        ratio_sub = tk.Frame(r_ratio, bg=self.COLOR_PANEL)
        ratio_sub.pack(anchor="center", pady=(3, 0))

        sp_f = tk.Frame(ratio_sub, bg="#d0d8e8", bd=1, relief=tk.RAISED, cursor="hand2")
        sp_f.pack(side=tk.LEFT, padx=(0, 2))
        tk.Label(sp_f, text="▲\n▼", bg="#d0d8e8", fg="#1a2030", font=("Arial", 6, "bold")).pack(padx=2, pady=1)

        read_f = tk.Frame(ratio_sub, bg="#000000", bd=2, relief=tk.SUNKEN)
        read_f.pack(side=tk.LEFT)
        self.lbl_ratio = tk.Label(read_f, text="0.0", bg="#000000", fg="#00ff00", font=self.font_digital, width=8, anchor="center")
        self.lbl_ratio.pack(padx=4, pady=1)

        self.refresh_table()

    def draw_fallback_logo(self, parent):
        logo_c = tk.Canvas(parent, width=150, height=65, bg=self.COLOR_PANEL, highlightthickness=0)
        logo_c.pack(anchor="center")
        logo_c.create_oval(10, 10, 48, 48, fill="#1b3d63", outline="")
        logo_c.create_text(29, 29, text="⚡", fill="white", font=("Arial", 16, "bold"))
        logo_c.create_line(16, 51, 42, 51, fill="#1b3d63", width=2)
        logo_c.create_line(20, 54, 38, 54, fill="#1b3d63", width=2)
        logo_c.create_line(24, 57, 34, 57, fill="#1b3d63", width=2)
        logo_c.create_text(98, 24, text="CARONA", fill="#1b3d63", font=("Arial", 12, "bold"))
        logo_c.create_text(94, 42, text="POWER", fill="#1b3d63", font=("Arial", 12, "bold"))

    def make_numeric_box(self, parent, default_val, precision=1, step=1.0):
        """Creates 1:1 LabVIEW numeric box matching media_1789869699771.png with pill stepper."""
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
            row_bg = self.COLOR_ORANGE if is_sel else "#ffffff"
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

    def on_nav_up(self):
        if self.selected_index > 0:
            self.select_row(self.selected_index - 1)

    def on_nav_down(self):
        if self.selected_index < len(self.curve_data) - 1:
            self.select_row(self.selected_index + 1)

    def on_add_point(self):
        try:
            d = float(self.entry_d.get())
            v = float(self.entry_v.get())
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

    def draw_graph(self):
        c = self.graph_canvas
        c.delete("all")

        cw = c.winfo_width()
        ch = c.winfo_height()
        if cw < 50 or ch < 50:
            cw, ch = 430, 450

        gx1 = 58
        gy1 = 20
        gx2 = max(gx1 + 100, cw - 16)
        gy2 = max(gy1 + 100, ch - 38)
        gw = gx2 - gx1
        gh = gy2 - gy1

        # Inner graph rectangle
        c.create_rectangle(gx1, gy1, gx2, gy2, fill="#000000", outline="#3c444c", width=1.5)

        # Y Ticks & Grid (0.0 to 100.0, step 5.0)
        for v in range(0, 105, 5):
            y = gy2 - (v / 100.0) * gh
            c.create_line(gx1, y, gx2, y, fill=self.COLOR_GRID, width=1)
            c.create_text(gx1 - 6, y, text=f"{v:.1f}", fill="#ffffff", font=self.font_axis, anchor="e")

        # X Ticks & Grid (0.0 to 50.0, step 5.0)
        for d in range(0, 55, 5):
            x = gx1 + (d / 50.0) * gw
            c.create_line(x, gy1, x, gy2, fill=self.COLOR_GRID, width=1)
            c.create_text(x, gy2 + 8, text=f"{d:.1f}", fill="#ffffff", font=self.font_axis, anchor="center")

        # Labels
        c.create_text(16, (gy1 + gy2) // 2, text="Charging Voltage [kV]", fill="#ffffff", font=self.font_header, angle=90)
        c.create_text((gx1 + gx2) // 2, gy2 + 22, text="Distance [mm]", fill="#ffffff", font=self.font_header)

        # Plot Red Curve connecting points
        sorted_pts = sorted(self.curve_data, key=lambda x: x[0])
        coords = []
        for d, v in sorted_pts:
            px = gx1 + (d / 50.0) * gw
            py = gy2 - (v / 100.0) * gh
            coords.extend([px, py])

        if len(coords) >= 4:
            c.create_line(coords, fill=self.COLOR_CURVE, width=2)

        # Highlight selected point
        if 0 <= self.selected_index < len(self.curve_data):
            sd, sv = self.curve_data[self.selected_index]
            spx = gx1 + (sd / 50.0) * gw
            spy = gy2 - (sv / 100.0) * gh
            c.create_oval(spx - 4, spy - 4, spx + 4, spy + 4, fill="#fdb926", outline="#ffffff", width=1.5)


# ==============================================================================
# Main LabVIEW Utility Application
# ==============================================================================
