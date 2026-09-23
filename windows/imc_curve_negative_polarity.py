import tkinter as tk
from .gtn_curve import VoltagePressureCurveWindow

class IMCCurveNegativePolarityWindow(VoltagePressureCurveWindow):
    """
    Dedicated IMC Curve Negative Polarity Window.
    Matches 'IMC Curve - Negative polarity' button on Utility Settings view.
    """
    def __init__(self, parent, app_ref=None):
        super().__init__(parent, curve_type="IMC_NEG", app_ref=app_ref)
