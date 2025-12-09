import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QComboBox, QScrollArea, QLabel, QFormLayout, QLineEdit, QGroupBox, QSizePolicy, QMessageBox, QInputDialog, QDialog, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, QRegularExpression, QSize
from PySide6.QtGui import QPixmap, QDoubleValidator, QRegularExpressionValidator, QIcon
from PySide6.QtSvgWidgets import *
from osbridge.backend.common import *
from osbridge.ui.additional_inputs import AdditionalInputsWidget
from osbridge.ui.custom_buttons import DockCustomButton


class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()  # Prevent changing selection on scroll

def apply_field_style(widget):
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    widget.setMinimumHeight(28)
    
    if isinstance(widget, QComboBox):
        style = """
            QComboBox{
                padding: 2px;
                border: 1px solid black;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
            QComboBox::drop-down{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border-left: 0px;
            }
            QComboBox::down-arrow{
                image: url(:/vectors/arrow_down_light.svg);
                width: 20px;
                height: 20px;
                margin-right: 8px;
            }
            QComboBox::down-arrow:on {
                image: url(:/vectors/arrow_up_light.svg);
                width: 20px;
                height: 20px;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView{
                background-color: white;
                border: 1px solid black;
                outline: none;
            }
            QComboBox QAbstractItemView::item{
                color: black;
                background-color: white;
                border: none;
                border: 1px solid white;
                border-radius: 0;
                padding: 2px;
            }
            QComboBox QAbstractItemView::item:hover{
                border: 1px solid #90AF13;
                background-color: #90AF13;
                color: black;
            }
            QComboBox QAbstractItemView::item:selected{
                background-color: #90AF13;
                color: black;
                border: 1px solid #90AF13;
            }
            QComboBox QAbstractItemView::item:selected:hover{
                background-color: #90AF13;
                color: black;
                border: 1px solid #94b816;
            } 
        """
        widget.setStyleSheet(style)
    elif isinstance(widget, QLineEdit):
        widget.setStyleSheet("""
            QLineEdit {
                padding: 1px 7px;
                border: 1px solid #070707;
                border-radius: 6px;
                background-color: white;
                color: #000000;
                font-weight: normal;
            }
        """)

