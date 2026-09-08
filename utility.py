import tkinter as tk
from tkinter import ttk
import math
import os
import re
from PIL import Image, ImageTk

# ==============================================================================
# Custom LabVIEW Sunken Dropdown Selector
# ==============================================================================
class LabVIEWDropdown(tk.Frame):
    def __init__(self, parent, values, default=None, width=9, command=None, bg="#949dbd"):
        super().__init__(parent, bg=bg)
        self.values = values
        self.current_val = tk.StringVar(value=default if default else values[0])
        self.command = command

        # Sunken box with authentic LabVIEW silver/blue-grey background
        self.box = tk.Frame(self, bg="#c4cede", bd=2, relief=tk.SUNKEN, cursor="hand2")
        self.box.pack(fill=tk.BOTH, expand=True)

        self.lbl = tk.Label(
            self.box, textvariable=self.current_val, bg="#c4cede", fg="#0a1018",
            font=("Arial", 8, "bold"), width=width, anchor="center"
        )
        self.lbl.pack(side=tk.LEFT, padx=(3, 1), pady=1)

        # White downward triangle arrow
        self.arrow = tk.Label(self.box, text="▼", bg="#c4cede", fg="#ffffff", font=("Arial", 6), cursor="hand2")
        self.arrow.pack(side=tk.RIGHT, padx=(1, 3), pady=1)

        self.menu = tk.Menu(self, tearoff=0, font=("Arial", 8), bg="#dce4f0", fg="black")
        for v in values:
            self.menu.add_command(label=v, command=lambda val=v: self.select(val))

        self.box.bind("<Button-1>", self.show_menu)
        self.lbl.bind("<Button-1>", self.show_menu)
        self.arrow.bind("<Button-1>", self.show_menu)

    def show_menu(self, event=None):
        try:
            x = self.box.winfo_rootx()
            y = self.box.winfo_rooty() + self.box.winfo_height()
            self.menu.tk_popup(x, y)
        finally:
            self.menu.grab_release()

    def select(self, val):
        self.current_val.set(val)
        if self.command:
            self.command(val)


