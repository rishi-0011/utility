import tkinter as tk
from widgets import (
    LabVIEWNumericBox,
    get_carona_logo,
    get_pill_stepper_image,
    get_increase_arrow_image,
    get_decrease_arrow_image,
)

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


    def make_digital_readout(self, parent, text, width=76, height=26):
        """Creates authentic LabVIEW black sunken digital readout box with exact pixel dimensions."""
        frame = tk.Frame(parent, bg="#000000", bd=2, relief=tk.SUNKEN, width=width, height=height)
        frame.pack_propagate(False)
        lbl = tk.Label(frame, text=text, bg="#000000", fg="#ffffff", font=getattr(self, "font_digital", ("Arial", 11, "bold")), anchor="center")
        lbl.pack(fill=tk.BOTH, expand=True)
        return frame, lbl

    def make_spin_input(self, parent, initial_val="0.0", delta=1.0, precision=1):
        """Creates 1:1 LabVIEW numeric box matching media_1789869699771.png with pill stepper."""
        def on_step(d):
            try:
                v = float(num_box.get().replace(",", "."))
            except ValueError:
                v = 0.0
            v = max(0.0, v + d * delta)
            num_box.set(f"{v:.{precision}f}")

        num_box = LabVIEWNumericBox(
            parent, initial_val=initial_val, width=62, height=26,
            font=("Arial", 10, "bold"), on_step=on_step, bg=self.COLOR_PANEL
        )
        return num_box, num_box

    def setup_ui(self):
        main_container = tk.Frame(self, bg=self.COLOR_BORDER, bd=2, relief=tk.SUNKEN)
        main_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # ----------------------------------------------------------------------
        # Top Header Bar: Title & Exit Button
        # ----------------------------------------------------------------------
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

        # UPPER SECTION
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

        # Labels in row 0
        tk.Label(row_s1, text="Set Dist. Min [mm]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).grid(row=0, column=0, sticky="w", padx=(0, 14), pady=(0, 2))
        tk.Label(row_s1, text="Voltage Read", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).grid(row=0, column=1, sticky="w", padx=(0, 14), pady=(0, 2))

        # Controls in row 1 (Perfect horizontal baseline alignment)
        self.spin_min, self.entry_min = self.make_spin_input(row_s1, "0.0")
        self.spin_min.grid(row=1, column=0, sticky="w", padx=(0, 14))

        self.box_v1, self.lbl_v1 = self.make_digital_readout(row_s1, f"{self.volt_read:.3f}", width=76, height=26)
        self.box_v1.grid(row=1, column=1, sticky="w", padx=(0, 14))

        f_enter1 = tk.Frame(row_s1, bg=self.COLOR_PANEL, width=76, height=26)
        f_enter1.pack_propagate(False)
        btn_enter1 = tk.Button(
            f_enter1, text="Enter", bg="#00cc00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2,
            cursor="hand2", command=self.on_enter_step1
        )
        btn_enter1.pack(fill=tk.BOTH, expand=True)
        f_enter1.grid(row=1, column=2, sticky="w")

        # --- Step #2 ---
        lbl_s2 = tk.Canvas(steps_left, height=18, bg=self.COLOR_PANEL, highlightthickness=0)
        lbl_s2.pack(anchor="w")
        lbl_s2.create_text(36, 10, text="Step #2", fill="#1a2030", font=self.font_section)
        lbl_s2.create_text(35, 9, text="Step #2", fill="#ffffff", font=self.font_section)

        row_s2 = tk.Frame(steps_left, bg=self.COLOR_PANEL)
        row_s2.pack(fill=tk.X, pady=(2, 4))

        # Labels in row 0
        tk.Label(row_s2, text="Set Dist. Max [mm]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).grid(row=0, column=0, sticky="w", padx=(0, 14), pady=(0, 2))
        tk.Label(row_s2, text="Voltage Read", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header).grid(row=0, column=1, sticky="w", padx=(0, 14), pady=(0, 2))

        # Controls in row 1 (Perfect horizontal baseline alignment)
        self.spin_max, self.entry_max = self.make_spin_input(row_s2, "0.0")
        self.spin_max.grid(row=1, column=0, sticky="w", padx=(0, 14))

        self.box_v2, self.lbl_v2 = self.make_digital_readout(row_s2, f"{self.volt_read:.3f}", width=76, height=26)
        self.box_v2.grid(row=1, column=1, sticky="w", padx=(0, 14))

        f_enter2 = tk.Frame(row_s2, bg=self.COLOR_PANEL, width=76, height=26)
        f_enter2.pack_propagate(False)
        btn_enter2 = tk.Button(
            f_enter2, text="Enter", bg="#00cc00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2,
            cursor="hand2", command=self.on_enter_step2
        )
        btn_enter2.pack(fill=tk.BOTH, expand=True)
        f_enter2.grid(row=1, column=2, sticky="w")

        # Vertical Beveled Divider Line
        sep_v = tk.Frame(upper_frame, bg="#ffffff", bd=1, relief=tk.SUNKEN, width=2)
        sep_v.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=8)

        # Upper Right: Increase, Distance [mm], Decrease (Single straight column with exact width 100px)
        act_right = tk.Frame(upper_frame, bg=self.COLOR_PANEL, width=260)
        act_right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 20), pady=10)
        act_right.pack_propagate(False)

        act_right.columnconfigure(0, minsize=110)
        act_right.columnconfigure(1, minsize=100)

        # Row 0: Increase (Orange button matching media_1789869689120.png with centered hyphens "< -  - >")
        tk.Label(act_right, text="Increase", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header, anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        f_inc = tk.Frame(act_right, bg=self.COLOR_PANEL, width=100, height=28)
        f_inc.pack_propagate(False)
        self.img_inc = get_increase_arrow_image(64, 20)
        btn_inc = tk.Button(
            f_inc, image=self.img_inc, bg="#fd8e16", activebackground="#ff9d2e",
            relief=tk.RAISED, bd=2, cursor="hand2", command=self.on_increase
        )
        btn_inc.pack(fill=tk.BOTH, expand=True)
        f_inc.grid(row=0, column=1, sticky="w", pady=4)

        # Row 1: Distance [mm] (Black Digital Readout, exact width 100px)
        tk.Label(act_right, text="Distance [mm]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header, anchor="w").grid(row=1, column=0, sticky="w", pady=4)
        self.box_dist, self.lbl_dist = self.make_digital_readout(act_right, f"{self.dist_val:.2f}", width=100, height=28)
        self.box_dist.grid(row=1, column=1, sticky="w", pady=4)

        # Row 2: Decrease (Orange button matching media_1789869689120.png with centered hyphens "- >  < -")
        tk.Label(act_right, text="Decrease", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header, anchor="w").grid(row=2, column=0, sticky="w", pady=4)
        f_dec = tk.Frame(act_right, bg=self.COLOR_PANEL, width=100, height=28)
        f_dec.pack_propagate(False)
        self.img_dec = get_decrease_arrow_image(64, 20)
        btn_dec = tk.Button(
            f_dec, image=self.img_dec, bg="#fd8e16", activebackground="#ff9d2e",
            relief=tk.RAISED, bd=2, cursor="hand2", command=self.on_decrease
        )
        btn_dec.pack(fill=tk.BOTH, expand=True)
        f_dec.grid(row=2, column=1, sticky="w", pady=4)

        # Horizontal Divider Line separating Upper from Lower
        sep_h = tk.Frame(body, bg="#ffffff", bd=1, relief=tk.SUNKEN, height=2)
        sep_h.pack(fill=tk.X, padx=2, pady=(2, 6))

        # LOWER SECTION: Calibration Graph & Step #3 Calculation
        lower_frame = tk.Frame(body, bg=self.COLOR_PANEL)
        lower_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        # Right: Step #3 Calculation Container (Exact straight column alignment matching upper right)
        calc_box = tk.Frame(lower_frame, bg=self.COLOR_PANEL, width=260)
        calc_box.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 20), pady=8)
        calc_box.pack_propagate(False)

        # Left: Graph Container
        graph_box = tk.Frame(lower_frame, bg=self.COLOR_PANEL)
        graph_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.graph_canvas = tk.Canvas(graph_box, bg=self.COLOR_PANEL, highlightthickness=0)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        self.graph_canvas.bind("<Configure>", lambda e: self.draw_graph())

        # Step #3 Grid in calc_box
        calc_box.columnconfigure(0, minsize=110)
        calc_box.columnconfigure(1, minsize=100)

        lbl_s3 = tk.Canvas(calc_box, width=70, height=24, bg=self.COLOR_PANEL, highlightthickness=0)
        lbl_s3.create_text(36, 13, text="Step #3", fill="#1a2030", font=self.font_section)
        lbl_s3.create_text(35, 12, text="Step #3", fill="#ffffff", font=self.font_section)
        lbl_s3.grid(row=0, column=0, sticky="w", pady=(4, 14))

        f_calc = tk.Frame(calc_box, bg=self.COLOR_PANEL, width=100, height=28)
        f_calc.pack_propagate(False)
        btn_calc = tk.Button(
            f_calc, text="Calculation", bg="#ffff00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2,
            cursor="hand2", command=self.on_calculate
        )
        btn_calc.pack(fill=tk.BOTH, expand=True)
        f_calc.grid(row=0, column=1, sticky="w", pady=(4, 14))

        # A [mm/V] Readout Row
        tk.Label(calc_box, text="A [mm/V]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header, anchor="w").grid(row=1, column=0, sticky="w", pady=6)
        self.box_a, self.lbl_a = self.make_digital_readout(calc_box, f"{self.coeff_a:.2f}", width=100, height=28)
        self.box_a.grid(row=1, column=1, sticky="w", pady=6)

        # B [mm] Readout Row
        tk.Label(calc_box, text="B [mm]", bg=self.COLOR_PANEL, fg="#0a1018", font=self.font_header, anchor="w").grid(row=2, column=0, sticky="w", pady=6)
        self.box_b, self.lbl_b = self.make_digital_readout(calc_box, f"{self.coeff_b:.2f}", width=100, height=28)
        self.box_b.grid(row=2, column=1, sticky="w", pady=6)

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