def create_group_box(title):
    """Create a styled group box"""
    group_box = QGroupBox(title)
    group_box.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            font-size: 12px;
            color: #333;
            border: 1px solid #90AF13;
            border-radius: 4px;
            margin-top: 0.8em;
            padding: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 8px;
            padding: 0 4px;
            margin-top: 4px;
            background-color: white;
            color: #333;
        }
    """)
    return group_box


def create_form_row(label_text, widget, tooltip=None):
    """Create a horizontal layout with label and widget side by side"""
    row = QHBoxLayout()
    row.setSpacing(10)
    
    label = QLabel(label_text)
    label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
    label.setMinimumWidth(140)
    label.setMaximumWidth(140)
    
    if tooltip:
        widget.setToolTip(tooltip)
    
    row.addWidget(label)
    row.addWidget(widget, 1)
    
    return row


class InputDock(QWidget):
    def __init__(self, backend, parent):
        super().__init__()
        self.parent = parent
        self.backend = backend
        self.input_widget = None
        self.structure_type_combo = None
        self.project_location_combo = None
        self.custom_location_input = None
        self.footpath_combo = None
        self.additional_inputs_window = None

        self.setStyleSheet("background: transparent;")
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.left_container = QWidget()

        # Get input fields from backend
        input_field_list = self.backend.input_values()

        self.build_left_panel(input_field_list)
        self.main_layout.addWidget(self.left_container)

        # Toggle strip
        self.toggle_strip = QWidget()
        self.toggle_strip.setStyleSheet("background-color: #90AF13;")
        self.toggle_strip.setFixedWidth(6)
        toggle_layout = QVBoxLayout(self.toggle_strip)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(0)
        toggle_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.toggle_btn = QPushButton("❮")
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setFixedSize(6, 60)
        self.toggle_btn.setToolTip("Hide panel")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c8408;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 0px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5e7407;
            }
        """)
        toggle_layout.addStretch()
        toggle_layout.addWidget(self.toggle_btn)
        toggle_layout.addStretch()
        self.main_layout.addWidget(self.toggle_strip)

    def get_validator(self, validator):
        if validator == 'Int Validator':
            return QRegularExpressionValidator(QRegularExpression("^(0|[1-9]\\d*)(\\.\\d+)?$"))
        elif validator == 'Double Validator':
            return QDoubleValidator()
        else:
            return None
    
    def on_structure_type_changed(self, text):
        """Handle structure type combo box changes"""
        if text == "Other":
            if hasattr(self, 'structure_note'):
                self.structure_note.setVisible(True)
        else:
            if hasattr(self, 'structure_note'):
                self.structure_note.setVisible(False)
    
    def on_project_location_changed(self, text):
        """Handle project location combo box changes"""
        if text == "Custom":
            custom_location, ok = QInputDialog.getText(
                self,
                "Custom Location",
                "Enter city name for load calculations",
                QLineEdit.Normal,
                ""
            )
            if ok and custom_location.strip():
                self.custom_location_input = custom_location.strip()
                QMessageBox.information(
                    self,
                    "Custom Location Set",
                    f"Custom location '{custom_location.strip()}' has been set.\n\n"
                    f"Note: Please ensure load calculation data is available for this location.",
                    QMessageBox.Ok
                )
                self.project_location_combo.addItem(custom_location.strip())
            elif ok:
                QMessageBox.warning(
                    self,
                    "No Location Entered",
                    "Please enter a valid city name or select from the dropdown.",
                    QMessageBox.Ok
                )
                if self.project_location_combo:
                    self.project_location_combo.setCurrentIndex(0)
        
    def show_project_location_dialog(self):
        """Show Project Location selection dialog"""
        state_districts = {
            "Select State": ["Select District"],
            "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", 
                      "North West Delhi", "South Delhi", "South East Delhi", "South West Delhi", "West Delhi"],
            "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", 
                           "Amravati", "Kolhapur", "Raigad", "Satara", "Sangli"],
            "Karnataka": ["Bangalore", "Mysore", "Hubli", "Belgaum", "Mangalore", "Gulbarga", 
                         "Bellary", "Bijapur", "Shimoga", "Tumkur", "Davangere"],
            "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", 
                          "Tiruppur", "Erode", "Vellore", "Thoothukudi", "Dindigul"],
            "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Siliguri", "Asansol", "Durgapur", 
                           "Bardhaman", "Malda", "Jalpaiguri", "Murshidabad", "Nadia"]
        }
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Project Location")
        dialog.setMinimumWidth(850)
        dialog.setMinimumHeight(650)
        
        # Set white background for the entire dialog
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QCheckBox {
                color: black;
            }
            QLabel {
                color: black;
            }
        """)
        
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # === Enter Coordinates Row ===
        coords_row = QHBoxLayout()
        coords_row.setSpacing(15)
        
        self.coords_checkbox = QCheckBox("Enter Coordinates")
        self.coords_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px; 
                font-weight: normal;
                color: black;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #b0b0b0;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #90AF13;
                border-color: #90AF13;
            }
            QCheckBox::indicator:hover {
                border-color: #7a9a12;
            }
        """)
        coords_row.addWidget(self.coords_checkbox)
        
        coords_row.addStretch()
        
        lat_label = QLabel("Latitude (°)")
        lat_label.setStyleSheet("font-size: 11px;")
        coords_row.addWidget(lat_label)
        
        self.latitude_input = QLineEdit()
        self.latitude_input.setMaximumWidth(120)
        self.latitude_input.setEnabled(False)
        apply_field_style(self.latitude_input)
        coords_row.addWidget(self.latitude_input)
        
        lng_label = QLabel("Longitude (°)")
        lng_label.setStyleSheet("font-size: 11px;")
        coords_row.addWidget(lng_label)
        
        self.longitude_input = QLineEdit()
        self.longitude_input.setMaximumWidth(120)
        self.longitude_input.setEnabled(False)
        apply_field_style(self.longitude_input)
        coords_row.addWidget(self.longitude_input)
        
        main_layout.addLayout(coords_row)
        
        # Separator line
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("background-color: #d0d0d0;")
        main_layout.addWidget(line1)
        
        # === Enter Location Name Row ===
        location_row = QHBoxLayout()
        location_row.setSpacing(15)
        
        self.location_checkbox = QCheckBox("Enter Location Name")
        self.location_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px; 
                font-weight: normal;
                color: black;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #b0b0b0;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #90AF13;
                border-color: #90AF13;
            }
            QCheckBox::indicator:hover {
                border-color: #7a9a12;
            }
        """)
        location_row.addWidget(self.location_checkbox)
        
        location_row.addStretch()
        
        state_label = QLabel("State")
        state_label.setStyleSheet("font-size: 11px;")
        location_row.addWidget(state_label)
        
        self.state_combo = NoScrollComboBox()
        self.state_combo.setMaximumWidth(150)
        self.state_combo.setEnabled(False)
        self.state_combo.addItems(list(state_districts.keys()))
        apply_field_style(self.state_combo)
        location_row.addWidget(self.state_combo)
        
        district_label = QLabel("District")
        district_label.setStyleSheet("font-size: 11px;")
        location_row.addWidget(district_label)
        
        self.district_combo = NoScrollComboBox()
        self.district_combo.setMaximumWidth(150)
        self.district_combo.setEnabled(False)
        self.district_combo.addItems(["Select District"])
        apply_field_style(self.district_combo)
        location_row.addWidget(self.district_combo)
        
        main_layout.addLayout(location_row)
        
        # Separator line
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("background-color: #d0d0d0;")
        main_layout.addWidget(line2)
        
        # === Select on Map Section ===
        map_section = QVBoxLayout()
        map_section.setSpacing(8)
        
        self.map_checkbox = QCheckBox("Select on Map")
        self.map_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px; 
                font-weight: normal;
                color: black;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #b0b0b0;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #90AF13;
                border-color: #90AF13;
            }
            QCheckBox::indicator:hover {
                border-color: #7a9a12;
            }
        """)
        map_section.addWidget(self.map_checkbox)
        
        # Map placeholder
        self.map_placeholder = QLabel()
        self.map_placeholder.setStyleSheet("""
            QLabel {
                border: 1px solid #e0e0e0;
                background-color: white;
                padding: 20px;
                color: #999999;
            }
        """)
        self.map_placeholder.setAlignment(Qt.AlignCenter)
        self.map_placeholder.setMinimumHeight(200)
        self.map_placeholder.setText("Map Placeholder\n(Will be added later)")
        self.map_placeholder.setEnabled(False)  # Disabled by default
        map_section.addWidget(self.map_placeholder)
        
        main_layout.addLayout(map_section)
        
        # Separator line
        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)
        line3.setStyleSheet("background-color: #d0d0d0;")
        main_layout.addWidget(line3)
        
        # === IRC 6 (2017) Values Section ===
        results_section = QVBoxLayout()
        results_section.setSpacing(8)
        
        results_title = QLabel("IRC 6 (2017) Values")
        results_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #4CAF50;")
        results_section.addWidget(results_title)
        
        self.wind_speed_label = QLabel("Basic Wind Speed (m/sec)")
        self.wind_speed_label.setStyleSheet("font-size: 11px; color: #4CAF50;")
        results_section.addWidget(self.wind_speed_label)
        
        self.seismic_zone_label = QLabel("Seismic Zone and Zone Factor")
        self.seismic_zone_label.setStyleSheet("font-size: 11px; color: #4CAF50;")
        results_section.addWidget(self.seismic_zone_label)
        
        self.temp_label = QLabel("Shade Air Temperature (°C)")
        self.temp_label.setStyleSheet("font-size: 11px; color: #4CAF50;")
        results_section.addWidget(self.temp_label)
        
        main_layout.addLayout(results_section)
        
        # Separator line
        line4 = QFrame()
        line4.setFrameShape(QFrame.HLine)
        line4.setFrameShadow(QFrame.Sunken)
        line4.setStyleSheet("background-color: #d0d0d0;")
        main_layout.addWidget(line4)
        
        # === Custom Loading Parameters Checkbox ===
        self.custom_params_checkbox = QCheckBox("Tabulate Custom Loading Parameters")
        self.custom_params_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 11px;
                color: black;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #b0b0b0;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #90AF13;
                border-color: #90AF13;
            }
            QCheckBox::indicator:hover {
                border-color: #7a9a12;
            }
        """)
        main_layout.addWidget(self.custom_params_checkbox)
        
        main_layout.addStretch()
        
        # === Bottom Buttons ===
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                padding: 6px 16px;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        ok_btn.setMinimumWidth(100)
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                padding: 6px 16px;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(btn_layout)
        
        # Function to update districts based on selected state
        def on_state_changed(state_name):
            districts = state_districts.get(state_name, ["Select District"])
            self.district_combo.clear()
            self.district_combo.addItems(districts)
        
        # Function to handle map checkbox
        def on_map_checkbox_changed(state):
            enabled = (state == 2)
            self.map_placeholder.setEnabled(enabled)
            if enabled:
                self.map_placeholder.setStyleSheet("""
                    QLabel {
                        border: 2px solid #90AF13;
                        background-color: white;
                        padding: 20px;
                        color: #666666;
                    }
                """)
                self.map_placeholder.setText("Map Placeholder\n(Click to select location)\n(Will be implemented later)")
            else:
                self.map_placeholder.setStyleSheet("""
                    QLabel {
                        border: 1px solid #e0e0e0;
                        background-color: #f5f5f5;
                        padding: 20px;
                        color: #999999;
                    }
                """)
                self.map_placeholder.setText("Map Placeholder\n(Will be added later)")
        
        # Connect checkbox signals to enable/disable fields
        self.coords_checkbox.stateChanged.connect(lambda state: self.latitude_input.setEnabled(state == 2) or self.longitude_input.setEnabled(state == 2))
        self.location_checkbox.stateChanged.connect(lambda state: self.state_combo.setEnabled(state == 2) or self.district_combo.setEnabled(state == 2))
        self.map_checkbox.stateChanged.connect(on_map_checkbox_changed)
        
        # Connect state combo to update districts
        self.state_combo.currentTextChanged.connect(on_state_changed)
        
        if dialog.exec() == QDialog.Accepted:
            pass
    
    def build_left_panel(self, field_list):
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.left_panel = QWidget()
        self.left_panel.setStyleSheet("background-color: white;")
        panel_layout = QVBoxLayout(self.left_panel)
        panel_layout.setContentsMargins(15, 10, 15, 10)
        panel_layout.setSpacing(0)

        # Top Bar with buttons
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)
        top_bar.setContentsMargins(0, 0, 0, 15)
        
        input_dock_btn = QPushButton("Basic Inputs")
        input_dock_btn.setStyleSheet("""
            QPushButton {
                background-color: #90AF13;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 4px;
                padding: 7px 20px;
                min-width: 80px;
            }
        """)
        input_dock_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_bar.addWidget(input_dock_btn)
        
        # Additional Inputs button with lock icon on the right
        additional_inputs_btn = QPushButton("Additional Inputs")
        additional_inputs_btn.setCursor(Qt.CursorShape.PointingHandCursor)        
        additional_inputs_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                font-weight: bold;
                font-size: 13px;
                border-radius: 5px;
                border: 1px solid black;
                padding: 7px 20px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #90AF13;
                border: 1px solid #90AF13;
                color: white;
            }
            QPushButton:pressed {
                color: black;
                background-color: white;
                border: 1px solid black;
            }
        """)
        additional_inputs_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        additional_inputs_btn.clicked.connect(self.show_additional_inputs)
        top_bar.addWidget(additional_inputs_btn)           

        # Load the icon from resources
        lock_button = QPushButton()
        lock_button.setCursor(Qt.CursorShape.PointingHandCursor) 
        lock_state = [1]  # Use list to make it mutable
        lock_button.setIcon(QIcon(":/vectors/lock_close.svg"))
        lock_button.setIconSize(QSize(30, 30))
        lock_button.setStyleSheet("border: none;")
        top_bar.addWidget(lock_button)

        def toggle_lock():
            if lock_state[0] == 0:
                lock_state[0] = 1
                lock_button.setIcon(QIcon(":/vectors/lock_close.svg"))
            elif lock_state[0] == 1:
                lock_state[0] = 0
                lock_button.setIcon(QIcon(":/vectors/lock_open.svg"))
                
        lock_button.clicked.connect(toggle_lock)
        
        panel_layout.addLayout(top_bar)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                padding: 0px 5px;
                border-top: 1px solid #909090;
                border-bottom: 1px solid #909090;
            }

            QScrollArea QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin-left: 2px;
            }

            QScrollArea QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }

            QScrollArea QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }

            QScrollArea QScrollBar::handle:vertical:pressed {
                background: #808080;
            }

            QScrollArea QScrollBar::add-line:vertical,
            QScrollArea QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }

            QScrollArea QScrollBar::add-page:vertical,
            QScrollArea QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        group_container = QWidget()
        self.input_widget = group_container
        group_container_layout = QVBoxLayout(group_container)
        group_container_layout.setContentsMargins(0, 0, 0, 0)
        group_container_layout.setSpacing(12)

        # === Type of Structure Box ===
        type_box = QGroupBox("Type of Structure")
        type_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #90AF13;
                border-radius: 4px;
                background-color: white;
                padding: 8px;
                margin-top: 12px;
                font-size: 10px;
                font-weight: bold;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 8px;
                padding: 0 4px;
                margin-top: 4px;
                background-color: white;
                color: #333;
            }
        """)
        type_box_layout = QVBoxLayout(type_box)
        type_box_layout.setContentsMargins(8, 8, 8, 8)
        type_box_layout.setSpacing(8)
        
        # Type of Structure field
        type_row = QHBoxLayout()
        type_field_label = QLabel("Type of Structure")
        type_field_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        type_field_label.setMinimumWidth(110)
        
        self.structure_type_combo = NoScrollComboBox()
        self.structure_type_combo.setObjectName(KEY_STRUCTURE_TYPE)
        apply_field_style(self.structure_type_combo)
        self.structure_type_combo.addItems(VALUES_STRUCTURE_TYPE)
        
        type_row.addWidget(type_field_label)
        type_row.addWidget(self.structure_type_combo, 1)
        type_box_layout.addLayout(type_row)

        self.structure_note = QLabel("*Other structures not included")
        self.structure_note.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        self.structure_note.setVisible(False)
        type_box_layout.addWidget(self.structure_note)

        self.structure_type_combo.currentTextChanged.connect(self.on_structure_type_changed)
        group_container_layout.addWidget(type_box)
        
        # === Project Location Box ===
        location_box = QGroupBox()
        location_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #90AF13;
                border-radius: 4px;
                background-color: white;
                padding: 8px;
                margin-top: 12px;
            }
        """)
        location_box_layout = QVBoxLayout(location_box)
        location_box_layout.setContentsMargins(8, 8, 8, 8)
        location_box_layout.setSpacing(8)

        loc_header = QHBoxLayout()
        loc_title = QLabel("Project Location")
        loc_title.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        loc_title.setMinimumWidth(110)
        loc_header.addWidget(loc_title)
        
        add_here_btn = QPushButton("Add Here")
        add_here_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_here_btn.setStyleSheet("""
            QPushButton {
                background-color: #90AF13;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 11px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7a9a12;
            }
        """)
        add_here_btn.clicked.connect(self.show_project_location_dialog)
        loc_header.addWidget(add_here_btn, 1)
        location_box_layout.addLayout(loc_header)
        
        self.project_location_combo = NoScrollComboBox()
        self.project_location_combo.setObjectName(KEY_PROJECT_LOCATION)
        self.project_location_combo.addItems(VALUES_PROJECT_LOCATION)
        self.project_location_combo.currentTextChanged.connect(self.on_project_location_changed)
        self.project_location_combo.hide()
        
        group_container_layout.addWidget(location_box)
        
        # === Superstructure Section (Contains Everything) ===
        structure_group = QGroupBox()
        structure_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #90AF13;
                border-radius: 5px;
                margin-top: 0px;
                padding-top: 5px;
                background-color: white;
            }
        """)
        structure_layout = QVBoxLayout()
        structure_layout.setContentsMargins(10, 10, 10, 10)
        structure_layout.setSpacing(10)
        
        # Header with title and collapse icon
        struct_header = QHBoxLayout()
        struct_title = QLabel("Superstructure")
        struct_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #333;")
        struct_header.addWidget(struct_title)
        struct_header.addStretch()
        
        # Collapse/expand toggle using SVG icon
        toggle_btn = QPushButton()
        toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle_btn.setCheckable(True)
        toggle_btn.setChecked(True)
        toggle_btn.setIcon(QIcon(":/vectors/arrow_up_light.svg"))
        toggle_btn.setIconSize(QSize(20, 20))
        toggle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 2px;
            }
            QPushButton:hover {
                background: transparent;
            }
            QPushButton:pressed {
                background: transparent;
            }
        """)
        struct_header.addWidget(toggle_btn)

        structure_layout.addLayout(struct_header)

        # body widget that contains everything inside the Superstructure and can be hidden
        structure_body = QFrame()
        structure_body.setFrameShape(QFrame.NoFrame)
        structure_body_layout = QVBoxLayout(structure_body)
        structure_body_layout.setContentsMargins(0, 0, 0, 0)
        structure_body_layout.setSpacing(10)
        structure_body.setVisible(True)
        structure_layout.addWidget(structure_body)

        def _toggle_structure(checked):
            # checked True means show body (open)
            structure_body.setVisible(checked)
            toggle_btn.setIcon(QIcon(":/vectors/arrow_up_light.svg" if checked else ":/vectors/arrow_down_light.svg"))

        toggle_btn.toggled.connect(_toggle_structure)
        
        # === Geometric Details Box ===
        geo_box = QGroupBox("Geometric Details")
        geo_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #90AF13;
                border-radius: 4px;
                background-color: white;
                padding: 8px;
                margin-top: 12px;
                font-size: 10px;
                font-weight: bold;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 8px;
                padding: 0 4px;
                margin-top: 4px;
                background-color: white;
                color: #333;
            }
        """)
        geo_box_layout = QVBoxLayout(geo_box)
        geo_box_layout.setContentsMargins(8, 8, 8, 8)
        geo_box_layout.setSpacing(8)
        
        # Span
        span_row = QHBoxLayout()
        span_label = QLabel("Span (m)")
        span_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        span_label.setMinimumWidth(110)
        self.span_input = QLineEdit()
        self.span_input.setObjectName(KEY_SPAN)
        apply_field_style(self.span_input)
        self.span_input.setValidator(QDoubleValidator(SPAN_MIN, SPAN_MAX, 2))
        self.span_input.setPlaceholderText(f"{SPAN_MIN}-{SPAN_MAX} m")
        span_row.addWidget(span_label)
        span_row.addWidget(self.span_input, 1)
        geo_box_layout.addLayout(span_row)
        
        # Carriageway Width
        carriageway_row = QHBoxLayout()
        carriageway_label = QLabel("Carriageway (m)")
        carriageway_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        carriageway_label.setMinimumWidth(110)
        self.carriageway_input = QLineEdit()
        self.carriageway_input.setObjectName(KEY_CARRIAGEWAY_WIDTH)
        apply_field_style(self.carriageway_input)
        self.carriageway_input.setValidator(QDoubleValidator(CARRIAGEWAY_WIDTH_MIN, 100.0, 2))
        self.carriageway_input.setPlaceholderText(f"Min {CARRIAGEWAY_WIDTH_MIN} m")
        carriageway_row.addWidget(carriageway_label)
        carriageway_row.addWidget(self.carriageway_input, 1)
        geo_box_layout.addLayout(carriageway_row)
        
        # Footpath
        footpath_row = QHBoxLayout()
        footpath_label = QLabel("Footpath")
        footpath_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        footpath_label.setMinimumWidth(110)
        self.footpath_combo = NoScrollComboBox()
        self.footpath_combo.setObjectName(KEY_FOOTPATH)
        apply_field_style(self.footpath_combo)
        self.footpath_combo.addItems(VALUES_FOOTPATH)
        self.footpath_combo.setCurrentIndex(0)
        self.footpath_combo.currentTextChanged.connect(self.on_footpath_changed)
        footpath_row.addWidget(footpath_label)
        footpath_row.addWidget(self.footpath_combo, 1)
        geo_box_layout.addLayout(footpath_row)
        
        # Skew Angle
        skew_row = QHBoxLayout()
        skew_label = QLabel("Skew Angle")
        skew_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        skew_label.setMinimumWidth(110)
        self.skew_input = QLineEdit()
        self.skew_input.setObjectName(KEY_SKEW_ANGLE)
        apply_field_style(self.skew_input)
        self.skew_input.setValidator(QDoubleValidator(SKEW_ANGLE_MIN, SKEW_ANGLE_MAX, 1))
        self.skew_input.setText(str(SKEW_ANGLE_DEFAULT))
        self.skew_input.setPlaceholderText(f"Default: {SKEW_ANGLE_DEFAULT}°")
        skew_row.addWidget(skew_label)
        skew_row.addWidget(self.skew_input, 1)
        geo_box_layout.addLayout(skew_row)
        
        # Additional Geometry (inside Geometric Details)
        add_geo_row = QHBoxLayout()
        add_geo_label = QLabel("Additional Geometry")
        add_geo_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        add_geo_label.setMinimumWidth(110)
        add_geo_row.addWidget(add_geo_label)
        
        modify_geo_btn = QPushButton("Modify Here")
        modify_geo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        modify_geo_btn.setStyleSheet("""
            QPushButton {
                background-color: #90AF13;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 11px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7a9a12;
            }
        """)
        modify_geo_btn.clicked.connect(self.show_additional_inputs)
        add_geo_row.addWidget(modify_geo_btn, 1)
        geo_box_layout.addLayout(add_geo_row)
        
        structure_body_layout.addWidget(geo_box)
        
        # === Material Inputs Box ===
        material_box = QGroupBox("Material Inputs")
        material_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #90AF13;
                border-radius: 4px;
                background-color: white;
                padding: 8px;
                margin-top: 12px;
                font-size: 10px;
                font-weight: bold;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 8px;
                padding: 0 4px;
                margin-top: 4px;
                background-color: white;
                color: #333;
            }
        """)
        material_box_layout = QVBoxLayout(material_box)
        material_box_layout.setContentsMargins(8, 8, 8, 8)
        material_box_layout.setSpacing(8)
        
        # Girder
        girder_row = QHBoxLayout()
        girder_label = QLabel("Girder")
        girder_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        girder_label.setMinimumWidth(110)
        self.girder_combo = NoScrollComboBox()
        self.girder_combo.setObjectName(KEY_GIRDER)
        apply_field_style(self.girder_combo)
        self.girder_combo.addItems(VALUES_MATERIAL)
        girder_row.addWidget(girder_label)
        girder_row.addWidget(self.girder_combo, 1)
        material_box_layout.addLayout(girder_row)
        
        # Cross Bracing
        cross_bracing_row = QHBoxLayout()
        cross_bracing_label = QLabel("Cross Bracing")
        cross_bracing_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        cross_bracing_label.setMinimumWidth(110)
        self.cross_bracing_combo = NoScrollComboBox()
        self.cross_bracing_combo.setObjectName(KEY_CROSS_BRACING)
        apply_field_style(self.cross_bracing_combo)
        self.cross_bracing_combo.addItems(VALUES_MATERIAL)
        cross_bracing_row.addWidget(cross_bracing_label)
        cross_bracing_row.addWidget(self.cross_bracing_combo, 1)
        material_box_layout.addLayout(cross_bracing_row)
        
        # Deck
        deck_row = QHBoxLayout()
        deck_label = QLabel("Deck")
        deck_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        deck_label.setMinimumWidth(110)
        self.deck_combo = NoScrollComboBox()
        self.deck_combo.setObjectName(KEY_DECK_CONCRETE_GRADE_BASIC)
        apply_field_style(self.deck_combo)
        self.deck_combo.addItems(VALUES_DECK_CONCRETE_GRADE)
        self.deck_combo.setCurrentText("M25")
        deck_row.addWidget(deck_label)
        deck_row.addWidget(self.deck_combo, 1)
        material_box_layout.addLayout(deck_row)

        # Material Properties header with button
        mat_prop_header = QHBoxLayout()
        mat_prop_title = QLabel("Modify Properties")
        mat_prop_title.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        mat_prop_title.setMinimumWidth(110)
        mat_prop_header.addWidget(mat_prop_title)
        
        modify_mat_btn = QPushButton("Modify Here")
        modify_mat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        modify_mat_btn.setStyleSheet("""
            QPushButton {
                background-color: #90AF13;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 11px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7a9a12;
            }
        """)
        mat_prop_header.addWidget(modify_mat_btn, 1)
        material_box_layout.addLayout(mat_prop_header)
        
        structure_body_layout.addWidget(material_box)
        
        # Close the Superstructure section
        structure_group.setLayout(structure_layout)
        group_container_layout.addWidget(structure_group)

        # === Substructure Section (empty body for now) ===
        sub_group = QGroupBox()
        sub_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #90AF13;
                border-radius: 5px;
                margin-top: 8px;
                padding-top: 5px;
                background-color: white;
            }
        """)
        sub_layout = QVBoxLayout()
        sub_layout.setContentsMargins(10, 10, 10, 10)
        sub_layout.setSpacing(8)

        sub_header = QHBoxLayout()
        sub_title = QLabel("Substructure")
        sub_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #333;")
        sub_header.addWidget(sub_title)
        sub_header.addStretch()

        sub_toggle = QPushButton()
        sub_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        sub_toggle.setCheckable(True)
        sub_toggle.setChecked(True)
        sub_toggle.setIcon(QIcon(":/vectors/arrow_up_light.svg"))
        sub_toggle.setIconSize(QSize(20, 20))
        sub_toggle.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 2px;
            }
            QPushButton:hover {
                background: transparent;
            }
            QPushButton:pressed {
                background: transparent;
            }
        """)
        sub_header.addWidget(sub_toggle)
        sub_layout.addLayout(sub_header)

        sub_body = QFrame()
        sub_body.setFrameShape(QFrame.NoFrame)
        sub_body_layout = QVBoxLayout(sub_body)
        sub_body_layout.setContentsMargins(0,0,0,0)
        sub_body_layout.setSpacing(6)
        sub_body.setVisible(True)
        sub_layout.addWidget(sub_body)

        def _toggle_sub(checked):
            sub_body.setVisible(checked)
            sub_toggle.setIcon(QIcon(":/vectors/arrow_up_light.svg" if checked else ":/vectors/arrow_down_light.svg"))

        sub_toggle.toggled.connect(_toggle_sub)

        sub_group.setLayout(sub_layout)
        group_container_layout.addWidget(sub_group)
        
        group_container_layout.addStretch()
        scroll_area.setWidget(group_container)

        self.data = {}
        panel_layout.addWidget(scroll_area)

        # Bottom buttons
        btn_button_layout = QHBoxLayout()
        btn_button_layout.setContentsMargins(0, 15, 0, 0)
        btn_button_layout.setSpacing(10)

        save_input_btn = DockCustomButton("Save Input", ":/vectors/save.svg")
        save_input_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_button_layout.addWidget(save_input_btn)

        design_btn = DockCustomButton("Design", ":/vectors/design.svg")
        design_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_button_layout.addWidget(design_btn)

        panel_layout.addLayout(btn_button_layout)

        # Horizontal scroll area
        h_scroll_area = QScrollArea()
        h_scroll_area.setWidgetResizable(True)
        h_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        h_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        h_scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        h_scroll_area.setStyleSheet("""
            QScrollArea{
                background: transparent;
            }
            QScrollBar:horizontal{
                background: #E0E0E0;
                height: 8px;
                margin: 3px 0px 0px 0px;
                border-radius: 2px;
            }
            QScrollBar::handle:horizontal{
                background: #A0A0A0;
                min-width: 30px;
                border-radius: 2px;
            }
            QScrollBar::handle:horizontal:hover{
                background: #707070;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal{
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal{
                background: none;
            }
        """)
        h_scroll_area.setWidget(self.left_panel)

        left_layout.addWidget(h_scroll_area)
    
    def show_additional_inputs(self):
        """Show Additional Inputs dialog"""
        footpath_value = self.footpath_combo.currentText() if self.footpath_combo else "None"
        
        carriageway_width = 7.5
        if self.input_widget:
            carriageway_field = self.input_widget.findChild(QLineEdit, KEY_CARRIAGEWAY_WIDTH)
            if carriageway_field and carriageway_field.text():
                try:
                    carriageway_width = float(carriageway_field.text())
                except ValueError:
                    carriageway_width = 7.5
        
        if self.additional_inputs_window is None or not self.additional_inputs_window.isVisible():
            self.additional_inputs_window = QDialog(self)
            self.additional_inputs_window.setWindowTitle("Additional Inputs - Manual Bridge Parameter Definition")
            self.additional_inputs_window.resize(900, 700)
            
            layout = QVBoxLayout(self.additional_inputs_window)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.additional_inputs_widget = AdditionalInputsWidget(footpath_value, carriageway_width, self.additional_inputs_window)
            layout.addWidget(self.additional_inputs_widget)
            
            self.additional_inputs_window.show()
        else:
            self.additional_inputs_window.raise_()
            self.additional_inputs_window.activateWindow()
    
    def on_footpath_changed(self, footpath_value):
        """Update additional inputs when footpath changes"""
        if self.additional_inputs_window and self.additional_inputs_window.isVisible():
            if hasattr(self, 'additional_inputs_widget'):
                self.additional_inputs_widget.update_footpath_value(footpath_value)