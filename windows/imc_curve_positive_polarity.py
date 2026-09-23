import tkinter as tk
from .gtn_curve import VoltagePressureCurveWindow

class IMCCurvePositivePolarityWindow(VoltagePressureCurveWindow):
    """
    Dedicated IMC Curve Positive Polarity Window.
    Matches 'IMC Curve - Positive polarity' button on Utility Settings view.
    """
    def __init__(self, parent, app_ref=None):
        super().__init__(parent, curve_type="IMC_POS", app_ref=app_ref)