# ==============================================================================
# Tektronix TDS 3032 Oscilloscope Window (Pixel-Perfect LabVIEW VI)
# ==============================================================================
class TektronixScopeWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Tektronix TDS 3032")
        self.geometry("860x760")
        self.resizable(True, True)
        self.minsize(860, 760)

        self.COLOR_BG = "#a7b1d7"
        self.COLOR_PANEL = "#949dbd"
        self.COLOR_BORDER = "#697391"
        self.configure(bg=self.COLOR_BG)

        self.font_title = ("Arial", 11, "bold")
        self.font_header = ("Arial", 8, "bold")
        self.font_btn = ("Arial", 8, "bold")
        self.font_label = ("Arial", 8)

        self.knob_angles = {}
        self.loaded_images = []

        self.setup_ui()

    def draw_dome_knob(self, canvas, cx, cy, radius, angle_deg, tag="knob"):
        canvas.delete(tag)
        canvas.create_oval(cx - radius - 1, cy - radius - 1, cx + radius + 1, cy + radius + 1, fill="#505a75", outline="#303848", tags=tag)
        
        for i in range(int(radius), 0, -1):
            factor = (radius - i) / radius
            hx = cx - factor * (radius * 0.35)
            hy = cy - factor * (radius * 0.35)
            r = int(109 + (192 - 109) * factor)
            g = int(118 + (201 - 118) * factor)
            b = int(143 + (231 - 143) * factor)
            hex_col = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_oval(hx - i, hy - i, hx + i, hy + i, fill=hex_col, outline="", tags=tag)

        c_rad = radius * 0.22
        canvas.create_oval(cx - radius*0.3 - c_rad, cy - radius*0.3 - c_rad, cx - radius*0.3 + c_rad, cy - radius*0.3 + c_rad, fill="#e2ebf8", outline="", tags=tag)

        rad = math.radians(angle_deg)
        x1 = cx + (radius * 0.30) * math.cos(rad)
        y1 = cy + (radius * 0.30) * math.sin(rad)
        x2 = cx + (radius * 0.88) * math.cos(rad)
        y2 = cy + (radius * 0.88) * math.sin(rad)
        canvas.create_line(x1, y1, x2, y2, fill="#ffffff", width=2.5, capstyle=tk.ROUND, tags=tag)

    def create_interactive_knob(self, parent, title, labels_angles, default_angle, width=130, height=135):
        box = tk.Frame(parent, bg=self.COLOR_PANEL)
        tk.Label(box, text=title, bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack()

        canvas = tk.Canvas(box, width=width, height=height, bg=self.COLOR_PANEL, highlightthickness=0, cursor="hand2")
        canvas.pack()

        cx, cy, radius = width // 2, height // 2 + 5, 23
        current_angle = [default_angle]

        for lbl, ang in labels_angles:
            ar = math.radians(ang)
            tx = cx + 42 * math.cos(ar)
            ty = cy + 42 * math.sin(ar)
            canvas.create_text(tx, ty, text=lbl, font=("Arial", 7, "bold"), fill="#0a1018")
            lx1 = cx + 27 * math.cos(ar)
            ly1 = cy + 27 * math.sin(ar)
            lx2 = cx + 33 * math.cos(ar)
            ly2 = cy + 33 * math.sin(ar)
            canvas.create_line(lx1, ly1, lx2, ly2, fill="#1c2438", width=1.5)

        self.draw_dome_knob(canvas, cx, cy, radius, current_angle[0], tag="knob_body")

        def on_click_drag(event):
            dx = event.x - cx
            dy = event.y - cy
            deg = math.degrees(math.atan2(dy, dx))
            deg = (deg + 360) % 360
            current_angle[0] = deg
            self.draw_dome_knob(canvas, cx, cy, radius, deg, tag="knob_body")

        canvas.bind("<Button-1>", on_click_drag)
        canvas.bind("<B1-Motion>", on_click_drag)

        return box

    def setup_ui(self):
        main_container = tk.Frame(self, bg=self.COLOR_BORDER, bd=2, relief=tk.SUNKEN)
        main_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Top Panel
        top_panel = tk.Frame(main_container, bg=self.COLOR_PANEL, bd=1, relief=tk.SOLID, height=210)
        top_panel.pack(fill=tk.X, padx=6, pady=6)
        top_panel.pack_propagate(False)

        scope_path = os.path.join(os.path.dirname(__file__), "assets", "tek_scope.png")
        if os.path.exists(scope_path):
            img_scope = Image.open(scope_path).resize((220, 165), Image.Resampling.LANCZOS)
            photo_scope = ImageTk.PhotoImage(img_scope)
            self.loaded_images.append(photo_scope)
            lbl_scope = tk.Label(top_panel, image=photo_scope, bg=self.COLOR_PANEL, bd=0)
            lbl_scope.place(x=15, y=5)

        logo_path = os.path.join(os.path.dirname(__file__), "assets", "wsts_logo.png")
        if os.path.exists(logo_path):
            img_logo = Image.open(logo_path).resize((130, 70), Image.Resampling.LANCZOS)
            photo_logo = ImageTk.PhotoImage(img_logo)
            self.loaded_images.append(photo_logo)
            lbl_logo = tk.Label(top_panel, image=photo_logo, bg=self.COLOR_PANEL, bd=0)
            lbl_logo.place(relx=1.0, x=-150, y=18)

        btn_ch1 = tk.Button(top_panel, text="CH1", bg="#ffff00", fg="black", font=self.font_btn, relief=tk.RAISED, bd=2, padx=14, pady=2, cursor="hand2")
        btn_ch1.place(x=290, y=170)

        btn_ch2 = tk.Button(top_panel, text="CH2", bg="#8cb3f2", fg="black", font=self.font_btn, relief=tk.RAISED, bd=2, padx=14, pady=2, cursor="hand2")
        btn_ch2.place(x=370, y=170)

        btn_auto = tk.Button(top_panel, text="Auto", bg="#00cc00", fg="black", font=self.font_btn, relief=tk.RAISED, bd=2, padx=14, pady=2, cursor="hand2")
        btn_auto.place(x=480, y=170)

        bar_path = os.path.join(os.path.dirname(__file__), "assets", "status_bar.png")
        if os.path.exists(bar_path):
            img_bar = Image.open(bar_path).resize((160, 26), Image.Resampling.LANCZOS)
            photo_bar = ImageTk.PhotoImage(img_bar)
            self.loaded_images.append(photo_bar)
            lbl_bar = tk.Label(top_panel, image=photo_bar, bg=self.COLOR_PANEL, bd=0)
            lbl_bar.place(relx=1.0, x=-180, y=172)

        # Middle Section
        mid_section = tk.Frame(main_container, bg=self.COLOR_BORDER)
        mid_section.pack(fill=tk.X, padx=6, pady=(0, 6))

        # Panel 1: Channel
        p_channel = tk.Frame(mid_section, bg=self.COLOR_PANEL, bd=1, relief=tk.SOLID, width=470, height=290)
        p_channel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        p_channel.pack_propagate(False)

        c_title = tk.Canvas(p_channel, height=24, bg=self.COLOR_PANEL, highlightthickness=0)
        c_title.pack(fill=tk.X, pady=(2, 0))
        c_title.create_text(236, 13, text="Channel", fill="#1c2438", font=self.font_title)
        c_title.create_text(235, 12, text="Channel", fill="#ff0000", font=self.font_title)

        knobs_frame = tk.Frame(p_channel, bg=self.COLOR_PANEL)
        knobs_frame.pack(fill=tk.X, padx=4)

        volt_labels = [("10m", 205), ("100m", 270), ("1", 335), ("10", 50), ("1m", 130)]
        k_volt = self.create_interactive_knob(knobs_frame, "Volt/Div", volt_labels, default_angle=270, width=135, height=135)
        k_volt.pack(side=tk.LEFT, expand=True)

        pos_labels = [
            ("-5", 125), ("-4", 155), ("-3", 185), ("-2", 215), ("-1", 245),
            ("0", 270), ("1", 295), ("2", 325), ("3", 355), ("4", 25), ("5", 55)
        ]
        k_pos = self.create_interactive_knob(knobs_frame, "Position [Div]", pos_labels, default_angle=270, width=135, height=135)
        k_pos.pack(side=tk.LEFT, expand=True)

        off_labels = [
            ("-0.8", 155), ("-0.6", 185), ("-0.4", 215), ("-0.2", 245),
            ("0.0", 270), ("0.2", 295), ("0.4", 325), ("0.6", 355), ("0.8", 25)
        ]
        k_off = self.create_interactive_knob(knobs_frame, "Offset [Volt]", off_labels, default_angle=270, width=135, height=135)
        k_off.pack(side=tk.LEFT, expand=True)

        ctrl_row = tk.Frame(p_channel, bg=self.COLOR_PANEL)
        ctrl_row.pack(fill=tk.X, pady=(6, 4))

        f_bw = tk.Frame(ctrl_row, bg=self.COLOR_PANEL)
        f_bw.pack(side=tk.LEFT, expand=True)
        tk.Label(f_bw, text="Bandwith Limit", bg=self.COLOR_PANEL, fg="#0a1018", font=("Arial", 8, "bold")).pack()
        LabVIEWDropdown(f_bw, ["Full", "20 MHz", "150 MHz"], default="Full", width=8).pack()

        f_off = tk.Frame(ctrl_row, bg=self.COLOR_PANEL)
        f_off.pack(side=tk.LEFT, expand=True)
        tk.Button(f_off, text="OFF", bg="#ffffff", fg="black", font=self.font_btn, relief=tk.RAISED, bd=2, width=6, cursor="hand2").pack(pady=(12, 0))

        f_cpl = tk.Frame(ctrl_row, bg=self.COLOR_PANEL)
        f_cpl.pack(side=tk.LEFT, expand=True)
        tk.Label(f_cpl, text="Coupling", bg=self.COLOR_PANEL, fg="#0a1018", font=("Arial", 8, "bold")).pack()
        LabVIEWDropdown(f_cpl, ["AC", "DC", "GND"], default="AC", width=8).pack()

        # Panel 2: Time
        p_time = tk.Frame(mid_section, bg=self.COLOR_PANEL, bd=1, relief=tk.SOLID, width=175, height=290)
        p_time.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        p_time.pack_propagate(False)

        t_title = tk.Canvas(p_time, height=24, bg=self.COLOR_PANEL, highlightthickness=0)
        t_title.pack(fill=tk.X, pady=(2, 0))
        t_title.create_text(88, 13, text="Time", fill="#1c2438", font=self.font_title)
        t_title.create_text(87, 12, text="Time", fill="#ff0000", font=self.font_title)

        tk.Label(p_time, text="Time/Div", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(pady=(2, 1))
        LabVIEWDropdown(p_time, ["1 ns", "2 ns", "5 ns", "10 ns", "20 ns", "50 ns", "100 ns"], default="2 ns", width=8).pack()

        delay_labels = [
            ("0", 125), ("10", 155), ("20", 185), ("30", 215), ("40", 245),
            ("50", 270), ("60", 295), ("70", 325), ("80", 355), ("90", 25), ("100", 55)
        ]
        k_delay = self.create_interactive_knob(p_time, "Delay [%]", delay_labels, default_angle=125, width=145, height=135)
        k_delay.pack(pady=(6, 0))

        # Panel 3: Trigger
        p_trig = tk.Frame(mid_section, bg=self.COLOR_PANEL, bd=1, relief=tk.SOLID, width=175, height=290)
        p_trig.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        p_trig.pack_propagate(False)

        tr_title = tk.Canvas(p_trig, height=24, bg=self.COLOR_PANEL, highlightthickness=0)
        tr_title.pack(fill=tk.X, pady=(2, 0))
        tr_title.create_text(88, 13, text="Trigger", fill="#1c2438", font=self.font_title)
        tr_title.create_text(87, 12, text="Trigger", fill="#ff0000", font=self.font_title)

        f_slope = tk.Frame(p_trig, bg=self.COLOR_PANEL)
        f_slope.pack(fill=tk.X, padx=10, pady=1)
        tk.Label(f_slope, text="Slope", bg=self.COLOR_PANEL, fg="#0a1018", font=("Arial", 7, "bold")).pack()
        LabVIEWDropdown(f_slope, ["Rise", "Fall"], default="Rise", width=8).pack()

        f_tcpl = tk.Frame(p_trig, bg=self.COLOR_PANEL)
        f_tcpl.pack(fill=tk.X, padx=10, pady=1)
        tk.Label(f_tcpl, text="Coupling", bg=self.COLOR_PANEL, fg="#0a1018", font=("Arial", 7, "bold")).pack()
        LabVIEWDropdown(f_tcpl, ["DC", "AC", "HF Rej", "LF Rej", "Noise Rej"], default="DC", width=8).pack()

        k_level = self.create_interactive_knob(p_trig, "Level [V]", off_labels, default_angle=270, width=145, height=115)
        k_level.pack(pady=(1, 0))

        f_src = tk.Frame(p_trig, bg=self.COLOR_PANEL)
        f_src.pack(fill=tk.X, padx=10, pady=(0, 2))
        tk.Label(f_src, text="Source", bg=self.COLOR_PANEL, fg="#0a1018", font=("Arial", 7, "bold")).pack()
        LabVIEWDropdown(f_src, ["CH1", "CH2", "Ext", "Line"], default="CH1", width=8).pack()

        # Bottom Section
        bot_frame = tk.Frame(main_container, bg=self.COLOR_BORDER)
        bot_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        white_box = tk.Canvas(bot_frame, bg="#ffffff", bd=2, relief=tk.SUNKEN, highlightthickness=0)
        white_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        exit_btn = tk.Button(
            bot_frame, text="Exit", bg="#ffff00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=16, pady=4,
            cursor="hand2", command=self.destroy
        )
        exit_btn.pack(side=tk.RIGHT, anchor="se", pady=6)


# ==============================================================================
# GTU - Distance Transducer Calibration Window (Pixel-Perfect LabVIEW VI)
# ==============================================================================
class GTUDistanceCalibrationWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Distance Trasducer Calibration")
        self.resizable(True, True)
        self.minsize(700, 520)

        # Uniform steel-slate theme palette from target screenshot
        self.COLOR_BG = "#8c97a8"        # Outer steel-slate
        self.COLOR_PANEL = "#8c97a8"     # Inner panel background
        self.COLOR_BORDER = "#5c6877"    # Bevel groove border
        self.COLOR_GRAPH = "#778394"     # Graph background
        self.configure(bg=self.COLOR_BG)

        self.font_title = ("Arial", 13, "bold")
        self.font_section = ("Arial", 10, "bold")
        self.font_header = ("Arial", 8, "bold")
        self.font_digital = ("Arial", 11, "bold")

        # Calibration state variables
        self.dist_val = 7.41
        self.volt_read = 1.121
        self.min_dist = 0.0
        self.max_dist = 0.0
        self.coeff_a = 7.74
        self.coeff_b = -1.26
        self.is_calculated = False

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

    def make_digital_readout(self, parent, text, width=7):
        """Creates authentic LabVIEW black sunken digital readout box."""
        frame = tk.Frame(parent, bg="#000000", bd=2, relief=tk.SUNKEN)
        lbl = tk.Label(frame, text=text, bg="#000000", fg="#ffffff", font=self.font_digital, width=width, anchor="center")
        lbl.pack(padx=2, pady=1)
        return frame, lbl

    def make_spin_input(self, parent, initial_val="0.0"):
        """Creates LabVIEW-style numeric box with spin buttons on left."""
        box = tk.Frame(parent, bg=self.COLOR_PANEL)
        
        # Spin arrows widget on left
        spin_f = tk.Frame(box, bg="#d0d8e8", bd=1, relief=tk.RAISED, cursor="hand2")
        spin_f.pack(side=tk.LEFT, padx=(0, 2))
        tk.Label(spin_f, text="▲\n▼", bg="#d0d8e8", fg="#1a2030", font=("Arial", 6, "bold")).pack(padx=2, pady=1)

        # White sunken entry box
        entry = tk.Entry(box, bg="#ffffff", fg="#000000", font=self.font_digital, width=6, justify="center", bd=2, relief=tk.SUNKEN)
        entry.insert(0, initial_val)
        entry.pack(side=tk.LEFT)

        return box, entry

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
            header_frame, text="Exit", bg="#ffff00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=14, pady=1,
            cursor="hand2", command=self.destroy
        )
        exit_btn.pack(side=tk.RIGHT, padx=6, pady=6)

        # Centered Yellow Title with dark drop shadow (dynamically centered on resize/maximize)
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
            self.title_canvas.create_text(cx + 1, cy + 1, text="GTU - Distance Trasducer Calibration", fill="#1a2030", font=self.font_title)
            self.title_canvas.create_text(cx, cy, text="GTU - Distance Trasducer Calibration", fill="#ffff00", font=self.font_title)

        self.title_canvas.bind("<Configure>", update_title)

        # Content Container (Panel Color)
        body = tk.Frame(main_container, bg=self.COLOR_PANEL)
        body.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # ----------------------------------------------------------------------
        # UPPER SECTION: Step #1, Step #2 and Actuation Controls
        # ----------------------------------------------------------------------
        upper_frame = tk.Frame(body, bg=self.COLOR_PANEL, height=210)
        upper_frame.pack(fill=tk.X, pady=(0, 2))
        upper_frame.pack_propagate(False)

        # Upper Left: Steps #1 and #2
        steps_left = tk.Frame(upper_frame, bg=self.COLOR_PANEL)
        steps_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 4), pady=4)

        # --- Step #1 ---
        lbl_s1 = tk.Canvas(steps_left, height=18, bg=self.COLOR_PANEL, highlightthickness=0)
        lbl_s1.pack(anchor="w")
        lbl_s1.create_text(36, 10, text="Step #1", fill="#1a2030", font=self.font_section)
        lbl_s1.create_text(35, 9, text="Step #1", fill="#ffffff", font=self.font_section)

        row_s1 = tk.Frame(steps_left, bg=self.COLOR_PANEL)
        row_s1.pack(fill=tk.X, pady=(2, 8))

        # Set Dist. Min [mm]
        f_min = tk.Frame(row_s1, bg=self.COLOR_PANEL)
        f_min.pack(side=tk.LEFT, padx=(0, 14))
        tk.Label(f_min, text="Set Dist. Min [mm]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(anchor="w")
        self.spin_min, self.entry_min = self.make_spin_input(f_min, "0.0")
        self.spin_min.pack(anchor="w")

        # Voltage Read
        f_v1 = tk.Frame(row_s1, bg=self.COLOR_PANEL)
        f_v1.pack(side=tk.LEFT, padx=(0, 14))
        tk.Label(f_v1, text="Voltage Read", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(anchor="w")
        self.box_v1, self.lbl_v1 = self.make_digital_readout(f_v1, f"{self.volt_read:.3f}", width=7)
        self.box_v1.pack(anchor="w")

        # Enter Button
        btn_enter1 = tk.Button(
            row_s1, text="Enter", bg="#00cc00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=16, pady=2,
            cursor="hand2", command=self.on_enter_step1
        )
        btn_enter1.pack(side=tk.LEFT, pady=(12, 0))

        # --- Step #2 ---
        lbl_s2 = tk.Canvas(steps_left, height=18, bg=self.COLOR_PANEL, highlightthickness=0)
        lbl_s2.pack(anchor="w")
        lbl_s2.create_text(36, 10, text="Step #2", fill="#1a2030", font=self.font_section)
        lbl_s2.create_text(35, 9, text="Step #2", fill="#ffffff", font=self.font_section)

        row_s2 = tk.Frame(steps_left, bg=self.COLOR_PANEL)
        row_s2.pack(fill=tk.X, pady=(2, 4))

        # Set Dist. Max [mm]
        f_max = tk.Frame(row_s2, bg=self.COLOR_PANEL)
        f_max.pack(side=tk.LEFT, padx=(0, 14))
        tk.Label(f_max, text="Set Dist. Max [mm]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(anchor="w")
        self.spin_max, self.entry_max = self.make_spin_input(f_max, "0.0")
        self.spin_max.pack(anchor="w")

        # Voltage Read
        f_v2 = tk.Frame(row_s2, bg=self.COLOR_PANEL)
        f_v2.pack(side=tk.LEFT, padx=(0, 14))
        tk.Label(f_v2, text="Voltage Read", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).pack(anchor="w")
        self.box_v2, self.lbl_v2 = self.make_digital_readout(f_v2, f"{self.volt_read:.3f}", width=7)
        self.box_v2.pack(anchor="w")

        # Enter Button
        btn_enter2 = tk.Button(
            row_s2, text="Enter", bg="#00cc00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=16, pady=2,
            cursor="hand2", command=self.on_enter_step2
        )
        btn_enter2.pack(side=tk.LEFT, pady=(12, 0))

        # Vertical Beveled Divider Line
        sep_v = tk.Frame(upper_frame, bg="#ffffff", bd=1, relief=tk.SUNKEN, width=2)
        sep_v.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=8)

        # Upper Right: Increase, Distance [mm], Decrease (anchored cleanly on right)
        act_right = tk.Frame(upper_frame, bg=self.COLOR_PANEL, width=270)
        act_right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 20), pady=10)
        act_right.pack_propagate(False)

        # Row: Increase
        r_inc = tk.Frame(act_right, bg=self.COLOR_PANEL)
        r_inc.pack(fill=tk.X, pady=4)
        tk.Label(r_inc, text="Increase", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header, width=12, anchor="w").pack(side=tk.LEFT)
        btn_inc = tk.Button(
            r_inc, text="<-  ->", bg="#ff9933", fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, padx=16, pady=2,
            cursor="hand2", command=self.on_increase
        )
        btn_inc.pack(side=tk.LEFT)

        # Row: Distance [mm]
        r_dist = tk.Frame(act_right, bg=self.COLOR_PANEL)
        r_dist.pack(fill=tk.X, pady=6)
        tk.Label(r_dist, text="Distance [mm]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header, width=12, anchor="w").pack(side=tk.LEFT)
        self.box_dist, self.lbl_dist = self.make_digital_readout(r_dist, f"{self.dist_val:.2f}", width=7)
        self.box_dist.pack(side=tk.LEFT)

        # Row: Decrease
        r_dec = tk.Frame(act_right, bg=self.COLOR_PANEL)
        r_dec.pack(fill=tk.X, pady=4)
        tk.Label(r_dec, text="Decrease", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header, width=12, anchor="w").pack(side=tk.LEFT)
        btn_dec = tk.Button(
            r_dec, text="->  <-", bg="#ff9933", fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, padx=16, pady=2,
            cursor="hand2", command=self.on_decrease
        )
        btn_dec.pack(side=tk.LEFT)

        # Horizontal Divider Line separating Upper from Lower
        sep_h = tk.Frame(body, bg="#ffffff", bd=1, relief=tk.SUNKEN, height=2)
        sep_h.pack(fill=tk.X, padx=2, pady=(2, 6))

        # ----------------------------------------------------------------------
        # LOWER SECTION: Calibration Graph & Step #3 Calculation
        # ----------------------------------------------------------------------
        lower_frame = tk.Frame(body, bg=self.COLOR_PANEL)
        lower_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        # Right: Step #3 Calculation Container
        calc_box = tk.Frame(lower_frame, bg=self.COLOR_PANEL, width=270)
        calc_box.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 20), pady=8)
        calc_box.pack_propagate(False)

        # Left: Graph Container (fills all available space dynamically)
        graph_box = tk.Frame(lower_frame, bg=self.COLOR_PANEL)
        graph_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.graph_canvas = tk.Canvas(graph_box, bg=self.COLOR_PANEL, highlightthickness=0)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        self.graph_canvas.bind("<Configure>", lambda e: self.draw_graph())

        # Step #3 & Calculation button row
        r_s3 = tk.Frame(calc_box, bg=self.COLOR_PANEL)
        r_s3.pack(fill=tk.X, pady=(6, 20))

        lbl_s3 = tk.Canvas(r_s3, width=70, height=24, bg=self.COLOR_PANEL, highlightthickness=0)
        lbl_s3.pack(side=tk.LEFT)
        lbl_s3.create_text(36, 13, text="Step #3", fill="#1a2030", font=self.font_section)
        lbl_s3.create_text(35, 12, text="Step #3", fill="#ffffff", font=self.font_section)

        btn_calc = tk.Button(
            r_s3, text="Calculation", bg="#ffff00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=14, pady=2,
            cursor="hand2", command=self.on_calculate
        )
        btn_calc.pack(side=tk.LEFT, padx=(10, 0))

        # A [mm/V] Readout Row
        r_a = tk.Frame(calc_box, bg=self.COLOR_PANEL)
        r_a.pack(fill=tk.X, pady=10)
        tk.Label(r_a, text="A [mm/V]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header, width=10, anchor="w").pack(side=tk.LEFT)
        self.box_a, self.lbl_a = self.make_digital_readout(r_a, f"{self.coeff_a:.2f}", width=8)
        self.box_a.pack(side=tk.LEFT)

        # B [mm] Readout Row
        r_b = tk.Frame(calc_box, bg=self.COLOR_PANEL)
        r_b.pack(fill=tk.X, pady=10)
        tk.Label(r_b, text="B [mm]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header, width=10, anchor="w").pack(side=tk.LEFT)
        self.box_b, self.lbl_b = self.make_digital_readout(r_b, f"{self.coeff_b:.2f}", width=8)
        self.box_b.pack(side=tk.LEFT)

    # ----------------------------------------------------------------------
    # Interactive Calibration Graph Rendering (Responsive)
    # ----------------------------------------------------------------------
    def draw_graph(self):
        c = self.graph_canvas
        c.delete("all")

        cw = c.winfo_width()
        ch = c.winfo_height()
        if cw < 50 or ch < 50:
            cw, ch = 430, 290

        # Layout metrics (dynamically adapting to canvas size)
        gx1 = 45
        gy1 = 15
        gx2 = max(gx1 + 100, cw - 20)
        gy2 = max(gy1 + 100, ch - 35)
        gw = gx2 - gx1
        gh = gy2 - gy1

        # Sunken Graph Background Area
        c.create_rectangle(gx1, gy1, gx2, gy2, fill=self.COLOR_GRAPH, outline="#5a6478", width=1.5)
        # Inner bevel shadow
        c.create_line(gx1, gy1, gx2, gy1, fill="#404a58")
        c.create_line(gx1, gy1, gx1, gy2, fill="#404a58")
        c.create_line(gx2, gy1, gx2, gy2, fill="#d0d8e8")
        c.create_line(gx1, gy2, gx2, gy2, fill="#d0d8e8")

        # Solid Cartesian Grid matching authentic LabVIEW screenshot
        for i in range(11):
            y_val = i
            py = gy2 - (y_val / 10.0) * gh
            c.create_line(gx1, py, gx2, py, fill="#8892a4")
            # Y Ticks & Labels
            c.create_line(gx1 - 3, py, gx1, py, fill="#0a1018")
            c.create_text(gx1 - 8, py, text=str(y_val), font=("Arial", 7, "bold"), fill="#0a1018", anchor="e")

        for i in range(11):
            x_val = i * 5
            px = gx1 + (x_val / 50.0) * gw
            c.create_line(px, gy1, px, gy2, fill="#8892a4")
            # X Ticks & Labels
            c.create_line(px, gy2, px, gy2 + 3, fill="#0a1018")
            c.create_text(px, gy2 + 10, text=str(x_val), font=("Arial", 7, "bold"), fill="#0a1018", anchor="n")

        # Vertical Y-Axis Label: "Pot Voltage [Volt]"
        c.create_text(14, gy1 + gh // 2, text="Pot Voltage [Volt]", font=("Arial", 8, "bold"), fill="#0a1018", angle=90)

        # Horizontal X-Axis Label: "Distance [mm]"
        c.create_text(gx1 + gw // 2, gy2 + 22, text="Distance [mm]", font=("Arial", 8, "bold"), fill="#0a1018")

        # Plotted Red Calibration Dot matching Image 2 at (x=0, y=3)
        dot_x = gx1 + (0 / 50.0) * gw
        dot_y = gy2 - (3.0 / 10.0) * gh
        c.create_oval(dot_x - 3.5, dot_y - 3.5, dot_x + 3.5, dot_y + 3.5, fill="#ff0000", outline="#990000")

        # If regression calculated, draw line
        if getattr(self, "is_calculated", False):
            v0 = (0.0 - self.coeff_b) / self.coeff_a
            v40 = (40.0 - self.coeff_b) / self.coeff_a
            p1 = (gx1, gy2 - (v0 / 10.0) * gh)
            p2 = (gx1 + (40.0 / 50.0) * gw, gy2 - (v40 / 10.0) * gh)
            c.create_line(p1, p2, fill="#ff0000", width=2)

    # ----------------------------------------------------------------------
    # Event Handlers
    # ----------------------------------------------------------------------
    def on_increase(self):
        self.dist_val = min(50.0, self.dist_val + 0.5)
        self.volt_read = (self.dist_val - self.coeff_b) / self.coeff_a
        self.lbl_dist.config(text=f"{self.dist_val:.2f}")
        self.lbl_v1.config(text=f"{self.volt_read:.3f}")
        self.lbl_v2.config(text=f"{self.volt_read:.3f}")

    def on_decrease(self):
        self.dist_val = max(0.0, self.dist_val - 0.5)
        self.volt_read = (self.dist_val - self.coeff_b) / self.coeff_a
        self.lbl_dist.config(text=f"{self.dist_val:.2f}")
        self.lbl_v1.config(text=f"{self.volt_read:.3f}")
        self.lbl_v2.config(text=f"{self.volt_read:.3f}")

    def on_enter_step1(self):
        try:
            self.min_dist = float(self.entry_min.get())
        except ValueError:
            pass

    def on_enter_step2(self):
        try:
            self.max_dist = float(self.entry_max.get())
        except ValueError:
            pass

    def on_calculate(self):
        self.is_calculated = True
        self.lbl_a.config(text=f"{self.coeff_a:.2f}")
        self.lbl_b.config(text=f"{self.coeff_b:.2f}")
        self.draw_graph()


# ==============================================================================
# Standard LabVIEW Sub-Window for Settings Buttons (Same Size & Placement)
# ==============================================================================
class LabVIEWSubWindow(tk.Toplevel):
    def __init__(self, parent, title_text, window_title=None, width=740, height=580):
        super().__init__(parent)
        self.parent = parent
        self.title(window_title or title_text)
        self.resizable(True, True)
        self.minsize(680, 500)

        # Exact sampled uniform color theme from target screenshot
        self.COLOR_BG = "#8c97a8"
        self.COLOR_PANEL = "#8c97a8"
        self.COLOR_BORDER = "#5c6877"
        self.COLOR_TOPBAR = "#333333"
        self.COLOR_EXIT = "#facc15"
        self.COLOR_GREEN = "#31c32f"
        self.configure(bg=self.COLOR_BG)

        self.font_title = ("Arial", 13, "bold")
        self.font_header = ("Arial", 9, "bold")

        # Position in exact same place (centered over parent) with same size (740x580)
        self.setup_ui(title_text)
        self.center_on_parent(width, height)

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

    def setup_ui(self, title_text):
        main_container = tk.Frame(self, bg=self.COLOR_BORDER, bd=2, relief=tk.SUNKEN)
        main_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Top Header Bar: Dark Charcoal #333333 Bar with Title & Exit Button
        header_frame = tk.Frame(main_container, bg=self.COLOR_TOPBAR, height=36)
        header_frame.pack(fill=tk.X, padx=2, pady=(2, 0))
        header_frame.pack_propagate(False)

        exit_btn = tk.Button(
            header_frame, text="EXIT", bg=self.COLOR_EXIT, fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, padx=14,
            cursor="hand2", command=self.destroy
        )
        exit_btn.pack(side=tk.RIGHT, fill=tk.Y, pady=2, padx=(10, 4))

        # Status: Green dot + Scope Connected
        status_f = tk.Frame(header_frame, bg=self.COLOR_TOPBAR)
        status_f.pack(side=tk.RIGHT, padx=10)
        c_led = tk.Canvas(status_f, width=10, height=10, bg=self.COLOR_TOPBAR, highlightthickness=0)
        c_led.pack(side=tk.LEFT, padx=(0, 4))
        c_led.create_oval(1, 1, 9, 9, fill=self.COLOR_GREEN, outline="#1a8018")
        tk.Label(status_f, text="Scope Connected", bg=self.COLOR_TOPBAR, fg=self.COLOR_GREEN, font=("Arial", 8, "bold")).pack(side=tk.LEFT)

        title_canvas = tk.Canvas(header_frame, bg=self.COLOR_TOPBAR, highlightthickness=0)
        title_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def update_title(event=None):
            title_canvas.delete("all")
            w = title_canvas.winfo_width()
            h = title_canvas.winfo_height()
            if w < 10:
                w = 400
            cx = w // 2
            cy = h // 2 if h > 10 else 18
            title_canvas.create_text(cx + 1, cy + 1, text=title_text, fill="#1a2030", font=self.font_title)
            title_canvas.create_text(cx, cy, text=title_text, fill="#ffff00", font=self.font_title)

        title_canvas.bind("<Configure>", update_title)

        # Body Container
        self.body = tk.Frame(main_container, bg=self.COLOR_PANEL)
        self.body.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Inner recessed frame ready for controls
        inner_box = tk.Frame(self.body, bg=self.COLOR_PANEL, bd=1, relief=tk.GROOVE)
        inner_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        msg_frame = tk.Frame(inner_box, bg=self.COLOR_PANEL)
        msg_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            msg_frame, text=f"LabVIEW Panel: {title_text}",
            bg=self.COLOR_PANEL, fg="#1a2030", font=("Arial", 12, "bold")
        ).pack(pady=(0, 6))

        tk.Label(
            msg_frame, text="Uniform theme active (#8c97a8) - Ready for development",
            bg=self.COLOR_PANEL, fg="#f0f4f8", font=("Arial", 9)
        ).pack()


# ==============================================================================
# IAAS - Carona Power Impulse Acquisition & Analysis Setup Window
# ==============================================================================
class IAASSetupWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("IAAS - Setup")
        self.resizable(True, True)
        self.minsize(740, 560)

        # Exact sampled uniform color theme from target screenshot
        self.COLOR_BG = "#8c97a8"          # Steel-slate workspace background
        self.COLOR_TOPBAR = "#333333"      # Charcoal top navigation bar
        self.COLOR_TAB_ACTIVE = "#eb5444"  # Active red tab (Setup)
        self.COLOR_TAB_INACTIVE = "#4d4d4d"# Inactive dark gray tab
        self.COLOR_BORDER = "#5c6877"      # Recessed panel/groove border
        self.COLOR_EXIT = "#facc15"        # Yellow EXIT button
        self.COLOR_GREEN = "#31c32f"       # Active / ENTER green button
        self.COLOR_DARK_BTN = "#333333"    # Inactive dark button
        self.COLOR_TEXT_LIGHT = "#ffffff"  # Crisp white label text

        self.configure(bg=self.COLOR_BG)

        self.font_tab = ("Arial", 9, "bold")
        self.font_header = ("Arial", 9, "bold")
        self.font_label = ("Arial", 9)
        self.font_btn = ("Arial", 9, "bold")

        # State
        self.ch1_active = True
        self.ch2_active = False

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
        # 1. Top Charcoal Navigation Bar
        top_bar = tk.Frame(self, bg=self.COLOR_TOPBAR, height=32)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)

        # Tabs on Left
        tabs_f = tk.Frame(top_bar, bg=self.COLOR_TOPBAR)
        tabs_f.pack(side=tk.LEFT, fill=tk.Y)

        btn_setup = tk.Label(tabs_f, text="Setup", bg=self.COLOR_TAB_ACTIVE, fg="white", font=self.font_tab, padx=16, cursor="hand2")
        btn_setup.pack(side=tk.LEFT, fill=tk.Y)

        for tab_name in ["View", "Review", "Analysis"]:
            btn = tk.Label(tabs_f, text=tab_name, bg=self.COLOR_TAB_INACTIVE, fg="white", font=self.font_tab, padx=12, bd=1, relief=tk.RAISED, cursor="hand2")
            btn.pack(side=tk.LEFT, fill=tk.Y, padx=(1, 0))

        # Far Right: EXIT button
        exit_btn = tk.Button(
            top_bar, text="EXIT", bg=self.COLOR_EXIT, fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, padx=14,
            cursor="hand2", command=self.destroy
        )
        exit_btn.pack(side=tk.RIGHT, fill=tk.Y, pady=2, padx=(10, 2))

        # Status: Green dot + "Scope Connected"
        status_f = tk.Frame(top_bar, bg=self.COLOR_TOPBAR)
        status_f.pack(side=tk.RIGHT, padx=15)

        led_canvas = tk.Canvas(status_f, width=12, height=12, bg=self.COLOR_TOPBAR, highlightthickness=0)
        led_canvas.pack(side=tk.LEFT, padx=(0, 4))
        led_canvas.create_oval(2, 2, 10, 10, fill=self.COLOR_GREEN, outline="#1a8018")

        tk.Label(status_f, text="Scope Connected", bg=self.COLOR_TOPBAR, fg=self.COLOR_GREEN, font=("Arial", 9, "bold")).pack(side=tk.LEFT)

        # 2. Main Content Body
        body = tk.Frame(self, bg=self.COLOR_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Header: Carona Power Logo (Left) & IAAS (Center)
        brand_bar = tk.Frame(body, bg=self.COLOR_BG, height=60)
        brand_bar.pack(fill=tk.X, pady=(4, 15))

        # Carona Power Logo
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carona_logo_ui.png")
        self.carona_logo = None
        loaded_iaas_logo = False
        if os.path.exists(logo_path):
            try:
                raw_img = Image.open(logo_path)
                scale_img = raw_img.resize((120, 50), Image.Resampling.LANCZOS)
                self.carona_logo = ImageTk.PhotoImage(scale_img)
                lbl_logo = tk.Label(brand_bar, image=self.carona_logo, bg=self.COLOR_BG)
                lbl_logo.pack(side=tk.LEFT, padx=(4, 0))
                loaded_iaas_logo = True
            except Exception:
                pass
        if not loaded_iaas_logo and "CARONA_LOGO_B64" in globals():
            try:
                import io
                raw_data = base64.b64decode(CARONA_LOGO_B64)
                raw_img = Image.open(io.BytesIO(raw_data))
                scale_img = raw_img.resize((120, 50), Image.Resampling.LANCZOS)
                self.carona_logo = ImageTk.PhotoImage(scale_img)
                lbl_logo = tk.Label(brand_bar, image=self.carona_logo, bg=self.COLOR_BG)
                lbl_logo.pack(side=tk.LEFT, padx=(4, 0))
                loaded_iaas_logo = True
            except Exception:
                pass
        if not loaded_iaas_logo:
            logo_c = tk.Canvas(brand_bar, width=160, height=54, bg=self.COLOR_BG, highlightthickness=0)
            logo_c.pack(side=tk.LEFT)
            logo_c.create_oval(10, 8, 44, 42, fill="#1b3d63", outline="")
            logo_c.create_text(27, 24, text="⚡", fill="white", font=("Arial", 14, "bold"))
            logo_c.create_text(96, 20, text="CARONA", fill="#1b3d63", font=("Arial", 11, "bold"))
            logo_c.create_text(92, 36, text="POWER", fill="#1b3d63", font=("Arial", 11, "bold"))

        # Center IAAS Logo
        iaas_c = tk.Canvas(brand_bar, width=180, height=54, bg=self.COLOR_BG, highlightthickness=0)
        iaas_c.pack(side=tk.LEFT, expand=True)
        iaas_c.create_text(90, 27, text="IAAS", fill="#1fa2b8", font=("Impact", 28, "italic"))
        iaas_c.create_text(92, 28, text="⚡", fill="#ffff00", font=("Arial", 16, "bold"))

        # 3. Main Split Panels: Left (Channels 1 & 2) and Right (Parameters)
        panels_f = tk.Frame(body, bg=self.COLOR_BG)
        panels_f.pack(fill=tk.BOTH, expand=True)

        panels_f.columnconfigure(0, weight=1, uniform="panels")
        panels_f.columnconfigure(1, weight=1, uniform="panels")
        panels_f.rowconfigure(0, weight=1)

        # LEFT PANEL: Channel 1 & Channel 2 Group Boxes
        left_box = tk.Frame(panels_f, bg=self.COLOR_BG, bd=1, relief=tk.GROOVE)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=4, ipady=8, ipadx=8)

        left_box.columnconfigure(0, weight=1)
        left_box.columnconfigure(1, weight=1)

        # --- Channel 1 LabelFrame ---
        ch1_frame = tk.LabelFrame(left_box, text="Channel 1", bg=self.COLOR_BG, fg=self.COLOR_TEXT_LIGHT, font=self.font_header, bd=1, relief=tk.GROOVE)
        ch1_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=8, ipadx=4, ipady=6)

        self.btn_ch1 = tk.Button(
            ch1_frame, text="Active", bg=self.COLOR_GREEN, fg="black",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2", width=12,
            command=self.toggle_ch1
        )
        self.btn_ch1.pack(pady=(4, 10))

        # Type
        f_t1 = tk.Frame(ch1_frame, bg=self.COLOR_BG)
        f_t1.pack(fill=tk.X, padx=4, pady=3)
        tk.Label(f_t1, text="Type", bg=self.COLOR_BG, fg=self.COLOR_TEXT_LIGHT, font=self.font_label).pack(side=tk.LEFT)
        self.cb_ch1_type = ttk.Combobox(f_t1, values=["Voltage", "Current"], width=9, state="readonly")
        self.cb_ch1_type.set("Voltage")
        self.cb_ch1_type.pack(side=tk.RIGHT)

        # Internal Att.
        f_ia1 = tk.Frame(ch1_frame, bg=self.COLOR_BG)
        f_ia1.pack(fill=tk.X, padx=4, pady=3)
        tk.Label(f_ia1, text="Internal Att.", bg=self.COLOR_BG, fg=self.COLOR_TEXT_LIGHT, font=self.font_label).pack(side=tk.LEFT)
        sp_ia1 = ttk.Spinbox(f_ia1, from_=1, to_=10000, width=7)
        sp_ia1.set(200)
        sp_ia1.pack(side=tk.RIGHT)

        # External Att.
        f_ea1 = tk.Frame(ch1_frame, bg=self.COLOR_BG)
        f_ea1.pack(fill=tk.X, padx=4, pady=3)
        tk.Label(f_ea1, text="External Att.", bg=self.COLOR_BG, fg=self.COLOR_TEXT_LIGHT, font=self.font_label).pack(side=tk.LEFT)
        sp_ea1 = ttk.Spinbox(f_ea1, from_=1, to_=10000, width=7)
        sp_ea1.set(1066)
        sp_ea1.pack(side=tk.RIGHT)

        # --- Channel 2 LabelFrame ---
        ch2_frame = tk.LabelFrame(left_box, text="Channel 2", bg=self.COLOR_BG, fg=self.COLOR_TEXT_LIGHT, font=self.font_header, bd=1, relief=tk.GROOVE)
        ch2_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=8, ipadx=4, ipady=6)

        self.btn_ch2 = tk.Button(
            ch2_frame, text="Inactive", bg=self.COLOR_DARK_BTN, fg="white",
            font=self.font_btn, relief=tk.RAISED, bd=2, cursor="hand2", width=12,
            command=self.toggle_ch2
        )
        self.btn_ch2.pack(pady=(4, 10))

        # Type
        f_t2 = tk.Frame(ch2_frame, bg=self.COLOR_BG)
        f_t2.pack(fill=tk.X, padx=4, pady=3)
        tk.Label(f_t2, text="Type", bg=self.COLOR_BG, fg=self.COLOR_TEXT_LIGHT, font=self.font_label).pack(side=tk.LEFT)
        self.cb_ch2_type = ttk.Combobox(f_t2, values=["Voltage", "Current"], width=9, state="readonly")
        self.cb_ch2_type.set("Current")
        self.cb_ch2_type.pack(side=tk.RIGHT)

        # Internal Att.
        f_ia2 = tk.Frame(ch2_frame, bg=self.COLOR_BG)
        f_ia2.pack(fill=tk.X, padx=4, pady=3)
        tk.Label(f_ia2, text="Internal Att.", bg=self.COLOR_BG, fg=self.COLOR_TEXT_LIGHT, font=self.font_label).pack(side=tk.LEFT)
        sp_ia2 = ttk.Spinbox(f_ia2, from_=1, to_=10000, width=7)
        sp_ia2.set(200)
        sp_ia2.pack(side=tk.RIGHT)

        # External Att.
        f_ea2 = tk.Frame(ch2_frame, bg=self.COLOR_BG)
        f_ea2.pack(fill=tk.X, padx=4, pady=3)
        tk.Label(f_ea2, text="External Att.", bg=self.COLOR_BG, fg=self.COLOR_TEXT_LIGHT, font=self.font_label).pack(side=tk.LEFT)
        sp_ea2 = ttk.Spinbox(f_ea2, from_=1, to_=10000, width=7)
        sp_ea2.set(10)
        sp_ea2.pack(side=tk.RIGHT)

        # RIGHT PANEL: Parameters Frame
        right_box = tk.Frame(panels_f, bg=self.COLOR_BG, bd=1, relief=tk.GROOVE)
        right_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=4, ipady=8, ipadx=8)

        params = [
            ("Impulse Type", "combo", ["Lightning", "Switching", "Chopped"], "Lightning"),
            ("Polarity", "combo", ["Positive", "Negative"], "Positive"),
            ("Expected Voltage [kV]", "spin", (1, 1000), 100),
            ("Expected Current [A]", "spin", (1, 5000), 300),
            ("N° of Shots", "spin", (1, 100), 1),
            ("Window Time", "combo", ["100 us", "200 us", "500 us", "1 ms"], "100 us"),
        ]

        for item in params:
            lbl, kind, choices, default = item
            r = tk.Frame(right_box, bg=self.COLOR_BG)
            r.pack(fill=tk.X, padx=16, pady=5)
            tk.Label(r, text=lbl, bg=self.COLOR_BG, fg=self.COLOR_TEXT_LIGHT, font=self.font_label, anchor="w").pack(side=tk.LEFT)
            if kind == "combo":
                cb = ttk.Combobox(r, values=choices, width=18, state="readonly")
                cb.set(default)
                cb.pack(side=tk.RIGHT)
            else:
                sp = ttk.Spinbox(r, from_=choices[0], to_=choices[1], width=18)
                sp.set(default)
                sp.pack(side=tk.RIGHT)

        # 4. Bottom Right Action Bar: ENTER Button
        bot_bar = tk.Frame(body, bg=self.COLOR_BG)
        bot_bar.pack(fill=tk.X, pady=(10, 0))

        btn_enter = tk.Button(
            bot_bar, text="ENTER", bg=self.COLOR_GREEN, fg="black",
            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2, padx=22, pady=4,
            cursor="hand2", command=self.on_enter
        )
        btn_enter.pack(side=tk.RIGHT)

    def toggle_ch1(self):
        self.ch1_active = not self.ch1_active
        if self.ch1_active:
            self.btn_ch1.config(text="Active", bg=self.COLOR_GREEN, fg="black")
        else:
            self.btn_ch1.config(text="Inactive", bg=self.COLOR_DARK_BTN, fg="white")

    def toggle_ch2(self):
        self.ch2_active = not self.ch2_active
        if self.ch2_active:
            self.btn_ch2.config(text="Active", bg=self.COLOR_GREEN, fg="black")
        else:
            self.btn_ch2.config(text="Inactive", bg=self.COLOR_DARK_BTN, fg="white")

    def on_enter(self):
        pass


