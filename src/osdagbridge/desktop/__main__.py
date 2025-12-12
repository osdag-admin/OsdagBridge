import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream

# Import template_page
from osdagbridge.desktop.ui.template_page import CustomWindow
from osdagbridge.core.bridge_types.plate_girder.ui_fields import FrontendData

def load_stylesheet():
    """Load the global QSS stylesheet from resources."""
    file = QFile(":/themes/lightstyle.qss")
    if file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(file)
        stylesheet = stream.readAll()
        file.close()
        return stylesheet
    return ""

def main():
    # Create the Qt application instance
    app = QApplication(sys.argv)
    
    # Load and apply the global stylesheet
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)
    
    window = CustomWindow("Osdag Bridge", FrontendData)
    window.showMaximized()
    window.show()

    # Execute the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
