import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMenuBar,
    QSplitter,
    QSizePolicy,
    QPushButton,
    QCheckBox,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Qt

#from input_dock import InputDock, NoScrollComboBox, apply_field_style
#from backend import BackendOsBridge
#from common import *
from PySide6.QtCore import Qt, QFile, QTextStream
from PySide6.QtGui import QIcon

# Import resources to register them
from osbridge.resources import resources_rc

from osbridge.ui.input_dock import InputDock, NoScrollComboBox, apply_field_style
from osbridge.ui.output_dock import OutputDock
from osbridge.backend.backend import BackendOsBridge
from osbridge.backend.common import *


class DummyCADWidget(QWidget):
    """Placeholder for CAD widget"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("CAD Window\n(Placeholder)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            """
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #999;
                padding: 40px;
                font-size: 18px;
                color: #666;
            }
            """
        )
        layout.addWidget(label)


class OutputDock(QWidget):
    """Output dock styled to match the provided mockup."""

    def __init__(self):
        super().__init__()
        self.setObjectName("outputDock")
        self.setStyleSheet(
            """
            QWidget#outputDock {
                background-color: #fdfdf8;
                border-left: 2px solid #d7d9c8;
            }
            """
        )
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)

        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setObjectName("outputHeader")
        title_bar.setStyleSheet(
            """
            QWidget#outputHeader {
                background-color: #90AF13;
                border-radius: 12px;
            }
            """
        )
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(14, 0, 14, 0)

        title_label = QLabel("Output Dock")
        title_label.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addWidget(title_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(14)

        analysis_frame, analysis_body_layout = self._create_section_frame("Analysis Results")
        self._populate_analysis_section(analysis_body_layout)
        scroll_layout.addWidget(analysis_frame)

        design_frame, design_body_layout = self._create_section_frame("Design")
        self._populate_design_section(design_body_layout)
        scroll_layout.addWidget(design_frame)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        button_style = """
            QPushButton {
                background-color: #90AF13;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 14px;
                padding: 10px 16px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7b980f;
            }
        """

        results_btn = QPushButton("Generate Results Table")
        results_btn.setStyleSheet(button_style)
        main_layout.addWidget(results_btn)

        report_btn = QPushButton("Generate Report")
        report_btn.setStyleSheet(button_style)
        main_layout.addWidget(report_btn)

    def _create_section_frame(self, title: str):
        frame = QFrame()
        frame.setObjectName("outputSection")
        frame.setStyleSheet(
            """
            QFrame#outputSection {
                border: 1px solid #cdd874;
                border-radius: 18px;
                background-color: white;
            }
            """
        )

        outer_layout = QVBoxLayout(frame)
        outer_layout.setContentsMargins(16, 12, 16, 16)
        outer_layout.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #2d2d2d;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        toggle_btn = QPushButton("-")
        toggle_btn.setObjectName("sectionToggle")
        toggle_btn.setCheckable(True)
        toggle_btn.setChecked(True)
        toggle_btn.setFixedSize(22, 22)
        toggle_btn.setStyleSheet(
            """
            QPushButton#sectionToggle {
                background-color: white;
                border: 1px solid #93ad1d;
                border-radius: 11px;
                color: #6d7a13;
                font-weight: bold;
            }
            QPushButton#sectionToggle:hover {
                background-color: #f5f5f5;
            }
            """
        )
        header_layout.addWidget(toggle_btn)
        outer_layout.addLayout(header_layout)

        accent_line = QFrame()
        accent_line.setFixedHeight(2)
        accent_line.setStyleSheet("background-color: #90AF13; border: none;")
        outer_layout.addWidget(accent_line)

        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(10)
        outer_layout.addWidget(body_widget)

        def on_toggle(checked):
            body_widget.setVisible(checked)
            toggle_btn.setText("-" if checked else "+")

        toggle_btn.toggled.connect(on_toggle)

        return frame, body_layout

    def _populate_analysis_section(self, layout: QVBoxLayout):
        member_row = QHBoxLayout()
        member_row.setSpacing(10)
        member_label = QLabel("Member:")
        member_label.setStyleSheet("font-size: 10px; color: #333;")
        member_label.setMinimumWidth(90)
        self.member_combo = NoScrollComboBox()
        self.member_combo.addItems(["All"])
        apply_field_style(self.member_combo)
        member_row.addWidget(member_label)
        member_row.addWidget(self.member_combo)
        layout.addLayout(member_row)

        load_row = QHBoxLayout()
        load_row.setSpacing(10)
        load_label = QLabel("Load Combination:")
        load_label.setStyleSheet("font-size: 10px; color: #333;")
        load_label.setMinimumWidth(90)
        self.load_combo = NoScrollComboBox()
        self.load_combo.addItems(["Envelope"])
        apply_field_style(self.load_combo)
        load_row.addWidget(load_label)
        load_row.addWidget(self.load_combo)
        layout.addLayout(load_row)

        forces_grid = QHBoxLayout()
        forces_grid.setSpacing(12)
        for items in (("Fx", "Mx", "Dx"), ("Fy", "My", "Dy"), ("Fz", "Mz", "Dz")):
            column = QVBoxLayout()
            column.setSpacing(6)
            for text in items:
                cb = QCheckBox(text)
                cb.setStyleSheet("font-size: 10px; color: #333;")
                column.addWidget(cb)
            forces_grid.addLayout(column)
        layout.addLayout(forces_grid)

        display_label = QLabel("Display Options:")
        display_label.setStyleSheet("font-size: 10px; color: #333;")
        layout.addWidget(display_label)

        display_row = QHBoxLayout()
        display_row.setSpacing(12)
        for text in ("Max", "Min"):
            cb = QCheckBox(text)
            cb.setStyleSheet("font-size: 10px; color: #333;")
            display_row.addWidget(cb)
        display_row.addStretch()
        layout.addLayout(display_row)

        utilization_check = QCheckBox("Controlling Utilization Ratio")
        utilization_check.setStyleSheet("font-size: 10px; color: #333;")
        layout.addWidget(utilization_check)

    def _populate_design_section(self, layout: QVBoxLayout):
        super_frame = self._create_design_subframe("Superstructure", ["Steel Design", "Deck Design"])
        layout.addWidget(super_frame)

        sub_frame = self._create_design_subframe("Substructure")
        layout.addWidget(sub_frame)

    def _create_design_subframe(self, title: str, button_labels=None):
        frame = QFrame()
        frame.setObjectName("designSubSection")
        frame.setStyleSheet(
            """
            QFrame#designSubSection {
                border: 1px solid #e0e8a4;
                border-radius: 14px;
                background-color: #fcfdf4;
            }
            """
        )

        outer_layout = QVBoxLayout(frame)
        outer_layout.setContentsMargins(12, 8, 12, 12)
        outer_layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #333;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        toggle_btn = QPushButton("-")
        toggle_btn.setObjectName("designToggle")
        toggle_btn.setCheckable(True)
        toggle_btn.setChecked(True)
        toggle_btn.setFixedSize(22, 22)
        toggle_btn.setStyleSheet(
            """
            QPushButton#designToggle {
                background-color: white;
                border: 1px solid #bcc66d;
                border-radius: 11px;
                color: #6d7a13;
                font-weight: bold;
            }
            QPushButton#designToggle:hover {
                background-color: #f5f5f5;
            }
            """
        )
        header_layout.addWidget(toggle_btn)
        outer_layout.addLayout(header_layout)

        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(6)
        outer_layout.addWidget(body_widget)

        if button_labels:
            for text in button_labels:
                btn = QPushButton(text)
                btn.setObjectName("designActionBtn")
                btn.setStyleSheet(
                    """
                    QPushButton#designActionBtn {
                        background-color: white;
                        color: #3b3b3b;
                        border: 1px solid #c7c7c7;
                        border-radius: 14px;
                        padding: 8px;
                        font-size: 10px;
                        font-weight: bold;
                    }
                    QPushButton#designActionBtn:hover {
                        background-color: #f7f7f7;
                    }
                    """
                )
                body_layout.addWidget(btn)
        else:
            placeholder = QLabel(" ")
            placeholder.setMinimumHeight(28)
            body_layout.addWidget(placeholder)

        def on_toggle(checked):
            body_widget.setVisible(checked)
            toggle_btn.setText("-" if checked else "+")

        toggle_btn.toggled.connect(on_toggle)

        return frame


class DummyLogDock(QWidget):
    """Placeholder for log dock."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Log Window\n(Placeholder)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            """
            QLabel {
                background-color: #fff3e0;
                border: 2px dashed #ff9800;
                padding: 20px;
                font-size: 14px;
                color: #e65100;
            }
            """
        )
        layout.addWidget(label)
        self.hide()


class CustomWindow(QWidget):
    def __init__(self, title: str, backend: object, parent=None):
        super().__init__()
        self.parent = parent
        self.backend = backend()

        self.setWindowTitle(title)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #ffffff;
                margin: 0px;
                padding: 0px;
            }
            QMenuBar {
                background-color: #F4F4F4;
                color: #000000;
                padding: 0px;
            }
            QMenuBar::item {
                padding: 5px 10px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #FFFFFF;
            }
            """
        )

        self.init_ui()

    def init_ui(self):
        main_v_layout = QVBoxLayout(self)
        main_v_layout.setContentsMargins(0, 0, 0, 0)
        main_v_layout.setSpacing(0)

        self.menu_bar = QMenuBar(self)
        self.menu_bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.menu_bar.setFixedHeight(28)
        self.menu_bar.setContentsMargins(0, 0, 0, 0)
        self.menu_bar.addMenu("File")
        self.menu_bar.addMenu("Edit")
        self.menu_bar.addMenu("Graphics")
        self.menu_bar.addMenu("Help")
        main_v_layout.addWidget(self.menu_bar)

        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal, body_widget)

        # Input dock
        input_dock = InputDock(backend=self.backend, parent=self)
        input_dock.setMinimumWidth(380)
        input_dock.setMaximumWidth(450)
        main_splitter.addWidget(input_dock)

        # CAD widget
        cad_widget = DummyCADWidget()
        main_splitter.addWidget(cad_widget)

        # Output dock
        output_dock = OutputDock()
        output_dock.setMinimumWidth(350)
        output_dock.setMaximumWidth(450)
        main_splitter.addWidget(output_dock)

        body_layout.addWidget(main_splitter)

        # Set stretch factors for main splitter
        main_splitter.setStretchFactor(0, 0)  # Input dock - fixed
        main_splitter.setStretchFactor(1, 1)  # Central area - expandable
        main_splitter.setStretchFactor(2, 0)  # Output dock - fixed

        # Set initial sizes
        input_dock_width = 350
        output_dock_width = 280
        total_width = self.width() if self.width() > 0 else 1200
        central_width = max(500, total_width - input_dock_width - output_dock_width)
        main_splitter.setSizes([input_dock_width, central_width, output_dock_width])

        main_v_layout.addWidget(body_widget)

        # Store references
        self.main_splitter = main_splitter
        self.input_dock = input_dock
        self.output_dock = output_dock
        self.cad_widget = cad_widget


def main():
    app = QApplication(sys.argv)   
    window = CustomWindow("Osdag Bridge", BackendOsBridge)
    window.showMaximized()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()