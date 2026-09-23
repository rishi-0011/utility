import tkinter as tk
import tkinter.font as tkfont
import os
import base64
from PIL import Image, ImageTk
from widgets import (
    LabVIEWNumericBox,
    get_carona_logo,
    get_pill_stepper_image,
    get_info_bubble_image,
    PILL_STEPPER_B64,
    INFO_BUBBLE_B64,
)

class VPCurveConfirmDialog(tk.Toplevel):
    def __init__(self, parent, title, message, on_yes, on_no):
        super().__init__(parent)
        self.parent = parent
        self.on_yes_cb = on_yes
        self.on_no_cb = on_no
        self.title(title)
        self.transient(parent)
        self.resizable(False, False)
        self.configure(bg="#8c97a8")
        self.geometry("480x180")

        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        x = px + max(0, (pw - 480) // 2)
        y = py + max(0, (ph - 180) // 2)
        self.geometry(f"480x180+{x}+{y}")

        self.setup_ui(title, message)
        self.grab_set()

    def setup_ui(self, title, message):
        content_f = tk.Frame(self, bg="#8c97a8")
        content_f.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))

        self.icon_img = get_info_bubble_image(56)

        if self.icon_img:
            lbl_icon = tk.Label(content_f, image=self.icon_img, bg="#8c97a8", bd=0)
            lbl_icon.pack(side=tk.LEFT, padx=(6, 18), anchor="n")
        else:
            icon_c = tk.Canvas(content_f, width=54, height=54, bg="#8c97a8", highlightthickness=0)
            icon_c.pack(side=tk.LEFT, padx=(6, 18), anchor="n")
            icon_c.create_oval(2, 2, 50, 50, fill="#ffffff", outline="#202020", width=1.5)
            icon_c.create_text(26, 26, text="i", fill="#0000cc", font=("Georgia", 22, "bold italic"))

        text_f = tk.Frame(content_f, bg="#8c97a8")
        text_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            text_f, text=title, bg="#8c97a8", fg="#000000",
            font=("Arial", 11, "bold"), anchor="w"
        ).pack(fill=tk.X, pady=(2, 6))

        tk.Label(
            text_f, text=message, bg="#8c97a8", fg="#000000",
            font=("Arial", 10, "bold"), justify="left", anchor="w"
        ).pack(fill=tk.X)

        btn_f = tk.Frame(self, bg="#8c97a8")
        btn_f.pack(fill=tk.X, padx=24, pady=(0, 18))

        btn_no = tk.Button(
            btn_f, text="No", bg="#ff0000", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, width=9, pady=2,
            cursor="hand2", command=self.on_no
        )
        btn_no.pack(side=tk.RIGHT, padx=(10, 0))

        btn_yes = tk.Button(
            btn_f, text="Yes", bg="#00cc00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, width=9, pady=2,
            cursor="hand2", command=self.on_yes
        )
        btn_yes.pack(side=tk.RIGHT)

    def on_yes(self):
        self.grab_release()
        self.destroy()
        if self.on_yes_cb:
            self.on_yes_cb()

    def on_no(self):
        self.grab_release()
        self.destroy()
        if self.on_no_cb:
            self.on_no_cb()


