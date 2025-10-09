import emzed
import tadamz
import os
from PyQt5.QtWidgets import QFormLayout, QMessageBox, QPushButton, QVBoxLayout, QWidget

from tadamz_gui import gui_fields
from tadamz_gui.run_wf import RunWorkflowWindow


class ReanalysisWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Reanalyze workflow results")

        form_layout = QFormLayout()

        self.config_path_field = gui_fields.add_file_field(
            "Workflow config (*.yaml)",
            file_types="Workflow config (*.yaml)",
            form_layout=form_layout,
        )
        self.result_table_field = gui_fields.add_file_field(
            "Result table (*.table)",
            file_types="Table files (*.table)",
            form_layout=form_layout,
        )
        self.cal_results_table_field = gui_fields.add_file_field(
            "Optional: Calibration results table (*.table)",
            file_types="Table files (*.table)",
            form_layout=form_layout,
            optional=True,
        )

        self.reanalyze_button = QPushButton("Start reanalysis")
        self.reanalyze_button.clicked.connect(self.start_reanalysis)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.reanalyze_button)

        self.setLayout(layout)

    def check_all_fields(self):
        """Return True if all fields are valid (is_valid attribute is True)."""
        valid = True
        for field in [
            self.config_path_field,
            self.result_table_field,
            self.cal_results_table_field,
        ]:
            if hasattr(field, "is_valid") and not field.is_valid:
                valid = False
        return valid

    def start_reanalysis(self):
        if not self.check_all_fields():
            QMessageBox.warning(
                self,
                "Validation error",
                "Please make sure that paths are valid before starting the reanalysis.",
            )
            return

        self.config = tadamz.load_config(self.config_path_field.text())
        self.t = emzed.io.load_table(self.result_table_field.text())

        # Set to None first and then overwrite if provided
        self.t_cal_results = None
        self.calibrants_table = None
        self.sample_table = None

        # Check if calibration results table is provided
        if self.cal_results_table_field.text().strip():
            self.t_cal_results = emzed.io.load_table(
                self.cal_results_table_field.text()
            )

        # Load calibrants table if provided in config
        calibrants_table_path = self.config["input"].get("calibrants_table_path")
        if calibrants_table_path:
            if not os.path.exists(calibrants_table_path):
                QMessageBox.warning(
                    self,
                    "File not found",
                    f"Calibrants table path defined in config does not exist:\n{calibrants_table_path}",
                )
                return
            self.calibrants_table = emzed.io.load_excel(calibrants_table_path)

        # Load sample table if provided in config
        sample_table_path = self.config["input"].get("sample_table_path")
        if sample_table_path:
            if not os.path.exists(sample_table_path):
                QMessageBox.warning(
                    self,
                    "File not found",
                    f"Sample table path defined in config does not exist:\n{sample_table_path}",
                )
                return
            self.sample_table = emzed.io.load_excel(sample_table_path)

        self.run_window = RunWorkflowWindow(
            result_table=self.t,
            config=self.config,
            t_cal_results=self.t_cal_results,
            sample_table=self.sample_table,
            samples=None,
            peak_table=None,
            calibrants_table=self.calibrants_table,
        )
        self.run_window.show()
        self.close()
