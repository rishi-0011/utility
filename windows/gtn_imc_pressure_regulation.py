import tkinter as tk
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

class GTNConfirmDialog(tk.Toplevel):
    def __init__(self, parent, on_yes, on_no):
        super().__init__(parent)
        self.parent = parent
        self.on_yes_cb = on_yes
        self.on_no_cb = on_no
        self.title("GTN")
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

        # 1. Left Info Bubble Icon
        self.icon_img = get_info_bubble_image(56)

        if self.icon_img:
            lbl_icon = tk.Label(content_f, image=self.icon_img, bg="#8c97a8", bd=0)
            lbl_icon.pack(side=tk.LEFT, padx=(6, 18), anchor="n")
        else:
            icon_c = tk.Canvas(content_f, width=54, height=54, bg="#8c97a8", highlightthickness=0)
            icon_c.pack(side=tk.LEFT, padx=(6, 18), anchor="n")
            icon_c.create_oval(2, 2, 50, 50, fill="#ffffff", outline="#202020", width=1.5)
            icon_c.create_text(26, 26, text="i", fill="#0000cc", font=("Georgia", 22, "bold italic"))

        # 2. Text Container
        text_f = tk.Frame(content_f, bg="#8c97a8")
        text_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            text_f, text="GTN", bg="#8c97a8", fg="#000000",
            font=("Arial", 11, "bold"), anchor="w"
        ).pack(fill=tk.X, pady=(2, 6))

        tk.Label(
            text_f, text="Do you want to overwrite Info trasducer\\nand Pressure Regulation  Values?",
            bg="#8c97a8", fg="#000000", font=("Arial", 10, "bold"),
            justify="left", anchor="w"
        ).pack(fill=tk.X)

        # 3. Bottom Action Buttons (Yes / No)
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
# GTN-IMC Pressure Regulation Window (One-to-One matching media_1789193391508)
# ==============================================================================
class GTNIMCPressureRegulationWindow(tk.Toplevel):
    def __init__(self, parent, app_ref=None):
        super().__init__(parent)
        self.parent = parent
        self.app_ref = app_ref
        self.title("GTN-IMC Sensibiliy A&B value")
        self.resizable(True, True)
        self.configure(bg="#8c97a8")

        default_vals = {
            "gtn_min_press": "0.00", "gtn_min_volt": "0.00",
            "gtn_max_press": "4.00", "gtn_max_volt": "10.00",
            "imc_min_press": "0.00", "imc_min_volt": "0.00",
            "imc_max_press": "2.00", "imc_max_volt": "5.00",
            "gtn_pos_prec": "0.01", "gtn_neg_prec": "-0.01",
            "gtn_pos_comp": "0.03", "gtn_neg_comp": "-0.03",
            "imc_pos_prec": "0.01", "imc_neg_prec": "-0.01",
            "imc_pos_comp": "0.03", "imc_neg_comp": "-0.01",
        }
        if self.app_ref and hasattr(self.app_ref, "gtn_imc_values"):
            self.current_vals = dict(self.app_ref.gtn_imc_values)
        else:
            self.current_vals = dict(default_vals)

        self.entries = {}
        self.pill_img = None
        self.load_pill_image()

        self.setup_ui()
        self.center_on_parent(960, 560)
        self.minsize(860, 500)

        self.protocol("WM_DELETE_WINDOW", self.on_exit_click)

    def load_pill_image(self):
        self.pill_img = get_pill_stepper_image(18, 26)

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

    def make_stepper_input(self, parent, key, is_black=True, width=62, height=26, delta=0.5, precision=2):
        box_bg = "#000000" if is_black else "#ffffff"
        text_fg = "#ffffff" if is_black else "#000000"

        def on_step(direction):
            self.step_value(key, direction * delta, precision)

        num_box = LabVIEWNumericBox(
            parent, initial_val=self.current_vals.get(key, "0.00"),
            width=62, height=26, font=("Arial", 10, "bold"),
            has_stepper=True, pill_img=self.pill_img,
            on_step=on_step, bg="#8c97a8", entry_bg=box_bg, entry_fg=text_fg
        )
        self.entries[key] = num_box
        return num_box

    def on_pill_click(self, event, key, delta, precision):
        if event.y < 13:
            self.step_value(key, delta, precision)
        else:
            self.step_value(key, -delta, precision)

    def step_value(self, key, delta, precision):
        entry = self.entries.get(key)
        if not entry:
            return
        try:
            val = float(entry.get().replace(",", "."))
        except ValueError:
            val = 0.0
        val += delta
        entry.delete(0, tk.END)
        entry.insert(0, f"{val:.{precision}f}")

    def setup_ui(self):
        # 1. Pure Black Top Bar (32px) with Yellow Exit Button
        top_bar = tk.Frame(self, bg="#000000", height=32)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)

        exit_btn = tk.Button(
            top_bar, text="Exit", bg="#ffff00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=14, pady=1,
            cursor="hand2", command=self.on_exit_click
        )
        exit_btn.pack(side=tk.RIGHT, padx=6, pady=2)

        # Sub-header strip on #8c97a8 matching utility.py
        sub_header = tk.Frame(self, bg="#8c97a8", height=36)
        sub_header.pack(fill=tk.X, padx=8, pady=(4, 0))
        sub_header.pack_propagate(False)

        # Carona Power Logo on Far Left (matching utility.py subheader)
        self.logo_img = get_carona_logo(height=28)
        if self.logo_img:
            self.lbl_logo = tk.Label(sub_header, image=self.logo_img, bg="#8c97a8", bd=0)
            self.lbl_logo.pack(side=tk.LEFT, padx=(0, 8), pady=4)

        # Right spacer to balance the logo so title is perfectly centered
        tk.Frame(sub_header, bg="#8c97a8", width=67).pack(side=tk.RIGHT)

        # Drop Shadow Title: "Trasducer Info and Pressure Regulation"
        title_c = tk.Canvas(sub_header, height=36, bg="#8c97a8", highlightthickness=0)
        title_c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def draw_title(e=None):
            title_c.delete("all")
            w = title_c.winfo_width()
            cx = w // 2 or 460
            title_c.create_text(cx + 2, 18, text="Trasducer Info and Pressure Regulation", fill="#000000", font=("Arial", 16, "bold"))
            title_c.create_text(cx, 16, text="Trasducer Info and Pressure Regulation", fill="#ffff00", font=("Arial", 16, "bold"))

        title_c.bind("<Configure>", draw_title)

        # 2. Main Body Container
        body = tk.Frame(self, bg="#8c97a8")
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 8))

        # 4. Main 2x2 Grid Container (Left Column: GTN, Right Column: IMC)
        grid_container = tk.Frame(body, bg="#8c97a8")
        grid_container.pack(fill=tk.BOTH, expand=True)
        grid_container.columnconfigure(0, weight=1)
        grid_container.columnconfigure(1, weight=1)
        grid_container.rowconfigure(0, weight=1)
        grid_container.rowconfigure(1, weight=1)

        # ==========================================
        # TOP-LEFT PANEL: GTN Trasducer
        # ==========================================
        panel_tl = tk.Frame(grid_container, bg="#8c97a8", bd=1, relief=tk.GROOVE)
        panel_tl.grid(row=0, column=0, sticky="nsew", padx=6, pady=6, ipadx=6, ipady=6)

        tk.Label(
            panel_tl, text="GTN Trasducer", bg="#8c97a8", fg="#0033cc",
            font=("Arial", 14, "bold")
        ).pack(pady=(4, 10))

        tl_content = tk.Frame(panel_tl, bg="#8c97a8")
        tl_content.pack(expand=True)

        r1_tl = tk.Frame(tl_content, bg="#8c97a8")
        r1_tl.pack(fill=tk.X, pady=6)
        tk.Label(r1_tl, text="Min Pressure", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold"), width=12, anchor="e").pack(side=tk.LEFT, padx=(0, 4))
        self.make_stepper_input(r1_tl, "gtn_min_press", is_black=True, delta=0.5, precision=2).pack(side=tk.LEFT, padx=(0, 16))
        tk.Label(r1_tl, text="Min Volt", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold"), width=8, anchor="e").pack(side=tk.LEFT, padx=(0, 4))
        self.make_stepper_input(r1_tl, "gtn_min_volt", is_black=False, delta=1.0, precision=2).pack(side=tk.LEFT)

        r2_tl = tk.Frame(tl_content, bg="#8c97a8")
        r2_tl.pack(fill=tk.X, pady=6)
        tk.Label(r2_tl, text="Max Pressure", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold"), width=12, anchor="e").pack(side=tk.LEFT, padx=(0, 4))
        self.make_stepper_input(r2_tl, "gtn_max_press", is_black=True, delta=0.5, precision=2).pack(side=tk.LEFT, padx=(0, 16))
        tk.Label(r2_tl, text="Max Volt", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold"), width=8, anchor="e").pack(side=tk.LEFT, padx=(0, 4))
        self.make_stepper_input(r2_tl, "gtn_max_volt", is_black=False, delta=1.0, precision=2).pack(side=tk.LEFT)

        # ==========================================
        # TOP-RIGHT PANEL: IMC Trasducer
        # ==========================================
        panel_tr = tk.Frame(grid_container, bg="#8c97a8", bd=1, relief=tk.GROOVE)
        panel_tr.grid(row=0, column=1, sticky="nsew", padx=6, pady=6, ipadx=6, ipady=6)

        tk.Label(
            panel_tr, text="IMC Trasducer", bg="#8c97a8", fg="#d80099",
            font=("Arial", 14, "bold")
        ).pack(pady=(4, 10))

        tr_content = tk.Frame(panel_tr, bg="#8c97a8")
        tr_content.pack(expand=True)

        r1_tr = tk.Frame(tr_content, bg="#8c97a8")
        r1_tr.pack(fill=tk.X, pady=6)
        tk.Label(r1_tr, text="Min Pressure", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold"), width=12, anchor="e").pack(side=tk.LEFT, padx=(0, 4))
        self.make_stepper_input(r1_tr, "imc_min_press", is_black=True, delta=0.5, precision=2).pack(side=tk.LEFT, padx=(0, 16))
        tk.Label(r1_tr, text="Min Volt", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold"), width=8, anchor="e").pack(side=tk.LEFT, padx=(0, 4))
        self.make_stepper_input(r1_tr, "imc_min_volt", is_black=False, delta=1.0, precision=2).pack(side=tk.LEFT)

        r2_tr = tk.Frame(tr_content, bg="#8c97a8")
        r2_tr.pack(fill=tk.X, pady=6)
        tk.Label(r2_tr, text="Max Pressure", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold"), width=12, anchor="e").pack(side=tk.LEFT, padx=(0, 4))
        self.make_stepper_input(r2_tr, "imc_max_press", is_black=True, delta=0.5, precision=2).pack(side=tk.LEFT, padx=(0, 16))
        tk.Label(r2_tr, text="Max Volt", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold"), width=8, anchor="e").pack(side=tk.LEFT, padx=(0, 4))
        self.make_stepper_input(r2_tr, "imc_max_volt", is_black=False, delta=1.0, precision=2).pack(side=tk.LEFT)

        # ==========================================
        # BOTTOM-LEFT PANEL: GTN Pressure Regulation
        # ==========================================
        panel_bl = tk.Frame(grid_container, bg="#8c97a8", bd=1, relief=tk.GROOVE)
        panel_bl.grid(row=1, column=0, sticky="nsew", padx=6, pady=6, ipadx=6, ipady=6)

        tk.Label(
            panel_bl, text="GTN Pressure Regulation", bg="#8c97a8", fg="#000000",
            font=("Arial", 11, "bold")
        ).pack(pady=(4, 6))

        bl_content = tk.Frame(panel_bl, bg="#8c97a8")
        bl_content.pack(expand=True)

        hdr1_bl = tk.Frame(bl_content, bg="#8c97a8")
        hdr1_bl.pack(fill=tk.X)
        tk.Label(hdr1_bl, text="Default Pos [+0,01 bar]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=(18, 0))
        tk.Label(hdr1_bl, text="Default Neg [-0,01 bar]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack(side=tk.RIGHT, padx=(0, 4))

        ctrl1_bl = tk.Frame(bl_content, bg="#8c97a8")
        ctrl1_bl.pack(fill=tk.X, pady=(2, 6))
        self.make_stepper_input(ctrl1_bl, "gtn_pos_prec", is_black=True, delta=0.01, precision=2).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(ctrl1_bl, text="Precision", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True)
        self.make_stepper_input(ctrl1_bl, "gtn_neg_prec", is_black=False, delta=0.01, precision=2).pack(side=tk.RIGHT)

        hdr2_bl = tk.Frame(bl_content, bg="#8c97a8")
        hdr2_bl.pack(fill=tk.X, pady=(4, 0))
        tk.Label(hdr2_bl, text="Default Pos [+0,03 bar]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=(18, 0))
        tk.Label(hdr2_bl, text="Default Neg [-0,03 bar]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack(side=tk.RIGHT, padx=(0, 4))

        ctrl2_bl = tk.Frame(bl_content, bg="#8c97a8")
        ctrl2_bl.pack(fill=tk.X, pady=(2, 6))
        self.make_stepper_input(ctrl2_bl, "gtn_pos_comp", is_black=True, delta=0.01, precision=2).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(ctrl2_bl, text="Compensation", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True)
        self.make_stepper_input(ctrl2_bl, "gtn_neg_comp", is_black=False, delta=0.01, precision=2).pack(side=tk.RIGHT)

        # ==========================================
        # BOTTOM-RIGHT PANEL: IMC Pressure Regulation
        # ==========================================
        panel_br = tk.Frame(grid_container, bg="#8c97a8", bd=1, relief=tk.GROOVE)
        panel_br.grid(row=1, column=1, sticky="nsew", padx=6, pady=6, ipadx=6, ipady=6)

        tk.Label(
            panel_br, text="IMC Pressure Regulation", bg="#8c97a8", fg="#000000",
            font=("Arial", 11, "bold")
        ).pack(pady=(4, 6))

        br_content = tk.Frame(panel_br, bg="#8c97a8")
        br_content.pack(expand=True)

        hdr1_br = tk.Frame(br_content, bg="#8c97a8")
        hdr1_br.pack(fill=tk.X)
        tk.Label(hdr1_br, text="Default Pos [+0,01 bar]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=(18, 0))
        tk.Label(hdr1_br, text="Default Neg [-0,01 bar]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack(side=tk.RIGHT, padx=(0, 4))

        ctrl1_br = tk.Frame(br_content, bg="#8c97a8")
        ctrl1_br.pack(fill=tk.X, pady=(2, 6))
        self.make_stepper_input(ctrl1_br, "imc_pos_prec", is_black=True, delta=0.01, precision=2).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(ctrl1_br, text="Precision", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True)
        self.make_stepper_input(ctrl1_br, "imc_neg_prec", is_black=False, delta=0.01, precision=2).pack(side=tk.RIGHT)

        hdr2_br = tk.Frame(br_content, bg="#8c97a8")
        hdr2_br.pack(fill=tk.X, pady=(4, 0))
        tk.Label(hdr2_br, text="Default Pos [+0,03 bar]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=(18, 0))
        tk.Label(hdr2_br, text="Default Neg [-0,03 bar]", bg="#8c97a8", fg="#000000", font=("Arial", 8, "bold")).pack(side=tk.RIGHT, padx=(0, 4))

        ctrl2_br = tk.Frame(br_content, bg="#8c97a8")
        ctrl2_br.pack(fill=tk.X, pady=(2, 6))
        self.make_stepper_input(ctrl2_br, "imc_pos_comp", is_black=True, delta=0.01, precision=2).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(ctrl2_br, text="Compensation", bg="#8c97a8", fg="#000000", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True)
        self.make_stepper_input(ctrl2_br, "imc_neg_comp", is_black=False, delta=0.01, precision=2).pack(side=tk.RIGHT)

    def on_exit_click(self):
        GTNConfirmDialog(self, on_yes=self.on_confirm_yes, on_no=self.on_confirm_no)

    def on_confirm_yes(self):
        if self.app_ref:
            for k, entry in self.entries.items():
                self.app_ref.gtn_imc_values[k] = entry.get()
        self.destroy()

    def on_confirm_no(self):
        self.destroy()
