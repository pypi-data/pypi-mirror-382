"""GUI for importing data from gcwerks.


It basically can take the parameters of the gcwerks and convert them to a dataframe.
"""
from __future__ import annotations
import sys
from pathlib import Path
import logging

from PySide6.QtCore import QDate, QSettings, Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QErrorMessage,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from avoca.bindings.gcwerks import (
    allowed_vars,
    export,
    get_gcwerks_folders,
    read_gcwerks,
)


class GCWerksImport(QWidget):
    def __init__(
        self,
        parent: QWidget = None,
        settings: QSettings | None = None,
        variables: list[str] = [],
    ):
        """Create a widget to import data from gcwerks.

        Args:
            parent : The parent widget.
            settings : The settings to use.
            variables: The variables to import. If not given, a selection of
                variables will be availabe. If given, the widget will only
                export the given variables.
        """
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)

        self.setWindowTitle("GCWerks Import")
        layout = QVBoxLayout()
        if settings is None:
            settings = QSettings("avoca", "gcwerks_import")
        elif isinstance(settings, QSettings):
            # get the subsetting
            settings = settings.childGroup("gcwerks_import")
        else:
            raise TypeError(f"settings must be a QSettings object or None, not {type(settings)=}")
        self.settings = settings

        # Comounds selection (Multi checkable radio buttons, with option to add more)
        compounds_overlayout = QVBoxLayout()
        compounds_layout = QVBoxLayout()
        compounds_overlayout.addLayout(compounds_layout)
        self.compounds_layout = compounds_layout
        layout.addLayout(compounds_overlayout)
        compounds = settings.value("compounds", [], type=list)
        for compound in compounds:
            checkbox = QCheckBox(compound)
            checkbox.setChecked(settings.value(f"cmp.{compound}.selected", False, bool))
            compounds_layout.addWidget(checkbox)
            # Connect to the settings
            checkbox.stateChanged.connect(
                lambda state, compound=compound: settings.setValue(
                    f"cmp.{compound}.selected", state == 2
                )
            )
        # add button to add more compounds
        add_compound = QPushButton("Add compound")
        add_compound.clicked.connect(self.add_compound)
        compounds_overlayout.addWidget(add_compound)

        # Add the variables selection (Multi checkable radio buttons)
        if variables:
            self.variables = variables
        else:
            vars_layout = QVBoxLayout()
            self.variables_layout = vars_layout
            layout.addLayout(vars_layout)

            for var in allowed_vars:
                checkbox = QCheckBox(var)
                checkbox.setChecked(settings.value(f"var.{var}.selected", False, bool))
                vars_layout.addWidget(checkbox)
                # Connect to the settings
                checkbox.stateChanged.connect(
                    lambda state, var=var: settings.setValue(
                        f"var.{var}.selected", state == 2
                    )
                )

        # Add datetime start and stop selection
        datetime_layout = QHBoxLayout()
        datetime_layout.addWidget(QLabel("Start:"))
        self.start_datetime = QDateEdit(
            settings.value("start_datetime", QDate.currentDate(), QDate),
            parent=self,
        )
        # Save to settings when changed
        self.start_datetime.dateChanged.connect(
            lambda date: settings.setValue("start_datetime", date)
        )
        datetime_layout.addWidget(self.start_datetime)
        datetime_layout.addWidget(QLabel("Stop:"))
        self.stop_datetime = QDateEdit(
            settings.value("end_datetime", QDate.currentDate(), QDate),
            parent=self,
        )
        self.stop_datetime.dateChanged.connect(
            lambda date: settings.setValue("end_datetime", date)
        )
        datetime_layout.addWidget(self.stop_datetime)
        layout.addLayout(datetime_layout)
        # Button to set the datetime to the current time
        set_now = QPushButton("Set now")
        set_now.clicked.connect(lambda: self.stop_datetime.setDate(QDate.currentDate()))
        datetime_layout.addWidget(set_now)

        # Folder selection (dropdown)
        folders = get_gcwerks_folders()
        folder_layout = QHBoxLayout()
        folder_widget = QComboBox()
        self.folder_widget = folder_widget
        folder_widget.addItems(map(str, folders))
        folder_layout.addWidget(QLabel("Folder:"))
        folder_layout.addWidget(folder_widget)
        layout.addLayout(folder_layout)
        # Select the folder from settings and connect 
        folder_widget.setCurrentText(settings.value("gcwerks_folder", "", str))
        folder_widget.currentTextChanged.connect(
            lambda text: settings.setValue("gcwerks_folder", text)
        )

        # Output file
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output file:"))
        self.output_file = QLabel(
            settings.value("output_file", ".gcwerk.dat", str), parent=self
        )
        self.select_file = QPushButton("Select file")
        self.select_file.clicked.connect(self.select_output_file)
        output_layout.addWidget(self.output_file)
        output_layout.addWidget(self.select_file)
        layout.addLayout(output_layout)

        self.btn = QPushButton("Import")
        self.btn.clicked.connect(self.import_data)
        layout.addWidget(self.btn)

        self.setLayout(layout)

    def get_selected_compounds(self) -> list[str]:
        compounds = []
        for i in range(self.compounds_layout.count()):
            widget = self.compounds_layout.itemAt(i).widget()
            if widget.isChecked():
                compounds.append(widget.text())
        return compounds

    def get_selected_variables(self) -> list[str]:
        if hasattr(self, "variables"):
            return self.variables
        variables = []
        for i in range(self.variables_layout.count()):
            widget = self.variables_layout.itemAt(i).widget()
            if widget.isChecked():
                variables.append(widget.text())
        return variables

    def import_data(self):
        out_file = Path(self.output_file.text())
        try:
            export(
                workdir="",
                gcdir=self.folder_widget.currentText(),
                out_file=out_file,
                compounds=self.get_selected_compounds(),
                variables=self.get_selected_variables(),
                date_start=self.start_datetime.dateTime().toPython(),
                date_end=self.stop_datetime.dateTime().toPython(),
            )
        except Exception as e:
            self.logger.exception(e)
            # Open an error dialog with the error
            error_dialog = QErrorMessage()
            error_dialog.showMessage(str(e))
            error_dialog.exec()

            return
        
        try:
            df = read_gcwerks(out_file)
            self.logger.info(f"Data imported to {out_file}")
            return df
        except Exception as e:
            self.logger.exception(e)
            # Open an error dialog with the error
            error_dialog = QErrorMessage()
            error_dialog.showMessage(f"Could not read the gcwerks file {out_file} becaues of {e}")
            error_dialog.exec()
            return

    def select_output_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Data files (*.dat)")
        if file_dialog.exec():
            output_file = file_dialog.selectedFiles()[0]
            self.output_file.setText(output_file)
            self.settings.setValue("output_file", output_file)

    def add_compound(self):
        """Open a dialog with a text input where user can add a new compound."""
        compound, ok = QInputDialog.getText(
            self,
            "Add compound",
            "Multiple compounds can be added separated by space. \n Compound(s):",
        )
        compunds = compound.split(" ")
        if ok:
            for compound in compunds:
                checkbox = QCheckBox(compound)
                checkbox.setChecked(True)
                self.compounds_layout.addWidget(checkbox)

            # Add the compounds to the settings
            all_compounds: list[str] = self.settings.value("compounds", [], type=list)
            all_compounds.extend(compunds)
            self.settings.setValue("compounds", all_compounds)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    app = QApplication(sys.argv)
    widget = GCWerksImport()
    widget.show()
    app.exec()
