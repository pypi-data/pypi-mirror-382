from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class PyQt6Framework:
    def __init__(self, app=None):
        self.App = app
        self.QtApp = QApplication([])
        self.Windows = {}
        
    def CreateWindow(self, name: str, title: str = "Window", size: tuple = (800, 600)) -> QMainWindow:
        window = QMainWindow()
        window.setWindowTitle(title)
        window.resize(*size)
        self.Windows[name] = window
        return window
    
    def CreateWidget(self, type_name: str, *args, **kwargs) -> QWidget:
        widget_types = {
            "button": QPushButton,
            "label": QLabel,
            "input": QLineEdit,
            "checkbox": QCheckBox,
            "combobox": QComboBox,
            "slider": QSlider,
            "progressbar": QProgressBar,
            "table": QTableWidget,
            "tree": QTreeWidget,
            "text": QTextEdit,
            "group": QGroupBox,
            "tab": QTabWidget,
            "scroll": QScrollArea
        }
        
        if type_name not in widget_types:
            raise ValueError(f"Unknown widget type: {type_name}")
            
        return widget_types[type_name](*args, **kwargs)
    
    def CreateLayout(self, type_name: str) -> QLayout:
        layout_types = {
            "vertical": QVBoxLayout,
            "horizontal": QHBoxLayout,
            "grid": QGridLayout,
            "form": QFormLayout
        }
        
        if type_name not in layout_types:
            raise ValueError(f"Unknown layout type: {type_name}")
            
        return layout_types[type_name]()
    
    def CreateMenu(self, window_name: str) -> QMenuBar:
        if window_name not in self.Windows:
            raise ValueError(f"Window '{window_name}' not found")
            
        return self.Windows[window_name].menuBar()
    
    def CreateDialog(self, dialog_type: str, title: str, text: str, buttons=None) -> QDialog:
        dialog_types = {
            "info": QMessageBox.information,
            "warning": QMessageBox.warning,
            "error": QMessageBox.critical,
            "question": QMessageBox.question
        }
        
        if dialog_type not in dialog_types:
            raise ValueError(f"Unknown dialog type: {dialog_type}")
            
        return dialog_types[dialog_type](None, title, text, buttons or QMessageBox.Ok)
    
    def CreateStyleSheet(self, element: QWidget, style: dict):
        style_str = "".join([f"{k}: {v};" for k, v in style.items()])
        element.setStyleSheet(style_str)
    
    def StartEventLoop(self):
        self.QtApp.exec()
    
    def QuitApplication(self):
        self.QtApp.quit()