# gui/employee_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QDialogButtonBox, QMessageBox

class EmployeeDialog(QDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent)
        self.employee = employee
        self.setWindowTitle('Сотрудник' if not employee else 'Редактирование сотрудника')
        self.layout = QVBoxLayout()

        form = QFormLayout()
        self.id_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.salary_spin = QDoubleSpinBox()
        self.salary_spin.setRange(0, 1000000)
        self.salary_spin.setSuffix(' руб.')
        self.position_edit = QLineEdit()

        if employee:
            self.id_edit.setText(employee.id)
            self.id_edit.setReadOnly(True)  # ID менять нельзя
            self.name_edit.setText(employee.name)
            self.salary_spin.setValue(employee.salary)
            self.position_edit.setText(employee.position or '')
        else:
            self.id_edit.setPlaceholderText('Табельный номер')

        form.addRow('ID сотрудника:', self.id_edit)
        form.addRow('ФИО:', self.name_edit)
        form.addRow('Оклад:', self.salary_spin)
        form.addRow('Должность:', self.position_edit)

        self.layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

        self.setLayout(self.layout)

    def get_data(self):
        return {
            'id': self.id_edit.text().strip(),
            'name': self.name_edit.text().strip(),
            'salary': self.salary_spin.value(),
            'position': self.position_edit.text().strip()
        }
        