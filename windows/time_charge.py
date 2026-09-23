import tkinter as tk
import os
import base64
from PIL import Image, ImageTk
from widgets import (
    LabVIEWNumericBox,
    get_carona_logo,
    get_info_bubble_image,
    INFO_BUBBLE_B64,
)

class TimeChargeConfirmDialog(tk.Toplevel):
    def __init__(self, parent, on_yes, on_no):
        super().__init__(parent)
        self.parent = parent
        self.on_yes_cb = on_yes
        self.on_no_cb = on_no
        self.title("Time Charge")
        self.transient(parent)
        self.resizable(False, False)
        self.configure(bg="#8c97a8")
        self.geometry("480x190")

        # Center on parent
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        x = px + max(0, (pw - 480) // 2)
        y = py + max(0, (ph - 190) // 2)
        self.geometry(f"480x190+{x}+{y}")

        self.setup_ui()
        self.grab_set()

    def setup_ui(self):
        content_f = tk.Frame(self, bg="#8c97a8")
        content_f.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))

        # 1. Left Info Bubble Icon
        self.icon_img = get_info_bubble_image(62)

        if self.icon_img:
            lbl_icon = tk.Label(content_f, image=self.icon_img, bg="#8c97a8", bd=0)
            lbl_icon.pack(side=tk.LEFT, padx=(4, 18), anchor="n")
        else:
            # Fallback canvas speech bubble
            icon_c = tk.Canvas(content_f, width=54, height=54, bg="#8c97a8", highlightthickness=0)
            icon_c.pack(side=tk.LEFT, padx=(4, 18), anchor="n")
            icon_c.create_oval(2, 2, 50, 50, fill="#ffffff", outline="#202020", width=1.5)
            icon_c.create_text(26, 26, text="i", fill="#0000cc", font=("Georgia", 22, "bold italic"))

        # 2. Text Container
        text_f = tk.Frame(content_f, bg="#8c97a8")
        text_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            text_f, text="Time Charge", bg="#8c97a8", fg="#000000",
            font=("Arial", 11, "bold"), anchor="w"
        ).pack(fill=tk.X, pady=(2, 6))

        tk.Label(
            text_f, text="Do you want to overwrite the Max Time Charge Value?",
            bg="#8c97a8", fg="#000000", font=("Arial", 10, "bold"),
            wraplength=310, justify="left", anchor="w"
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
# Time Charge Window ("Max Time Charge Value" - One-to-One matching reference)
# ==============================================================================
class TimeChargeWindow(tk.Toplevel):
    def __init__(self, parent, app_ref=None):
        super().__init__(parent)
        self.parent = parent
        self.app_ref = app_ref
        self.title("Max Time Charge Value")
        self.resizable(True, True)
        self.minsize(680, 360)
        self.configure(bg="#8c97a8")

        # Initial values from app state or default 90
        self.last_charge_time = getattr(self.app_ref, "max_charge_time", 90) if self.app_ref else 90

        self.setup_ui()
        self.center_on_parent(740, 380)

        # Intercept window close button
        self.protocol("WM_DELETE_WINDOW", self.on_exit_click)

    def center_on_parent(self, width=740, height=380):
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
        # 1. Pure Black Top Bar (32px) with Yellow Exit Button
        top_bar = tk.Frame(self, bg="#000000", height=32)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)

        exit_btn = tk.Button(
            top_bar, text="Exit", bg="#ffff00", fg="black",
            font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=16, pady=1,
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

        # 3. 3D Drop-Shadow Title: "Max Charge Time"
        title_c = tk.Canvas(sub_header, height=36, bg="#8c97a8", highlightthickness=0)
        title_c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def draw_title(e=None):
            title_c.delete("all")
            w = title_c.winfo_width()
            cx = w // 2 or 350
            title_c.create_text(cx + 2, 20, text="Max Charge Time", fill="#111111", font=("Arial", 18, "bold"))
            title_c.create_text(cx, 18, text="Max Charge Time", fill="#ffff00", font=("Arial", 18, "bold"))

        title_c.bind("<Configure>", draw_title)

        # 2. Main Body Container
        body = tk.Frame(self, bg="#8c97a8")
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        # 4. Controls Frame: Two Columns
        controls_f = tk.Frame(body, bg="#8c97a8")
        controls_f.pack(fill=tk.X, expand=True, pady=10)
        controls_f.columnconfigure(0, weight=1)
        controls_f.columnconfigure(1, weight=1)

        # LEFT COLUMN: Last Max Charge Time [s]
        col_left = tk.Frame(controls_f, bg="#8c97a8")
        col_left.grid(row=0, column=0, sticky="n")

        tk.Label(
            col_left, text="Last Max Charge Time [s]", bg="#8c97a8", fg="#0a1018",
            font=("Arial", 10, "bold")
        ).pack(pady=(0, 8))

        box_last = tk.Frame(col_left, bg="#000000", bd=2, relief=tk.SUNKEN, width=62, height=26)
        box_last.pack()
        box_last.pack_propagate(False)

        self.lbl_last = tk.Label(
            box_last, text=str(self.last_charge_time), bg="#000000", fg="#ffffff",
            font=("Arial", 10, "bold"), anchor="center"
        )
        self.lbl_last.pack(fill=tk.BOTH, expand=True)

        # RIGHT COLUMN: New Max Charge Time [s]
        col_right = tk.Frame(controls_f, bg="#8c97a8")
        col_right.grid(row=0, column=1, sticky="n")

        tk.Label(
            col_right, text="New Max Charge Time [s]", bg="#8c97a8", fg="#0a1018",
            font=("Arial", 10, "bold")
        ).pack(pady=(0, 8))

        def on_step_new(direction):
            self.step_value(direction)

        self.entry_new = LabVIEWNumericBox(
            col_right, initial_val=str(self.last_charge_time),
            width=62, height=26, font=("Arial", 10, "bold"),
            on_step=on_step_new, bg="#8c97a8"
        )
        self.entry_new.pack()

    def step_value(self, delta):
        try:
            val = int(self.entry_new.get())
        except ValueError:
            val = 90
        val = max(1, val + delta)
        self.entry_new.set(str(val))

    def on_exit_click(self):
        TimeChargeConfirmDialog(self, on_yes=self.on_confirm_yes, on_no=self.on_confirm_no)

    def on_confirm_yes(self):
        try:
            new_val = int(self.entry_new.get())
        except ValueError:
            new_val = self.last_charge_time
        if self.app_ref:
            self.app_ref.max_charge_time = new_val
        self.destroy()

    def on_confirm_no(self):
        self.destroy()
