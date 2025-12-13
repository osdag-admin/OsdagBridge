from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,  QWidget,
    QCheckBox, QFrame, QPushButton, QComboBox, QSizePolicy, QSizeGrip
)
from PySide6.QtCore import Qt
from osdagbridge.desktop.ui.utils.custom_titlebar import CustomTitleBar

class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()  # Prevent changing selection on scroll

def apply_field_style(widget):
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    widget.setMinimumHeight(28)
    
    if isinstance(widget, QComboBox):
        style = """
            QComboBox{
                padding: 1px 7px;
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


class ProjectLocationDialog(QDialog):
    """Dialog for selecting project location with multiple input methods"""
    
    STATE_DISTRICTS = {
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(850)
        self.setMinimumHeight(650)
        self.setObjectName("project_location_dialog")
        self.setStyleSheet("""
            QDialog#project_location_dialog {
                background-color: #FFFFFF;
                border: 1px solid #90AF13;
            }
        """)
        
        self._setup_ui()
        self._connect_signals()
    
    def setupWrapper(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)
        
        self.title_bar = CustomTitleBar()
        self.title_bar.setTitle("Project Location")
        main_layout.addWidget(self.title_bar)
        
        self.content_widget = QWidget(self)
        main_layout.addWidget(self.content_widget, 1)

        size_grip = QSizeGrip(self)
        size_grip.setFixedSize(16, 16)

        overlay = QHBoxLayout()
        overlay.setContentsMargins(0, 0, 4, 4)
        overlay.addStretch(1)
        overlay.addWidget(size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        main_layout.addLayout(overlay)
    
    def _setup_ui(self):
        """Setup the user interface"""
        self.setupWrapper()
        main_layout = QVBoxLayout(self.content_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Add sections
        self._add_coordinates_section(main_layout)
        self._add_separator(main_layout)
        self._add_location_name_section(main_layout)
        self._add_separator(main_layout)
        self._add_map_section(main_layout)
        self._add_separator(main_layout)
        self._add_irc_values_section(main_layout)
        self._add_separator(main_layout)
        self._add_custom_params_section(main_layout)
        
        main_layout.addStretch()
        
        self._add_buttons(main_layout)
    
    def _add_coordinates_section(self, layout):
        """Add the coordinates input section"""
        coords_row = QHBoxLayout()
        coords_row.setSpacing(15)
        
        self.coords_checkbox = QCheckBox("Enter Coordinates")
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
        
        layout.addLayout(coords_row)
    
    def _add_location_name_section(self, layout):
        """Add the location name input section"""
        location_row = QHBoxLayout()
        location_row.setSpacing(15)
        
        self.location_checkbox = QCheckBox("Enter Location Name")
        location_row.addWidget(self.location_checkbox)
        location_row.addStretch()
        
        state_label = QLabel("State")
        state_label.setStyleSheet("font-size: 11px;")
        location_row.addWidget(state_label)
        
        self.state_combo = NoScrollComboBox()
        self.state_combo.setMaximumWidth(150)
        self.state_combo.setEnabled(False)
        self.state_combo.addItems(list(self.STATE_DISTRICTS.keys()))
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
        
        layout.addLayout(location_row)
    
    def _add_map_section(self, layout):
        """Add the map selection section"""
        map_section = QVBoxLayout()
        map_section.setSpacing(8)
        
        self.map_checkbox = QCheckBox("Select on Map")
        map_section.addWidget(self.map_checkbox)
        
        # Map placeholder
        self.map_placeholder = QLabel()
        self.map_placeholder.setAlignment(Qt.AlignCenter)
        self.map_placeholder.setMinimumHeight(200)
        self.map_placeholder.setText("Map Placeholder\n(Will be added later)")
        self.map_placeholder.setEnabled(False)
        map_section.addWidget(self.map_placeholder)
        
        layout.addLayout(map_section)
    
    def _add_irc_values_section(self, layout):
        """Add the IRC 6 (2017) values section"""
        results_section = QVBoxLayout()
        results_section.setSpacing(8)
        
        results_title = QLabel("IRC 6 (2017) Values")
        results_section.addWidget(results_title)
        
        self.wind_speed_label = QLabel("Basic Wind Speed (m/sec)")
        results_section.addWidget(self.wind_speed_label)
        
        self.seismic_zone_label = QLabel("Seismic Zone and Zone Factor")
        results_section.addWidget(self.seismic_zone_label)
        
        self.temp_label = QLabel("Shade Air Temperature (°C)")
        results_section.addWidget(self.temp_label)
        
        layout.addLayout(results_section)
    
    def _add_custom_params_section(self, layout):
        """Add the custom loading parameters checkbox"""
        self.custom_params_checkbox = QCheckBox("Tabulate Custom Loading Parameters")
        layout.addWidget(self.custom_params_checkbox)
    
    def _add_separator(self, layout):
        """Add a horizontal separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #d0d0d0;")
        layout.addWidget(line)
    
    def _add_buttons(self, layout):
        """Add OK and Cancel buttons"""
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setMinimumWidth(100)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _connect_signals(self):
        """Connect all signal handlers"""
        # Enable/disable coordinates inputs
        self.coords_checkbox.stateChanged.connect(
            lambda state: self._toggle_coordinates_inputs(state == 2)
        )
        
        # Enable/disable location inputs
        self.location_checkbox.stateChanged.connect(
            lambda state: self._toggle_location_inputs(state == 2)
        )
        
        # Handle map checkbox
        self.map_checkbox.stateChanged.connect(self._on_map_checkbox_changed)
        
        # Update districts when state changes
        self.state_combo.currentTextChanged.connect(self._on_state_changed)
    
    def _toggle_coordinates_inputs(self, enabled):
        """Enable or disable coordinate input fields"""
        self.latitude_input.setEnabled(enabled)
        self.longitude_input.setEnabled(enabled)
    
    def _toggle_location_inputs(self, enabled):
        """Enable or disable location input fields"""
        self.state_combo.setEnabled(enabled)
        self.district_combo.setEnabled(enabled)
    
    def _on_state_changed(self, state_name):
        """Update districts based on selected state"""
        districts = self.STATE_DISTRICTS.get(state_name, ["Select District"])
        self.district_combo.clear()
        self.district_combo.addItems(districts)
    
    def _on_map_checkbox_changed(self, state):
        """Handle map checkbox state changes"""
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
            self.map_placeholder.setText(
                "Map Placeholder\n(Click to select location)\n(Will be implemented later)"
            )
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
    
    def get_selected_location(self):
        """
        Get the selected location data
        
        Returns:
            dict: Dictionary containing location information based on selection method
        """
        result = {
            'method': None,
            'data': {}
        }
        
        if self.coords_checkbox.isChecked():
            result['method'] = 'coordinates'
            result['data'] = {
                'latitude': self.latitude_input.text(),
                'longitude': self.longitude_input.text()
            }
        elif self.location_checkbox.isChecked():
            result['method'] = 'location_name'
            result['data'] = {
                'state': self.state_combo.currentText(),
                'district': self.district_combo.currentText()
            }
        elif self.map_checkbox.isChecked():
            result['method'] = 'map'
            result['data'] = {}  # Will be populated when map is implemented
        
        result['custom_params'] = self.custom_params_checkbox.isChecked()
        
        return result