# gui/timesheet_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QSpinBox, QDoubleSpinBox, QDialogButtonBox, QDateEdit
from PyQt5.QtCore import QDate
from datetime import date

class TimesheetDialog(QDialog):
    def __init__(self, parent=None, timesheet=None, employee_name=''):
        super().__init__(parent)
        self.timesheet = timesheet
        self.setWindowTitle(f'Табель: {employee_name}' if employee_name else 'Ввод табеля')
        self.layout = QVBoxLayout()

        form = QFormLayout()
        # Выбор месяца и года
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('MMMM yyyy')
        self.date_edit.setDate(QDate.currentDate())
        if timesheet:
            self.date_edit.setDate(QDate(timesheet.year, timesheet.month, 1))
            self.date_edit.setReadOnly(True)  # месяц не меняем при редактировании

        self.norm_spin = QDoubleSpinBox()
        self.norm_spin.setRange(0, 1000)
        self.norm_spin.setSuffix(' ч')
        self.norm_spin.setDecimals(1)

        self.regular_spin = QDoubleSpinBox()
        self.regular_spin.setRange(0, 1000)
        self.regular_spin.setSuffix(' ч')
        self.regular_spin.setDecimals(1)

        self.overtime_spin = QDoubleSpinBox()
        self.overtime_spin.setRange(0, 1000)
        self.overtime_spin.setSuffix(' ч')
        self.overtime_spin.setDecimals(1)

        self.weekend_spin = QDoubleSpinBox()
        self.weekend_spin.setRange(0, 1000)
        self.weekend_spin.setSuffix(' ч')
        self.weekend_spin.setDecimals(1)

        if timesheet:
            self.norm_spin.setValue(timesheet.norm_hours)
            self.regular_spin.setValue(timesheet.regular_hours)
            self.overtime_spin.setValue(timesheet.overtime_hours)
            self.weekend_spin.setValue(timesheet.weekend_hours)

        form.addRow('Месяц:', self.date_edit)
        form.addRow('Норма часов в месяце:', self.norm_spin)
        form.addRow('Обычные часы:', self.regular_spin)
        form.addRow('Сверхурочные часы:', self.overtime_spin)
        form.addRow('Часы в выходные дни:', self.weekend_spin)

        self.layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

        self.setLayout(self.layout)

    def get_data(self):
        dt = self.date_edit.date()
        return {
            'year': dt.year(),
            'month': dt.month(),
            'norm_hours': self.norm_spin.value(),
            'regular_hours': self.regular_spin.value(),
            'overtime_hours': self.overtime_spin.value(),
            'weekend_hours': self.weekend_spin.value()
        }
        