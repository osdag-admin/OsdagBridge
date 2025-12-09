"""
Additional Inputs Widget for Highway Bridge Design
Provides detailed input fields for manual bridge parameter definition
"""
import sys
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit,
    QComboBox, QGroupBox, QFormLayout, QPushButton, QScrollArea,
    QCheckBox, QMessageBox, QSizePolicy, QSpacerItem, QStackedWidget,
    QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator

from osbridge.backend.common import *


def get_combobox_style():
    """Return the common stylesheet for dropdowns with the SVG icon from resources."""
    return """
        QComboBox {
            padding: 6px 42px 6px 14px;
            border: 1px solid #b8b8b8;
            border-radius: 8px;
            background-color: #ffffff;
            color: #2b2b2b;
            font-size: 12px;
            min-height: 34px;
        }
        QComboBox:hover {
            border: 1px solid #909090;
        }
        QComboBox:focus {
            border: 1px solid #4a7ba7;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: center right;
            width: 26px;
            height: 26px;
            width: 26px;
            height: 26px;
            border: none;
            background: transparent;
            right: 8px;
        }
        QComboBox::down-arrow {
            image: url(:/vectors/arrow_down_light.svg);
            width: 16px;
            height: 16px;
        }
        /* when popup is open show the up arrow */
        QComboBox::down-arrow:on {
            image: url(:/vectors/arrow_up_light.svg);
            width: 16px;
            height: 16px;
        }
        QComboBox QAbstractItemView {{
            border: 1px solid #b8b8b8;
            background: #ffffff;
            selection-background-color: #e7f2ff;
            selection-color: #1f1f1f;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 6px 10px;
            font-size: 12px;
        }}
    """


def get_lineedit_style():
    """Return the shared stylesheet for line edits in the section inputs."""
    return """
        QLineEdit {
            padding: 6px 12px;
            border: 1px solid #b8b8b8;
            border-radius: 8px;
            background-color: #ffffff;
            color: #2b2b2b;
            font-size: 12px;
            min-height: 34px;
        }
        QLineEdit:hover {
            border: 1px solid #909090;
        }
        QLineEdit:focus {
            border: 1px solid #4a7ba7;
        }
        QLineEdit:disabled {
            background-color: #f0f0f0;
            color: #9b9b9b;
        }
    """


def apply_field_style(widget):
    """Apply the appropriate style to combo boxes and line edits."""
    widget.setMinimumHeight(34)
    if isinstance(widget, QComboBox):
        widget.setStyleSheet(get_combobox_style())
    elif isinstance(widget, QLineEdit):
        widget.setStyleSheet(get_lineedit_style())


SECTION_NAV_BUTTON_STYLE = """
    QPushButton {
        background-color: #f4f4f4;
        border: 2px solid #d2d2d2;
        border-radius: 12px;
        padding: 20px 16px;
        text-align: left;
        font-weight: bold;
        font-size: 12px;
        color: #333333;
    }
    QPushButton:hover {
        border-color: #b5b5b5;
    }
    QPushButton:checked {
        background-color: #90af13;
        border-color: #7da523;
        color: #ffffff;
    }
"""


class OptimizableField(QWidget):
    """Widget that allows selection between Optimized/Customized/All modes with input field"""
    
    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        
        # Mode selector
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(VALUES_OPTIMIZATION_MODE)
        self.mode_combo.setMinimumWidth(140)
        self.mode_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setEnabled(False)  # Disabled by default for "Optimized"
        self.input_field.setVisible(False)
        self.input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.layout.addWidget(self.mode_combo)
        self.layout.addWidget(self.input_field)
        
        # Connect signal
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.on_mode_changed(self.mode_combo.currentText())
    
    def on_mode_changed(self, text):
        """Enable/disable input field based on selection"""
        if text in ("Optimized", "All"):
            self.input_field.setEnabled(False)
            self.input_field.clear()
            self.input_field.setVisible(False)
        else:
            self.input_field.setEnabled(True)
            self.input_field.setVisible(True)
    
    def get_value(self):
        """Returns tuple of (mode, value)"""
        return (self.mode_combo.currentText(), self.input_field.text())


