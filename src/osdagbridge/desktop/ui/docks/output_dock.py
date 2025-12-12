from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy,
    QPushButton, QGroupBox, QCheckBox, QScrollArea, QFrame, QComboBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from osdagbridge.desktop.ui.utils.custom_buttons import DockCustomButton

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

class OutputDock(QWidget):
    """Output dock with collapsible design controls and scrollable layout."""

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        self.init_ui()

    def init_ui(self):
        # Main horizontal layout to hold toggle strip and content
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Toggle strip on the left
        self.toggle_strip = QWidget()
        self.toggle_strip.setStyleSheet("background-color: #90AF13;")
        self.toggle_strip.setFixedWidth(6)
        toggle_layout = QVBoxLayout(self.toggle_strip)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(0)
        toggle_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.toggle_btn = QPushButton("❯")
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setFixedSize(6, 60)
        self.toggle_btn.setToolTip("Hide panel")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #7a9a12;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 0px;
                border: none;
            }
            QPushButton:hover {
                background-color: #6a8a10;
            }
        """)
        toggle_layout.addStretch()
        toggle_layout.addWidget(self.toggle_btn)
        toggle_layout.addStretch()
        self.main_layout.addWidget(self.toggle_strip)

        # Content container
        content_container = QWidget()
        content_container.setStyleSheet("background-color: white;")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(10)

        # Top Bar with buttons
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)
        top_bar.setContentsMargins(0, 0, 0, 15)
        
        input_dock_btn = QPushButton("Output Dock")
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
        top_bar.addStretch()
        content_layout.addLayout(top_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)

        results_group = QGroupBox("Analysis Results")
        results_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 11px;
                color: #333;
                border: 1px solid #90AF13;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 8px;
                padding: 0 4px;
                background-color: white;
            }
            """
        )
        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(10, 8, 10, 10)
        results_layout.setSpacing(8)

        member_row = QHBoxLayout()
        member_label = QLabel("Member:")
        member_label.setStyleSheet("font-size: 10px; color: #333; font-weight: normal;")
        member_label.setMinimumWidth(100)
        self.member_combo = NoScrollComboBox()
        self.member_combo.addItems(["All"])
        apply_field_style(self.member_combo)
        member_row.addWidget(member_label)
        member_row.addWidget(self.member_combo)
        results_layout.addLayout(member_row)

        load_combo_row = QHBoxLayout()
        load_combo_label = QLabel("Load Combination:")
        load_combo_label.setStyleSheet("font-size: 10px; color: #333; font-weight: normal;")
        load_combo_label.setMinimumWidth(100)
        self.load_combo = NoScrollComboBox()
        self.load_combo.addItems(["Envelope"])
        apply_field_style(self.load_combo)
        load_combo_row.addWidget(load_combo_label)
        load_combo_row.addWidget(self.load_combo)
        results_layout.addLayout(load_combo_row)

        forces_grid = QHBoxLayout()
        forces_grid.setSpacing(8)

        col1 = QVBoxLayout()
        for text in ["Fx", "Mx", "Dx"]:
            cb = QCheckBox(text)
            col1.addWidget(cb)
        col2 = QVBoxLayout()
        for text in ["Fy", "My", "Dy"]:
            cb = QCheckBox(text)
            col2.addWidget(cb)
        col3 = QVBoxLayout()
        for text in ["Fz", "Mz", "Dz"]:
            cb = QCheckBox(text)
            col3.addWidget(cb)
        forces_grid.addLayout(col1)
        forces_grid.addLayout(col2)
        forces_grid.addLayout(col3)
        results_layout.addLayout(forces_grid)

        display_label = QLabel("Display Options:")
        display_label.setStyleSheet("font-size: 10px; color: #333; font-weight: normal; margin-top: 4px;")
        results_layout.addWidget(display_label)

        display_row = QHBoxLayout()
        display_row.setSpacing(12)
        for text in ["Max", "Min"]:
            cb = QCheckBox(text)
            display_row.addWidget(cb)
        display_row.addStretch()
        results_layout.addLayout(display_row)

        utilization_check = QCheckBox("Controlling Utilization Ratio")
        results_layout.addWidget(utilization_check)

        scroll_layout.addWidget(results_group)

        design_group = QGroupBox("Design")
        design_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 11px;
                color: #333;
                border: 1px solid #90AF13;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 8px;
                padding: 0 4px;
                background-color: white;
            }
            """
        )
        design_layout = QVBoxLayout(design_group)
        design_layout.setContentsMargins(10, 8, 10, 10)
        design_layout.setSpacing(8)

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
        super_toggle_btn = QPushButton()
        super_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        super_toggle_btn.setCheckable(True)
        super_toggle_btn.setChecked(True)
        super_toggle_btn.setIcon(QIcon(":/vectors/arrow_up_light.svg"))
        super_toggle_btn.setIconSize(QSize(20, 20))
        super_toggle_btn.setStyleSheet("""
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
        struct_header.addWidget(super_toggle_btn)

        structure_layout.addLayout(struct_header)

        # body widget that contains everything inside the Superstructure and can be hidden
        super_body = QFrame()
        super_body.setFrameShape(QFrame.NoFrame)
        super_body_layout = QVBoxLayout(super_body)
        super_body_layout.setContentsMargins(0, 0, 0, 0)
        super_body_layout.setSpacing(10)
        super_body.setVisible(True)
        
        # Additional Geometry (inside Superstructure body)
        add_geo_row = QHBoxLayout()
        add_geo_label = QLabel("Steel Design")
        add_geo_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        add_geo_label.setMinimumWidth(110)
        add_geo_row.addWidget(add_geo_label)
        
        modify_geo_btn = QPushButton("Here")
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
        super_body_layout.addLayout(add_geo_row)

        #---------------------------------------------

                # Additional Geometry (inside Superstructure body)
        add_geo_row = QHBoxLayout()
        add_geo_label = QLabel("Deck Design")
        add_geo_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 12px;
                background: transparent;
            }
        """)
        add_geo_label.setMinimumWidth(110)
        add_geo_row.addWidget(add_geo_label)
        
        modify_geo_btn = QPushButton("Here")
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
        super_body_layout.addLayout(add_geo_row)
        
        
        # Add body to structure layout
        structure_layout.addWidget(super_body)

        def _toggle_superstructure(checked, body=super_body, btn=super_toggle_btn):
            # checked True means show body (open)
            body.setVisible(checked)
            btn.setIcon(QIcon(":/vectors/arrow_up_light.svg" if checked else ":/vectors/arrow_down_light.svg"))

        super_toggle_btn.toggled.connect(_toggle_superstructure)
        structure_group.setLayout(structure_layout)
        design_layout.addWidget(structure_group)

        # === Substructure Section (Contains Everything) ===
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
        struct_title = QLabel("Substructure")
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
        
        
        # Add body to structure layout
        structure_layout.addWidget(structure_body)

        def _toggle_structure(checked):
            # checked True means show body (open)
            structure_body.setVisible(checked)
            toggle_btn.setIcon(QIcon(":/vectors/arrow_up_light.svg" if checked else ":/vectors/arrow_down_light.svg"))

        toggle_btn.toggled.connect(_toggle_structure)
        structure_group.setLayout(structure_layout)
        design_layout.addWidget(structure_group)

        scroll_layout.addWidget(design_group)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        content_layout.addWidget(scroll)

        h_layout = QHBoxLayout()
        h_layout.setSpacing(5)
        h_layout.setContentsMargins(0, 0, 0, 0)

        results_btn = DockCustomButton("Generate Results Table", ":/vectors/design_report.svg")
        results_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        h_layout.addWidget(results_btn)

        report_btn = DockCustomButton("Generate Report", ":/vectors/design_report.svg")
        report_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        h_layout.addWidget(report_btn)
        content_layout.addLayout(h_layout)
        
        # Add content container to main layout
        self.main_layout.addWidget(content_container)

    def show_additional_inputs(self):
        """Handle showing additional geometry inputs."""
        # Implement your logic here
        print("Show additional inputs clicked")