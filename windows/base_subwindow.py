import tkinter as tk
from widgets import get_carona_logo

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

        # Carona Power Logo on Far Left
        self.logo_img = get_carona_logo(height=26)
        if self.logo_img:
            self.lbl_logo = tk.Label(header_frame, image=self.logo_img, bg=self.COLOR_TOPBAR, bd=0)
            self.lbl_logo.pack(side=tk.LEFT, padx=(6, 8), pady=2)

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
