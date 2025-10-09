import os
import sys

import tadamz
import tadamz.track_changes
import yaml
from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from tadamz_gui.inspect_calibration import InspectCalibrationWindow


class RunWorkflowWindow(QWidget):
    def __init__(
        self,
        peak_table,
        samples,
        config,
        sample_table,
        calibrants_table=None,
        result_table=None,
        t_cal_results=None,
    ):
        super().__init__()

        self.peak_table = peak_table
        self.samples = samples
        self.config = config
        self.sample_table = sample_table
        self.calibrants_table = calibrants_table
        self.t = result_table
        self.t_cal_results = t_cal_results

        # allow redirection of outputs to GUI as well as saving to logfile
        # if results are reanalyzed (and thus result_table is provided), it will be appended to the logfile
        if self.t is not None:
            append = True
        else:
            append = False
        self.redirector = OutputRedirector(
            log_file_path=os.path.join(
                self.config["output"]["folder_path"], "workflow_terminal_log.log"
            ),
            append=append,
        )
        self.redirector.outputWritten.connect(self.update_terminal_output)
        # Connect the signal to dynamically update current step label
        self.redirector.currentStepChanged.connect(self.update_current_step_label)

        self.setWindowTitle("Run workflow")
        self.setMinimumWidth(600)

        # GUI contents
        layout_wf_steps = QVBoxLayout()

        processing_steps_label = ", ".join(self.config["processing_steps"])
        self.run_processing_button = QPushButton("Start processing")
        self.run_processing_button.clicked.connect(self.run_processing)
        layout_wf_steps.addWidget(self.run_processing_button)

        self.wf_steps_label = QLabel(f"Workflow steps: {processing_steps_label}")
        self.wf_steps_label.setAlignment(Qt.AlignCenter)
        layout_wf_steps.addWidget(self.wf_steps_label)

        if self.calibrants_table is not None or t_cal_results is not None:
            self.run_calibration_button = QPushButton("Run calibration")
            self.run_calibration_button.setEnabled(False)
            self.run_calibration_button.clicked.connect(self.run_calibration)
            layout_wf_steps.addWidget(self.run_calibration_button)

            self.inspect_calibration_button = QPushButton("Inspect calibration")
            self.inspect_calibration_button.setEnabled(False)
            self.inspect_calibration_button.clicked.connect(self.inspect_calibration)
            layout_wf_steps.addWidget(self.inspect_calibration_button)

            self.run_quantification_button = QPushButton("Run quantification")
            self.run_quantification_button.setEnabled(False)
            self.run_quantification_button.clicked.connect(self.run_quantification)
            layout_wf_steps.addWidget(self.run_quantification_button)

        self.inspect_table_button = QPushButton("Inspect table")
        self.inspect_table_button.clicked.connect(self.inspect_table)
        self.inspect_table_button.setEnabled(False)

        self.export_table_button = QPushButton("Export table as CSV")
        self.export_table_button.clicked.connect(self.export_table)
        self.export_table_button.setEnabled(False)

        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)

        # Create and add status bar
        self.status_bar = QStatusBar()
        self.busy_indicator_label = QLabel()
        self.current_step_label = QLabel("Ready")
        self.update_busy_indicator(False)
        self.status_bar.addPermanentWidget(self.current_step_label)
        self.status_bar.addPermanentWidget(self.busy_indicator_label)

        layout_general_buttons = QHBoxLayout()
        layout_general_buttons.addWidget(self.inspect_table_button)
        layout_general_buttons.addWidget(self.export_table_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_wf_steps)
        main_layout.addWidget(self.terminal_output)
        main_layout.addLayout(layout_general_buttons)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)

        self.enable_usable_buttons()

    def update_busy_indicator(self, busy):
        color = "orange" if busy else "green"

        pixmap = QPixmap(20, 20)
        pixmap.fill(QColor("transparent"))

        painter = QPainter(pixmap)
        painter.setBrush(QColor(color))
        painter.setPen(QColor(color))
        painter.drawEllipse(0, 0, 20, 20)
        painter.end()

        self.busy_indicator_label.setPixmap(pixmap)

    def run_processing(self):
        # Save config before running workflow
        self.save_results("config")

        self.worker_thread = WorkerThread(
            function_to_run=tadamz.run_workflow,
            redirector=self.redirector,
            parent=self,
            args=[
                self.peak_table,
                self.samples,
                self.config,
                None,  # t_cal
                self.sample_table,
            ],
        )

        def _on_workflow_finish():
            if not self.worker_thread.error:
                self.t = self.worker_thread.func_return

                message = "Finished processing. Saving results."
                self.print_to_GUI_terminal(message)
                self.status_bar.showMessage(message)

                self.save_results("result_table")
            else:
                self.display_error(str(self.worker_thread.error))

            self.enable_usable_buttons()

        self.worker_thread.finished.connect(_on_workflow_finish)
        self.worker_thread.start()

    def run_calibration(self):
        self.worker_thread = WorkerThread(
            function_to_run=tadamz.run_calibration,
            redirector=self.redirector,
            parent=self,
            args=[
                self.t,
                self.calibrants_table,
                self.sample_table,
                self.config,
            ],
        )

        def _on_calibration_finish():
            if not self.worker_thread.error:
                self.t_cal_results = self.worker_thread.func_return

                message = "Finished calibration. Saving calibration."
                self.print_to_GUI_terminal(message)
                self.status_bar.showMessage(message)

                self.save_results("calibration_table")
            else:
                self.display_error(str(self.worker_thread.error))

            self.enable_usable_buttons()

        self.worker_thread.finished.connect(_on_calibration_finish)
        self.worker_thread.start()

    def inspect_calibration(self):
        self.inspect_calibration_window = InspectCalibrationWindow(
            self.t_cal_results, self
        )
        self.inspect_calibration_window.show()

    def run_quantification(self):
        step_id = self.config["postprocessings"].index("quantification")

        self.worker_thread = WorkerThread(
            function_to_run=tadamz.postprocess_result_table,
            redirector=self.redirector,
            parent=self,
            args=[
                self.t,
                self.config,
                step_id,
                self.t_cal_results,
            ],
        )

        def _on_postprocessing_finish():
            if not self.worker_thread.error:
                self.t = self.worker_thread.func_return

                message = "Finished quantification. Saving results."
                self.print_to_GUI_terminal(message)
                self.status_bar.showMessage(message)

                self.save_results("result_table")
            else:
                self.display_error(str(self.worker_thread.error))

            self.enable_usable_buttons()

        self.worker_thread.finished.connect(_on_postprocessing_finish)
        self.worker_thread.start()

    def display_error(self, error_message):
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

    def inspect_table(self):
        if self.t is None:
            self.status_bar.showMessage("No table to inspect.")
            return

        id_before = self.t.unique_id
        tadamz.track_changes.inspect_with_track_changes(self.t)
        changed_rows = self.t.meta_data.get("changed_rows", [])
        id_after = self.t.unique_id

        # check if rows have changed and if there are any postprocessing steps to run
        if len(changed_rows) > 0 and self.config.get("postprocessings"):
            message = (
                f"Running post-processing due to {len(changed_rows)} modified rows."
            )
            self.print_to_GUI_terminal(message)
            self.status_bar.showMessage(message)

            # in case pqn is used, all rows have to be post-processed
            pqn_present = "pqn" in self.config["postprocessings"]
            postprocessing1_present = (
                "postprocessing1" in self.config["postprocessings"]
            )

            if postprocessing1_present:
                callback = self.pqn_postprocessing if pqn_present else None

                step_id = self.config["postprocessings"].index("postprocessing1")
                self.run_postprocessing(
                    postprocess_id=step_id,
                    process_only_tracked_changes=True,
                    finished_callback=callback,
                )

            # only pqn postprocessing
            else:
                if pqn_present:
                    self.pqn_postprocessing()

            if "quantification" in self.config["postprocessings"]:
                QMessageBox.information(
                    self,
                    "Notice",
                    "Rows have been modified and post-processing steps are running."
                    "Please consider re-running quantification and/or calibration steps.",
                )

            # table is saved during run_postprocessing (also in case of pqn)

        # in case no postprocessings have to be run, but table was still modified
        # Todo: id can also change when no changes have been made since changed_rows in meta data becomes empty after inspection
        elif id_before != id_after:
            message = "Result table saved."
            self.status_bar.showMessage(message)
            self.print_to_GUI_terminal(message)
            self.save_results("result_table")

    def pqn_postprocessing(self):
        pqn_index = self.config["postprocessings"].index("pqn")

        message = "Re-running PQ normalization."
        self.print_to_GUI_terminal(message)
        self.status_bar.showMessage(message)

        self.run_postprocessing(pqn_index, process_only_tracked_changes=False)

    def run_postprocessing(
        self, postprocess_id, process_only_tracked_changes, finished_callback=None
    ):
        self.worker_thread = WorkerThread(
            function_to_run=tadamz.postprocess_result_table,
            redirector=self.redirector,
            parent=self,
            args=[
                self.t,
                self.config,
                postprocess_id,
                None,  # calibration_table
                process_only_tracked_changes,
            ],
        )

        def _on_postprocessing_finish():
            if not self.worker_thread.error:
                self.t = self.worker_thread.func_return

                message = "Finished post-processing. Saving results."
                self.print_to_GUI_terminal(message)
                self.status_bar.showMessage(message)

                self.save_results("result_table")
            else:
                self.display_error(str(self.worker_thread.error))

            if finished_callback:
                finished_callback()

            self.enable_usable_buttons()

        self.worker_thread.finished.connect(_on_postprocessing_finish)
        self.worker_thread.start()

    def save_results(self, objects_to_save):
        folder = self.config["output"]["folder_path"]
        base_filename = self.config["output"]["base_filename"]

        def _save_result_table():
            if self.t is not None:
                self.t.save(
                    os.path.join(folder, base_filename + "_result_table.table"),
                    overwrite=True,
                )

        def _save_calibration_results_table():
            if self.t_cal_results is not None:
                self.t_cal_results.save(
                    os.path.join(folder, base_filename + "_calibration_table.table"),
                    overwrite=True,
                )

        def _save_config():
            with open(
                os.path.join(folder, base_filename + "_config.yaml"), "w"
            ) as file:
                yaml.dump(self.config, file)

        if "result_table" in objects_to_save:
            _save_result_table()
        if "calibration_table" in objects_to_save:
            _save_calibration_results_table()
        if "config" in objects_to_save:
            _save_config()

    def export_table(self):
        if self.t is not None:
            options = QFileDialog.Options()
            file, _ = QFileDialog.getSaveFileName(
                self,
                "Export results as CSV",
                os.path.join(
                    self.config["output"]["folder_path"], "workflow_results.csv"
                ),
                filter="CSV file (*.csv)",
                options=options,
            )

            if file:
                try:
                    self.t.save_csv(file, overwrite=True)
                    self.status_bar.showMessage(f"Table exported to: {file}")
                except Exception as e:
                    self.display_error(f"Could not export table: {e}")
        else:
            self.status_bar.showMessage("No table to export.")

    @pyqtSlot(str)
    def update_terminal_output(self, text):
        cursor = self.terminal_output.textCursor()
        cursor.movePosition(cursor.End)
        if "\r" in text:
            cursor.select(cursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()
        cursor.insertText(text)
        self.terminal_output.setTextCursor(cursor)
        self.terminal_output.ensureCursorVisible()

    @pyqtSlot(str)
    def update_current_step_label(self, step):
        self.current_step_label.setText(f"Running step: {step}")

    def print_to_GUI_terminal(self, text):
        self.redirector.write(text + "\n")

    def enable_usable_buttons(self):
        if self.t is not None:
            self.run_processing_button.setEnabled(False)
            self.inspect_table_button.setEnabled(True)
            self.export_table_button.setEnabled(True)

            # calibration table is only provided for abs quant workflowƒs
            if self.calibrants_table is not None:
                # this column is only present if normalization (by IS) was run
                if "normalized_area_chromatogram" in self.t.col_names:
                    self.run_calibration_button.setEnabled(True)
                # in case of no IS and thus no normalization, we run calibration after peak extraction
                elif "normalize_peaks" not in self.config["processing_steps"]:
                    self.run_calibration_button.setEnabled(True)
        else:
            self.run_processing_button.setEnabled(True)

        if self.t_cal_results is not None:
            self.inspect_calibration_button.setEnabled(True)
            self.run_quantification_button.setEnabled(True)

    def disable_all_buttons(self):
        self.run_processing_button.setEnabled(False)
        self.inspect_table_button.setEnabled(False)
        self.export_table_button.setEnabled(False)

        if self.calibrants_table is not None or self.t_cal_results is not None:
            self.run_calibration_button.setEnabled(False)
            self.inspect_calibration_button.setEnabled(False)
            self.run_quantification_button.setEnabled(False)

    def closeEvent(self, event):
        self.redirector.close()
        event.accept()


class OutputRedirector(QObject):
    outputWritten = pyqtSignal(str)
    currentStepChanged = pyqtSignal(str)

    def __init__(self, log_file_path=None, append=False):
        super().__init__()
        self.buffer = ""
        self.log_file_path = log_file_path
        self.log_file = None
        if self.log_file_path:
            open_mode = "a" if append else "w"
            self.log_file = open(self.log_file_path, open_mode, encoding="utf-8")

    def write(self, text):
        self.buffer += text
        if "\r" in text or "\n" in text:
            self.flush()

        # Check for current processing step
        if "Current processing step:" in text:
            step = text.split("Current processing step: ")[-1].strip()
            self.currentStepChanged.emit(step)

    def flush(self):
        self.outputWritten.emit(self.buffer)
        if self.log_file:
            self.log_file.write(self.buffer)
            self.log_file.flush()
        self.buffer = ""

    def close(self):
        if self.log_file:
            self.log_file.close()
            self.log_file = None


class WorkerThread(QThread):
    def __init__(self, function_to_run, redirector, parent, args=None):
        super().__init__()
        self.function_to_run = function_to_run
        self.redirector = redirector
        self.args = args
        self.error = None
        self.func_return = None
        self.parent = parent

    def run(self):
        self.parent.update_busy_indicator(True)
        self.parent.disable_all_buttons()

        # Redirect output
        old_stdout = sys.stdout
        sys.stdout = self.redirector

        try:
            self.func_return = self.function_to_run(*self.args)
        except Exception as e:
            self.error = e
        finally:
            # Redirect output back
            sys.stdout = old_stdout

            self.parent.update_busy_indicator(False)
            self.parent.current_step_label.setText("Ready")
