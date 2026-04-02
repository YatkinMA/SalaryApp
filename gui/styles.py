# gui/styles.py
APP_STYLE = """
QMainWindow {
    background-color: #f0f0f0;
}
QPushButton {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 5px 10px;
    border-radius: 3px;
}
QPushButton:hover {
    background-color: #45a049;
}
QPushButton:pressed {
    background-color: #3d8b40;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    padding: 4px;
    border: 1px solid #ccc;
    border-radius: 3px;
}
QTableWidget {
    gridline-color: #ddd;
}
QHeaderView::section {
    background-color: #e0e0e0;
    padding: 4px;
}
"""