class BridgeGeometryTab(QWidget):
    """Sub-tab for Bridge Geometry inputs"""
    
    footpath_changed = Signal(str)  # Signal when footpath status changes
    
    def __init__(self, footpath_value="None", carriageway_width=7.5, parent=None):
        super().__init__(parent)
        self.footpath_value = footpath_value
        self.carriageway_width = carriageway_width
        self.updating_fields = False  # Flag to prevent circular updates
        self.init_ui()
    
    def style_input_field(self, field):
        """Apply consistent styling to input fields"""
        apply_field_style(field)
    
    def style_group_box(self, group_box):
        """Apply consistent styling to group boxes"""
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #d0d0d0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #f9f9f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                background-color: white;
                color: #4a7ba7;
            }
        """)
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # TOP: Diagram placeholder
        diagram_widget = QWidget()
        diagram_widget.setStyleSheet("""
            QWidget {
                background-color: #d9d9d9;
                border-bottom: 1px solid #b0b0b0;
            }
        """)
        diagram_widget.setMinimumHeight(150)
        diagram_widget.setMaximumHeight(200)
        diagram_layout = QVBoxLayout(diagram_widget)
        diagram_layout.setContentsMargins(20, 20, 20, 20)
        diagram_layout.setAlignment(Qt.AlignCenter)
        
        # Diagram image placeholder
        diagram_label = QLabel("Bridge Geometry\nDiagram")
        diagram_label.setAlignment(Qt.AlignCenter)
        diagram_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 20px;
                font-size: 13px;
                color: #333;
            }
        """)
        diagram_layout.addWidget(diagram_label, 0, Qt.AlignCenter)
        
        main_layout.addWidget(diagram_widget)
        
        # BOTTOM: Tabbed Input Interface
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(0)
        
        # Create sub-tabs for different input categories
        self.input_tabs = QTabWidget()
        self.input_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #b0b0b0;
                border-top: none;
                background-color: white;
                border-radius: 0px 0px 8px 8px;
            }
            QTabBar::tab {
                background-color: #e8e8e8;
                color: #555;
                padding: 8px 20px;
                border: 1px solid #b0b0b0;
                border-bottom: none;
                border-right: none;
                font-size: 11px;
                min-width: 80px;
            }
            QTabBar::tab:last {
                border-right: 1px solid #b0b0b0;
            }
            QTabBar::tab:selected {
                background-color: #90AF13;
                color: white;
                font-weight: bold;
                border: 1px solid #90AF13;
                border-bottom: none;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d0d0d0;
            }
        """)
        
        # Create each sub-tab
        self.create_layout_tab()
        self.create_deck_tab()
        self.create_crash_barrier_tab()
        self.create_railing_tab()
        self.create_wearing_course_tab()
        self.create_lane_details_tab()
        
        input_layout.addWidget(self.input_tabs)
        
        main_layout.addWidget(input_container, 1)
        
        # Connect deck thickness to footpath thickness
        self.deck_thickness.textChanged.connect(self.update_footpath_thickness)
        
        # Initialize calculations with default values
        self.recalculate_girders()
    
    def create_layout_tab(self):
        """Create the Layout tab with girder spacing and deck overhang"""
        layout_widget = QWidget()
        layout_widget.setStyleSheet("background-color: white;")
        layout_layout = QVBoxLayout(layout_widget)
        layout_layout.setContentsMargins(25, 25, 25, 25)
        layout_layout.setSpacing(20)
        
        # --- Inputs Group ---
        inputs_group = QGroupBox()
        inputs_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #a0a0a0;
                border-radius: 10px;
                margin-top: 10px;
            }
        """)
        inputs_layout = QVBoxLayout(inputs_group)
        inputs_layout.setContentsMargins(20, 20, 20, 20)
        inputs_layout.setSpacing(15)
        
        # Title inside the group
        title_label = QLabel("Inputs:")
        title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000; border: none;")
        inputs_layout.addWidget(title_label)
        
        # Create grid for inputs
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(20)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        
        # Row 0: Girder Spacing and No. of Girders
        girder_spacing_label = QLabel("Girder Spacing (m):")
        girder_spacing_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        girder_spacing_label.setMinimumWidth(150)
        self.girder_spacing = QLineEdit()
        self.girder_spacing.setValidator(QDoubleValidator(0.01, 50.0, 3))
        self.girder_spacing.setText(str(DEFAULT_GIRDER_SPACING))
        self.style_input_field(self.girder_spacing)
        self.girder_spacing.textChanged.connect(self.on_girder_spacing_changed)
        
        no_girders_label = QLabel("No. of Girders:")
        no_girders_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        no_girders_label.setMinimumWidth(150)
        self.no_of_girders = QLineEdit()
        self.no_of_girders.setValidator(QIntValidator(2, 100))
        self.style_input_field(self.no_of_girders)
        self.no_of_girders.textChanged.connect(self.on_no_of_girders_changed)
        
        grid.addWidget(girder_spacing_label, 0, 0, Qt.AlignLeft)
        grid.addWidget(self.girder_spacing, 0, 1)
        grid.addWidget(no_girders_label, 0, 2, Qt.AlignLeft)
        grid.addWidget(self.no_of_girders, 0, 3)
        
        # Row 1: Deck Overhang Width
        deck_overhang_label = QLabel("Deck Overhang Width (m):")
        deck_overhang_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        deck_overhang_label.setMinimumWidth(150)
        self.deck_overhang = QLineEdit()
        self.deck_overhang.setValidator(QDoubleValidator(0.0, 10.0, 3))
        self.deck_overhang.setText(str(DEFAULT_DECK_OVERHANG))
        self.style_input_field(self.deck_overhang)
        self.deck_overhang.textChanged.connect(self.on_deck_overhang_changed)
        
        grid.addWidget(deck_overhang_label, 1, 0, Qt.AlignLeft)
        grid.addWidget(self.deck_overhang, 1, 1)
        
        inputs_layout.addLayout(grid)
        layout_layout.addWidget(inputs_group)
        
        # --- Overall Bridge Width Group ---
        width_group = QGroupBox()
        width_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #a0a0a0;
                border-radius: 10px;
                margin-top: 10px;
            }
        """)
        width_layout = QHBoxLayout(width_group)
        width_layout.setContentsMargins(20, 20, 20, 20)
        width_layout.setSpacing(40)
        
        overall_width_label = QLabel("Overall Bridge Width (m):")
        overall_width_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        overall_width_label.setMinimumWidth(150)
        
        self.overall_width_display = QLineEdit()
        self.overall_width_display.setReadOnly(True)
        self.style_input_field(self.overall_width_display)
        
        width_layout.addWidget(overall_width_label)
        width_layout.addWidget(self.overall_width_display)
        width_layout.addStretch()
        
        layout_layout.addWidget(width_group)
        layout_layout.addStretch()
        
        self.input_tabs.addTab(layout_widget, "Layout")
    
    def create_deck_tab(self):
        """Create the Deck tab with deck and footpath parameters"""
        deck_widget = QWidget()
        deck_widget.setStyleSheet("background-color: white;")
        deck_layout = QVBoxLayout(deck_widget)
        deck_layout.setContentsMargins(25, 25, 25, 25)
        deck_layout.setSpacing(20)
        
        # --- Deck Inputs Group ---
        inputs_group = QGroupBox()
        inputs_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #a0a0a0;
                border-radius: 10px;
                margin-top: 10px;
            }
        """)
        inputs_layout = QVBoxLayout(inputs_group)
        inputs_layout.setContentsMargins(20, 20, 20, 20)
        inputs_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Deck Inputs:")
        title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000; border: none;")
        inputs_layout.addWidget(title_label)
        
        # Create grid for inputs
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(20)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        
        # Row 0: Deck Thickness and Decking Plate
        deck_thickness_label = QLabel("Deck Thickness:")
        deck_thickness_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        deck_thickness_label.setMinimumWidth(150)
        self.deck_thickness = QLineEdit()
        self.deck_thickness.setValidator(QDoubleValidator(0.0, 500.0, 0))
        self.style_input_field(self.deck_thickness)
        
        decking_plate_label = QLabel("Decking Plate:")
        decking_plate_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        decking_plate_label.setMinimumWidth(150)
        self.decking_plate = QComboBox()
        self.decking_plate.addItems(VALUES_DECKING_PLATE)
        self.style_input_field(self.decking_plate)
        
        grid.addWidget(deck_thickness_label, 0, 0, Qt.AlignLeft)
        grid.addWidget(self.deck_thickness, 0, 1)
        grid.addWidget(decking_plate_label, 0, 2, Qt.AlignLeft)
        grid.addWidget(self.decking_plate, 0, 3)
        
        # Row 1: Footpath Width and Footpath Thickness
        footpath_width_label = QLabel("Footpath Width (m):")
        footpath_width_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        footpath_width_label.setMinimumWidth(150)
        self.footpath_width = QLineEdit()
        self.footpath_width.setValidator(QDoubleValidator(MIN_FOOTPATH_WIDTH, 5.0, 3))
        self.style_input_field(self.footpath_width)
        self.footpath_width.textChanged.connect(self.on_footpath_width_changed)
        
        footpath_thickness_label = QLabel("Footpath Thickness :")
        footpath_thickness_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        footpath_thickness_label.setMinimumWidth(150)
        self.footpath_thickness = QLineEdit()
        self.footpath_thickness.setValidator(QDoubleValidator(0.0, 500.0, 0))
        self.style_input_field(self.footpath_thickness)
        
        grid.addWidget(footpath_width_label, 1, 0, Qt.AlignLeft)
        grid.addWidget(self.footpath_width, 1, 1)
        grid.addWidget(footpath_thickness_label, 1, 2, Qt.AlignLeft)
        grid.addWidget(self.footpath_thickness, 1, 3)
        
        # Row 2: Safety Kerb Thickness and Safety Kerb Width
        safety_kerb_thickness_label = QLabel("Safety Kerb Thickness (mm):")
        safety_kerb_thickness_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        safety_kerb_thickness_label.setMinimumWidth(150)
        self.safety_kerb_thickness = QLineEdit()
        self.safety_kerb_thickness.setValidator(QDoubleValidator(0.0, 500.0, 0))
        self.style_input_field(self.safety_kerb_thickness)
        
        safety_kerb_width_label = QLabel("Safety Kerb Width (m):")
        safety_kerb_width_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        safety_kerb_width_label.setMinimumWidth(150)
        self.safety_kerb_width = QLineEdit()
        self.safety_kerb_width.setValidator(QDoubleValidator(MIN_SAFETY_KERB_WIDTH, 2.0, 3))
        self.style_input_field(self.safety_kerb_width)
        
        grid.addWidget(safety_kerb_thickness_label, 2, 0, Qt.AlignLeft)
        grid.addWidget(self.safety_kerb_thickness, 2, 1)
        grid.addWidget(safety_kerb_width_label, 2, 2, Qt.AlignLeft)
        grid.addWidget(self.safety_kerb_width, 2, 3)
        
        # Row 3: Load Case
        load_case_label = QLabel("Load Case:")
        load_case_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        load_case_label.setMinimumWidth(150)
        self.deck_load_case = QComboBox()
        self.deck_load_case.addItems(VALUES_LOAD_CASE)
        self.style_input_field(self.deck_load_case)
        
        grid.addWidget(load_case_label, 3, 0, Qt.AlignLeft)
        grid.addWidget(self.deck_load_case, 3, 1)
        
        inputs_layout.addLayout(grid)
        deck_layout.addWidget(inputs_group)
        deck_layout.addStretch()
        
        self.input_tabs.addTab(deck_widget, "Deck")
    
    def create_crash_barrier_tab(self):
        """Create the Crash Barrier tab"""
        crash_widget = QWidget()
        crash_widget.setStyleSheet("background-color: white;")
        crash_layout = QVBoxLayout(crash_widget)
        crash_layout.setContentsMargins(25, 25, 25, 25)
        crash_layout.setSpacing(20)
        
        # --- Inputs Group ---
        inputs_group = QGroupBox()
        inputs_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #a0a0a0;
                border-radius: 10px;
                margin-top: 10px;
            }
        """)
        inputs_layout = QVBoxLayout(inputs_group)
        inputs_layout.setContentsMargins(20, 20, 20, 20)
        inputs_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Inputs:")
        title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000; border: none;")
        inputs_layout.addWidget(title_label)
        
        # Create grid for inputs
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(20)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        
        # Row 0: Crash Barrier Type
        crash_type_label = QLabel("Crash Barrier Type:")
        crash_type_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        crash_type_label.setMinimumWidth(180)
        self.crash_barrier_type = QComboBox()
        self.crash_barrier_type.addItems(VALUES_CRASH_BARRIER_TYPE)
        self.style_input_field(self.crash_barrier_type)
        self.crash_barrier_type.currentTextChanged.connect(self.on_crash_barrier_type_changed)
        
        grid.addWidget(crash_type_label, 0, 0, Qt.AlignLeft)
        grid.addWidget(self.crash_barrier_type, 0, 1, 1, 3)
        
        # Row 1: Crash Barrier Width
        crash_width_label = QLabel("Crash Barrier Width (m):")
        crash_width_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        crash_width_label.setMinimumWidth(180)
        self.crash_barrier_width = QLineEdit()
        self.crash_barrier_width.setValidator(QDoubleValidator(0.0, 2.0, 3))
        self.crash_barrier_width.setText(str(DEFAULT_CRASH_BARRIER_WIDTH))
        self.style_input_field(self.crash_barrier_width)
        self.crash_barrier_width.textChanged.connect(self.recalculate_girders)
        
        grid.addWidget(crash_width_label, 1, 0, Qt.AlignLeft)
        grid.addWidget(self.crash_barrier_width, 1, 1, 1, 3)
        
        # Row 2: Crash Barrier Material density
        crash_density_label = QLabel("Crash Barrier Material density")
        crash_density_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        crash_density_label.setMinimumWidth(180)
        self.crash_barrier_density = QLineEdit()
        self.crash_barrier_density.setValidator(QDoubleValidator(0.0, 100.0, 2))
        self.style_input_field(self.crash_barrier_density)
        
        grid.addWidget(crash_density_label, 2, 0, Qt.AlignLeft)
        grid.addWidget(self.crash_barrier_density, 2, 1, 1, 3)
        
        # Row 3: Crash Barrier Area
        crash_area_label = QLabel("Crash Barrier Area (m2 ):")
        crash_area_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        crash_area_label.setMinimumWidth(180)
        self.crash_barrier_area = QLineEdit()
        self.crash_barrier_area.setValidator(QDoubleValidator(0.0, 10.0, 4))
        self.style_input_field(self.crash_barrier_area)
        
        grid.addWidget(crash_area_label, 3, 0, Qt.AlignLeft)
        grid.addWidget(self.crash_barrier_area, 3, 1, 1, 3)
        
        # Row 4: Load Case
        load_case_label = QLabel("Load Case:")
        load_case_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        load_case_label.setMinimumWidth(180)
        self.crash_load_case = QComboBox()
        self.crash_load_case.addItems(VALUES_LOAD_CASE)
        self.crash_load_case.setCurrentText("Super-imposed Dead Load (SIDL)")
        self.style_input_field(self.crash_load_case)
        
        grid.addWidget(load_case_label, 4, 0, Qt.AlignLeft)
        grid.addWidget(self.crash_load_case, 4, 1, 1, 3)
        
        inputs_layout.addLayout(grid)
        crash_layout.addWidget(inputs_group)
        crash_layout.addStretch()
        
        self.input_tabs.addTab(crash_widget, "Crash Barrier")
    
    def create_railing_tab(self):
        """Create the Railing tab"""
        railing_widget = QWidget()
        railing_widget.setStyleSheet("background-color: white;")
        railing_layout = QVBoxLayout(railing_widget)
        railing_layout.setContentsMargins(25, 25, 25, 25)
        railing_layout.setSpacing(20)
        
        # --- Inputs Group ---
        inputs_group = QGroupBox()
        inputs_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #a0a0a0;
                border-radius: 10px;
                margin-top: 10px;
            }
        """)
        inputs_layout = QVBoxLayout(inputs_group)
        inputs_layout.setContentsMargins(20, 20, 20, 20)
        inputs_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Inputs:")
        title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000; border: none;")
        inputs_layout.addWidget(title_label)
        
        # Create grid for inputs
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(20)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        
        # Row 0: Railing Width
        railing_width_label = QLabel("Railing Width (mm):")
        railing_width_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        railing_width_label.setMinimumWidth(180)
        self.railing_width = QLineEdit()
        self.railing_width.setValidator(QDoubleValidator(0.0, 1000.0, 1))
        self.style_input_field(self.railing_width)
        self.railing_width.textChanged.connect(self.recalculate_girders)
        
        grid.addWidget(railing_width_label, 0, 0, Qt.AlignLeft)
        grid.addWidget(self.railing_width, 0, 1, 1, 3)
        
        # Row 1: Railing Height
        railing_height_label = QLabel("Railing Height (mm):")
        railing_height_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        railing_height_label.setMinimumWidth(180)
        self.railing_height = QLineEdit()
        self.railing_height.setValidator(QDoubleValidator(0.0, 2000.0, 1))
        self.style_input_field(self.railing_height)
        self.railing_height.editingFinished.connect(self.validate_railing_height)
        
        grid.addWidget(railing_height_label, 1, 0, Qt.AlignLeft)
        grid.addWidget(self.railing_height, 1, 1, 1, 3)
        
        # Row 2: Railing Load
        railing_load_label = QLabel("Railing Load (kN/m)")
        railing_load_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        railing_load_label.setMinimumWidth(180)
        self.railing_load = QLineEdit()
        self.railing_load.setValidator(QDoubleValidator(0.0, 100.0, 2))
        self.style_input_field(self.railing_load)
        
        grid.addWidget(railing_load_label, 2, 0, Qt.AlignLeft)
        grid.addWidget(self.railing_load, 2, 1, 1, 3)
        
        # Row 3: Load Case
        load_case_label = QLabel("Load Case:")
        load_case_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        load_case_label.setMinimumWidth(180)
        self.railing_load_case = QComboBox()
        self.railing_load_case.addItems(VALUES_LOAD_CASE)
        self.railing_load_case.setCurrentText("Super-imposed Dead Load (SIDL)")
        self.style_input_field(self.railing_load_case)
        
        grid.addWidget(load_case_label, 3, 0, Qt.AlignLeft)
        grid.addWidget(self.railing_load_case, 3, 1, 1, 3)
        
        inputs_layout.addLayout(grid)
        railing_layout.addWidget(inputs_group)
        railing_layout.addStretch()
        
        self.input_tabs.addTab(railing_widget, "Railing")
    
    def create_wearing_course_tab(self):
        """Create the Wearing Course tab"""
        wearing_widget = QWidget()
        wearing_widget.setStyleSheet("background-color: white;")
        wearing_layout = QVBoxLayout(wearing_widget)
        wearing_layout.setContentsMargins(25, 25, 25, 25)
        wearing_layout.setSpacing(20)
        
        # --- Inputs Group ---
        inputs_group = QGroupBox()
        inputs_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #a0a0a0;
                border-radius: 10px;
                margin-top: 10px;
            }
        """)
        inputs_layout = QVBoxLayout(inputs_group)
        inputs_layout.setContentsMargins(20, 20, 20, 20)
        inputs_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Inputs:")
        title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000; border: none;")
        inputs_layout.addWidget(title_label)
        
        # Create grid for inputs
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(20)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        
        # Row 0: Wearing Course Material
        wc_material_label = QLabel("Wearing Course Material:")
        wc_material_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        wc_material_label.setMinimumWidth(180)
        self.wc_material = QComboBox()
        self.wc_material.addItems(VALUES_WEARING_COAT_MATERIAL)
        self.style_input_field(self.wc_material)
        
        grid.addWidget(wc_material_label, 0, 0, Qt.AlignLeft)
        grid.addWidget(self.wc_material, 0, 1, 1, 3)
        
        # Row 1: Wearing Coat Density
        wc_density_label = QLabel("Wearing Coat Density (kN/m^3):")
        wc_density_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        wc_density_label.setMinimumWidth(180)
        self.wc_density = QLineEdit()
        self.wc_density.setValidator(QDoubleValidator(0.0, 100.0, 2))
        self.style_input_field(self.wc_density)
        
        grid.addWidget(wc_density_label, 1, 0, Qt.AlignLeft)
        grid.addWidget(self.wc_density, 1, 1, 1, 3)
        
        # Row 2: Wearing Coat Thickness
        wc_thickness_label = QLabel("Wearing Coat Thickness (mm):")
        wc_thickness_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        wc_thickness_label.setMinimumWidth(180)
        self.wc_thickness = QLineEdit()
        self.wc_thickness.setValidator(QDoubleValidator(0.0, 500.0, 1))
        self.style_input_field(self.wc_thickness)
        
        grid.addWidget(wc_thickness_label, 2, 0, Qt.AlignLeft)
        grid.addWidget(self.wc_thickness, 2, 1, 1, 3)
        
        # Row 3: Load Case
        load_case_label = QLabel("Load Case:")
        load_case_label.setStyleSheet("font-size: 11px; color: #555; border: none;")
        load_case_label.setMinimumWidth(180)
        self.wc_load_case = QComboBox()
        self.wc_load_case.addItems(VALUES_LOAD_CASE)
        self.wc_load_case.setCurrentText("Dead Load of Wearing Course (DW)")
        self.style_input_field(self.wc_load_case)
        
        grid.addWidget(load_case_label, 3, 0, Qt.AlignLeft)
        grid.addWidget(self.wc_load_case, 3, 1, 1, 3)
        
        inputs_layout.addLayout(grid)
        wearing_layout.addWidget(inputs_group)
        wearing_layout.addStretch()
        
        self.input_tabs.addTab(wearing_widget, "Wearing Course")
    
    def create_lane_details_tab(self):
        """Create the Lane Details tab"""
        lane_widget = QWidget()
        lane_widget.setStyleSheet("background-color: white;")
        lane_layout = QVBoxLayout(lane_widget)
        lane_layout.setContentsMargins(25, 25, 25, 25)
        lane_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Inputs:")
        title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #000;")
        lane_layout.addWidget(title_label)
        
        # Create grid for inputs
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(20)
        grid.setColumnStretch(1, 1)
        
        # Row 0: No. of Lanes
        no_lanes_label = QLabel("No. of Lanes:")
        no_lanes_label.setStyleSheet("font-size: 11px; color: #555;")
        no_lanes_label.setMinimumWidth(150)
        self.no_of_lanes = QComboBox()
        self.no_of_lanes.addItems(VALUES_NO_OF_LANES)
        self.style_input_field(self.no_of_lanes)
        
        grid.addWidget(no_lanes_label, 0, 0, Qt.AlignLeft)
        grid.addWidget(self.no_of_lanes, 0, 1)
        
        # Row 1: Lane Width
        lane_width_label = QLabel("Lane Width (m):")
        lane_width_label.setStyleSheet("font-size: 11px; color: #555;")
        lane_width_label.setMinimumWidth(150)
        self.lane_width = QLineEdit()
        self.lane_width.setValidator(QDoubleValidator(0.0, 20.0, 2))
        self.style_input_field(self.lane_width)
        
        grid.addWidget(lane_width_label, 1, 0, Qt.AlignLeft)
        grid.addWidget(self.lane_width, 1, 1)
        
        lane_layout.addLayout(grid)
        lane_layout.addStretch()
        
        self.input_tabs.addTab(lane_widget, "Lane Details")
    
    def update_footpath_value(self, footpath_value):
        """Update visibility based on footpath selection"""
        self.footpath_value = footpath_value
        # Update visibility of footpath-related fields in Deck tab
        if hasattr(self, 'footpath_width'):
            self.footpath_width.setEnabled(footpath_value != "None")
            self.footpath_thickness.setEnabled(footpath_value != "None")
        self.recalculate_girders()  # Recalculate when footpath changes
        self.footpath_changed.emit(footpath_value)
    
    def get_overall_bridge_width(self):
        """Calculate Overall Bridge Width = Carriageway + Footpath + Crash Barrier/Railing"""
        try:
            overall_width = self.carriageway_width
            
            # Add footpath width
            if self.footpath_value != "None":
                footpath_width = float(self.footpath_width.text()) if self.footpath_width.text() else 0
                # Count footpaths: "Single Sided" = 1, "Both" = 2
                num_footpaths = 2 if self.footpath_value == "Both" else (1 if self.footpath_value == "Single Sided" else 0)
                overall_width += footpath_width * num_footpaths
            
            # Add crash barrier width
            crash_barrier_width = float(self.crash_barrier_width.text()) if self.crash_barrier_width.text() else DEFAULT_CRASH_BARRIER_WIDTH
            # Assuming crash barriers on both edges
            overall_width += crash_barrier_width * 2
            
            # Add railing width (if footpath present)
            if self.footpath_value != "None":
                railing_width = float(self.railing_width.text()) if self.railing_width.text() else DEFAULT_RAILING_WIDTH
                # Railings on both sides if footpath exists
                overall_width += railing_width * 2
            
            return overall_width
        except:
            return self.carriageway_width
    
    def recalculate_girders(self):
        """Recalculate based on the formula: (Overall Bridge Width - Deck Overhang) / Girder Spacing = No. of Girders"""
        if self.updating_fields:
            return
        
        try:
            overall_width = self.get_overall_bridge_width()
            
            # Update the display field if it exists
            if hasattr(self, 'overall_width_display'):
                self.overall_width_display.setText(f"{overall_width:.3f}")
            
            spacing = float(self.girder_spacing.text()) if self.girder_spacing.text() else DEFAULT_GIRDER_SPACING
            overhang = float(self.deck_overhang.text()) if self.deck_overhang.text() else DEFAULT_DECK_OVERHANG
            
            # Validate: spacing and overhang should be less than overall bridge width
            if spacing >= overall_width or overhang >= overall_width:
                self.no_of_girders.setText("")
                return
            
            # Calculate: No. of Girders = (Overall Width - 2*Overhang) / Spacing + 1
            if spacing > 0:
                no_girders = int(round((overall_width - 2 * overhang) / spacing)) + 1
                if no_girders >= 2:
                    self.updating_fields = True
                    self.no_of_girders.setText(str(no_girders))
                    self.updating_fields = False
        except:
            pass
    
    def on_girder_spacing_changed(self):
        """When user changes girder spacing, recalculate number of girders"""
        if not self.updating_fields:
            try:
                overall_width = self.get_overall_bridge_width()
                spacing_text = self.girder_spacing.text()
                if spacing_text:
                    spacing = float(spacing_text)
                    if spacing >= overall_width:
                        QMessageBox.warning(self, "Invalid Girder Spacing", 
                            f"Girder spacing ({spacing:.2f} m) must be less than overall bridge width ({overall_width:.2f} m).")
                        return
                self.recalculate_girders()
            except:
                pass
    
    def on_deck_overhang_changed(self):
        """When user changes deck overhang, recalculate number of girders"""
        if not self.updating_fields:
            try:
                overall_width = self.get_overall_bridge_width()
                overhang_text = self.deck_overhang.text()
                if overhang_text:
                    overhang = float(overhang_text)
                    if overhang >= overall_width:
                        QMessageBox.warning(self, "Invalid Deck Overhang", 
                            f"Deck overhang ({overhang:.2f} m) must be less than overall bridge width ({overall_width:.2f} m).")
                        return
                self.recalculate_girders()
            except:
                pass
    
    def on_no_of_girders_changed(self):
        """When user changes number of girders, recalculate girder spacing"""
        if not self.updating_fields:
            try:
                no_girders_text = self.no_of_girders.text()
                if no_girders_text:
                    no_girders = int(no_girders_text)
                    if no_girders < 2:
                        QMessageBox.warning(self, "Invalid Number of Girders", 
                            "Number of girders must be at least 2.")
                        return
                    
                    overall_width = self.get_overall_bridge_width()
                    overhang = float(self.deck_overhang.text()) if self.deck_overhang.text() else DEFAULT_DECK_OVERHANG
                    
                    # Calculate spacing: Spacing = (Overall Width - 2*Overhang) / (No. of Girders - 1)
                    if no_girders > 1:
                        new_spacing = (overall_width - 2 * overhang) / (no_girders - 1)
                        self.updating_fields = True
                        self.girder_spacing.setText(f"{new_spacing:.3f}")
                        self.updating_fields = False
            except:
                pass
    
    def on_footpath_width_changed(self):
        """When footpath width changes, recalculate girders"""
        if not self.updating_fields:
            self.recalculate_girders()
    
    def validate_footpath_width(self):
        """Validate footpath width meets minimum IRC 5 requirements"""
        try:
            if self.footpath_width.text():
                width = float(self.footpath_width.text())
                if width < MIN_FOOTPATH_WIDTH:
                    QMessageBox.critical(self, "Footpath Width Error", 
                        f"Footpath width must be at least {MIN_FOOTPATH_WIDTH} m as per IRC 5 Clause 104.3.6.")
        except:
            pass
    
    def validate_railing_height(self):
        """Validate railing height meets minimum IRC 5 requirements"""
        try:
            if self.railing_height.text():
                height = float(self.railing_height.text())
                if height < MIN_RAILING_HEIGHT:
                    QMessageBox.critical(self, "Railing Height Error", 
                        f"Railing height must be at least {MIN_RAILING_HEIGHT} m as per IRC 5 Clauses 109.7.2.3 and 109.7.2.4.")
        except:
            pass
    
    def validate_safety_kerb_width(self):
        """Validate safety kerb width meets minimum IRC 5 requirements"""
        try:
            if self.safety_kerb_width.text():
                width = float(self.safety_kerb_width.text())
                if width < MIN_SAFETY_KERB_WIDTH:
                    QMessageBox.critical(self, "Safety Kerb Width Error", 
                        f"Safety kerb width must be at least {MIN_SAFETY_KERB_WIDTH} m (750 mm) as per IRC 5 Clause 101.41.")
        except:
            pass
    
    def update_footpath_thickness(self):
        """Pre-fill footpath thickness with deck thickness"""
        if self.deck_thickness.text() and not self.footpath_thickness.text():
            self.footpath_thickness.setText(self.deck_thickness.text())
    
    def on_crash_barrier_type_changed(self, barrier_type):
        """Warn if flexible/semi-rigid barrier without footpath"""
        if (barrier_type in ["Flexible", "Semi-Rigid"]) and (self.footpath_value == "None"):
            QMessageBox.critical(self, "Crash Barrier Type Not Permitted", 
                f"{barrier_type} crash barriers are not permitted on bridges without an outer footpath per IRC 5 Clause 109.6.4.")


class SectionPropertiesTab(QWidget):
    """Sub-tab for Section Properties with custom navigation layout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nav_buttons = []
        self.init_ui()

    def init_ui(self):
        """Initialize styled navigation and content panels."""
        self.setStyleSheet("background-color: #f0f0f0;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Top navigation bar (horizontal)
        nav_bar = QWidget()
        nav_bar.setStyleSheet("background-color: transparent;")
        nav_bar_layout = QHBoxLayout(nav_bar)
        nav_bar_layout.setContentsMargins(0, 0, 0, 0)
        nav_bar_layout.setSpacing(0)
        
        main_layout.addWidget(nav_bar)

        # Content frame
        content_frame = QFrame()
        content_frame.setObjectName("sectionContentFrame")
        content_frame.setStyleSheet("""
            QFrame#sectionContentFrame {
                background-color: #f0f0f0;
                border: none;
            }
        """)
        content_inner_layout = QVBoxLayout(content_frame)
        content_inner_layout.setContentsMargins(0, 0, 0, 0)
        content_inner_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setObjectName("sectionStack")
        self.stack.setStyleSheet("QStackedWidget#sectionStack { background-color: transparent; }")
        content_inner_layout.addWidget(self.stack)

        main_layout.addWidget(content_frame, 1)

        sections = [
            ("Girder Details:", GirderDetailsTab),
            ("Stiffener Details:", StiffenerDetailsTab),
            ("Cross-Bracing Details:", CrossBracingDetailsTab),
            ("End Diaphragm Details:", EndDiaphragmDetailsTab),
        ]

        for i, (label, widget_class) in enumerate(sections):
            btn = QPushButton(label)
            btn.setObjectName("sectionNavBtn")
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton#sectionNavBtn {
                    background-color: white;
                    color: #333;
                    border: 1px solid #b0b0b0;
                    border-right: none;
                    padding: 10px 20px;
                    text-align: center;
                    font-size: 11px;
                    font-weight: normal;
                    min-height: 30px;
                }
                QPushButton#sectionNavBtn:first {
                    border-top-left-radius: 5px;
                    border-bottom-left-radius: 5px;
                }
                QPushButton#sectionNavBtn:last {
                    border-right: 1px solid #b0b0b0;
                    border-top-right-radius: 5px;
                    border-bottom-right-radius: 5px;
                }
                QPushButton#sectionNavBtn:checked {
                    background-color: #90AF13;
                    color: white;
                    font-weight: bold;
                    border: 1px solid #90AF13;
                }
                QPushButton#sectionNavBtn:hover:!checked {
                    background-color: #f5f5f5;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.switch_section(idx))
            self.nav_buttons.append(btn)
            nav_bar_layout.addWidget(btn)

            section_widget = widget_class()
            self.stack.addWidget(section_widget)

        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
            self.stack.setCurrentIndex(0)

    def switch_section(self, index):
        """Switch the stacked widget page and update navigation states."""
        self.stack.setCurrentIndex(index)
        for btn_index, button in enumerate(self.nav_buttons):
            button.setChecked(btn_index == index)


