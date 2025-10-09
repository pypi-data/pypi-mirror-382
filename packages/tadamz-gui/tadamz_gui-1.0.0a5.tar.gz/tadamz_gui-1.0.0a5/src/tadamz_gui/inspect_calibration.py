import mplcursors
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT
from PyQt5.QtWidgets import (
    QComboBox,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class InspectCalibrationWindow(QWidget):
    def __init__(self, t_cal, parent):
        super().__init__()

        self.t_cal = t_cal
        self.parent = parent

        # save table id to determine changes
        self.id_before = t_cal.unique_id

        self.setWindowTitle("Inspect calibration")

        # Plotting widget
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.fig.canvas.mpl_connect("pick_event", self._on_pick)
        self.canvas = FigureCanvas(self.fig)
        # Add a toolbar to control the plot
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # Table widget
        self.table = QTableWidget()
        headers = ["Compound", "Model", "Weight"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.t_cal))

        combo_box_options_models = ["linear", "quadratic"]
        combo_box_options_weights = ["none", "1/x", "1/x^2", "1/s^2"]

        # add rows to table
        for i, row in enumerate(t_cal.rows):
            compound = row["compound"]
            row_model = row["calibration_model"]

            model_name_combo = QComboBox()
            weights_combo = QComboBox()

            model_name_combo.setObjectName("model_name_combo")
            weights_combo.setObjectName("weights_combo")

            model_name_combo.addItems(combo_box_options_models)
            weights_combo.addItems(combo_box_options_weights)

            # set model name for row
            model_name_combo.setCurrentText(row_model.model_name)
            model_name_combo.currentTextChanged.connect(self._on_combo_changed)

            # set weights for row
            weights_combo.setCurrentText(row_model.calibration_weight)
            weights_combo.currentTextChanged.connect(self._on_combo_changed)

            # add cells to row
            self.table.setItem(i, 0, QTableWidgetItem(compound))
            self.table.setCellWidget(i, 1, model_name_combo)
            self.table.setCellWidget(i, 2, weights_combo)

        self.table.resizeColumnsToContents()
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        # Select first row
        self.table.selectRow(0)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)  # Add toolbar before canvas
        layout.addWidget(self.canvas)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def _on_pick(self, event):
        ind = event.ind[0]

        # Get the currently selected row to access the correct model
        selected_row = self.table.selectedItems()[0].row()
        model = self.t_cal.rows[selected_row]["calibration_model"]

        # Determine if we clicked an included or excluded point
        if event.artist.get_label() == "_included":
            i, j = self.included_indices[ind]
        elif event.artist.get_label() == "_excluded":
            i, j = self.excluded_indices[ind]

        # Invert inclusion status
        sample_name, included = model.included_samples[i][j]
        model.included_samples[i][j] = (sample_name, not included)

        model.fit_calibration_curve()
        model.determine_limits()
        col_index_model = self.t_cal.col_names.index("calibration_model")
        self.t_cal._set_value([selected_row], col_index_model, model)
        self._show_plot_for_row(selected_row)

    def _on_selection_changed(self):
        selected_items = self.table.selectedItems()

        if selected_items:
            # get index of first row of selected rows in table
            row_index = selected_items[0].row()
            self._show_plot_for_row(row_index)

    def _on_combo_changed(self, new_combo_value):
        sender = self.sender()
        sender_name = sender.objectName()
        row_index = self.table.indexAt(sender.pos()).row()

        model = self.t_cal.rows[row_index]["calibration_model"]

        if sender_name == "model_name_combo":
            col_index = self.t_cal.col_names.index("calibration_model_name")
            # Change value in table
            self.t_cal._set_value([row_index], col_index, new_combo_value)

            model.model_name = new_combo_value

        elif sender_name == "weights_combo":
            model.calibration_weight = new_combo_value

        # Update fit and add new model to table
        model.fit_calibration_curve()
        col_index_model = self.t_cal.col_names.index("calibration_model")
        self.t_cal._set_value([row_index], col_index_model, model)

        # Update plot and select row (in case the dropdown of a non-selected row was changed)
        self._show_plot_for_row(row_index)
        self.table.selectRow(row_index)

    def _show_plot_for_row(self, row_id):
        model = self.t_cal.rows[row_id]["calibration_model"]

        # clear old plot
        self.ax.cla()

        # Create index mappings for both included and excluded points
        # TODO: use model.get_plotting_data() to get the included/excluded data
        self.included_indices = []
        self.excluded_indices = []
        included_x = []
        included_y = []
        included_filename = []
        excluded_x = []
        excluded_y = []
        excluded_filename = []

        for i, (x, y_list, included_list) in enumerate(
            zip(model.xvalues, model.yvalues, model.included_samples)
        ):
            for j, (y, (filename, included)) in enumerate(zip(y_list, included_list)):
                if included:
                    included_x.append(x)
                    included_y.append(y)
                    included_filename.append(filename)
                    self.included_indices.append((i, j))
                else:
                    excluded_x.append(x)
                    excluded_y.append(y)
                    excluded_filename.append(filename)
                    self.excluded_indices.append((i, j))

        # Plot excluded points in grey
        if excluded_x:
            self.ax.plot(
                excluded_x,
                excluded_y,
                "o",
                color="grey",
                picker=True,
                label="_excluded",
            )

        # Plot included points in blue
        if included_x:
            self.ax.plot(included_x, included_y, "ob", picker=True, label="_included")

        # Enable hovering to show more info
        def _show_datapoint_info(sel):
            ind = sel.index
            if sel.artist.get_label() == "_included":
                filename = included_filename[ind]
            elif sel.artist.get_label() == "_excluded":
                filename = excluded_filename[ind]
            sel.annotation.set_text(f"{filename}")

        mplcursors.cursor(hover=mplcursors.HoverMode.Transient).connect(
            "add", _show_datapoint_info
        )

        # Plot calibration curve
        x = np.linspace(model.xvalues.min(), model.xvalues.max(), num=100)
        y_fit = model.fun(x, *model.params)
        if y_fit is not None:
            y_fit = [y.nominal_value for y in y_fit]
            self.ax.plot(x, y_fit, "-", color="black")
        else:
            print("Fitting failed for compound:", model.compound)

        self.ax.set_title(model.compound)
        self.ax.set_xlabel(f"Amount ({model.unit})")
        self.ax.set_ylabel("Normalized area")

        self.fig.tight_layout()
        self.fig.canvas.draw_idle()

    def closeEvent(self, event):
        # determine if t_cal has changed
        if self.id_before != self.t_cal.unique_id:
            self.parent.save_results("calibration_table")
            message = "Calibration table saved."
            self.parent.status_bar.showMessage(message)
            self.parent.print_to_GUI_terminal(message)

            QMessageBox.information(
                self,
                "Notice",
                "Calibration data has change."
                "Please consider re-running the quantification step.",
            )
        event.accept()
