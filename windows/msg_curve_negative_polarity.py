import tkinter as tk
from .msg_curve_positive_polarity import MSGCurveWindow

class MSGCurveNegativePolarityWindow(MSGCurveWindow):
    """
    Dedicated MSG Curve Negative Polarity Window.
    Matches 'MSG Curve - Negative polarity' button on Utility Settings view.
    """
    def __init__(self, parent, app_ref=None):
        super().__init__(parent, polarity="Negative", app_ref=app_ref)
