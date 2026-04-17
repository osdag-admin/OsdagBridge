#if openpyxl not yet installed, run "pip install openpyxl"
import openpyxl
from PySide6.QtWidgets import (
    QDialog, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QSizeGrip, QFileDialog,
    QFrame, QTableWidget, QTableWidgetItem, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from osdagbridge.desktop.ui.utils.custom_titlebar import CustomTitleBar


class ExportTableDialog(QDialog):
    """
    Export Results Table Dialog
    Structure matched with ProjectLocationDialog
    """

    def __init__(self, selected_tables=None, parent=None):
        super().__init__(parent)

        self.selected_tables = selected_tables or {}
        self.setMinimumWidth(780)
        self.setMinimumHeight(620)
        self.setObjectName("export_table_dialog")

        self.setStyleSheet("""
        QDialog#export_table_dialog {
            background: white;
            border: 1px solid #90AF13;
        }

        QLabel {
            color: #1f1f1f;
            font-size: 12px;
        }

        QPushButton#primary {
            background: white;
            color: black;
            border-radius: 6px;
            padding: 8px 18px;
            font-weight: 600;
            min-width: 110px;
        }

        QPushButton#primary:hover {
            background: #90AF13;
        }

        QPushButton#ghost {
            background: white;
            color: black;
            border-radius: 6px;
            padding: 8px 18px;
            font-weight: 600;
            min-width: 110px;
        }

        QPushButton#ghost:hover {
            background: #90AF13;
        }

        QTreeWidget {
            background: white;
            border: none;
            outline: none;
            font-size: 12px;
            color: black;
        }

        QTreeWidget::item {
            height: 28px;
            padding-left: 6px;
            border: none;
        }

        QTreeWidget::item:hover {
            background: rgba(144,175,19,45);
        }

        QTreeWidget::item:selected {
            background: rgba(144,175,19,60);
            color: black;
        }

        QHeaderView::section {
            background: #dbe6b4;
            border: 1px solid #c7d87e;
            padding: 5px;
            font-weight: 600;
        }

        QTableWidget {
            border: 1px solid #90AF13;
            background: white;
            color: black;
            gridline-color: #d6dfb0;
            selection-background-color: rgba(144,175,19,60);
            selection-color: black;
        }

        QTableWidget::item {
            padding: 4px;
            color: black;
            background: white;
        }

        QTableWidget::item:selected {
            color: black;
            background: rgba(144,175,19,60);
        }
                           
        """)

        self._setup_ui()


    def setupWrapper(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar()
        self.title_bar.setTitle("Export Results")
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


    def _setup_ui(self):
        self.setupWrapper()

        main_layout = QVBoxLayout(self.content_widget)
        main_layout.setContentsMargins(18, 18, 18, 14)
        main_layout.setSpacing(14)

        card = QFrame()
        card.setStyleSheet("""
        QFrame {
            background: white;
            border: 1px solid #90AF13;
            border-radius: 12px;
        }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(10)

        # Top split layout
        split = QHBoxLayout()
        split.setSpacing(10)

        # Left tree
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFixedWidth(290)
        self.tree.itemClicked.connect(self.load_selected_table)
        split.addWidget(self.tree)

        # Right preview table
        self.preview = QTableWidget()
        self.preview.setAlternatingRowColors(False)
        self.preview.setStyleSheet("color: black; background: white;")
        self.preview.setColumnCount(2)
        self.preview.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.preview.horizontalHeader().setStretchLastSection(True)
        split.addWidget(self.preview, 1)

        card_layout.addLayout(split)
        main_layout.addWidget(card, 1)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("ghost")
        cancel_btn.clicked.connect(self.reject)

        export_btn = QPushButton("Export")
        export_btn.setObjectName("primary")
        export_btn.clicked.connect(self.export_excel)

        footer.addWidget(cancel_btn)
        footer.addWidget(export_btn)

        main_layout.addLayout(footer)

        self.populate_tree()

    def populate_tree(self):
        """
        Example selected_tables structure:
        {
            "Model Definition": {
                "Bridge Configuration": {
                    "Bridge Configuration Summary": {
                        "Overall Width (m)": "12.5",
                        "Span": "30"
                    }
                }
            }
        }
        """
        for lvl1, sub1 in self.selected_tables.items():
            p1 = QTreeWidgetItem(self.tree, [lvl1])

            for lvl2, sub2 in sub1.items():
                p2 = QTreeWidgetItem(p1, [lvl2])

                for lvl3, data in sub2.items():
                    p3 = QTreeWidgetItem(p2, [lvl3])
                    p3.setData(0, Qt.UserRole, data)

        self.tree.expandAll()


    def load_selected_table(self, item, column):
        data = item.data(0, Qt.UserRole)

        if not isinstance(data, dict):
            return

        columns = data.get("columns", [])
        rows = data.get("rows", [])

        if not columns or not rows:
            return

        # Convert horizontal schema into vertical table
        row_data = rows[0]

        self.preview.clear()
        self.preview.setColumnCount(2)
        self.preview.setRowCount(len(columns))
        self.preview.setHorizontalHeaderLabels(["Parameter", "Value"])

        for i, header in enumerate(columns):

            # Left cell = parameter name
            key_item = QTableWidgetItem(str(header))
            key_item.setForeground(Qt.black)
            key_item.setBackground(QColor("#ffffff"))

            # Right cell = value
            val = row_data[i] if i < len(row_data) else ""
            val_item = QTableWidgetItem(str(val))
            val_item.setForeground(Qt.black)

            self.preview.setItem(i, 0, key_item)
            self.preview.setItem(i, 1, val_item)

            self.preview.verticalHeader().setVisible(False)

            # full width behavior
            header = self.preview.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Fixed)

            table_width = self.preview.viewport().width()

            left_width = int(table_width * 0.60)
            right_width = int(table_width * 0.40)

            self.preview.setColumnWidth(0, left_width)
            self.preview.setColumnWidth(1, right_width)

    # Export to excel
    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel File",
            "results.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not path:
            return

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Results"

        # headers
        for c in range(self.preview.columnCount()):
            header = self.preview.horizontalHeaderItem(c)
            ws.cell(row=1, column=c+1).value = header.text()

        # rows
        for r in range(self.preview.rowCount()):
            for c in range(self.preview.columnCount()):
                item = self.preview.item(r, c)
                ws.cell(row=r+2, column=c+1).value = item.text() if item else ""

        wb.save(path)
        self.accept()