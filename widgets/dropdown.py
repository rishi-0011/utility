import tkinter as tk

class LabVIEWDropdown(tk.Frame):
    """LabVIEW-style customized sunken dropdown combobox."""
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