# ==============================================================================
# Voltage-Pressure Curves Window (GTN, IMC Positive, IMC Negative)
# ==============================================================================
VP_CURVE_CONFIGS = {
    "IMC_POS": {
        "title": "Definition IMC Positive Voltage-Pressure Curves",
        "header_prefix": "Definition IMC ",
        "header_highlight": "Positive",
        "header_highlight_color": "#ff2020",
        "header_suffix": " Voltage-Pressure Curves",
        "y_label": "Positive Charge Voltage [kV]",
        "dlg_title": "IMC Positive",
        "dlg_msg": "Do you want to overwrite IMC Positive\\nCurve values?",
        "limits": {"A": "60.0", "C": "110.0", "E": "145.0"},
        "setpoint": {"charge": "100", "pressure": "0.90", "curve": "2"},
        "default_table": [
            ("Curve1", "40,0", "0,20", "65,0", "1,20", "#e2d636"),
            ("Curve2", "70,0", "0,40", "115,0", "1,15", "#ff3333"),
            ("Curve3", "95,0", "0,36", "150,0", "1,16", "#33cc33"),
            ("Curve4", "130,0", "0,36", "190,0", "1,24", "#3399ff"),
        ],
        "curves": {
            1: {"p1_c": "50.0", "p1_p": "0.50", "p2_c": "65.0", "p2_p": "1.10"},
            2: {"p1_c": "70.0", "p1_p": "0.29", "p2_c": "100.0", "p2_p": "0.90"},
            3: {"p1_c": "125.0", "p1_p": "0.70", "p2_c": "180.0", "p2_p": "1.50"},
            4: {"p1_c": "105.0", "p1_p": "0.00", "p2_c": "160.0", "p2_p": "0.70"},
        },
    },
    "IMC_NEG": {
        "title": "Definition IMC Negative Voltage-Pressure Curves",
        "header_prefix": "Definition IMC ",
        "header_highlight": "Negative",
        "header_highlight_color": "#2b66ff",
        "header_suffix": " Voltage-Pressure Curves",
        "y_label": "Negative Charge Voltage [kV]",
        "dlg_title": "IMC Negative",
        "dlg_msg": "Do you want to overwrite IMC Negative\\nCurve values?",
        "limits": {"A": "70.0", "C": "100.0", "E": "145.0"},
        "setpoint": {"charge": "100", "pressure": "1.07", "curve": "2"},
        "default_table": [
            ("Curve1", "45,0", "0,10", "80,0", "1,24", "#e2d636"),
            ("Curve2", "70,0", "0,20", "105,0", "1,22", "#ff3333"),
            ("Curve3", "100,0", "0,40", "150,0", "1,27", "#33cc33"),
            ("Curve4", "130,0", "0,40", "190,0", "1,36", "#3399ff"),
        ],
        "curves": {
            1: {"p1_c": "45.0", "p1_p": "0.10", "p2_c": "85.0", "p2_p": "1.40"},
            2: {"p1_c": "70.0", "p1_p": "0.20", "p2_c": "125.0", "p2_p": "1.80"},
            3: {"p1_c": "100.0", "p1_p": "0.40", "p2_c": "180.0", "p2_p": "1.80"},
            4: {"p1_c": "130.0", "p1_p": "0.40", "p2_c": "180.0", "p2_p": "1.20"},
        },
    },
    "GTN": {
        "title": "Definition GTN Voltage-Pressure Curves",
        "header_prefix": "Definition GTN Voltage-Pressure Curves",
        "header_highlight": "",
        "header_highlight_color": "#ffffff",
        "header_suffix": "",
        "y_label": "Charge Voltage [kV]",
        "dlg_title": "GTN Curve",
        "dlg_msg": "Do you want to overwrite GTN Curve\\nvalues?",
        "limits": {"A": "70.0", "C": "110.0", "E": "150.0"},
        "setpoint": {"charge": "100", "pressure": "1.15", "curve": "2"},
        "default_table": [
            ("Curve1", "40", "0,27", "60,0", "1,20", "#e2d636"),
            ("Curve2", "75,0", "0,41", "105,0", "1,28", "#ff3333"),
            ("Curve3", "100,0", "0,41", "140,0", "1,25", "#33cc33"),
            ("Curve4", "120,0", "0,30", "190,0", "1,52", "#3399ff"),
        ],
        "curves": {
            1: {"p1_c": "45.0", "p1_p": "0.50", "p2_c": "60.0", "p2_p": "1.20"},
            2: {"p1_c": "75.0", "p1_p": "0.40", "p2_c": "85.0", "p2_p": "0.70"},
            3: {"p1_c": "100.0", "p1_p": "0.40", "p2_c": "175.0", "p2_p": "2.00"},
            4: {"p1_c": "120.0", "p1_p": "0.30", "p2_c": "200.0", "p2_p": "1.70"},
        },
    },
}

