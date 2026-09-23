import tkinter as tk
from .gtu_curve import GTUCurveWindow

class MSGCurveWindow(GTUCurveWindow):
    """
    Dedicated 1:1 LabVIEW Window for MSG Curves (Positive & Negative Polarity).
    Inherits authentic table, stepper boxes, graphic canvas, and Carona Power branding.
    """
    def __init__(self, parent, polarity="Positive", app_ref=None):
        pol_str = str(polarity).strip()
        if "neg" in pol_str.lower():
            self.polarity = "Negative"
        else:
            self.polarity = "Positive"
        self.state_key = f"msg_curve_{self.polarity.lower()}"
        self.display_title = f"Voltage vs Sphere Distance ({self.polarity} Polarity)"
        super().__init__(parent, app_ref=app_ref, state_key=self.state_key)
        self.title(f"Gap Distance Setting - {self.polarity} Polarity")



class MSGCurvePositivePolarityWindow(MSGCurveWindow):
    """
    Dedicated MSG Curve Positive Polarity Window.
    Matches 'MSG Curve - Positive polarity' button on Utility Settings view.
    """
    def __init__(self, parent, app_ref=None):
        super().__init__(parent, polarity="Positive", app_ref=app_ref)
