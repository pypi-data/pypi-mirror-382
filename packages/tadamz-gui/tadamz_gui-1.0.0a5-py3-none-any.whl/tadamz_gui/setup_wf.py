import os

import emzed
import tadamz
import yaml
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from tadamz_gui import gui_fields, processing_steps
from tadamz_gui.run_wf import RunWorkflowWindow


class SetupWFForm(QDialog):
    def __init__(self, quant_type, normalization):
        super().__init__()

        self.setWindowTitle(
            f"Setup workflow (quantification: {quant_type}, normalization: {normalization})"
        )
        self.resize(700, self.height())

        self.quant_type = quant_type
        self.normalization = normalization

        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Add tabs
        self.add_input_tab()
        self.add_output_tab()
        self.add_peak_extraction_tab()
        self.add_peak_classification_tab()
        self.add_coelution_tab()
        self.add_check_qualifiers_tab()
        if quant_type == "absolute":
            self.add_calibration_tab()

        # Add tabs to the main layout
        self.layout.addWidget(self.tabs)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load config")
        self.load_button.clicked.connect(self.load_config)
        self.save_button = QPushButton("Save config")
        self.save_button.clicked.connect(self.save_config)
        self.run_workflow_button = QPushButton("Run workflow")
        self.run_workflow_button.setDefault(True)
        self.run_workflow_button.clicked.connect(self.run_workflow)
        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.run_workflow_button)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

    def add_input_tab(self):
        form_layout = QFormLayout()
        self.config__input__target_table_path = gui_fields.add_file_field(
            "Target table (.xlsx)",
            file_types="Excel tables (*.xlsx)",
            form_layout=form_layout,
        )
        self.config__input__sample_table_path = gui_fields.add_file_field(
            "Sample table (.xlsx)",
            file_types="Excel tables (*.xlsx)",
            form_layout=form_layout,
        )
        if self.quant_type == "absolute":
            self.config__input__calibrants_table_path = gui_fields.add_file_field(
                "Calibrants table (.xlsx)",
                file_types="Excel tables (*.xlsx)",
                form_layout=form_layout,
            )
        self.config__input__sample_folder_path = gui_fields.add_directory_field(
            "Sample folder",
            tooltip="Folder where the samples defined in the sample table are located",
            form_layout=form_layout,
        )
        self.tabs.addTab(self.create_tab_widget(form_layout), "Input")

    def add_output_tab(self):
        form_layout = QFormLayout()
        self.config__output__folder_path = gui_fields.add_directory_field(
            "Output folder",
            tooltip="Folder where results will be saved (incl. config)",
            form_layout=form_layout,
        )
        self.config__output__base_filename = gui_fields.add_text_field(
            "Base filename",
            tooltip="Base filename used as prefix for all output files. No need to add suffix or file extension.",
            default="workflow",
            form_layout=form_layout,
        )
        self.tabs.addTab(self.create_tab_widget(form_layout), "Output")

    def add_peak_extraction_tab(self):
        form_layout = QFormLayout()
        self.config__extract_peaks__ms_data_type = gui_fields.add_combo_field(
            "MS data type",
            [("Spectra", "Spectra"), ("Chromatograms only", "MS_Chromatogram")],
            default="MS_Chromatogram",
            form_layout=form_layout,
        )
        self.config__extract_peaks__integration_algorithm = gui_fields.add_combo_field(
            "Integration algorithm",
            [
                ("Linear", "linear"),
                ("EMG", "emg"),
                ("Savitzky-Golay", "sgolay"),
                ("Asym. Gauss", "asym_gauss"),
                ("No integration", "no_integration"),
            ],
            default="emg",
            form_layout=form_layout,
        )
        self.config__extract_peaks__mz_tol_abs = gui_fields.add_float_field(
            "Absolute m/z tolerance (Th)",
            default=0.3,
            tooltip="Unit: Th",
            form_layout=form_layout,
        )
        self.config__extract_peaks__mz_tol_rel = gui_fields.add_float_field(
            "Relative m/z tolerance (ppm)",
            default=0.0,
            tooltip="Unit: ppm",
            form_layout=form_layout,
        )
        self.config__extract_peaks__precursor_mz_tol = gui_fields.add_float_field(
            "Precursor absolute m/z tolerance",
            default=0.3,
            tooltip="Only required for MS2/MRM",
            form_layout=form_layout,
        )
        self.config__extract_peaks__subtract_baseline = gui_fields.add_checkbox_field(
            "Subtract baseline", form_layout=form_layout
        )
        self.tabs.addTab(self.create_tab_widget(form_layout), "Peak extraction")

    def add_peak_classification_tab(self):
        form_layout = QFormLayout()
        self.run_peak_classification = gui_fields.add_checkbox_field(
            "Classify peak quality",
            tooltip="Enable to run the peak classification step.",
            default=True,
            form_layout=form_layout,
        )

        self.run_peak_classification.stateChanged.connect(
            lambda state: self.toggle_fields(state, "config__classify_peaks")
        )

        self.config__classify_peaks__scoring_model = gui_fields.add_combo_field(
            "Scoring model",
            [("Random forest classification", "random_forest_classification")],
            default="random_forest_classification",
            form_layout=form_layout,
        )
        self.config__classify_peaks__scoring_model_params__classifier_name = (
            gui_fields.add_combo_field(
                "Classifier name",
                [
                    ("SRM peak classifier", "srm_peak_classifier"),
                    ("UPLC MS1 peak classifier", "uplc_MS1_QEx_peak_classifier"),
                ],
                default="srm_peak_classifier",
                form_layout=form_layout,
            )
        )
        self.tabs.addTab(self.create_tab_widget(form_layout), "Peak classification")

    def add_coelution_tab(self):
        form_layout = QFormLayout()
        self.run_coelution_analysis = gui_fields.add_checkbox_field(
            "Determine co-elution",
            tooltip="Enable to run the co-elution analysis step.",
            default=True,
            form_layout=form_layout,
        )

        self.run_coelution_analysis.stateChanged.connect(
            lambda state: self.toggle_fields(state, "config__coeluting_peaks")
        )

        self.config__coeluting_peaks__only_use_ref_peaks = gui_fields.add_checkbox_field(
            "Only use reference peaks",
            default=True,
            tooltip="If true, only target(s) flagged with is_coelution_ref_peak will be used.",
            form_layout=form_layout,
        )

        self.tabs.addTab(self.create_tab_widget(form_layout), "Co-elution analysis")

    def add_check_qualifiers_tab(self):
        form_layout = QFormLayout()
        self.check_qualifiers = gui_fields.add_checkbox_field(
            "Check quantifier/qualifier ratios",
            tooltip="Requires specific columns in the target table.",
            form_layout=form_layout,
        )
        self.tabs.addTab(self.create_tab_widget(form_layout), "Check qualifiers")

    def add_calibration_tab(self):
        form_layout = QFormLayout()
        self.config__calibrate__calibration_model_name = gui_fields.add_combo_field(
            "Calibration model",
            [("Linear", "linear"), ("Quadratic", "quadratic")],
            default="linear",
            form_layout=form_layout,
        )
        self.config__calibrate__alpha_model = gui_fields.add_float_field(
            "Alpha value for model", default=0.05, form_layout=form_layout
        )
        self.config__calibrate__alpha_lodq = gui_fields.add_float_field(
            "Alpha value for LODQ", default=0.00135, form_layout=form_layout
        )
        self.config__calibrate__calibration_weight = gui_fields.add_combo_field(
            "Calibration weight",
            ["none", "1/x", "1/x^2", "1/s^2"],
            default="1/x^2",
            form_layout=form_layout,
        )

        self.tabs.addTab(self.create_tab_widget(form_layout), "Calibration")

    def toggle_fields(self, state, attribute_startswith):
        for attr_name in dir(self):
            if attr_name.startswith(attribute_startswith):
                field = getattr(self, attr_name)
                if hasattr(field, "setEnabled"):
                    field.setEnabled(state)

    def create_tab_widget(self, layout):
        """Wrap a QFormLayout in a QWidget for use in tabs."""
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def load_config(self):
        """Load parameters from a YAML file and populate the form fields."""
        config_path, _ = QFileDialog.getOpenFileName(
            self, "Load config", "", "Workflow config (*.yaml)"
        )
        if not config_path:
            return  # User canceled the dialog

        try:
            config_dict = tadamz.load_config(config_path)

            # Flatten the nested YAML structure
            flat_config = flatten_config(config_dict)

            # Populate form fields
            for key, value in flat_config.items():
                field = getattr(self, key, None)
                if field:
                    if isinstance(field, QLineEdit):
                        field.setText(str(value))
                    elif isinstance(field, QComboBox):
                        index = field.findData(value)
                        if index != -1:
                            field.setCurrentIndex(index)
                    elif isinstance(field, QCheckBox):
                        field.setChecked(bool(value))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load config: {e}")

        # Check for processing steps that should be enabled
        ps = config_dict.get("processing_steps", [])
        self.check_qualifiers.setChecked("check_qualifier_peaks" in ps)
        self.run_peak_classification.setChecked("classify_peaks" in ps)
        self.run_coelution_analysis.setChecked("coeluting_peaks" in ps)

    def save_config(self):
        """Save the current form field values to a YAML file."""
        config_path, _ = QFileDialog.getSaveFileName(
            self, "Save config", "", "Workflow config (*.yaml)"
        )
        if not config_path:
            return  # User canceled the dialog

        config = self.create_config_dict()

        # Save to YAML
        with open(config_path, "w") as file:
            yaml.dump(config, file)

        QMessageBox.information(self, "Success", f"Config saved to: {config_path}")

    def check_all_fields(self):
        """Return True if all fields are valid (is_valid attribute is True)."""
        prefix = "config__"
        valid = True
        for attr in dir(self):
            if attr.startswith(prefix):
                field = getattr(self, attr)
                if hasattr(field, "is_valid"):
                    if not field.is_valid:
                        valid = False
        return valid

    def run_workflow(self):
        if self.check_all_fields():
            config = self.create_config_dict()

            # load tables
            peak_table = tadamz.in_out.load_targets_table(
                self.config__input__target_table_path.text()
            )
            sample_table = emzed.io.load_excel(
                self.config__input__sample_table_path.text()
            )
            if self.quant_type == "absolute":
                calibrants_table = emzed.io.load_excel(
                    self.config__input__calibrants_table_path.text()
                )
            else:
                calibrants_table = None

            # get list of filenames from sample table
            filenames = sample_table.filename.to_list()
            samples = [
                os.path.join(self.config__input__sample_folder_path.text(), filename)
                for filename in filenames
            ]

            # run workflow
            self.run_window = RunWorkflowWindow(
                peak_table,
                samples,
                config,
                sample_table,
                calibrants_table,
            )
            self.run_window.show()
            self.close()  # close SetupWFForm

        else:
            QMessageBox.warning(
                self,
                "Validation error",
                "Please fill in all required fields and make sure that paths are valid before running the workflow.",
            )

    def add_processing_steps(self, config):
        """Add processing steps to the configuration dictionary"""

        # Workaround until sample_types have default values
        if self.quant_type == "absolute":
            config["calibrate"]["sample_types"] = dict()
            config["calibrate"]["sample_types"]["blank"] = "Blank"
            config["calibrate"]["sample_types"]["qc"] = "QC"
            config["calibrate"]["sample_types"]["sample"] = "Unknown"
            config["calibrate"]["sample_types"]["calibrant"] = "Calibrant"

        # workflow type-specific processing steps
        if self.quant_type == "absolute":
            if self.normalization == "IS":
                config = processing_steps.add_abs_quant_is(config)
            elif self.normalization == "none":
                config = processing_steps.add_abs_quant_no_norm(config)

        if self.quant_type == "relative":
            if self.normalization == "none":
                config = processing_steps.add_rel_quant_no_norm(config)
            elif self.normalization == "TIC":
                config = processing_steps.add_rel_quant_TIC(config)
            elif self.normalization == "PQN":
                config = processing_steps.add_rel_quant_PQN(config)
            elif self.normalization == "IS":
                config = processing_steps.add_rel_quant_IS(config)

        # check which steps are enabled
        if self.check_qualifiers.isChecked():
            config = processing_steps.add_step_to_processing_and_postprocessing(
                config, "check_qualifier_peaks"
            )
        if self.run_peak_classification.isChecked():
            config = processing_steps.add_step_to_processing_and_postprocessing(
                config, "classify_peaks"
            )
        if self.run_coelution_analysis.isChecked():
            config = processing_steps.add_step_to_processing_and_postprocessing(
                config, "coeluting_peaks"
            )

        return config

    def create_config_dict(self):
        """Create a configuration dictionary from the form fields and add the processing steps."""

        separator = "__"
        prefix = "config"

        attribute_names = [a for a in dir(self) if a.startswith(prefix + separator)]

        config = {}
        for atr in attribute_names:
            field = getattr(self, atr)
            if isinstance(field, QLineEdit):
                value = field.text()
                # Check if the field has a QDoubleValidator
                if isinstance(field.validator(), QDoubleValidator):
                    value = float(value)
            elif isinstance(field, QComboBox):
                value = field.currentData()
            elif isinstance(field, QCheckBox):
                value = field.isChecked()

            parts = atr.split(separator)
            current = config
            for part in parts[1:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value

        # Add processing steps
        config = self.add_processing_steps(config)

        return config


def flatten_config(config_dict, prefix="config", separator="__"):
    """Flatten a nested dictionary into a single-level dictionary with keys separated by `separator`."""
    result = {}
    for key, value in config_dict.items():
        new_key = f"{prefix}{separator}{key}"
        if isinstance(value, dict):
            result.update(flatten_config(value, new_key, separator))
        else:
            result[new_key] = value
    return result
