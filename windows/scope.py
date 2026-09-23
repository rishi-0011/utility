import os
import math
import tkinter as tk
from PIL import Image, ImageTk
from widgets import LabVIEWDropdown, get_asset_file, get_carona_logo

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

        # Top Header Bar: Exit Button, Carona Logo & Title
        header_frame = tk.Frame(main_container, bg=self.COLOR_PANEL, height=44)
        header_frame.pack(fill=tk.X, padx=4, pady=(4, 0))
        header_frame.pack_propagate(False)

        exit_btn = tk.Button(
            header_frame, text="Exit", bg="#ffff00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=14, pady=1,
            cursor="hand2", command=self.destroy
        )
        exit_btn.pack(side=tk.RIGHT, padx=6, pady=6)

        # Carona Power Logo on Far Left
        self.logo_img = get_carona_logo(height=28)
        if self.logo_img:
            self.lbl_logo = tk.Label(header_frame, image=self.logo_img, bg=self.COLOR_PANEL, bd=0)
            self.lbl_logo.pack(side=tk.LEFT, padx=(6, 8), pady=4)

        title_canvas = tk.Canvas(header_frame, bg=self.COLOR_PANEL, highlightthickness=0)
        title_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def update_title(event=None):
            title_canvas.delete("all")
            w = title_canvas.winfo_width()
            cx = w // 2 or 300
            title_canvas.create_text(cx + 1, 21, text="Tektronix TDS 3032", fill="#1a2030", font=self.font_title)
            title_canvas.create_text(cx, 20, text="Tektronix TDS 3032", fill="#ffff00", font=self.font_title)

        title_canvas.bind("<Configure>", update_title)

        # Top Panel
        top_panel = tk.Frame(main_container, bg=self.COLOR_PANEL, bd=1, relief=tk.SOLID, height=210)
        top_panel.pack(fill=tk.X, padx=6, pady=6)
        top_panel.pack_propagate(False)

        scope_path = get_asset_file("tek_scope.png")
        if scope_path and os.path.exists(scope_path):
            img_scope = Image.open(scope_path).resize((220, 165), Image.Resampling.LANCZOS)
            photo_scope = ImageTk.PhotoImage(img_scope)
            self.loaded_images.append(photo_scope)
            lbl_scope = tk.Label(top_panel, image=photo_scope, bg=self.COLOR_PANEL, bd=0)
            lbl_scope.place(x=15, y=5)

        btn_ch1 = tk.Button(top_panel, text="CH1", bg="#ffff00", fg="black", font=self.font_btn, relief=tk.RAISED, bd=2, padx=14, pady=2, cursor="hand2")
        btn_ch1.place(x=290, y=170)

        btn_ch2 = tk.Button(top_panel, text="CH2", bg="#8cb3f2", fg="black", font=self.font_btn, relief=tk.RAISED, bd=2, padx=14, pady=2, cursor="hand2")
        btn_ch2.place(x=370, y=170)

        btn_auto = tk.Button(top_panel, text="Auto", bg="#00cc00", fg="black", font=self.font_btn, relief=tk.RAISED, bd=2, padx=14, pady=2, cursor="hand2")
        btn_auto.place(x=480, y=170)

        bar_path = get_asset_file("status_bar.png")
        if bar_path and os.path.exists(bar_path):
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