class GirderDetailsTab(QWidget):
    """Tab for Girder Details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
        )
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(10)

        # Common label style
        label_style = "QLabel { color: #333333; font-size: 11px; background-color: transparent; }"
        title_style = "QLabel { color: #333333; font-weight: bold; font-size: 12px; margin-bottom: 10px; background-color: transparent; }"

        # --- Top Section ---
        top_group = QGroupBox()
        top_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #b0b0b0;
                border-radius: 8px;
            }
        """)
        top_layout = QGridLayout(top_group)
        top_layout.setContentsMargins(15, 15, 15, 15)
        top_layout.setHorizontalSpacing(20)
        top_layout.setVerticalSpacing(15)

        # Row 0
        lbl_girder = QLabel("Select Girder:")
        lbl_girder.setStyleSheet(label_style)
        top_layout.addWidget(lbl_girder, 0, 0)
        
        self.select_girder = QComboBox()
        self.select_girder.addItems(["Girder 1", "Girder 2", "Girder 3"]) # Placeholder items
        apply_field_style(self.select_girder)
        top_layout.addWidget(self.select_girder, 0, 1)
        
        # Spacer
        top_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 2)

        # Row 1
        lbl_span = QLabel("Span:")
        lbl_span.setStyleSheet(label_style)
        top_layout.addWidget(lbl_span, 1, 0)
        
        self.span_combo = QComboBox()
        self.span_combo.addItems(["Custom", "Span 1", "Span 2"])
        apply_field_style(self.span_combo)
        top_layout.addWidget(self.span_combo, 1, 1)

        lbl_member_id = QLabel("Member ID:")
        lbl_member_id.setStyleSheet(label_style)
        top_layout.addWidget(lbl_member_id, 1, 3)
        
        self.member_id = QLineEdit("G1-1")
        apply_field_style(self.member_id)
        top_layout.addWidget(self.member_id, 1, 4)

        # Row 2
        lbl_dist = QLabel("Distance from left edge (m):")
        lbl_dist.setStyleSheet(label_style)
        top_layout.addWidget(lbl_dist, 2, 0)
        
        dist_layout = QHBoxLayout()
        dist_layout.setSpacing(10)
        
        dist_start_layout = QVBoxLayout()
        self.dist_start = QLineEdit()
        apply_field_style(self.dist_start)
        self.dist_start.setFixedWidth(80)
        dist_start_layout.addWidget(self.dist_start)
        
        dist_start_label = QLabel("Start")
        dist_start_label.setAlignment(Qt.AlignCenter)
        dist_start_label.setStyleSheet("font-size: 10px; color: #555555;")
        dist_start_layout.addWidget(dist_start_label)
        dist_layout.addLayout(dist_start_layout)

        dist_end_layout = QVBoxLayout()
        self.dist_end = QLineEdit()
        apply_field_style(self.dist_end)
        self.dist_end.setFixedWidth(80)
        dist_end_layout.addWidget(self.dist_end)
        
        dist_end_label = QLabel("End")
        dist_end_label.setAlignment(Qt.AlignCenter)
        dist_end_label.setStyleSheet("font-size: 10px; color: #555555;")
        dist_end_layout.addWidget(dist_end_label)
        dist_layout.addLayout(dist_end_layout)
        
        top_layout.addLayout(dist_layout, 2, 1)

        lbl_length = QLabel("Length (m):")
        lbl_length.setStyleSheet(label_style)
        top_layout.addWidget(lbl_length, 2, 3)
        
        self.length_input = QLineEdit()
        apply_field_style(self.length_input)
        top_layout.addWidget(self.length_input, 2, 4)

        container_layout.addWidget(top_group)

        # --- Main Content (Left/Right) ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # Left Column
        left_column = QVBoxLayout()
        left_column.setSpacing(10)

        # Section Inputs Group
        inputs_group = QGroupBox()
        inputs_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #b0b0b0;
                border-radius: 8px;
                padding-top: 10px;
            }
        """)
        inputs_layout = QVBoxLayout(inputs_group)
        inputs_layout.setContentsMargins(15, 15, 15, 15)
        
        inputs_title = QLabel("Section Inputs:")
        inputs_title.setStyleSheet(title_style)
        inputs_layout.addWidget(inputs_title)

        inputs_grid = QGridLayout()
        inputs_grid.setHorizontalSpacing(15)
        inputs_grid.setVerticalSpacing(15)
        inputs_grid.setColumnStretch(1, 1)

        row = 0
        lbl_design = QLabel("Design:")
        lbl_design.setStyleSheet(label_style)
        inputs_grid.addWidget(lbl_design, row, 0)
        
        self.design_combo = QComboBox()
        self.design_combo.addItems(["Customized", "Standard"])
        apply_field_style(self.design_combo)
        inputs_grid.addWidget(self.design_combo, row, 1)
        row += 1

        lbl_type = QLabel("Type:")
        lbl_type.setStyleSheet(label_style)
        inputs_grid.addWidget(lbl_type, row, 0)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Welded", "Rolled"])
        apply_field_style(self.type_combo)
        inputs_grid.addWidget(self.type_combo, row, 1)
        row += 1

        lbl_symmetry = QLabel("Symmetry:")
        lbl_symmetry.setStyleSheet(label_style)
        inputs_grid.addWidget(lbl_symmetry, row, 0)
        
        self.symmetry_combo = QComboBox()
        self.symmetry_combo.addItems(["Girder Symmetric", "Asymmetric"])
        apply_field_style(self.symmetry_combo)
        inputs_grid.addWidget(self.symmetry_combo, row, 1)
        row += 1

        lbl_depth = QLabel("Total Depth (mm):")
        lbl_depth.setStyleSheet(label_style)
        inputs_grid.addWidget(lbl_depth, row, 0)
        
        self.total_depth = QLineEdit()
        apply_field_style(self.total_depth)
        inputs_grid.addWidget(self.total_depth, row, 1)
        row += 1

        lbl_web_thick = QLabel("Web Thickness (mm):")
        lbl_web_thick.setStyleSheet(label_style)
        inputs_grid.addWidget(lbl_web_thick, row, 0)
        
        self.web_thickness = QComboBox()
        self.web_thickness.addItems(["All", "Custom"])
        apply_field_style(self.web_thickness)
        inputs_grid.addWidget(self.web_thickness, row, 1)
        row += 1

        lbl_top_width = QLabel("Width of Top Flange (mm):")
        lbl_top_width.setStyleSheet(label_style)
        inputs_grid.addWidget(lbl_top_width, row, 0)
        
        self.top_flange_width = QLineEdit()
        apply_field_style(self.top_flange_width)
        inputs_grid.addWidget(self.top_flange_width, row, 1)
        row += 1

        lbl_top_thick = QLabel("Top Flange Thickness (mm):")
        lbl_top_thick.setStyleSheet(label_style)
        inputs_grid.addWidget(lbl_top_thick, row, 0)
        
        self.top_flange_thickness = QComboBox()
        self.top_flange_thickness.addItems(["All", "Custom"])
        apply_field_style(self.top_flange_thickness)
        inputs_grid.addWidget(self.top_flange_thickness, row, 1)
        row += 1

        lbl_bot_width = QLabel("Width of Bottom Flange (mm):")
        lbl_bot_width.setStyleSheet(label_style)
        inputs_grid.addWidget(lbl_bot_width, row, 0)
        
        self.bottom_flange_width = QLineEdit()
        apply_field_style(self.bottom_flange_width)
        inputs_grid.addWidget(self.bottom_flange_width, row, 1)
        row += 1

        lbl_bot_thick = QLabel("Bottom Flange Thickness (mm):")
        lbl_bot_thick.setStyleSheet(label_style)
        inputs_grid.addWidget(lbl_bot_thick, row, 0)
        
        self.bottom_flange_thickness = QComboBox()
        self.bottom_flange_thickness.addItems(["All", "Custom"])
        apply_field_style(self.bottom_flange_thickness)
        inputs_grid.addWidget(self.bottom_flange_thickness, row, 1)
        row += 1

        inputs_layout.addLayout(inputs_grid)
        left_column.addWidget(inputs_group)

        # Restraints Group
        restraints_group = QGroupBox()
        restraints_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #b0b0b0;
                border-radius: 8px;
            }
        """)
        restraints_layout = QGridLayout(restraints_group)
        restraints_layout.setContentsMargins(15, 15, 15, 15)
        restraints_layout.setHorizontalSpacing(15)
        restraints_layout.setVerticalSpacing(15)
        restraints_layout.setColumnStretch(1, 1)

        r_row = 0
        lbl_torsion = QLabel("Torsional Restraint:")
        lbl_torsion.setStyleSheet(label_style)
        restraints_layout.addWidget(lbl_torsion, r_row, 0)
        
        self.torsional_restraint = QComboBox()
        self.torsional_restraint.addItems(["Fully Restrained", "Free"])
        apply_field_style(self.torsional_restraint)
        restraints_layout.addWidget(self.torsional_restraint, r_row, 1)
        r_row += 1

        lbl_warping = QLabel("Warping Restraint:")
        lbl_warping.setStyleSheet(label_style)
        restraints_layout.addWidget(lbl_warping, r_row, 0)
        
        self.warping_restraint = QComboBox()
        self.warping_restraint.addItems(["Both flanges fully restrained", "Free"])
        apply_field_style(self.warping_restraint)
        restraints_layout.addWidget(self.warping_restraint, r_row, 1)
        r_row += 1

        lbl_web_type = QLabel("Web Type*:")
        lbl_web_type.setStyleSheet(label_style)
        restraints_layout.addWidget(lbl_web_type, r_row, 0)
        
        self.web_type = QComboBox()
        self.web_type.addItems(["Thin Web with ITS", "Stocky Web"])
        apply_field_style(self.web_type)
        restraints_layout.addWidget(self.web_type, r_row, 1)

        left_column.addWidget(restraints_group)
        content_layout.addLayout(left_column, 1)

        # Right Column
        right_column = QVBoxLayout()
        right_column.setSpacing(10)

        # Image Preview
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                background-color: #d9d9d9;
                border: 1px solid #b0b0b0;
                border-radius: 8px;
            }
        """)
        image_frame.setMinimumHeight(200)
        image_layout = QVBoxLayout(image_frame)
        image_label = QLabel("Dynamic Image")
        image_label.setStyleSheet("color: #333333; font-weight: bold;")
        image_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(image_label)
        
        right_column.addWidget(image_frame)

        # Section Properties Group
        props_group = QGroupBox()
        props_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #b0b0b0;
                border-radius: 8px;
                padding-top: 10px;
            }
        """)
        props_layout = QVBoxLayout(props_group)
        props_layout.setContentsMargins(15, 15, 15, 15)
        
        props_title = QLabel("Section Properties:")
        props_title.setStyleSheet(title_style)
        props_layout.addWidget(props_title)

        props_grid = QGridLayout()
        props_grid.setHorizontalSpacing(15)
        props_grid.setVerticalSpacing(10)
        props_grid.setColumnStretch(1, 1)

        properties = [
            ("Mass, M (Kg/m)", ""),
            ("Sectional Area, a (cm2)", ""),
            ("2nd Moment of Area, Iz (cm4)", ""),
            ("2nd Moment of Area, Iv (cm4)", ""),
            ("Radius of Gyration, rz (cm)", ""),
            ("Radius of Gyration, rv (cm)", ""),
            ("Elastic Modulus, Zz (cm3)", ""),
            ("Elastic Modulus, Zv (cm3)", ""),
            ("Plastic Modulus, Zuz (cm3)", ""),
            ("Plastic Modulus, Zuv (cm3)", ""),
            ("Torsion Constant, It (cm4)", ""),
            ("Warping Constant, Iw (cm6)", ""),
        ]

        self.prop_inputs = {}
        for i, (label_text, _) in enumerate(properties):
            lbl_prop = QLabel(label_text)
            lbl_prop.setStyleSheet(label_style)
            props_grid.addWidget(lbl_prop, i, 0)
            
            line_edit = QLineEdit()
            line_edit.setReadOnly(True)
            apply_field_style(line_edit)
            props_grid.addWidget(line_edit, i, 1)
            self.prop_inputs[label_text] = line_edit

        props_layout.addLayout(props_grid)
        right_column.addWidget(props_group)

        content_layout.addLayout(right_column, 1)
        container_layout.addLayout(content_layout)
        container_layout.addStretch()