# ==============================================================================
# GTU Curve Window ("Gap Distance Setting" - Voltage vs Sphere Distance)
# ==============================================================================
CARONA_LOGO_B64 = """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"""

class GTUCurveWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
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
            self.title_canvas.create_text(cx + 1, cy + 1, text="Voltage vs Sphere Distance", fill="#1a2030", font=self.font_title)
            self.title_canvas.create_text(cx, cy, text="Voltage vs Sphere Distance", fill="#ffffff", font=self.font_title)

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
        # RIGHT: Carona Power Logo, Data Table, Inputs, Ratio
        # ----------------------------------------------------------------------
        right_panel = tk.Frame(content_split, bg=self.COLOR_PANEL, width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 4), pady=4)
        right_panel.pack_propagate(False)

        # 1. Carona Power Logo (In place of WSTS logo!)
        logo_frame = tk.Frame(right_panel, bg=self.COLOR_PANEL, height=80)
        logo_frame.pack(fill=tk.X, pady=(0, 6))
        logo_frame.pack_propagate(False)

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carona_logo_ui.png")
        loaded = False
        if os.path.exists(logo_path):
            try:
                raw_img = Image.open(logo_path)
                self.logo_img = ImageTk.PhotoImage(raw_img)
                lbl_logo = tk.Label(logo_frame, image=self.logo_img, bg=self.COLOR_PANEL)
                lbl_logo.pack(anchor="center")
                loaded = True
            except Exception:
                pass
        if not loaded and "CARONA_LOGO_B64" in globals():
            try:
                import io
                raw_data = base64.b64decode(CARONA_LOGO_B64)
                raw_img = Image.open(io.BytesIO(raw_data))
                self.logo_img = ImageTk.PhotoImage(raw_img)
                lbl_logo = tk.Label(logo_frame, image=self.logo_img, bg=self.COLOR_PANEL)
                lbl_logo.pack(anchor="center")
                loaded = True
            except Exception:
                pass
        if not loaded:
            self.draw_fallback_logo(logo_frame)

        # 2. Table + Side Buttons (p / q) Container
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

    def make_numeric_box(self, parent, default_val):
        box = tk.Frame(parent, bg=self.COLOR_PANEL)
        sp = tk.Frame(box, bg="#d0d8e8", bd=1, relief=tk.RAISED, cursor="hand2")
        sp.pack(side=tk.LEFT, padx=(0, 2))
        tk.Label(sp, text="▲\n▼", bg="#d0d8e8", fg="#1a2030", font=("Arial", 6, "bold")).pack(padx=2, pady=1)

        ent = tk.Entry(box, width=7, font=self.font_digital, bg="#ffffff", fg="#000000", bd=2, relief=tk.SUNKEN, justify="center")
        ent.insert(0, default_val)
        ent.pack(side=tk.LEFT)
        return box, ent

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
            GTUCurveWindow(self.root)
        elif name == "TDG":
            IAASSetupWindow(self.root)
        else:
            LabVIEWSubWindow(self.root, name)

    def create_led(self, parent, is_on=False, size=12, name=None, interactive=False):
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
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    m = re.match(r"^\s*\d+\s+(.+?)\s+DO\s+Channel", line, re.IGNORECASE)
                    if m:
                        labels.append(m.group(1).strip())
                    else:
                        parts = re.split(r"\s{2,}|\t+", line)
                        if len(parts) >= 2:
                            labels.append(parts[1].strip())
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

        # Option 1: Carona Power Logo in Sub-Header (Top-Left under Tabs)
        self.logo_sub_img = None
        sub_logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carona_logo_ui.png")
        if os.path.exists(sub_logo_path):
            try:
                raw_logo = Image.open(sub_logo_path)
                h_sub = 28
                w_sub = int(raw_logo.width * (h_sub / raw_logo.height))
                scaled_sub = raw_logo.resize((w_sub, h_sub), Image.Resampling.LANCZOS)
                self.logo_sub_img = ImageTk.PhotoImage(scaled_sub)
            except Exception:
                pass
        if not self.logo_sub_img and "CARONA_LOGO_B64" in globals():
            try:
                import io
                raw_data = base64.b64decode(CARONA_LOGO_B64)
                raw_logo = Image.open(io.BytesIO(raw_data))
                h_sub = 28
                w_sub = int(raw_logo.width * (h_sub / raw_logo.height))
                scaled_sub = raw_logo.resize((w_sub, h_sub), Image.Resampling.LANCZOS)
                self.logo_sub_img = ImageTk.PhotoImage(scaled_sub)
            except Exception:
                pass

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

    def switch_tab(self, tab_name):
        self.current_tab = tab_name
        if tab_name == "cFP":
            self.cfp_btn.config(bg=self.COLOR_TAB_ACTIVE, font=self.font_header)
            self.settings_btn.config(bg=self.COLOR_TAB_INACTIVE, font=self.font_label)
            self.status_box.place(relx=1.0, x=-95, y=34, anchor="ne")
            self.settings_frame.pack_forget()
            self.cfp_frame.pack(fill=tk.BOTH, expand=True)
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
        p1_body.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)
        p1_body.columnconfigure(0, weight=1)
        p1_body.columnconfigure(1, weight=1)

        p1_col1 = tk.Frame(p1_body, bg=self.COLOR_PANEL)
        p1_col1.grid(row=0, column=0, sticky="nsew", padx=2)

        p1_col2 = tk.Frame(p1_body, bg=self.COLOR_PANEL)
        p1_col2.grid(row=0, column=1, sticky="nsew", padx=2)

        txt_path = os.path.join(os.path.dirname(__file__), "sample_txt for utility.txt")
        file_labels = self.load_channel_labels(txt_path)

        if len(file_labels) >= 30:
            do1_items = file_labels[:15]
            do2_items = file_labels[15:30]
        elif len(file_labels) > 0:
            half = len(file_labels) // 2
            do1_items = file_labels[:half]
            do2_items = file_labels[half:]
        else:
            do1_items = [
                "H.V. Charging", "Emergency Signal", "MTSignal", "Pol+ Gen CC",
                "Pol- Gen CC", "Hooter", "GND Control", "IMC FS Supply",
                "Decrease Dist GTU", "Increase Dist GTU", "Increase MSG",
                "Start Charge", "Pol - Card", "Pol + Card", "xx"
            ]
            do2_items = [
                "Inc Press GTN", "Dec Press GTN", "Plunger All Stages", "Plunger 1 Stage",
                "Plunger 2 Stage", "Sphere A GTN", "Sphere B GTN", "Sphere A IMC",
                "Sphere B IMC", "Inc Press IMC", "Dec Press IMC", "xx", "xx", "xx", "xx"
            ]

        for item in do1_items:
            if item is None:
                tk.Frame(p1_col1, bg=self.COLOR_PANEL, height=12).pack()
                continue
            row = tk.Frame(p1_col1, bg=self.COLOR_PANEL)
            row.pack(anchor="w", pady=0.5)
            led = self.create_led(row, is_on=False, name=f"DO1_{item}", interactive=True)
            led.pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(row, text=item, bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_label).pack(side=tk.LEFT)

        for item in do2_items:
            if item is None:
                tk.Frame(p1_col2, bg=self.COLOR_PANEL, height=12).pack()
                continue
            row = tk.Frame(p1_col2, bg=self.COLOR_PANEL)
            row.pack(anchor="w", pady=0.5)
            led = self.create_led(row, is_on=False, name=f"DO2_{item}", interactive=True)
            led.pack(side=tk.LEFT, padx=(0, 4))
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
        p3_body.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)
        p3_body.columnconfigure(0, weight=1)
        p3_body.columnconfigure(1, weight=1)

        p3_col1 = tk.Frame(p3_body, bg=self.COLOR_PANEL)
        p3_col1.grid(row=0, column=0, sticky="nsew", padx=2)

        p3_col2 = tk.Frame(p3_body, bg=self.COLOR_PANEL)
        p3_col2.grid(row=0, column=1, sticky="nsew", padx=2)

        di4_items = [
            ("NoGND", False), ("GND", False), ("FCPol+", False), ("FCPol-", False),
            ("FCatOFF", False), ("FCatON", False), ("Key", False), ("Emergency", False),
            ("ProtExt", False), ("Fusibili", False), ("BadLoad", False), ("ReteOK", False),
            ("noAriaGTUGTN", False), ("FCminGTU", False), ("FCmaxGTU", False), ("noAriaIMC", False)
        ]

        di5_items = [
            ("FCminMSG", False), ("FCmaxMSG", False), ("xx", False), ("xx", False),
            ("xx", False), ("xx", False), ("xx", False), ("xx", False),
            ("xx", False), ("xx", False), ("xx", False), ("xx", False),
            ("xx", False), ("xx", False), ("xx", False), ("xx", False)
        ]

        # Digital inputs are indicators: non-interactive (interactive=False)
        for item, st in di4_items:
            row = tk.Frame(p3_col1, bg=self.COLOR_PANEL)
            row.pack(anchor="w", pady=0.5)
            led = self.create_led(row, is_on=st, name=f"DI4_{item}", interactive=False)
            led.pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(row, text=item, bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_label).pack(side=tk.LEFT)

        for item, st in di5_items:
            row = tk.Frame(p3_col2, bg=self.COLOR_PANEL)
            row.pack(anchor="w", pady=0.5)
            led = self.create_led(row, is_on=st, name=f"DI5_{item}", interactive=False)
            led.pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(row, text=item, bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_label).pack(side=tk.LEFT)

    # ----------------------------------------------------------------------
    # TAB 2: Settings View (Fully Responsive & Proportionate)
    # ----------------------------------------------------------------------
    def build_settings_view(self):
        self.settings_frame = tk.Frame(self.container, bg=self.COLOR_PANEL)

        # Upper Recessed Panel (3 Buttons: Time Charge, Scope TEK30xx, TDG)
        top_box = tk.Frame(self.settings_frame, bg=self.COLOR_PANEL, bd=2, relief=tk.GROOVE, height=130)
        top_box.pack(fill=tk.X, padx=16, pady=(16, 8))
        top_box.pack_propagate(False)

        top_box.columnconfigure(0, weight=1)
        top_box.columnconfigure(1, weight=1)
        top_box.columnconfigure(2, weight=1)
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

        bottom_box.columnconfigure(0, weight=1)
        bottom_box.columnconfigure(1, weight=1)
        bottom_box.columnconfigure(2, weight=1)

        # Column 1 (Left) - Opens GTU Distance Transducer Calibration!
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

        # Column 2 (Middle)
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

        # Column 3 (Right)
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


if __name__ == "__main__":
    root = tk.Tk()
    app = LabVIEWUtilityApp(root)
    root.mainloop()