import tkinter as tk
import os
import base64
from PIL import Image, ImageTk
from widgets import (
    LabVIEWNumericBox,
    get_carona_logo,
    get_pill_stepper_image,
    get_info_bubble_image,
    get_increase_arrow_image,
    get_decrease_arrow_image,
    PILL_STEPPER_B64,
    INFO_BUBBLE_B64,
)

class CalibrationConfirmDialog(tk.Toplevel):
    def __init__(self, parent, on_yes, on_no):
        super().__init__(parent)
        self.parent = parent
        self.on_yes_cb = on_yes
        self.on_no_cb = on_no
        self.title("Calibration")
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

        self.setup_ui()
        self.grab_set()

    def setup_ui(self):
        content_f = tk.Frame(self, bg="#8c97a8")
        content_f.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))

        # Left Info Bubble Icon
        self.icon_img = get_info_bubble_image(56)
        if self.icon_img:
            lbl_icon = tk.Label(content_f, image=self.icon_img, bg="#8c97a8", bd=0)
            lbl_icon.pack(side=tk.LEFT, padx=(6, 18), anchor="n")
        else:
            icon_c = tk.Canvas(content_f, width=54, height=54, bg="#8c97a8", highlightthickness=0)
            icon_c.pack(side=tk.LEFT, padx=(6, 18), anchor="n")
            icon_c.create_oval(2, 2, 50, 50, fill="#ffffff", outline="#202020", width=1.5)
            icon_c.create_text(26, 26, text="i", fill="#0000cc", font=("Georgia", 22, "bold italic"))

        # Text Container
        text_f = tk.Frame(content_f, bg="#8c97a8")
        text_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            text_f, text="Calibration", bg="#8c97a8", fg="#000000",
            font=("Arial", 11, "bold"), anchor="w"
        ).pack(fill=tk.X, pady=(2, 6))

        tk.Label(
            text_f, text="Do you want to overwrite the calibration\\ndata?",
            bg="#8c97a8", fg="#000000", font=("Arial", 10, "bold"),
            justify="left", anchor="w"
        ).pack(fill=tk.X)

        # Bottom Action Buttons (Yes / No)
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
# MSG - Distance Transducer Calibration Window (One-to-One media_1789193808590)
# ==============================================================================
class MSGDistanceCalibrationWindow(tk.Toplevel):
    def __init__(self, parent, app_ref=None):
        super().__init__(parent)
        self.parent = parent
        self.app_ref = app_ref
        self.title("Distance Trasducer Calibration")
        self.resizable(True, True)
        self.minsize(740, 560)
        self.configure(bg="#8c97a8")

        # Initial Values from Screenshot media_1789193808590
        defaults = {
            "min_dist": "0.0",
            "max_dist": "0.0",
            "volt_read_1": "0.003",
            "volt_read_2": "0.003",
            "distance_mm": "-151.79",
            "coeff_a": "98.93",
            "coeff_b": "-152.08"
        }
        if self.app_ref and hasattr(self.app_ref, "msg_cal_values"):
            self.vals = dict(self.app_ref.msg_cal_values)
        else:
            self.vals = dict(defaults)

        self.pill_img = None
        self.load_pill_image()

        self.setup_ui()
        self.center_on_parent(780, 580)

        self.protocol("WM_DELETE_WINDOW", self.on_exit_click)

    def load_pill_image(self):
        self.pill_img = get_pill_stepper_image(18, 26)

    def center_on_parent(self, width=780, height=580):
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

    def make_digital_readout(self, parent, text, width=76, height=26):
        """Creates authentic LabVIEW black sunken digital readout box with exact pixel dimensions."""
        frame = tk.Frame(parent, bg="#000000", bd=2, relief=tk.SUNKEN, width=width, height=height)
        frame.pack_propagate(False)
        lbl = tk.Label(frame, text=text, bg="#000000", fg="#ffffff", font=("Arial", 11, "bold"), anchor="center")
        lbl.pack(fill=tk.BOTH, expand=True)
        return frame, lbl

    def make_stepper_box(self, parent, initial_val="0.0", on_step=None):
        num_box = LabVIEWNumericBox(
            parent, initial_val=initial_val, width=62, height=26,
            font=("Arial", 10, "bold"), on_step=lambda d: on_step(type("Event", (), {"y": 5 if d > 0 else 20})()) if on_step else None,
            bg="#8c97a8"
        )
        return num_box, num_box

    def setup_ui(self):
        main_container = tk.Frame(self, bg="#5c6877", bd=2, relief=tk.SUNKEN)
        main_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # 1. Top Header Bar: Title & Exit Button
        header_frame = tk.Frame(main_container, bg="#8c97a8", height=44)
        header_frame.pack(fill=tk.X, padx=4, pady=(4, 0))
        header_frame.pack_propagate(False)

        exit_btn = tk.Button(
            header_frame, text="Exit", bg="#ffff00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=14, pady=1,
            cursor="hand2", command=self.on_exit_click
        )
        exit_btn.pack(side=tk.RIGHT, padx=6, pady=6)

        # Carona Power Logo on Far Left
        self.logo_img = get_carona_logo(height=28)
        if self.logo_img:
            self.lbl_logo = tk.Label(header_frame, image=self.logo_img, bg="#8c97a8", bd=0)
            self.lbl_logo.pack(side=tk.LEFT, padx=(6, 8), pady=4)

        title_canvas = tk.Canvas(header_frame, bg="#8c97a8", highlightthickness=0)
        title_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def update_title(event=None):
            title_canvas.delete("all")
            w = title_canvas.winfo_width()
            cx = w // 2 or 370
            title_canvas.create_text(cx + 2, 20, text="MSG - Distance Trasducer Calibration", fill="#000000", font=("Arial", 15, "bold"))
            title_canvas.create_text(cx, 18, text="MSG - Distance Trasducer Calibration", fill="#ffff00", font=("Arial", 15, "bold"))

        title_canvas.bind("<Configure>", update_title)

        # 2. Content Body
        body = tk.Frame(main_container, bg="#8c97a8")
        body.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # UPPER SECTION
        upper_frame = tk.Frame(body, bg="#8c97a8", height=210)
        upper_frame.pack(fill=tk.X, pady=(0, 2))
        upper_frame.pack_propagate(False)

        # Upper Left: Steps #1 and #2
        steps_left = tk.Frame(upper_frame, bg="#8c97a8")
        steps_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 4), pady=4)

        # --- Step #1 ---
        lbl_s1 = tk.Canvas(steps_left, height=18, bg="#8c97a8", highlightthickness=0)
        lbl_s1.pack(anchor="w")
        lbl_s1.create_text(36, 10, text="Step #1", fill="#000000", font=("Arial", 10, "bold"))
        lbl_s1.create_text(35, 9, text="Step #1", fill="#ffffff", font=("Arial", 10, "bold"))

        row_s1 = tk.Frame(steps_left, bg="#8c97a8")
        row_s1.pack(fill=tk.X, pady=(2, 8))

        # Labels in row 0
        tk.Label(row_s1, text="Set Dist. Min [mm]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 14), pady=(0, 2))
        tk.Label(row_s1, text="Voltage Read", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).grid(row=0, column=1, sticky="w", padx=(0, 14), pady=(0, 2))

        # Controls in row 1 (Perfect horizontal baseline alignment)
        self.spin_min, self.entry_min = self.make_stepper_box(row_s1, self.vals["min_dist"], lambda e: self.step_entry(self.entry_min, e, 1.0))
        self.spin_min.grid(row=1, column=0, sticky="w", padx=(0, 14))

        self.box_v1, self.lbl_v1 = self.make_digital_readout(row_s1, self.vals["volt_read_1"], width=76, height=26)
        self.box_v1.grid(row=1, column=1, sticky="w", padx=(0, 14))

        f_enter1 = tk.Frame(row_s1, bg="#8c97a8", width=76, height=26)
        f_enter1.pack_propagate(False)
        btn_enter1 = tk.Button(
            f_enter1, text="Enter", bg="#00cc00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2,
            cursor="hand2", command=self.on_enter_step1
        )
        btn_enter1.pack(fill=tk.BOTH, expand=True)
        f_enter1.grid(row=1, column=2, sticky="w")

        # --- Step #2 ---
        lbl_s2 = tk.Canvas(steps_left, height=18, bg="#8c97a8", highlightthickness=0)
        lbl_s2.pack(anchor="w")
        lbl_s2.create_text(36, 10, text="Step #2", fill="#000000", font=("Arial", 10, "bold"))
        lbl_s2.create_text(35, 9, text="Step #2", fill="#ffffff", font=("Arial", 10, "bold"))

        row_s2 = tk.Frame(steps_left, bg="#8c97a8")
        row_s2.pack(fill=tk.X, pady=(2, 4))

        # Labels in row 0
        tk.Label(row_s2, text="Set Dist. Max [mm]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 14), pady=(0, 2))
        tk.Label(row_s2, text="Voltage Read", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).grid(row=0, column=1, sticky="w", padx=(0, 14), pady=(0, 2))

        # Controls in row 1 (Perfect horizontal baseline alignment)
        self.spin_max, self.entry_max = self.make_stepper_box(row_s2, self.vals["max_dist"], lambda e: self.step_entry(self.entry_max, e, 1.0))
        self.spin_max.grid(row=1, column=0, sticky="w", padx=(0, 14))

        self.box_v2, self.lbl_v2 = self.make_digital_readout(row_s2, self.vals["volt_read_2"], width=76, height=26)
        self.box_v2.grid(row=1, column=1, sticky="w", padx=(0, 14))

        f_enter2 = tk.Frame(row_s2, bg="#8c97a8", width=76, height=26)
        f_enter2.pack_propagate(False)
        btn_enter2 = tk.Button(
            f_enter2, text="Enter", bg="#00cc00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2,
            cursor="hand2", command=self.on_enter_step2
        )
        btn_enter2.pack(fill=tk.BOTH, expand=True)
        f_enter2.grid(row=1, column=2, sticky="w")

        # Vertical Divider Line
        sep_v = tk.Frame(upper_frame, bg="#ffffff", bd=1, relief=tk.SUNKEN, width=2)
        sep_v.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=8)

        # Upper Right: Increase, Distance, Decrease (Single straight column with exact width 100px)
        act_right = tk.Frame(upper_frame, bg="#8c97a8", width=260)
        act_right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 20), pady=10)
        act_right.pack_propagate(False)

        act_right.columnconfigure(0, minsize=110)
        act_right.columnconfigure(1, minsize=100)

        # Row 0: Increase (Orange button matching media_1789869689118.png with centered hyphens "< -  - >")
        tk.Label(act_right, text="Increase", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold"), anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        f_inc = tk.Frame(act_right, bg="#8c97a8", width=100, height=28)
        f_inc.pack_propagate(False)
        self.img_inc = get_increase_arrow_image(64, 20)
        btn_inc = tk.Button(
            f_inc, image=self.img_inc, bg="#fd8e16", activebackground="#ff9d2e",
            relief=tk.RAISED, bd=2, cursor="hand2"
        )
        btn_inc.pack(fill=tk.BOTH, expand=True)
        f_inc.grid(row=0, column=1, sticky="w", pady=4)

        # Row 1: Distance [mm] (Black Digital Readout, exact width 100px)
        tk.Label(act_right, text="Distance [mm]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold"), anchor="w").grid(row=1, column=0, sticky="w", pady=4)
        self.box_dist, self.lbl_dist = self.make_digital_readout(act_right, self.vals["distance_mm"], width=100, height=28)
        self.box_dist.grid(row=1, column=1, sticky="w", pady=4)

        # Row 2: Decrease (Orange button matching media_1789869689120.png with centered hyphens "- >  < -")
        tk.Label(act_right, text="Decrease", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold"), anchor="w").grid(row=2, column=0, sticky="w", pady=4)
        f_dec = tk.Frame(act_right, bg="#8c97a8", width=100, height=28)
        f_dec.pack_propagate(False)
        self.img_dec = get_decrease_arrow_image(64, 20)
        btn_dec = tk.Button(
            f_dec, image=self.img_dec, bg="#fd8e16", activebackground="#ff9d2e",
            relief=tk.RAISED, bd=2, cursor="hand2"
        )
        btn_dec.pack(fill=tk.BOTH, expand=True)
        f_dec.grid(row=2, column=1, sticky="w", pady=4)

        # Horizontal Divider Line separating Upper from Lower
        sep_h = tk.Frame(body, bg="#ffffff", bd=1, relief=tk.SUNKEN, height=2)
        sep_h.pack(fill=tk.X, padx=2, pady=(2, 6))

        # LOWER SECTION
        lower_frame = tk.Frame(body, bg="#8c97a8")
        lower_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        # Right: Step #3 Calculation Container (Exact straight column alignment matching upper right)
        calc_box = tk.Frame(lower_frame, bg="#8c97a8", width=260)
        calc_box.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 20), pady=8)
        calc_box.pack_propagate(False)

        # Left: Graph Container
        graph_box = tk.Frame(lower_frame, bg="#8c97a8")
        graph_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.graph_canvas = tk.Canvas(graph_box, bg="#8c97a8", highlightthickness=0)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        self.graph_canvas.bind("<Configure>", lambda e: self.draw_graph())

        # Step #3 Grid in calc_box
        calc_box.columnconfigure(0, minsize=110)
        calc_box.columnconfigure(1, minsize=100)

        lbl_s3 = tk.Canvas(calc_box, width=70, height=24, bg="#8c97a8", highlightthickness=0)
        lbl_s3.create_text(36, 13, text="Step #3", fill="#000000", font=("Arial", 10, "bold"))
        lbl_s3.create_text(35, 12, text="Step #3", fill="#ffffff", font=("Arial", 10, "bold"))
        lbl_s3.grid(row=0, column=0, sticky="w", pady=(4, 14))

        f_calc = tk.Frame(calc_box, bg="#8c97a8", width=100, height=28)
        f_calc.pack_propagate(False)
        btn_calc = tk.Button(
            f_calc, text="Calculation", bg="#ffff00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2,
            cursor="hand2", command=self.on_calculate
        )
        btn_calc.pack(fill=tk.BOTH, expand=True)
        f_calc.grid(row=0, column=1, sticky="w", pady=(4, 14))

        # A [mm/V] Readout Row
        tk.Label(calc_box, text="A [mm/V]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold"), anchor="w").grid(row=1, column=0, sticky="w", pady=6)
        self.box_a, self.lbl_a = self.make_digital_readout(calc_box, self.vals["coeff_a"], width=100, height=28)
        self.box_a.grid(row=1, column=1, sticky="w", pady=6)

        # B [mm] Readout Row
        tk.Label(calc_box, text="B [mm]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold"), anchor="w").grid(row=2, column=0, sticky="w", pady=6)
        self.box_b, self.lbl_b = self.make_digital_readout(calc_box, self.vals["coeff_b"], width=100, height=28)
        self.box_b.grid(row=2, column=1, sticky="w", pady=6)

    def step_entry(self, entry, event, delta):
        if event.y < 13:
            change = delta
        else:
            change = -delta
        try:
            v = float(entry.get())
        except ValueError:
            v = 0.0
        v = max(0.0, v + change)
        entry.delete(0, tk.END)
        entry.insert(0, f"{v:.1f}")

    def draw_graph(self):
        c = self.graph_canvas
        c.delete("all")

        cw = c.winfo_width()
        ch = c.winfo_height()
        if cw < 50 or ch < 50:
            cw, ch = 430, 290

        gx1 = 45
        gy1 = 15
        gx2 = max(gx1 + 100, cw - 20)
        gy2 = max(gy1 + 100, ch - 35)
        gw = gx2 - gx1
        gh = gy2 - gy1

        # Plot Background Area
        c.create_rectangle(gx1, gy1, gx2, gy2, fill="#778394", outline="#5a6478", width=1.5)
        c.create_line(gx1, gy1, gx2, gy1, fill="#404a58")
        c.create_line(gx1, gy1, gx1, gy2, fill="#404a58")
        c.create_line(gx2, gy1, gx2, gy2, fill="#d0d8e8")
        c.create_line(gx1, gy2, gx2, gy2, fill="#d0d8e8")

        # Y Ticks: 0 to 10
        for i in range(11):
            y_val = i
            py = gy2 - (y_val / 10.0) * gh
            c.create_line(gx1, py, gx2, py, fill="#8892a4")
            c.create_line(gx1 - 3, py, gx1, py, fill="#0a1018")
            c.create_text(gx1 - 8, py, text=str(y_val), font=("Arial", 7, "bold"), fill="#0a1018", anchor="e")

        # X Ticks: 0 to 50
        for i in range(11):
            x_val = i * 5
            px = gx1 + (x_val / 50.0) * gw
            c.create_line(px, gy1, px, gy2, fill="#8892a4")
            c.create_line(px, gy2, px, gy2 + 3, fill="#0a1018")
            c.create_text(px, gy2 + 10, text=str(x_val), font=("Arial", 7, "bold"), fill="#0a1018", anchor="n")

        # Y Axis Label
        c.create_text(14, gy1 + gh // 2, text="Pot Voltage [Volt]", font=("Arial", 8, "bold"), fill="#0a1018", angle=90)
        # X Axis Label
        c.create_text(gx1 + gw // 2, gy2 + 22, text="Distance [mm]", font=("Arial", 8, "bold"), fill="#0a1018")

        # Plotted Red Calibration Dot matching screenshot at (x=0, y=3)
        dot_x = gx1 + (0 / 50.0) * gw
        dot_y = gy2 - (3.0 / 10.0) * gh
        c.create_oval(dot_x - 3.5, dot_y - 3.5, dot_x + 3.5, dot_y + 3.5, fill="#ff0000", outline="#990000")

    def on_enter_step1(self):
        pass

    def on_enter_step2(self):
        pass

    def on_calculate(self):
        pass

    def on_exit_click(self):
        CalibrationConfirmDialog(self, on_yes=self.on_confirm_yes, on_no=self.on_confirm_no)

    def on_confirm_yes(self):
        if self.app_ref:
            self.app_ref.msg_cal_values = {
                "min_dist": self.entry_min.get(),
                "max_dist": self.entry_max.get(),
                "volt_read_1": self.lbl_v1.cget("text"),
                "volt_read_2": self.lbl_v2.cget("text"),
                "distance_mm": self.lbl_dist.cget("text"),
                "coeff_a": self.lbl_a.cget("text"),
                "coeff_b": self.lbl_b.cget("text")
            }
        self.destroy()

    def on_confirm_no(self):
        self.destroy()
