"""
Carona Power - LabVIEW Utility Application
=========================================
Main Application Entry Point and Sub-Window Launcher.

Modularized Architecture:
- widgets/: Reusable authentic LabVIEW widgets (steppers, dropdowns, asset loader).
- windows/: Sub-windows split strictly by button names appearing on the UI.
- assets/: Images and icons organized in assets/images/ and assets/icons/.
"""

import os
import re
import math
import base64
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# ==============================================================================
# Backwards Compatibility Re-Exports from widgets package
# ==============================================================================
from widgets import (
    CARONA_LOGO_B64,
    PILL_STEPPER_B64,
    INFO_BUBBLE_B64,
    get_carona_logo_image,
    get_carona_logo,
    get_pill_stepper_image,
    get_info_bubble_image,
    get_asset_file,
    LabVIEWNumericBox,
    LabVIEWDropdown,
)

# ==============================================================================
# Backwards Compatibility Re-Exports from windows package
# ==============================================================================
from windows import (
    LabVIEWSubWindow,
    TektronixScopeWindow,
    TimeChargeWindow,
    TimeChargeConfirmDialog,
    TDGWindow,
    GTUDistanceCalibrationWindow,
    GTUCurveWindow,
    GTNIMCPressureRegulationWindow,
    GTNConfirmDialog,
    MSGDistanceCalibrationWindow,
    CalibrationConfirmDialog,
    VoltagePressureCurveWindow,
    VPCurveConfirmDialog,
    GTNCurveWindow,
    IMCCurvePositivePolarityWindow,
    IMCCurveNegativePolarityWindow,
    MSGCurveWindow,
    MSGCurvePositivePolarityWindow,
    MSGCurveNegativePolarityWindow,
)