class VoltagePressureCurveWindow(tk.Toplevel):
    def __init__(self, parent, curve_type="IMC_POS", app_ref=None):
        super().__init__(parent)
        self.parent = parent
        self.app_ref = app_ref
        self.curve_type = curve_type
        self.cfg = VP_CURVE_CONFIGS.get(curve_type, VP_CURVE_CONFIGS["IMC_POS"])

        self.title(self.cfg["title"])
        self.resizable(True, True)
        self.minsize(940, 620)
        self.configure(bg="#8c97a8")

        # Load values from app_ref or defaults
        state_key = f"vp_curves_{curve_type.lower()}"
        if self.app_ref and getattr(self.app_ref, state_key, None):
            self.curve_data = dict(getattr(self.app_ref, state_key))
        else:
            self.curve_data = {
                "limits": dict(self.cfg["limits"]),
                "setpoint": dict(self.cfg["setpoint"]),
                "curves": {c: dict(self.cfg["curves"][c]) for c in range(1, 5)},
            }

        self.entries = {}
        self.pill_img = None
        self.load_pill_image()

        self.setup_ui()
        self.center_on_parent(980, 640)

        self.protocol("WM_DELETE_WINDOW", self.on_exit_click)

    def load_pill_image(self):
        self.pill_img = get_pill_stepper_image(18, 26)

    def center_on_parent(self, width=980, height=640):
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

    def make_stepper_box(self, parent, key, initial_val="0.0", width=62, delta=1.0, precision=1):
        def on_step_action(direction):
            entry = self.entries.get(key)
            if not entry:
                return
            try:
                val = float(entry.get().replace(",", "."))
            except ValueError:
                val = 0.0
            val += direction * delta
            entry.set(f"{val:.{precision}f}")
            self.draw_graph()

        num_box = LabVIEWNumericBox(
            parent, initial_val=initial_val, width=width, height=26,
            font=("Arial", 10, "bold"), on_step=on_step_action,
            on_change=self.draw_graph, bg="#8c97a8"
        )
        self.entries[key] = num_box
        return num_box

    def on_pill_click(self, event, key, delta, precision):
        entry = self.entries.get(key)
        if not entry:
            return
        try:
            val = float(entry.get().replace(",", "."))
        except ValueError:
            val = 0.0
        if event.y < 13:
            val += delta
        else:
            val -= delta
        entry.delete(0, tk.END)
        entry.insert(0, f"{val:.{precision}f}")
        self.draw_graph()

    def setup_ui(self):
        main_c = tk.Frame(self, bg="#5c6877", bd=2, relief=tk.SUNKEN)
        main_c.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # 1. Top Header Bar: Exit Button & Title
        header_f = tk.Frame(main_c, bg="#8c97a8", height=42)
        header_f.pack(fill=tk.X, padx=4, pady=(4, 0))
        header_f.pack_propagate(False)

        exit_btn = tk.Button(
            header_f, text="Exit", bg="#ffff00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=14, pady=1,
            cursor="hand2", command=self.on_exit_click
        )
        exit_btn.pack(side=tk.RIGHT, padx=6, pady=4)

        # Carona Power Logo on Far Left
        self.logo_img = get_carona_logo(height=28)
        if self.logo_img:
            self.lbl_logo = tk.Label(header_f, image=self.logo_img, bg="#8c97a8", bd=0)
            self.lbl_logo.pack(side=tk.LEFT, padx=(6, 8), pady=4)

        # Title canvas with 3D drop-shadow
        title_c = tk.Canvas(header_f, bg="#8c97a8", highlightthickness=0)
        title_c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        f_font = ("Arial", 15, "bold")
        font_obj = tkfont.Font(family="Arial", size=15, weight="bold")

        def draw_title(e=None):
            title_c.delete("all")
            w = title_c.winfo_width()
            cx = w // 2 or 380

            prefix = self.cfg.get("header_prefix", "")
            hi = self.cfg.get("header_highlight", "")
            suffix = self.cfg.get("header_suffix", "")
            hi_col = self.cfg.get("header_highlight_color", "#ffffff")

            if not hi:
                full_text = prefix or self.cfg.get("title", "Voltage-Pressure Curves")
                title_c.create_text(cx + 1, 21, text=full_text, fill="#000000", font=f_font, anchor="center")
                title_c.create_text(cx, 20, text=full_text, fill="#ffffff", font=f_font, anchor="center")
            else:
                w_pre = font_obj.measure(prefix)
                w_hi = font_obj.measure(hi)
                w_suf = font_obj.measure(suffix)
                total_w = w_pre + w_hi + w_suf
                x_start = cx - total_w // 2

                # 1. 3D Drop-Shadow (offset +1, +1 for each segment identically)
                title_c.create_text(x_start + 1, 21, text=prefix, fill="#000000", font=f_font, anchor="w")
                title_c.create_text(x_start + w_pre + 1, 21, text=hi, fill="#000000", font=f_font, anchor="w")
                title_c.create_text(x_start + w_pre + w_hi + 1, 21, text=suffix, fill="#000000", font=f_font, anchor="w")

                # 2. Foreground Two-Tone Text
                title_c.create_text(x_start, 20, text=prefix, fill="#ffffff", font=f_font, anchor="w")
                title_c.create_text(x_start + w_pre, 20, text=hi, fill=hi_col, font=f_font, anchor="w")
                title_c.create_text(x_start + w_pre + w_hi, 20, text=suffix, fill="#ffffff", font=f_font, anchor="w")

        title_c.bind("<Configure>", draw_title)

        # 2. Main Middle Area (Graph on Left, Controls & Presets on Right)
        mid_f = tk.Frame(main_c, bg="#8c97a8")
        mid_f.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        # Left Column: Graph (Canvas)
        left_graph_f = tk.Frame(mid_f, bg="#8c97a8")
        left_graph_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 6))

        g_border = tk.Frame(left_graph_f, bg="#3c444c", bd=2, relief=tk.SUNKEN)
        g_border.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(g_border, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw_graph())

        # Right Column: Controls & Presets
        right_panel = tk.Frame(mid_f, bg="#8c97a8", width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 4))
        right_panel.pack_propagate(False)

        # P1, P2, P3, P4 Buttons Row
        p_row = tk.Frame(right_panel, bg="#8c97a8")
        p_row.pack(fill=tk.X, pady=(2, 6))
        p_cols = [("P1", "#d8d4a0"), ("P2", "#e8a0a0"), ("P3", "#a8e0a0"), ("P4", "#90c0f8")]
        for p_txt, p_bg in p_cols:
            btn_p = tk.Button(p_row, text=p_txt, bg=p_bg, fg="black", font=("Arial", 8, "bold"), relief=tk.RAISED, bd=1, width=5, cursor="hand2")
            btn_p.pack(side=tk.LEFT, expand=True, padx=1)

        # Man / Auto Buttons Row
        ma_row = tk.Frame(right_panel, bg="#8c97a8")
        ma_row.pack(fill=tk.X, pady=(0, 6))
        btn_man = tk.Button(ma_row, text="Man", bg="#00cc00", fg="black", font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, width=8, cursor="hand2")
        btn_man.pack(side=tk.LEFT, padx=(10, 0))
        btn_auto = tk.Button(ma_row, text="Auto", bg="#d800d8", fg="white", font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, width=8, cursor="hand2")
        btn_auto.pack(side=tk.RIGHT, padx=(0, 10))

        # Charge Voltage input
        tk.Label(right_panel, text="Charge Voltage", bg="#8c97a8", fg="#ffffff", font=("Arial", 9, "bold")).pack()
        cv_f = tk.Frame(right_panel, bg="#8c97a8")
        cv_f.pack(pady=1)
        self.make_stepper_box(cv_f, "setpoint_charge", self.curve_data["setpoint"]["charge"], width=62, delta=5.0, precision=0).pack()

        # Pressure [bar] and Curve readouts
        pc_row = tk.Frame(right_panel, bg="#8c97a8")
        pc_row.pack(fill=tk.X, pady=4)

        # Pressure [bar]
        p_sub = tk.Frame(pc_row, bg="#8c97a8")
        p_sub.pack(side=tk.LEFT, expand=True)
        tk.Label(p_sub, text="Pressure [bar]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack()
        f_pbox = tk.Frame(p_sub, bg="#3c444c", bd=1, relief=tk.SUNKEN)
        f_pbox.pack()
        self.lbl_pressure = tk.Label(f_pbox, text=self.curve_data["setpoint"]["pressure"], bg="#ffffff", fg="#000000", font=("Arial", 9, "bold"), width=7)
        self.lbl_pressure.pack()

        # Curve
        c_sub = tk.Frame(pc_row, bg="#8c97a8")
        c_sub.pack(side=tk.LEFT, expand=True)
        tk.Label(c_sub, text="Curve", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack()
        f_cbox = tk.Frame(c_sub, bg="#3c444c", bd=1, relief=tk.SUNKEN)
        f_cbox.pack()
        self.lbl_curve = tk.Label(f_cbox, text=self.curve_data["setpoint"]["curve"], bg="#ffffff", fg="#000000", font=("Arial", 9, "bold"), width=5)
        self.lbl_curve.pack()

        # Horizontal Divider
        tk.Frame(right_panel, bg="#ffffff", height=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=4)

        # Auto Curve Limits
        tk.Label(right_panel, text="Auto Curve Limits", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack()
        lim_row = tk.Frame(right_panel, bg="#8c97a8")
        lim_row.pack(fill=tk.X, pady=2)

        for l_key, l_hdr in [("A", "A [60 kV]" if "60" in str(self.cfg["limits"]["A"]) else "A [70 kV]"),
                             ("C", "C [100 kV]" if "100" in str(self.cfg["limits"]["C"]) else "C [110 kV]"),
                             ("E", "E [145 kV]" if "145" in str(self.cfg["limits"]["E"]) else "E [150 kV]")]:
            l_box = tk.Frame(lim_row, bg="#8c97a8")
            l_box.pack(side=tk.LEFT, expand=True)
            tk.Label(l_box, text=l_hdr, bg="#8c97a8", fg="#000000", font=("Arial", 7, "bold")).pack()
            self.make_stepper_box(l_box, f"lim_{l_key}", self.curve_data["limits"][l_key], width=62, delta=5.0, precision=1).pack()

        # Default Curves Matrix Table
        tk.Label(right_panel, text="Default Curves", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack(pady=(4, 1))

        tbl_f = tk.Frame(right_panel, bg="#5c6877", bd=1, relief=tk.SUNKEN)
        tbl_f.pack(fill=tk.X, padx=4)

        # Table Header
        th = tk.Frame(tbl_f, bg="#5c6877")
        th.pack(fill=tk.X)
        for h_txt, h_w in [("", 6), ("Point1\n[kV]", 6), ("Point1\n[bar]", 6), ("Point2\n[kV]", 6), ("Point2\n[bar]", 6)]:
            tk.Label(th, text=h_txt, bg="#5c6877", fg="#ffffff", font=("Arial", 7, "bold"), width=h_w).pack(side=tk.LEFT)

        # Table Rows
        for r_name, p1k, p1b, p2k, p2b, c_color in self.cfg["default_table"]:
            tr = tk.Frame(tbl_f, bg="#5c6877")
            tr.pack(fill=tk.X, pady=0.5)
            tk.Label(tr, text=r_name, bg="#5c6877", fg=c_color, font=("Arial", 7, "bold"), width=6, anchor="w").pack(side=tk.LEFT)
            for c_val in [p1k, p1b, p2k, p2b]:
                tk.Label(tr, text=c_val, bg="#5c6877", fg="#ffffff", font=("Arial", 7), width=6).pack(side=tk.LEFT)

        # 3. Bottom Row: 4 Color-Coded Curve Group Boxes
        bot_f = tk.Frame(main_c, bg="#8c97a8")
        bot_f.pack(fill=tk.X, padx=4, pady=(4, 4))
        bot_f.columnconfigure(0, weight=1)
        bot_f.columnconfigure(1, weight=1)
        bot_f.columnconfigure(2, weight=1)
        bot_f.columnconfigure(3, weight=1)

        box_themes = [
            (1, "Curve 1", "#e2d636", "#ffff00", "black"),
            (2, "Curve 2", "#ff3333", "#ff0000", "white"),
            (3, "Curve 3", "#33cc33", "#00ee00", "black"),
            (4, "Curve 4", "#3399ff", "#0088ff", "white"),
        ]

        for idx, c_name, border_col, hdr_bg, hdr_fg in box_themes:
            c_box = tk.Frame(bot_f, bg=hdr_bg, bd=2, relief=tk.GROOVE)
            c_box.grid(row=0, column=idx-1, sticky="nsew", padx=3)

            # Header
            tk.Label(c_box, text=c_name, bg=hdr_bg, fg=hdr_fg, font=("Arial", 8, "bold")).pack(anchor="w", padx=2)

            pts_row = tk.Frame(c_box, bg=hdr_bg)
            pts_row.pack(fill=tk.X, padx=2, pady=2)

            # Point 1
            p1_box = tk.Frame(pts_row, bg=hdr_bg)
            p1_box.pack(side=tk.LEFT, expand=True, padx=2)
            tk.Label(p1_box, text="Point 1", bg=hdr_bg, fg=hdr_fg, font=("Arial", 7, "bold")).pack(anchor="w")
            tk.Label(p1_box, text="Charge [kV]", bg=hdr_bg, fg=hdr_fg, font=("Arial", 7)).pack(anchor="w")
            self.make_stepper_box(p1_box, f"c{idx}_p1_c", self.curve_data["curves"][idx]["p1_c"], width=62, delta=5.0, precision=1).pack()
            tk.Label(p1_box, text="Pressure [bar]", bg=hdr_bg, fg=hdr_fg, font=("Arial", 7)).pack(anchor="w")
            self.make_stepper_box(p1_box, f"c{idx}_p1_p", self.curve_data["curves"][idx]["p1_p"], width=62, delta=0.05, precision=2).pack()

            # Point 2
            p2_box = tk.Frame(pts_row, bg=hdr_bg)
            p2_box.pack(side=tk.RIGHT, expand=True, padx=2)
            tk.Label(p2_box, text="Point 2", bg=hdr_bg, fg=hdr_fg, font=("Arial", 7, "bold")).pack(anchor="w")
            tk.Label(p2_box, text="Charge [kV]", bg=hdr_bg, fg=hdr_fg, font=("Arial", 7)).pack(anchor="w")
            self.make_stepper_box(p2_box, f"c{idx}_p2_c", self.curve_data["curves"][idx]["p2_c"], width=62, delta=5.0, precision=1).pack()
            tk.Label(p2_box, text="Pressure [bar]", bg=hdr_bg, fg=hdr_fg, font=("Arial", 7)).pack(anchor="w")
            self.make_stepper_box(p2_box, f"c{idx}_p2_p", self.curve_data["curves"][idx]["p2_p"], width=62, delta=0.05, precision=2).pack()

    def draw_graph(self):
        c = self.canvas
        c.delete("all")

        w = c.winfo_width()
        h = c.winfo_height()
        if w < 50 or h < 50:
            return

        pad_l = 48
        pad_r = 16
        pad_t = 16
        pad_b = 34

        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        c.create_rectangle(pad_l, pad_t, pad_l + plot_w, pad_t + plot_h, fill="#000000", outline="#444444")

        # Y Ticks: 0 to 220 in steps of 10
        for y_val in range(0, 230, 10):
            ratio = y_val / 220.0
            py = pad_t + plot_h - ratio * plot_h
            line_col = "#333333" if y_val % 20 != 0 else "#444444"
            c.create_line(pad_l, py, pad_l + plot_w, py, fill=line_col)
            c.create_text(pad_l - 6, py, text=str(y_val), fill="#ffffff", font=("Arial", 7, "bold"), anchor="e")

        # X Ticks: 0.0 to 2.0 in steps of 0.1
        for i in range(21):
            x_val = i * 0.1
            ratio = x_val / 2.0
            px = pad_l + ratio * plot_w
            line_col = "#333333" if i % 2 != 0 else "#444444"
            c.create_line(px, pad_t, px, pad_t + plot_h, fill=line_col)
            c.create_text(px, pad_t + plot_h + 8, text=f"{x_val:.1f}", fill="#ffffff", font=("Arial", 7, "bold"), anchor="n")

        # Axis Labels
        c.create_text(12, pad_t + plot_h // 2, text=self.cfg["y_label"], fill="#ffffff", font=("Arial", 8, "bold"), angle=90)
        c.create_text(pad_l + plot_w // 2, pad_t + plot_h + 22, text="Relative Pressure [bar]", fill="#ffffff", font=("Arial", 8, "bold"))

        # Linear Curves 1 to 4
        colors = ["#e2d636", "#ff2020", "#00e000", "#00bfff"]
        for idx in range(1, 5):
            e_p1_c = self.entries.get(f"c{idx}_p1_c")
            e_p1_p = self.entries.get(f"c{idx}_p1_p")
            e_p2_c = self.entries.get(f"c{idx}_p2_c")
            e_p2_p = self.entries.get(f"c{idx}_p2_p")

            if e_p1_c and e_p1_p and e_p2_c and e_p2_p:
                try:
                    v1 = float(e_p1_c.get().replace(",", "."))
                    p1 = float(e_p1_p.get().replace(",", "."))
                    v2 = float(e_p2_c.get().replace(",", "."))
                    p2 = float(e_p2_p.get().replace(",", "."))
                except ValueError:
                    continue

                if p2 != p1:
                    m = (v2 - v1) / (p2 - p1)
                    k = v1 - m * p1
                    v_start = k
                    v_end = m * 2.0 + k

                    y1_px = pad_t + plot_h - (v_start / 220.0) * plot_h
                    y2_px = pad_t + plot_h - (v_end / 220.0) * plot_h

                    c.create_line(pad_l, y1_px, pad_l + plot_w, y2_px, fill=colors[idx-1], width=1.5)

        # Plot Marker Target on Curve 2 (Setpoint)
        try:
            sp_p = float(self.curve_data["setpoint"]["pressure"])
            sp_v = float(self.curve_data["setpoint"]["charge"])
            target_x = pad_l + (sp_p / 2.0) * plot_w
            target_y = pad_t + plot_h - (sp_v / 220.0) * plot_h
            # White square with inner black dot matching screenshot
            c.create_rectangle(target_x - 4, target_y - 4, target_x + 4, target_y + 4, outline="#ffffff", width=1.5, fill="#000000")
        except Exception:
            pass

        # Markers A, C, E
        markers = [("A", 0.9, 60.0), ("C", 1.1, 110.0), ("E", 1.0, 145.0)]
        if self.curve_type == "GTN":
            markers = [("A", 1.65, 70.0), ("C", 1.45, 110.0), ("E", 1.47, 150.0)]
        elif self.curve_type == "IMC_NEG":
            markers = [("A", 0.9, 70.0), ("C", 1.07, 100.0), ("E", 1.2, 145.0)]

        for lbl, mx, my in markers:
            px = pad_l + (mx / 2.0) * plot_w
            py = pad_t + plot_h - (my / 220.0) * plot_h
            c.create_polygon(px, py - 4, px + 4, py, px, py + 4, px - 4, py, fill="#ff00ff", outline="#ffffff")
            c.create_text(px, py - 10, text=lbl, fill="#ff00ff", font=("Arial", 8, "bold"))

    def on_exit_click(self):
        VPCurveConfirmDialog(
            self,
            title=self.cfg["dlg_title"],
            message=self.cfg["dlg_msg"],
            on_yes=self.on_confirm_yes,
            on_no=self.on_confirm_no
        )

    def on_confirm_yes(self):
        if self.app_ref:
            state_key = f"vp_curves_{self.curve_type.lower()}"
            updated = {
                "limits": {k: self.entries[f"lim_{k}"].get() for k in ["A", "C", "E"] if f"lim_{k}" in self.entries},
                "setpoint": {"charge": self.entries["setpoint_charge"].get() if "setpoint_charge" in self.entries else "100",
                             "pressure": self.lbl_pressure.cget("text"), "curve": self.lbl_curve.cget("text")},
                "curves": {
                    idx: {
                        "p1_c": self.entries[f"c{idx}_p1_c"].get(), "p1_p": self.entries[f"c{idx}_p1_p"].get(),
                        "p2_c": self.entries[f"c{idx}_p2_c"].get(), "p2_p": self.entries[f"c{idx}_p2_p"].get()
                    } for idx in range(1, 5) if f"c{idx}_p1_c" in self.entries
                }
            }
            setattr(self.app_ref, state_key, updated)
        self.destroy()

    def on_confirm_no(self):
        self.destroy()



class GTNCurveWindow(VoltagePressureCurveWindow):
    """
    Dedicated GTN Curve Window (GTN Voltage-Pressure Curves).
    Matches GTN Curve button on Utility Settings view.
    """
    def __init__(self, parent, app_ref=None):
        super().__init__(parent, curve_type="GTN", app_ref=app_ref)
