import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QMenuBar, QSplitter, QSizePolicy, QPushButton, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtCore import Qt, QFile, QTextStream
from PySide6.QtGui import QIcon

from osdagbridge.desktop.ui.docks.input_dock import InputDock
from osdagbridge.desktop.ui.docks.output_dock import OutputDock
from osdagbridge.desktop.ui.docks.log_dock import LogDock

from osdagbridge.core.bridge_types.plate_girder.ui_fields import FrontendData
from osdagbridge.core.utils.common import *

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
        output_dock.setMinimumWidth(380)
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