# ==============================================================================
# Main Application Class: LabVIEWUtilityApp
# ==============================================================================
class LabVIEWUtilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Utility")
        self.root.geometry("940x630")
        self.root.resizable(True, True)
        self.root.minsize(940, 630)

        # Uniform steel-slate theme palette matching target screenshot
        self.COLOR_BG = "#8c97a8"           # Outer window background
        self.COLOR_RECESSED = "#5c6877"     # Inner frame surround
        self.COLOR_PANEL = "#8c97a8"        # Panel background
        self.COLOR_PANEL_BORDER = "#4a5460" # Dark bevel border
        self.COLOR_TOPBAR = "#333333"       # Charcoal top bar
        self.COLOR_TAB_ACTIVE = "#cad2db"   # Active tab
        self.COLOR_TAB_INACTIVE = "#606c78" # Inactive tab on black bar

        self.root.configure(bg=self.COLOR_BG)

        self.font_title = ("Arial", 11, "bold")
        self.font_header = ("Arial", 8, "bold")
        self.font_btn = ("Arial", 8, "bold")
        self.font_label = ("Arial", 8)
        self.font_val = ("Arial", 8)

        self.sliders = {}
        self.leds = {}
        self.current_tab = "cFP"
        self.last_charge_time = 90
        self.gtu_curve = None
        self.msg_curve_positive = None
        self.msg_curve_negative = None
        self.vp_curves_gtn = None
        self.vp_curves_imc_pos = None
        self.vp_curves_imc_neg = None
        self.msg_cal_values = {
            "min_dist": "0.0", "volt_read_1": "0.003",
            "max_dist": "0.0", "volt_read_2": "0.003",
            "distance_mm": "-151.79", "coeff_a": "98.93", "coeff_b": "-152.08"
        }
        self.gtn_imc_values = {
            "p_setpoint": "0.00", "p_actual": "-0.01",
            "p_tol": "0.00", "reg_state": "STOP",
            "gtu_dist": "0.00", "gtu_spark": "0.00",
            "msg_dist": "0.00", "msg_spark": "0.00"
        }

        self.setup_ui()

    def open_scope_window(self):
        """Opens the Tektronix TDS 3032 Oscilloscope window."""
        TektronixScopeWindow(self.root)

    def open_gtu_calibration_window(self):
        """Opens the GTU Distance Transducer Calibration window."""
        GTUDistanceCalibrationWindow(self.root)

    def open_sub_window(self, name):
        """Opens dedicated sub-window for any settings button in the exact same size and place."""
        if name == "Dist. Calibration Sphere GTU":
            self.open_gtu_calibration_window()
        elif name == "GTU Curve":
            GTUCurveWindow(self.root, app_ref=self)
        elif name == "GTN Curve":
            GTNCurveWindow(self.root, app_ref=self)
        elif name == "IMC Curve - Positive polarity":
            IMCCurvePositivePolarityWindow(self.root, app_ref=self)
        elif name == "IMC Curve - Negative polarity":
            IMCCurveNegativePolarityWindow(self.root, app_ref=self)
        elif name == "MSG Curve - Positive polarity":
            MSGCurvePositivePolarityWindow(self.root, app_ref=self)
        elif name == "MSG Curve - Negative polarity":
            MSGCurveNegativePolarityWindow(self.root, app_ref=self)
        elif name == "TDG":
            TDGWindow(self.root)
        elif name == "Dist. Calibration Sphere MSG":
            MSGDistanceCalibrationWindow(self.root, app_ref=self)
        elif name == "GTN-IMC Pressure Regulation":
            GTNIMCPressureRegulationWindow(self.root, app_ref=self)
        elif name == "Time Charge":
            TimeChargeWindow(self.root, app_ref=self)
        elif name == "Scope":
            TektronixScopeWindow(self.root)
        else:
            LabVIEWSubWindow(self.root, name)

    def create_led(self, parent, is_on=False, size=13, name=None, interactive=False):
        """Draws glossy 3D sphere LED matching LabVIEW."""
        cursor_type = "hand2" if interactive else "arrow"
        canvas = tk.Canvas(parent, width=size, height=size, bg=self.COLOR_PANEL, highlightthickness=0, cursor=cursor_type)
        state = [is_on]

        def draw():
            canvas.delete("all")
            cur_on = state[0]
            canvas.create_oval(0, 0, size, size, fill="#142814" if cur_on else "#0a180a", outline="#050d05")
            if cur_on:
                canvas.create_oval(1, 1, size-1, size-1, fill="#00ff00", outline="#00aa00")
                canvas.create_oval(2, 2, size//2 + 1, size//2 + 1, fill="#d8ffd8", outline="")
            else:
                canvas.create_oval(1, 1, size-1, size-1, fill="#003800", outline="#002200")
                canvas.create_oval(2, 2, size//2 + 1, size//2 + 1, fill="#006600", outline="")

        if interactive:
            def toggle(event):
                state[0] = not state[0]
                draw()
            canvas.bind("<Button-1>", toggle)

        draw()
        if name:
            self.leds[name] = (canvas, state, draw)
        return canvas

    def load_channel_labels(self, filepath):
        """Reads channel labels from text file (extracts 2nd column/label, ignores index and rest)."""
        labels = []
        if filepath and os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # 1. Standard format: "1  H V Charging  DO  Channel 0  HVCharg"
                    m = re.match(r"^\s*\d+\s+(.+?)\s+DO\s+Channel", line, re.IGNORECASE)
                    if m:
                        labels.append(m.group(1).strip())
                        continue
                    # 2. Multi-space/tab delimited columns
                    parts = re.split(r"\s{2,}|\t+", line)
                    if len(parts) >= 2:
                        labels.append(parts[1].strip())
                        continue
                    # 3. Simple list with numbers: "1. Label" or "1 - Label" or "1 Label"
                    m3 = re.match(r"^\s*\d+[\.\:\)\-]?\s*[-–—]?\s*(.*)$", line)
                    if m3 and m3.group(1).strip():
                        txt = m3.group(1).strip()
                        txt = re.sub(r"\s+DO\b.*$", "", txt, flags=re.IGNORECASE).strip()
                        labels.append(txt)
                        continue
                    # 4. Fallback: whole line
                    labels.append(line)
        return labels

    def setup_ui(self):
        # Top Horizontal Toolbar (Authentic Solid Black strip)
        top_bar = tk.Frame(self.root, bg="#000000", height=30)
        top_bar.pack(side=tk.TOP, fill=tk.X)
        top_bar.pack_propagate(False)

        # Tabs on Left
        tabs_box = tk.Frame(top_bar, bg="#000000")
        tabs_box.pack(side=tk.LEFT, padx=4, pady=2)

        self.cfp_btn = tk.Button(
            tabs_box, text="cFP", bg=self.COLOR_TAB_ACTIVE, fg="black", 
            font=self.font_header, relief=tk.RAISED, bd=2, padx=14, pady=1,
            cursor="hand2", command=lambda: self.switch_tab("cFP")
        )
        self.cfp_btn.pack(side=tk.LEFT, padx=(0, 2))

        self.settings_btn = tk.Button(
            tabs_box, text="Settings", bg=self.COLOR_TAB_INACTIVE, fg="black", 
            font=self.font_label, relief=tk.RAISED, bd=2, padx=12, pady=1,
            cursor="hand2", command=lambda: self.switch_tab("Settings")
        )
        self.settings_btn.pack(side=tk.LEFT)

        # Exit Button on Right
        exit_btn = tk.Button(
            top_bar, text="Exit", bg="#ffff00", fg="black", 
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, padx=12, pady=0,
            cursor="hand2", command=self.root.quit
        )
        exit_btn.pack(side=tk.RIGHT, padx=2, pady=2)

        # Carona Power Logo in Sub-Header (Top-Left under Tabs)
        self.logo_sub_img = get_carona_logo_image(height=28)
        if self.logo_sub_img:
            self.lbl_sub_logo = tk.Label(self.root, image=self.logo_sub_img, bg=self.COLOR_BG, bd=0)
            self.lbl_sub_logo.place(x=8, y=32, anchor="nw")

        # Status Badge (shown only in cFP view) - anchored to top-right
        self.status_box = tk.Frame(self.root, bg="#00ff00", bd=2, relief=tk.RAISED)
        self.status_box.place(relx=1.0, x=-95, y=34, anchor="ne")
        tk.Label(
            self.status_box, text=" cFP Status OK ", bg="#00ff00", fg="black", 
            font=self.font_header
        ).pack(padx=4, pady=1)

        # Version Label - anchored to top-right
        self.ver_lbl = tk.Label(self.root, text="Ver. 2.1cFP", bg=self.COLOR_BG, fg="#1a222a", font=("Arial", 8, "bold"))
        self.ver_lbl.place(relx=1.0, x=-10, y=38, anchor="ne")

        # Main Recessed Container Panel
        self.container = tk.Frame(self.root, bg=self.COLOR_RECESSED, bd=2, relief=tk.SUNKEN)
        self.container.pack(fill=tk.BOTH, expand=True, padx=6, pady=(34, 6))

        # Build Views
        self.build_cfp_view()
        self.build_settings_view()

        # Start on cFP view
        self.switch_tab("cFP")

        # Real-time synchronization with sample_txt for utility.txt
        self.root.bind("<FocusIn>", self.check_txt_reload)
        self.root.after(1000, self._poll_txt_reload)

    def check_txt_reload(self, event=None):
        """Checks if sample_txt for utility.txt was modified on disk and dynamically reloads channel labels."""
        if hasattr(self, "txt_path") and os.path.exists(self.txt_path):
            try:
                curr_mtime = os.path.getmtime(self.txt_path)
                if curr_mtime != getattr(self, "last_txt_mtime", 0):
                    self.populate_do_channels()
            except Exception:
                pass

    def _poll_txt_reload(self):
        """Periodic background poll to sync UI with txt file changes."""
        self.check_txt_reload()
        try:
            self.root.after(1000, self._poll_txt_reload)
        except Exception:
            pass

    def switch_tab(self, tab_name):
        self.current_tab = tab_name
        if tab_name == "cFP":
            self.cfp_btn.config(bg=self.COLOR_TAB_ACTIVE, font=self.font_header)
            self.settings_btn.config(bg=self.COLOR_TAB_INACTIVE, font=self.font_label)
            self.status_box.place(relx=1.0, x=-95, y=34, anchor="ne")
            self.settings_frame.pack_forget()
            self.cfp_frame.pack(fill=tk.BOTH, expand=True)
            self.check_txt_reload()
        else:
            self.cfp_btn.config(bg=self.COLOR_TAB_INACTIVE, font=self.font_label)
            self.settings_btn.config(bg=self.COLOR_TAB_ACTIVE, font=self.font_header)
            self.status_box.place_forget()
            self.cfp_frame.pack_forget()
            self.settings_frame.pack(fill=tk.BOTH, expand=True)

    # ----------------------------------------------------------------------
    # TAB 1: cFP Main View (Fully Responsive & Proportionate)
    # ----------------------------------------------------------------------
    def build_cfp_view(self):
        self.cfp_frame = tk.Frame(self.container, bg=self.COLOR_RECESSED)

        # Proportionate 3-column layout filling 100% width: Panel 1 (37%), Panel 2 (28%), Panel 3 (35%)
        self.cfp_frame.columnconfigure(0, weight=37)
        self.cfp_frame.columnconfigure(1, weight=28)
        self.cfp_frame.columnconfigure(2, weight=35)
        self.cfp_frame.rowconfigure(0, weight=1)

        # PANEL 1: Output (DO-401 @1 and @2)
        p1 = tk.Frame(self.cfp_frame, bg=self.COLOR_PANEL, bd=1, relief=tk.SOLID)
        p1.grid(row=0, column=0, sticky="nsew", padx=(3, 2), pady=3)

        p1_lbl = tk.Canvas(p1, height=22, bg=self.COLOR_PANEL, highlightthickness=0)
        p1_lbl.pack(fill=tk.X, pady=(2, 0))
        def update_p1_lbl(e=None):
            p1_lbl.delete("all")
            cx = p1_lbl.winfo_width() // 2 or 170
            p1_lbl.create_text(cx + 1, 13, text="Output", fill="#ffffff", font=self.font_title)
            p1_lbl.create_text(cx, 12, text="Output", fill="#ff0000", font=self.font_title)
        p1_lbl.bind("<Configure>", update_p1_lbl)

        p1_hdr = tk.Frame(p1, bg=self.COLOR_PANEL)
        p1_hdr.pack(fill=tk.X, padx=8, pady=(0, 2))
        p1_hdr.columnconfigure(0, weight=1)
        p1_hdr.columnconfigure(1, weight=1)
        tk.Label(p1_hdr, text="cFP-DO-401 @1", bg=self.COLOR_PANEL, fg="#1a222a", font=self.font_header).grid(row=0, column=0, sticky="w", padx=4)
        tk.Label(p1_hdr, text="cFP-DO-401 @2", bg=self.COLOR_PANEL, fg="#1a222a", font=self.font_header).grid(row=0, column=1, sticky="w", padx=4)

        p1_body = tk.Frame(p1, bg=self.COLOR_PANEL)
        p1_body.pack(fill=tk.BOTH, expand=True, padx=6, pady=(2, 6))
        p1_body.columnconfigure(0, weight=1)
        p1_body.columnconfigure(1, weight=1)
        p1_body.rowconfigure(0, weight=1)

        self.p1_col1 = tk.Frame(p1_body, bg=self.COLOR_PANEL)
        self.p1_col1.grid(row=0, column=0, sticky="nsew", padx=2)

        self.p1_col2 = tk.Frame(p1_body, bg=self.COLOR_PANEL)
        self.p1_col2.grid(row=0, column=1, sticky="nsew", padx=2)

        self.p1_col1.columnconfigure(0, weight=1)
        self.p1_col2.columnconfigure(0, weight=1)

        self.populate_do_channels()

    def populate_do_channels(self):
        """Populates or refreshes Digital Output channel indicators and labels from sample_txt for utility.txt."""
        for child in self.p1_col1.winfo_children():
            child.destroy()
        for child in self.p1_col2.winfo_children():
            child.destroy()

        # Clean existing DO leds from self.leds
        self.leds = {k: v for k, v in self.leds.items() if not k.startswith("DO1_") and not k.startswith("DO2_")}

        # Prioritize root directory where user directly edits sample_txt for utility.txt
        root_txt = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_txt for utility.txt")
        self.txt_path = root_txt if os.path.exists(root_txt) else (get_asset_file("sample_txt for utility.txt") or root_txt)

        try:
            self.last_txt_mtime = os.path.getmtime(self.txt_path) if os.path.exists(self.txt_path) else 0
        except Exception:
            self.last_txt_mtime = 0

        file_labels = self.load_channel_labels(self.txt_path)

        if len(file_labels) > 0:
            do1_items = file_labels[:15]
            do2_items = file_labels[15:30]
        else:
            do1_items = [
                "H.V. Charging", "Emergency Signal", "MTSignal", "Pol+ Gen CC",
                "Pol- Gen CC", "Hooter", "GND Control", "IMC FS Supply",
                "Decrease Dist GTU", "Increase Dist GTU", "Increase MSG",
                "Start Charge", "Pol - Card", "Pol + Card", "Maharshi"
            ]
            do2_items = [
                "Inc Press GTN", "Dec Press GTN", "Plunger All Stages", "Plunger 1 Stage",
                "Plunger 2 Stage", "Sphere A GTN", "Sphere B GTN", "Sphere A IMC",
                "Sphere B IMC", "Inc Press IMC", "Dec Press IMC", "xx", "xx", "xx", "xx"
            ]

        num_do_rows = max(len(do1_items), len(do2_items), 15)
        for i in range(num_do_rows):
            self.p1_col1.rowconfigure(i, weight=1)
            self.p1_col2.rowconfigure(i, weight=1)

        for i, item in enumerate(do1_items):
            if item is None:
                tk.Frame(self.p1_col1, bg=self.COLOR_PANEL).grid(row=i, column=0, sticky="w")
                continue
            row = tk.Frame(self.p1_col1, bg=self.COLOR_PANEL)
            row.grid(row=i, column=0, sticky="w")
            led = self.create_led(row, is_on=False, size=13, name=f"DO1_{item}", interactive=True)
            led.pack(side=tk.LEFT, padx=(0, 5))
            tk.Label(row, text=item, bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_label).pack(side=tk.LEFT)

        for i, item in enumerate(do2_items):
            if item is None:
                tk.Frame(self.p1_col2, bg=self.COLOR_PANEL).grid(row=i, column=0, sticky="w")
                continue
            row = tk.Frame(self.p1_col2, bg=self.COLOR_PANEL)
            row.grid(row=i, column=0, sticky="w")
            led = self.create_led(row, is_on=False, size=13, name=f"DO2_{item}", interactive=True)
            led.pack(side=tk.LEFT, padx=(0, 5))
            tk.Label(row, text=item, bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_label).pack(side=tk.LEFT)

        # PANEL 2: Input & Output Sliders (AIO-610 @3)
        p2 = tk.Frame(self.cfp_frame, bg=self.COLOR_PANEL, bd=1, relief=tk.SOLID)
        p2.grid(row=0, column=1, sticky="nsew", padx=2, pady=3)

        p2_in_lbl = tk.Canvas(p2, height=22, bg=self.COLOR_PANEL, highlightthickness=0)
        p2_in_lbl.pack(fill=tk.X, pady=(2, 0))
        def update_p2_in(e=None):
            p2_in_lbl.delete("all")
            cx = p2_in_lbl.winfo_width() // 2 or 130
            p2_in_lbl.create_text(cx + 1, 13, text="Input", fill="#ffffff", font=self.font_title)
            p2_in_lbl.create_text(cx, 12, text="Input", fill="#00cc00", font=self.font_title)
        p2_in_lbl.bind("<Configure>", update_p2_in)

        tk.Label(p2, text="cFP-AIO-610 @3", bg=self.COLOR_PANEL, fg="#1a222a", font=self.font_header).pack(anchor="center")

        p2_body = tk.Frame(p2, bg=self.COLOR_PANEL)
        p2_body.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)

        input_sliders = [
            ("DivTens", -0.003, -10, 10, ["-10", "-5", "0", "5", "10"], True),
            ("DistGTU-PressGTN", 1.999, 0, 10, ["0", "2", "4", "6", "8", "10"], True),
            ("Pressure IMC", 0.021, 0, 10, ["0", "2", "4", "6", "8", "10"], True),
            ("Distance MSG", 0.000, 0, 10, ["0", "2", "4", "6", "8", "10"], True)
        ]

        # Input sliders are indicators (read-only telemetry, non-interactive)
        for name, val, min_v, max_v, ticks, blue_fill in input_sliders:
            self.build_labview_slider(p2_body, name, val, min_v, max_v, ticks, blue_fill=blue_fill, has_spin=False, interactive=False)

        p2_out_lbl = tk.Canvas(p2_body, height=20, bg=self.COLOR_PANEL, highlightthickness=0)
        p2_out_lbl.pack(fill=tk.X, pady=(2, 0))
        def update_p2_out(e=None):
            p2_out_lbl.delete("all")
            cx = p2_out_lbl.winfo_width() // 2 or 125
            p2_out_lbl.create_text(cx + 1, 11, text="Output", fill="#ffffff", font=self.font_title)
            p2_out_lbl.create_text(cx, 10, text="Output", fill="#ff0000", font=self.font_title)
        p2_out_lbl.bind("<Configure>", update_p2_out)

        output_sliders = [
            ("Ritardo", 0.000, 0, 10, ["0", "2", "4", "6", "8", "10"]),
            ("Carica", 0.000, 0, 10, ["0", "2", "4", "6", "8", "10"]),
            ("Gradi", 0.000, 0, 10, ["0", "2", "4", "6", "8", "10"]),
            ("xx", 0.000, 0, 10, ["0", "2", "4", "6", "8", "10"])
        ]

        # Output sliders are setpoint controls (user-interactive)
        for name, val, min_v, max_v, ticks in output_sliders:
            self.build_labview_slider(p2_body, name, val, min_v, max_v, ticks, blue_fill=False, has_spin=True, interactive=True)

        # PANEL 3: Input (DI-301 @4 & @5) - Field Digital Inputs (Read-only Indicators)
        p3 = tk.Frame(self.cfp_frame, bg=self.COLOR_PANEL, bd=1, relief=tk.SOLID)
        p3.grid(row=0, column=2, sticky="nsew", padx=(2, 3), pady=3)

        p3_lbl = tk.Canvas(p3, height=22, bg=self.COLOR_PANEL, highlightthickness=0)
        p3_lbl.pack(fill=tk.X, pady=(2, 0))
        def update_p3_lbl(e=None):
            p3_lbl.delete("all")
            cx = p3_lbl.winfo_width() // 2 or 148
            p3_lbl.create_text(cx + 1, 13, text="Input", fill="#ffffff", font=self.font_title)
            p3_lbl.create_text(cx, 12, text="Input", fill="#00cc00", font=self.font_title)
        p3_lbl.bind("<Configure>", update_p3_lbl)

        p3_hdr = tk.Frame(p3, bg=self.COLOR_PANEL)
        p3_hdr.pack(fill=tk.X, padx=8, pady=(0, 2))
        p3_hdr.columnconfigure(0, weight=1)
        p3_hdr.columnconfigure(1, weight=1)
        tk.Label(p3_hdr, text="cFP-DI-301 @4", bg=self.COLOR_PANEL, fg="#1a222a", font=self.font_header).grid(row=0, column=0, sticky="w", padx=4)
        tk.Label(p3_hdr, text="cFP-DI-301 @5", bg=self.COLOR_PANEL, fg="#1a222a", font=self.font_header).grid(row=0, column=1, sticky="w", padx=4)

        p3_body = tk.Frame(p3, bg=self.COLOR_PANEL)
        p3_body.pack(fill=tk.BOTH, expand=True, padx=6, pady=(2, 6))
        p3_body.columnconfigure(0, weight=1)
        p3_body.columnconfigure(1, weight=1)
        p3_body.rowconfigure(0, weight=1)

        p3_col1 = tk.Frame(p3_body, bg=self.COLOR_PANEL)
        p3_col1.grid(row=0, column=0, sticky="nsew", padx=2)

        p3_col2 = tk.Frame(p3_body, bg=self.COLOR_PANEL)
        p3_col2.grid(row=0, column=1, sticky="nsew", padx=2)

        p3_col1.columnconfigure(0, weight=1)
        p3_col2.columnconfigure(0, weight=1)

        di4_items = [
            "Thermal Magnet 1", "Thermal Magnet 2", "Thermal Magnet 3", "Mains Ok",
            "Emergency Stop", "Door Interlock", "Ground SW Open", "Ground SW Close",
            "Polarity +", "Polarity -", "Charging Ready", "Spark Gap Ready",
            "Trigger Ready", "Safety Loop", "xx"
        ]
        di5_items = [
            "Pressure GTN OK", "Pressure IMC OK", "Vacuum OK", "Air Pressure OK",
            "Water Flow OK", "Overvoltage Alarm", "Overcurrent Alarm", "Gas Alarm",
            "Stage 1 Spark", "Stage 2 Spark", "Stage 3 Spark", "Stage 4 Spark",
            "Spare Input 1", "Spare Input 2", "Spare Input 3"
        ]

        num_di_rows = max(len(di4_items), len(di5_items))
        for i in range(num_di_rows):
            p3_col1.rowconfigure(i, weight=1)
            p3_col2.rowconfigure(i, weight=1)

        for i, item in enumerate(di4_items):
            row = tk.Frame(p3_col1, bg=self.COLOR_PANEL)
            row.grid(row=i, column=0, sticky="w")
            led = self.create_led(row, is_on=False, size=13, name=f"DI4_{item}", interactive=False)
            led.pack(side=tk.LEFT, padx=(0, 5))
            tk.Label(row, text=item, bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_label).pack(side=tk.LEFT)

        for i, item in enumerate(di5_items):
            row = tk.Frame(p3_col2, bg=self.COLOR_PANEL)
            row.grid(row=i, column=0, sticky="w")
            led = self.create_led(row, is_on=False, size=13, name=f"DI5_{item}", interactive=False)
            led.pack(side=tk.LEFT, padx=(0, 5))
            tk.Label(row, text=item, bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_label).pack(side=tk.LEFT)

    # ----------------------------------------------------------------------
    # TAB 2: Settings View (Pixel-Perfect 3-Column Alignment & Exact Sizing)
    # ----------------------------------------------------------------------
    def build_settings_view(self):
        self.settings_frame = tk.Frame(self.container, bg=self.COLOR_PANEL)

        # Upper Recessed Panel (3 Buttons: Time Charge, Scope, TDG)
        top_box = tk.Frame(self.settings_frame, bg=self.COLOR_PANEL, bd=2, relief=tk.GROOVE, height=130)
        top_box.pack(fill=tk.X, padx=16, pady=(16, 8))
        top_box.pack_propagate(False)

        top_box.columnconfigure(0, weight=1, uniform="settings_col")
        top_box.columnconfigure(1, weight=1, uniform="settings_col")
        top_box.columnconfigure(2, weight=1, uniform="settings_col")
        top_box.rowconfigure(0, weight=1)

        btn_time = tk.Button(
            top_box, text="Time Charge", bg="#ffffff", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=lambda: self.open_sub_window("Time Charge")
        )
        btn_time.grid(row=0, column=0, padx=25, pady=35, sticky="ew", ipady=6)

        btn_scope = tk.Button(
            top_box, text="Scope", bg="#7fa6ea", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=lambda: self.open_sub_window("Scope")
        )
        btn_scope.grid(row=0, column=1, padx=25, pady=35, sticky="ew", ipady=6)

        btn_tdg = tk.Button(
            top_box, text="TDG", bg="#b462f8", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=lambda: self.open_sub_window("TDG")
        )
        btn_tdg.grid(row=0, column=2, padx=25, pady=35, sticky="ew", ipady=6)

        # Lower Recessed Panel (Calibration & Curve Buttons)
        bottom_box = tk.Frame(self.settings_frame, bg=self.COLOR_PANEL, bd=2, relief=tk.GROOVE)
        bottom_box.pack(fill=tk.BOTH, expand=True, padx=16, pady=(8, 16))

        bottom_box.columnconfigure(0, weight=1, uniform="settings_col")
        bottom_box.columnconfigure(1, weight=1, uniform="settings_col")
        bottom_box.columnconfigure(2, weight=1, uniform="settings_col")

        # Column 1 (Left) - Opens GTU Distance Transducer Calibration & Curve
        btn_cal_gtu = tk.Button(
            bottom_box, text="Dist. Calibration Sphere GTU", bg="#f37b12", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=self.open_gtu_calibration_window
        )
        btn_cal_gtu.grid(row=0, column=0, padx=25, pady=(25, 12), sticky="ew", ipady=6)

        btn_gtu_curve = tk.Button(
            bottom_box, text="GTU Curve", bg="#ffff00", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=lambda: self.open_sub_window("GTU Curve")
        )
        btn_gtu_curve.grid(row=1, column=0, padx=25, pady=12, sticky="ew", ipady=6)

        # Column 2 (Middle) - GTN & IMC Buttons
        btn_gtn_imc = tk.Button(
            bottom_box, text="GTN-IMC Pressure Regulation", bg="#3f8cef", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=lambda: self.open_sub_window("GTN-IMC Pressure Regulation")
        )
        btn_gtn_imc.grid(row=0, column=1, padx=25, pady=(25, 12), sticky="ew", ipady=6)

        btn_gtn_curve = tk.Button(
            bottom_box, text="GTN Curve", bg="#0e53d8", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=lambda: self.open_sub_window("GTN Curve")
        )
        btn_gtn_curve.grid(row=1, column=1, padx=25, pady=12, sticky="ew", ipady=6)

        btn_imc_pos = tk.Button(
            bottom_box, text="IMC Curve - Positive polarity", bg="#9a00d8", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=lambda: self.open_sub_window("IMC Curve - Positive polarity")
        )
        btn_imc_pos.grid(row=2, column=1, padx=25, pady=12, sticky="ew", ipady=6)

        btn_imc_neg = tk.Button(
            bottom_box, text="IMC Curve - Negative polarity", bg="#e60099", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=lambda: self.open_sub_window("IMC Curve - Negative polarity")
        )
        btn_imc_neg.grid(row=3, column=1, padx=25, pady=12, sticky="ew", ipady=6)

        # Column 3 (Right) - MSG Buttons
        btn_cal_msg = tk.Button(
            bottom_box, text="Dist. Calibration Sphere MSG", bg="#00c060", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=lambda: self.open_sub_window("Dist. Calibration Sphere MSG")
        )
        btn_cal_msg.grid(row=0, column=2, padx=25, pady=(25, 12), sticky="ew", ipady=6)

        btn_msg_pos = tk.Button(
            bottom_box, text="MSG Curve - Positive polarity", bg="#5ce020", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=lambda: self.open_sub_window("MSG Curve - Positive polarity")
        )
        btn_msg_pos.grid(row=1, column=2, padx=25, pady=12, sticky="ew", ipady=6)

        btn_msg_neg = tk.Button(
            bottom_box, text="MSG Curve - Negative polarity", bg="#b4e060", fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2",
            command=lambda: self.open_sub_window("MSG Curve - Negative polarity")
        )
        btn_msg_neg.grid(row=2, column=2, padx=25, pady=12, sticky="ew", ipady=6)

    # ----------------------------------------------------------------------
    # Slider Helper (Dynamic Scaling Slider Track)
    # ----------------------------------------------------------------------
    def build_labview_slider(self, parent, label_text, val, min_val, max_val, tick_labels, blue_fill=False, has_spin=False, interactive=True):
        box = tk.Frame(parent, bg=self.COLOR_PANEL)
        box.pack(fill=tk.X, pady=1)

        tk.Label(box, text=label_text, bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(anchor="w")

        sub = tk.Frame(box, bg=self.COLOR_PANEL)
        sub.pack(fill=tk.X)

        c_h = 32
        cursor_type = "sb_h_double_arrow" if interactive else "arrow"
        canvas = tk.Canvas(sub, height=c_h, bg=self.COLOR_PANEL, highlightthickness=0, cursor=cursor_type)
        canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

        current_val = [val]

        val_bg = "#f4f6f8" if interactive else "#e8ebf0"
        val_box = tk.Entry(sub, width=6, font=self.font_val, justify=tk.RIGHT, bg=val_bg, relief=tk.SUNKEN, bd=1)
        val_box.insert(0, f"{val:.3f}")
        if not interactive:
            val_box.config(state="readonly")

        if has_spin:
            spin_btn = tk.Label(sub, text="🎛", bg=self.COLOR_PANEL, font=("Arial", 7), cursor="hand2")
            spin_btn.pack(side=tk.RIGHT, padx=(1, 0))

        val_box.pack(side=tk.RIGHT, padx=(2, 0))

        def get_metrics():
            w = canvas.winfo_width()
            if w < 50:
                w = 165
            x1 = 10
            x2 = max(x1 + 40, w - 10)
            return x1, x2, x2 - x1, 8, 14

        def redraw(event=None):
            canvas.delete("all")
            track_x1, track_x2, track_w, track_y1, track_y2 = get_metrics()

            canvas.create_rectangle(track_x1, track_y1, track_x2, track_y2, fill="#c0c8d0", outline="#505860")

            norm = (current_val[0] - min_val) / (max_val - min_val)
            norm = max(0.0, min(1.0, norm))
            thumb_x = track_x1 + norm * track_w

            if blue_fill:
                zero_norm = (0 - min_val) / (max_val - min_val) if min_val < 0 else 0
                start_x = track_x1 + zero_norm * track_w
                canvas.create_rectangle(start_x, track_y1 + 1, thumb_x, track_y2 - 1, fill="#0055ff", outline="")

            num_ticks = len(tick_labels)
            for i in range(num_ticks):
                tx = track_x1 + (i / (num_ticks - 1)) * track_w
                canvas.create_line(tx, track_y1 - 3, tx, track_y1, fill="#202830")
                canvas.create_line(tx, track_y2, tx, track_y2 + 3, fill="#202830")
                canvas.create_text(tx, track_y2 + 8, text=tick_labels[i], fill="#0a1018", font=("Arial", 7))

            for i in range((num_ticks - 1) * 2):
                tx = track_x1 + (i / ((num_ticks - 1) * 2)) * track_w
                canvas.create_line(tx, track_y2, tx, track_y2 + 2, fill="#505860")

            thumb_color = "#0055ff" if (blue_fill and not has_spin) else "#d46a00"
            canvas.create_rectangle(thumb_x - 3, track_y1 - 3, thumb_x + 3, track_y2 + 3, fill=thumb_color, outline="#101820")

        def update_from_x(x):
            if not interactive:
                return
            track_x1, track_x2, track_w, track_y1, track_y2 = get_metrics()
            norm = (x - track_x1) / track_w
            norm = max(0.0, min(1.0, norm))
            v = min_val + norm * (max_val - min_val)
            current_val[0] = v
            val_box.delete(0, tk.END)
            val_box.insert(0, f"{v:.3f}")
            redraw()

        if interactive:
            canvas.bind("<Button-1>", lambda e: update_from_x(e.x))
            canvas.bind("<B1-Motion>", lambda e: update_from_x(e.x))

            def on_entry_change(event=None):
                try:
                    v = float(val_box.get())
                    v = max(min_val, min(max_val, v))
                    current_val[0] = v
                    redraw()
                except ValueError:
                    pass

            val_box.bind("<Return>", on_entry_change)
            val_box.bind("<FocusOut>", on_entry_change)

        canvas.bind("<Configure>", redraw)
        redraw()


# ==============================================================================
# Application Main Entry Point
# ==============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = LabVIEWUtilityApp(root)
    root.mainloop()