class StiffenerDetailsTab(QWidget):
    """Tab for Stiffener Details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
        )
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        form_frame = QFrame()
        form_frame.setStyleSheet("QFrame { background: transparent; }")
        self.form_layout = QGridLayout(form_frame)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setHorizontalSpacing(28)
        self.form_layout.setVerticalSpacing(20)
        self.form_layout.setColumnMinimumWidth(0, 240)
        self.form_layout.setColumnStretch(1, 1)
        container_layout.addWidget(form_frame)
        container_layout.addStretch()

        row = 0
        self.method_combo = QComboBox()
        self.method_combo.addItems(VALUES_STIFFENER_DESIGN)
        apply_field_style(self.method_combo)
        row = self.add_row(row, "Stiffener design method:", self.method_combo)

        self.thick_combo = QComboBox()
        self.thick_combo.addItems(["Optimized", "All"])
        apply_field_style(self.thick_combo)
        row = self.add_row(row, "Stiffener Plate Thickness (mm):", self.thick_combo)

        self.spacing_field = OptimizableField("Stiffener Spacing")
        self.spacing_field.mode_combo.clear()
        self.spacing_field.mode_combo.addItems(["Optimized", "Customized"])
        self.spacing_field.on_mode_changed(self.spacing_field.mode_combo.currentText())
        self.prepare_optimizable_field(self.spacing_field)
        row = self.add_row(row, "Stiffener Spacing (mm):", self.spacing_field)

        self.long_req_combo = QComboBox()
        self.long_req_combo.addItems(VALUES_YES_NO)
        apply_field_style(self.long_req_combo)
        row = self.add_row(row, "Longitudinal stiffener requirement:", self.long_req_combo)

        self.long_thick_combo = QComboBox()
        self.long_thick_combo.addItems(["Optimized", "All"])
        self.long_thick_combo.setEnabled(False)
        apply_field_style(self.long_thick_combo)
        self.add_row(row, "Longitudinal stiffener thickness:", self.long_thick_combo)

        self.long_req_combo.currentTextChanged.connect(self.on_long_req_changed)

    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("font-size: 13px; color: #2f2f2f; font-weight: 600;")
        return label

    def add_row(self, row, text, widget):
        label = self.create_label(text)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.form_layout.addWidget(label, row, 0, Qt.AlignVCenter)
        self.form_layout.addWidget(widget, row, 1)
        return row + 1

    def prepare_optimizable_field(self, field):
        field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        apply_field_style(field.mode_combo)
        apply_field_style(field.input_field)

    def on_long_req_changed(self, text):
        """Enable/disable longitudinal stiffener thickness based on requirement"""
        self.long_thick_combo.setEnabled(text == "Yes")


class CrossBracingDetailsTab(QWidget):
    """Tab for Cross-Bracing Details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
        )
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        form_frame = QFrame()
        form_frame.setStyleSheet("QFrame { background: transparent; }")
        self.form_layout = QGridLayout(form_frame)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setHorizontalSpacing(28)
        self.form_layout.setVerticalSpacing(20)
        self.form_layout.setColumnMinimumWidth(0, 210)
        self.form_layout.setColumnStretch(1, 1)
        container_layout.addWidget(form_frame)
        container_layout.addStretch()

        row = 0
        self.type_combo = QComboBox()
        self.type_combo.addItems(VALUES_CROSS_BRACING_TYPE)
        apply_field_style(self.type_combo)
        row = self.add_row(row, "Type of Bracing:", self.type_combo)

        self.section_combo = QComboBox()
        self.section_combo.addItems([
            "Select Section",
            "ISA 50x50x6", "ISA 65x65x6", "ISA 75x75x6", "ISA 90x90x8",
            "ISA 100x100x8", "ISA 110x110x10", "ISA 130x130x10",
            "2-ISA 50x50x6 (LL)", "2-ISA 65x65x6 (LL)", "2-ISA 75x75x6 (LL)",
            "2-ISA 50x50x6 (SL)", "2-ISA 65x65x6 (SL)", "2-ISA 75x75x6 (SL)",
            "ISMC 75", "ISMC 100", "ISMC 125", "ISMC 150",
            "2-ISMC 75", "2-ISMC 100", "2-ISMC 125"
        ])
        apply_field_style(self.section_combo)
        row = self.add_row(row, "Bracing Section:", self.section_combo)

        self.bracket_combo = QComboBox()
        self.bracket_combo.addItems([
            "Select Section",
            "ISA 50x50x6", "ISA 65x65x6", "ISA 75x75x6", "ISA 90x90x8",
            "ISA 100x100x8", "ISA 110x110x10",
            "2-ISA 50x50x6 (LL)", "2-ISA 65x65x6 (LL)", "2-ISA 75x75x6 (LL)",
            "2-ISA 50x50x6 (SL)", "2-ISA 65x65x6 (SL)", "2-ISA 75x75x6 (SL)",
            "ISMC 75", "ISMC 100", "ISMC 125",
            "2-ISMC 75", "2-ISMC 100"
        ])
        self.bracket_combo.setEnabled(False)
        apply_field_style(self.bracket_combo)
        row = self.add_row(row, "Bracket Section:", self.bracket_combo)

        self.spacing_input = QLineEdit()
        self.spacing_input.setPlaceholderText("Enter spacing in mm")
        self.spacing_input.setValidator(QDoubleValidator(0, 100000, 2))
        apply_field_style(self.spacing_input)
        self.add_row(row, "Spacing (mm):", self.spacing_input)

        self.type_combo.currentTextChanged.connect(self.on_bracing_type_changed)

    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("font-size: 13px; color: #2f2f2f; font-weight: 600;")
        return label

    def add_row(self, row, text, widget):
        label = self.create_label(text)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.form_layout.addWidget(label, row, 0, Qt.AlignVCenter)
        self.form_layout.addWidget(widget, row, 1)
        return row + 1

    def on_bracing_type_changed(self, text):
        """Enable/disable bracket section based on bracing type"""
        has_bracket = "bracket" in text.lower()
        self.bracket_combo.setEnabled(has_bracket)


