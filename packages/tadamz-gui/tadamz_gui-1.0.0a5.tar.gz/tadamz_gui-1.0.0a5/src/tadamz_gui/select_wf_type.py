from PyQt5.QtWidgets import (
    QFormLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tadamz_gui import gui_fields
from tadamz_gui.setup_wf import SetupWFForm


class WFTypeWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Select workflow type to setup")

        form_layout = QFormLayout()
        self.combo_quant_type = gui_fields.add_combo_field(
            "Quantification type",
            [("Absolute", "absolute"), ("Relative", "relative")],
            form_layout=form_layout,
        )
        # Connect the signal to dynamically update normalization options
        self.combo_quant_type.currentIndexChanged.connect(
            self.update_normalization_options
        )

        # Add only temp option, as these are updated dynamically
        self.combo_normalization = gui_fields.add_combo_field(
            "Normalization",
            ["temp"],
            form_layout=form_layout,
        )
        self.update_normalization_options()

        self.button_setup_wf = QPushButton("Setup workflow")
        self.button_setup_wf.setDefault(True)
        self.button_setup_wf.clicked.connect(self.show_setup_WF_window)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.button_setup_wf)
        self.setLayout(layout)

    def update_normalization_options(self):
        """Update the options in combo_normalization based on the selected quantification type."""
        quant_type = self.combo_quant_type.currentData()
        self.combo_normalization.clear()  # Clear existing options

        if quant_type == "absolute":
            self.combo_normalization.addItem("Internal standard", "IS")
            self.combo_normalization.addItem("None", "none")
        else:
            self.combo_normalization.addItem("Internal standard", "IS")
            self.combo_normalization.addItem("Total ion count", "TIC")
            self.combo_normalization.addItem("PQN", "PQN")
            self.combo_normalization.addItem("None", "none")

    def show_setup_WF_window(self):
        quant_type = self.combo_quant_type.currentData()
        normalization = self.combo_normalization.currentData()
        wf_form = SetupWFForm(
            quant_type,
            normalization,
        )
        self.close()
        wf_form.show()
