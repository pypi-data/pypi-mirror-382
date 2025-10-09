import os

from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)


def add_text_field(label, default="", tooltip="", form_layout=None, optional=False):
    """Add a text field to the form."""
    field_label = QLabel(label)
    field_label.setToolTip(tooltip)
    field = QLineEdit()
    field.setText(default)
    field.setToolTip(tooltip)
    form_layout.addRow(field_label, field)

    _attach_empty_highlight(field, optional=optional)

    return field


def add_float_field(label, default=0.0, tooltip="", form_layout=None, optional=False):
    """Add a float field with validation to the form."""
    field_label = QLabel(label)
    field_label.setToolTip(tooltip)
    field = QLineEdit()
    field.setValidator(QDoubleValidator())
    field.setText(str(default))
    field.setToolTip(tooltip)
    form_layout.addRow(field_label, field)

    _attach_empty_highlight(field, optional=optional)

    return field


def add_combo_field(label, options, default=None, form_layout=None):
    """Add a combo box to the form, with options provided as tuple of display and actual value."""
    field = QComboBox()
    for option in options:
        if isinstance(option, tuple):
            display_value, actual_value = option
            field.addItem(display_value, actual_value)
        else:
            field.addItem(option, option)  # If no tuple, use the same value for both

    if default:
        # Set the default value by matching the actual value
        index = field.findData(default)
        if index != -1:
            field.setCurrentIndex(index)

    form_layout.addRow(QLabel(label), field)
    return field


def add_checkbox_field(label, default=False, tooltip="", form_layout=None):
    """Add a checkbox to the form."""
    field_label = QLabel(label)
    field_label.setToolTip(tooltip)
    field = QCheckBox()
    field.setChecked(default)
    field.setToolTip(tooltip)
    form_layout.addRow(field_label, field)
    return field


def add_file_field(label, file_types=None, form_layout=None, optional=False):
    """Add a file selection field to the form."""
    field = QLineEdit()
    button = QPushButton("Browse")
    button.clicked.connect(lambda: _browse_file(field, file_types))
    row_layout = QHBoxLayout()
    row_layout.addWidget(field)
    row_layout.addWidget(button)
    form_layout.addRow(QLabel(label), row_layout)

    _attach_path_highlight(field, optional=optional)

    return field


def add_directory_field(label, tooltip="", form_layout=None, optional=False):
    """Add a directory selection field to the form."""
    field_label = QLabel(label)
    field_label.setToolTip(tooltip)
    field = QLineEdit()
    field.setToolTip(tooltip)
    button = QPushButton("Browse")
    button.clicked.connect(lambda: _browse_directory(field))
    row_layout = QHBoxLayout()
    row_layout.addWidget(field)
    row_layout.addWidget(button)
    form_layout.addRow(QLabel(label), row_layout)

    _attach_path_highlight(field, optional=optional)

    return field


def _browse_file(field, file_types=None):
    """Open a file dialog and set the selected file path."""
    file_path, _ = QFileDialog.getOpenFileName(None, "Select File", filter=file_types)
    if file_path:
        field.setText(file_path)


def _browse_directory(field):
    """Open a directory dialog and set the selected directory path."""
    directory_path = QFileDialog.getExistingDirectory(None, "Select Directory")
    if directory_path:
        field.setText(directory_path)


def _attach_empty_highlight(field, optional=False):
    """Highlight orange if empty (when not optional). Also set _is_valid attribute."""

    def highlight():
        if not field.text().strip() and not optional:
            field.setStyleSheet("background-color: orange;")
            field.is_valid = False
        else:
            field.setStyleSheet("")
            field.is_valid = True

    field.textChanged.connect(highlight)
    highlight()


def _attach_path_highlight(field, optional=False):
    """Highlight orange if empty (when not optional), red if path does not exist (if not empty). Also set _is_valid attribute."""

    def highlight():
        text = field.text().strip()
        if not text and not optional:
            field.setStyleSheet("background-color: orange;")
            field.is_valid = False
        elif text and not os.path.exists(text):
            field.setStyleSheet("background-color: red;")
            field.is_valid = False
        else:
            field.setStyleSheet("")
            field.is_valid = True

    field.textChanged.connect(highlight)
    highlight()
