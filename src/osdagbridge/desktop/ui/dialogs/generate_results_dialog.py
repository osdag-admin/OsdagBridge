from PySide6.QtWidgets import (
    QDialog, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QComboBox, QSizeGrip,
    QRadioButton, QButtonGroup, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from osdagbridge.desktop.ui.utils.generate_results_schema import GENERATE_RESULTS_SCHEMA
from osdagbridge.desktop.ui.utils.generate_results_default import GENERATE_RESULTS_DEFAULTS
from osdagbridge.desktop.ui.utils.custom_titlebar import CustomTitleBar
from osdagbridge.desktop.ui.dialogs.export_table_dialog import ExportTableDialog
from osdagbridge.desktop.ui.dialogs.custom_messagebox import CustomMessageBox, MessageBoxType

class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


def apply_field_style(widget):
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    widget.setMinimumHeight(30)

    if isinstance(widget, QComboBox):
        widget.setStyleSheet("""
        QComboBox {
            padding: 1px 8px;
            border: 1px solid black;
            border-radius: 6px;
            background: white;
            color: black;
        }

        QComboBox::drop-down {
            border: none;
            width: 26px;
        }

        QComboBox QAbstractItemView {
            background: white;
            border: none;
            outline: 0px;
            selection-background-color: rgba(144,175,19,45);
            selection-color: black;
            color: black;
        }

        QComboBox QAbstractItemView::item {
            padding: 5px;
            margin: 0px;
            border: none;
        }
        QComboBox QAbstractItemView::item:hover {
            background: rgba(144,175,19,45);
            border: none;
            outline: none;
        }

        QComboBox QAbstractItemView::item:selected {
            background: rgba(144,175,19,65);
            border: none;
            outline: none;
        }
        """)


class GenerateResultsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumWidth(920)
        self.setMinimumHeight(650)
        self.setObjectName("generate_results_dialog")

        self.setStyleSheet("""
            QDialog#generate_results_dialog {
                background: white;
                border: 1px solid #90AF13;
            }

            QLabel {
                color: #1f1f1f;
                font-size: 12px;
            }

            QLabel#section {
                font-size: 13px;
                font-weight: 700;
                color: #2d2d2d;
            }

            QRadioButton {
                font-size: 12px;
                color: #1f1f1f;
                spacing: 6px;
            }

            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }

            QRadioButton::indicator:unchecked {
                border: 2px solid #90AF13;
                border-radius: 8px;
                background: white;
            }

            QRadioButton::indicator:hover {
                background: rgba(144,175,19,45);
                border: 2px solid #90AF13;
                border-radius: 8px;
            }

            QRadioButton::indicator:checked {
                border: 2px solid #90AF13;
                border-radius: 8px;
                background: #90AF13;
            }

            QPushButton#primary {
                background: white;
                color: black;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }

            QPushButton#primary:hover {
                background: #90AF13;
            }

            QPushButton#ghost {
                background: white;
                color: black;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }

            QPushButton#ghost:hover {
                background: #90AF13;
            }

            QTreeWidget {
                background: white;
                border: none;
                color: black;
                font-size: 12px;
                outline: 0;
                show-decoration-selected: 0;
            }

            QTreeWidget::item {
                height: 24px;
                border: none;
                padding: 2px 4px;
            }

            QTreeWidget::item:hover {
                background: rgba(144,175,19,45);
                border: none;
                color: black;
            }

            QTreeWidget::item:selected {
                background: rgba(144,175,19,55);
                border: none;
                color: black;
            }

            QTreeWidget::branch:selected {
                background: transparent;
            }
            QTreeView::branch {
                background: transparent;
                border: none;
                image: none;           
            }

            QTreeView::branch:selected {
                background: transparent;
            }

            QTreeView::branch:has-siblings:!adjoins-item,
            QTreeView::branch:has-siblings:adjoins-item,
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:has-children:!has-siblings:open,
            QTreeView::branch:closed:has-children,
            QTreeView::branch:open:has-children {
                border-image: none;
                image: none;
            }              

        """)

        self.setup_ui()

    def setupWrapper(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar()
        self.title_bar.setTitle("Generate Results Table")
        main_layout.addWidget(self.title_bar)

        self.content_widget = QWidget(self)
        main_layout.addWidget(self.content_widget, 1)

        size_grip = QSizeGrip(self)
        size_grip.setFixedSize(16, 16)

        overlay = QHBoxLayout()
        overlay.setContentsMargins(0, 0, 4, 4)
        overlay.addStretch()
        overlay.addWidget(size_grip, 0, Qt.AlignBottom | Qt.AlignRight)

        main_layout.addLayout(overlay)


    def setup_ui(self):
        self.setupWrapper()

        main_layout = QVBoxLayout(self.content_widget)
        main_layout.setContentsMargins(18, 18, 18, 14)
        main_layout.setSpacing(12)

        body = QHBoxLayout()
        body.setSpacing(14)


        left_card = QFrame()
        left_card.setObjectName("leftCard")
        left_card.setStyleSheet("""
            QFrame#leftCard {
                background: white;
                border: 1px solid #d8e2c4;
                border-radius: 10px;
            }
        """)

        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(14, 12, 14, 12)
        left_layout.setSpacing(12)

        top_bar = QHBoxLayout()

        title = QLabel("Select Tables")
        title.setObjectName("section")
        top_bar.addWidget(title)

        top_bar.addStretch()

        self.select_radio = QRadioButton("Select All")
        self.clear_radio = QRadioButton("Clear All")

        group = QButtonGroup(self)
        group.addButton(self.select_radio)
        group.addButton(self.clear_radio)

        self.select_radio.toggled.connect(
            lambda checked: self.select_all_items() if checked else None
        )
        self.clear_radio.toggled.connect(
            lambda checked: self.clear_all_items() if checked else None
        )

        top_bar.addWidget(self.select_radio)
        top_bar.addWidget(self.clear_radio)

        left_layout.addLayout(top_bar)

        self.tree = QTreeWidget()
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        self.tree.setFocusPolicy(Qt.NoFocus)
        self.tree.setAllColumnsShowFocus(False)
        self.tree.setRootIsDecorated(False)
        self.tree.setIndentation(18)
        self.tree.setHeaderHidden(True)
        self.tree.itemChanged.connect(self.handle_item_changed)

        left_layout.addWidget(self.tree, 1)

        body.addWidget(left_card, 2)


        right_card = QFrame()
        right_card.setObjectName("rightCard")
        right_card.setStyleSheet("""
            QFrame#rightCard {
                background: white;
                border: 1px solid #90AF13;
                border-radius: 10px;
            }
        """)

        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(14, 12, 14, 12)
        right_layout.setSpacing(10)

        lc_label = QLabel("Load Case")
        lc_label.setObjectName("section")
        right_layout.addWidget(lc_label)

        self.load_case_combo = NoScrollComboBox()
        self.load_case_combo.addItems([
            "DL", "DW", "SIDL", "LL",
            "Wind", "Seismic", "Temperature",
            "ULS Combo", "SLS Combo"
        ])
        apply_field_style(self.load_case_combo)
        right_layout.addWidget(self.load_case_combo)

        member_label = QLabel("Member Case")
        member_label.setObjectName("section")
        right_layout.addWidget(member_label)

        self.member_combo = NoScrollComboBox()
        self.member_combo.addItems([
            "All Girders",
            "Girder 1",
            "Girder 2",
            "Girder 3",
            "Girder 4"
        ])
        apply_field_style(self.member_combo)
        right_layout.addWidget(self.member_combo)

        right_layout.addStretch()

        body.addWidget(right_card, 1)

        main_layout.addLayout(body)


        footer = QHBoxLayout()
        footer.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("ghost")
        cancel_btn.clicked.connect(self.reject)

        self.show_btn = QPushButton("Show Selections")
        self.show_btn.setObjectName("primary")
        self.show_btn.clicked.connect(self.show_selections)

        footer.addWidget(cancel_btn)
        footer.addWidget(self.show_btn)

        main_layout.addLayout(footer)

        self.build_tree()

    def build_tree(self):
        self.tree.blockSignals(True)

        for main_group, sub_groups in GENERATE_RESULTS_SCHEMA.items():

            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, main_group)
            parent.setFlags(parent.flags() | Qt.ItemIsUserCheckable)
            parent.setCheckState(0, Qt.Unchecked)

            for sub_group, tables in sub_groups.items():

                child = QTreeWidgetItem(parent)
                child.setText(0, sub_group)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setCheckState(0, Qt.Unchecked)

                for table in tables:
                    leaf = QTreeWidgetItem(child)
                    leaf.setText(0, table)
                    leaf.setFlags(leaf.flags() | Qt.ItemIsUserCheckable)
                    leaf.setCheckState(0, Qt.Unchecked)

        self.tree.expandToDepth(1)
        self.tree.blockSignals(False)

    
    def handle_item_changed(self, item, column):
        state = item.checkState(0)

        self.tree.blockSignals(True)

        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
            self.update_children(child, state)

        self.update_parents(item)

        self.tree.blockSignals(False)

    def update_children(self, item, state):
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
            self.update_children(child, state)

    def update_parents(self, item):
        parent = item.parent()

        while parent:
            checked = 0
            unchecked = 0

            for i in range(parent.childCount()):
                st = parent.child(i).checkState(0)

                if st == Qt.Checked:
                    checked += 1
                elif st == Qt.Unchecked:
                    unchecked += 1

            if checked == parent.childCount():
                parent.setCheckState(0, Qt.Checked)
            elif unchecked == parent.childCount():
                parent.setCheckState(0, Qt.Unchecked)
            else:
                parent.setCheckState(0, Qt.PartiallyChecked)

            parent = parent.parent()


    def select_all_items(self):
        self.tree.blockSignals(True)

        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, Qt.Checked)
            self.update_children(item, Qt.Checked)

        self.tree.blockSignals(False)

    def clear_all_items(self):
        self.tree.blockSignals(True)

        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, Qt.Unchecked)
            self.update_children(item, Qt.Unchecked)

        self.tree.blockSignals(False)

    def get_selected_tables(self):
        selected = []

        root = self.tree.invisibleRootItem()

        for i in range(root.childCount()):
            main_item = root.child(i)

            for j in range(main_item.childCount()):
                group = main_item.child(j)

                for k in range(group.childCount()):
                    leaf = group.child(k)

                    if leaf.checkState(0) == Qt.Checked:
                        selected.append(leaf.text(0))

        return selected

    def show_selections(self):
        selected_names = self.get_selected_tables()

        if not selected_names:
            CustomMessageBox(
                title="No Table Selected",
                text="Please select at least one table to continue.",
                dialogType=MessageBoxType.Warning
            ).exec()
            return

        export_data = {}

        for main_key, groups in GENERATE_RESULTS_DEFAULTS.items():
            main_bucket = {}

            for group_key, tables in groups.items():
                group_bucket = {}

                for table_key, table_data in tables.items():

                    if table_data["label"] in selected_names:
                        group_bucket[table_data["label"]] = table_data

                if group_bucket:
                    main_bucket[group_key.replace("_", " ").title()] = group_bucket

            if main_bucket:
                export_data[main_key.replace("_", " ").title()] = main_bucket

        dlg = ExportTableDialog(export_data)
        dlg.exec()

    def on_tree_item_clicked(self, item, column):
        current = item.checkState(0)

        if current == Qt.Checked:
            item.setCheckState(0, Qt.Unchecked)
        else:
            item.setCheckState(0, Qt.Checked)     