class EndDiaphragmDetailsTab(QWidget):
    """Tab for End Diaphragm Details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plate_rows = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
        )
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        form_frame = QFrame()
        form_frame.setStyleSheet("QFrame { background: transparent; }")
        self.form_layout = QGridLayout(form_frame)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setHorizontalSpacing(28)
        self.form_layout.setVerticalSpacing(20)
        self.form_layout.setColumnMinimumWidth(0, 230)
        self.form_layout.setColumnStretch(1, 1)
        container_layout.addWidget(form_frame)
        container_layout.addStretch()

        row = 0
        self.type_combo = QComboBox()
        self.type_combo.addItems(VALUES_END_DIAPHRAGM_TYPE)
        apply_field_style(self.type_combo)
        self.form_layout.addWidget(self.create_label("Type of Section:"), row, 0, Qt.AlignVCenter)
        self.form_layout.addWidget(self.type_combo, row, 1)
        row += 1

        self.is_section_label = self.create_label("Select IS Beam Section:")
        self.is_beam_combo = QComboBox()
        self.is_beam_combo.addItems([
            "Select Section",
            "ISMB 100", "ISMB 125", "ISMB 150", "ISMB 175", "ISMB 200",
            "ISMB 225", "ISMB 250", "ISMB 300", "ISMB 350", "ISMB 400",
            "ISWB 150", "ISWB 175", "ISWB 200", "ISWB 225", "ISWB 250",
            "ISWB 300", "ISWB 350", "ISWB 400"
        ])
        apply_field_style(self.is_beam_combo)
        self.form_layout.addWidget(self.is_section_label, row, 0, Qt.AlignVCenter)
        self.form_layout.addWidget(self.is_beam_combo, row, 1)
        row += 1

        self.top_width_field = OptimizableField("Top Flange Width")
        self.prepare_optimizable_field(self.top_width_field)
        row = self.add_plate_row(row, "Top Flange Width (mm):", self.top_width_field)

        self.top_thick_field = OptimizableField("Top Flange Thickness")
        self.prepare_optimizable_field(self.top_thick_field)
        row = self.add_plate_row(row, "Top Flange Thickness (mm):", self.top_thick_field)

        self.bottom_width_field = OptimizableField("Bottom Flange Width")
        self.prepare_optimizable_field(self.bottom_width_field)
        row = self.add_plate_row(row, "Bottom Flange Width (mm):", self.bottom_width_field)

        self.bottom_thick_field = OptimizableField("Bottom Flange Thickness")
        self.prepare_optimizable_field(self.bottom_thick_field)
        row = self.add_plate_row(row, "Bottom Flange Thickness (mm):", self.bottom_thick_field)

        self.depth_field = OptimizableField("Depth of Section")
        self.prepare_optimizable_field(self.depth_field)
        row = self.add_plate_row(row, "Depth of Section (mm):", self.depth_field)

        self.web_thick_field = OptimizableField("Web Thickness")
        self.prepare_optimizable_field(self.web_thick_field)
        row = self.add_plate_row(row, "Web Thickness (mm):", self.web_thick_field)

        self.spacing_input = QLineEdit()
        self.spacing_input.setPlaceholderText("Enter spacing in mm")
        self.spacing_input.setValidator(QDoubleValidator(0, 100000, 2))
        apply_field_style(self.spacing_input)
        self.spacing_label = self.create_label("Spacing (mm):")
        self.form_layout.addWidget(self.spacing_label, row, 0, Qt.AlignVCenter)
        self.form_layout.addWidget(self.spacing_input, row, 1)

        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        self.on_type_changed(self.type_combo.currentText())

    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("font-size: 13px; color: #2f2f2f; font-weight: 600;")
        return label

    def prepare_optimizable_field(self, field):
        field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        apply_field_style(field.mode_combo)
        apply_field_style(field.input_field)

    def add_plate_row(self, row, text, widget):
        label = self.create_label(text)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.form_layout.addWidget(label, row, 0, Qt.AlignVCenter)
        self.form_layout.addWidget(widget, row, 1)
        self.plate_rows.append((label, widget))
        return row + 1

    def on_type_changed(self, text):
        """Show/hide sections based on diaphragm type"""
        is_same = text == "Same as cross-bracing"
        is_rolled = text == "Rolled Beam Section"

        self.is_section_label.setVisible(is_rolled)
        self.is_beam_combo.setVisible(is_rolled)

        show_plate = text == "Plate Girder Section"
        for label, widget in self.plate_rows:
            label.setVisible(show_plate)
            widget.setVisible(show_plate)

        if is_same:
            self.spacing_input.setEnabled(False)
            self.spacing_label.setEnabled(False)
            self.spacing_input.clear()
        else:
            self.spacing_input.setEnabled(True)
            self.spacing_label.setEnabled(True)


class AdditionalInputsWidget(QWidget):
    """Main widget for Additional Inputs with tabbed interface"""
    
    def __init__(self, footpath_value="None", carriageway_width=7.5, parent=None):
        super().__init__(parent)
        self.footpath_value = footpath_value
        self.carriageway_width = carriageway_width
        self.init_ui()
    
    def init_ui(self):
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: white;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: white; border-bottom: 1px solid #d0d0d0;")
        header_widget.setMinimumHeight(50)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("Additional Inputs")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        
        main_layout.addWidget(header_widget)
        
        # Main tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #ffffff;
                margin-top: -1px;
            }
            QTabBar {
                background: #ffffff;
            }
            QTabBar::tab {
                background: #e9e9e9;
                color: #3a3a3a;
                border: 1px solid #d1d1d1;
                border-bottom: none;
                padding: 10px 22px;
                margin-right: 4px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: #90af13;
                color: #ffffff;
                border: 1px solid #90af13;
                border-bottom: none;
            }
            QTabBar::tab:hover:!selected {
                background: #f5f5f5;
            }
            QTabWidget {
                background-color: white;
            }
        """)
        
        # Sub-Tab 1: Typical Section Details
        self.bridge_geometry_tab = BridgeGeometryTab(self.footpath_value, self.carriageway_width)
        self.tabs.addTab(self.bridge_geometry_tab, "Typical Section Details")
        
        # Sub-Tab 2: Member Properties
        self.section_properties_tab = SectionPropertiesTab()
        self.tabs.addTab(self.section_properties_tab, "Member Properties")
        
        # Sub-Tab 3: Loading
        loading_tab = self.create_placeholder_tab(
            "Loading",
            "This tab will contain:\n\n" +
            "• Dead Load (Self Weight, Wearing Coat, etc.)\n" +
            "• Live Load (IRC Vehicles, Custom Loads)\n" +
            "• Lateral Load (Wind, Seismic)\n\n" +
            "Implementation in progress..."
        )
        self.tabs.addTab(loading_tab, "Loading")
        
        # Sub-Tab 4: Support Conditions
        support_tab = self.create_placeholder_tab(
            "Support Conditions",
            "This tab will contain:\n\n" +
            "• Left Support (Fixed/Pinned)\n" +
            "• Right Support (Fixed/Pinned)\n" +
            "• Bearing Length (mm)\n\n" +
            "Note: If bearing length is 0, the end bearing\n" +
            "stiffener will not be designed.\n\n" +
            "Implementation in progress..."
        )
        self.tabs.addTab(support_tab, "Support Conditions")
        
        # Sub-Tab 5: Design Options
        shear_connection_tab = self.create_placeholder_tab(
            "Design Options",
            "This tab will contain:\n\n" +
            "• Shear Connector Type\n" +
            "• Connector Size and Spacing\n" +
            "• Connection Details\n\n" +
            "Implementation in progress..."
        )
        self.tabs.addTab(shear_connection_tab, "Design Options")
        
        # Sub-Tab 6: Design Options (Cont.)
        analysis_design_tab = self.create_placeholder_tab(
            "Design Options (Cont.)",
            "This tab will contain:\n\n" +
            "• Analysis Method\n" +
            "• Design Code Options\n" +
            "• Safety Factors\n" +
            "• Other Design Parameters\n\n" +
            "Implementation in progress..."
        )
        self.tabs.addTab(analysis_design_tab, "Design Options (Cont.)")
        
        main_layout.addWidget(self.tabs)
    
    def create_placeholder_tab(self, title, description):
        """Create a styled placeholder tab with title and description"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Icon or visual indicator
        icon_label = QLabel("🚧")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-top: 20px;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Status
        status_label = QLabel("Under Development")
        status_label.setStyleSheet("""
            font-size: 14px;
            color: #f39c12;
            font-weight: bold;
            margin-bottom: 20px;
        """)
        status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #666;
            line-height: 1.6;
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setMaximumWidth(600)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        return widget
    
    def update_footpath_value(self, footpath_value):
        """Update footpath value across all tabs"""
        self.footpath_value = footpath_value
        self.bridge_geometry_tab.update_footpath_value(footpath_value)
