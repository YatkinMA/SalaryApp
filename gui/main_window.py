# gui/main_window.py
import sys
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QMessageBox,
    QTabWidget,
    QHeaderView,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QComboBox,
    QDateEdit,
    QSpinBox,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from db import Database
from salary_calc import SalaryCalculator
from gui.employee_dialog import EmployeeDialog
from gui.timesheet_dialog import TimesheetDialog
from gui.styles import APP_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Табель + Начисление зарплаты")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(APP_STYLE)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Вкладки
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Вкладка "Сотрудники"
        self.emp_tab = QWidget()
        tabs.addTab(self.emp_tab, "Сотрудники")
        self.setup_employees_tab()

        # Вкладка "Табель"
        self.timesheet_tab = QWidget()
        tabs.addTab(self.timesheet_tab, "Табель")
        self.setup_timesheet_tab()

        # Вкладка "Расчет зарплаты"
        self.calc_tab = QWidget()
        tabs.addTab(self.calc_tab, "Расчет зарплаты")
        self.setup_calc_tab()

        # Загрузка данных
        self.load_employees_table()
        self.load_timesheet_table()

    def setup_employees_tab(self):
        layout = QVBoxLayout(self.emp_tab)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_emp_btn = QPushButton("Добавить сотрудника")
        self.add_emp_btn.clicked.connect(self.add_employee)
        self.edit_emp_btn = QPushButton("Редактировать")
        self.edit_emp_btn.clicked.connect(self.edit_employee)
        self.del_emp_btn = QPushButton("Удалить")
        self.del_emp_btn.clicked.connect(self.delete_employee)
        btn_layout.addWidget(self.add_emp_btn)
        btn_layout.addWidget(self.edit_emp_btn)
        btn_layout.addWidget(self.del_emp_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Таблица сотрудников
        self.emp_table = QTableWidget()
        self.emp_table.setColumnCount(4)
        self.emp_table.setHorizontalHeaderLabels(
            ["ID", "ФИО", "Должность", "Оклад, руб."]
        )
        self.emp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.emp_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.emp_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.emp_table)

    def setup_timesheet_tab(self):
        layout = QVBoxLayout(self.timesheet_tab)

        # Фильтр по сотруднику
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Сотрудник:"))
        self.ts_emp_combo = QComboBox()
        self.ts_emp_combo.currentIndexChanged.connect(self.load_timesheet_table)
        filter_layout.addWidget(self.ts_emp_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.add_ts_btn = QPushButton("Добавить табель")
        self.add_ts_btn.clicked.connect(self.add_timesheet)
        self.edit_ts_btn = QPushButton("Редактировать")
        self.edit_ts_btn.clicked.connect(self.edit_timesheet)
        self.del_ts_btn = QPushButton("Удалить")
        self.del_ts_btn.clicked.connect(self.delete_timesheet)
        btn_layout.addWidget(self.add_ts_btn)
        btn_layout.addWidget(self.edit_ts_btn)
        btn_layout.addWidget(self.del_ts_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Таблица табелей
        self.ts_table = QTableWidget()
        self.ts_table.setColumnCount(6)
        self.ts_table.setHorizontalHeaderLabels(
            ["Год", "Месяц", "Норма, ч", "Обычные, ч", "Сверхурочные, ч", "Выходные, ч"]
        )
        self.ts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.ts_table)

    def setup_calc_tab(self):
        layout = QVBoxLayout(self.calc_tab)

        # Выбор сотрудника и периода
        group = QGroupBox("Параметры расчета")
        form = QFormLayout(group)

        self.calc_emp_combo = QComboBox()
        self.calc_emp_combo.currentIndexChanged.connect(self.on_calc_employee_changed)
        form.addRow("Сотрудник:", self.calc_emp_combo)

        self.calc_year_spin = QSpinBox()
        self.calc_year_spin.setRange(2020, 2030)
        self.calc_year_spin.setValue(QDate.currentDate().year())
        self.calc_year_spin.valueChanged.connect(self.on_calc_period_changed)
        self.calc_month_spin = QSpinBox()
        self.calc_month_spin.setRange(1, 12)
        self.calc_month_spin.setValue(QDate.currentDate().month())
        self.calc_month_spin.valueChanged.connect(self.on_calc_period_changed)
        form.addRow("Год:", self.calc_year_spin)
        form.addRow("Месяц:", self.calc_month_spin)

        layout.addWidget(group)

        # Результаты расчета (нередактируемые поля)
        res_group = QGroupBox("Результат расчета")
        res_layout = QFormLayout(res_group)

        self.lbl_hourly_rate = QLineEdit()
        self.lbl_hourly_rate.setReadOnly(True)
        self.lbl_regular = QLineEdit()
        self.lbl_regular.setReadOnly(True)
        self.lbl_overtime = QLineEdit()
        self.lbl_overtime.setReadOnly(True)
        self.lbl_weekend = QLineEdit()
        self.lbl_weekend.setReadOnly(True)
        self.lbl_total = QLineEdit()
        self.lbl_total.setReadOnly(True)
        self.lbl_total.setFont(QFont("Arial", 12, QFont.Bold))

        res_layout.addRow("Ставка за час, руб.:", self.lbl_hourly_rate)
        res_layout.addRow("Оплата обычных часов:", self.lbl_regular)
        res_layout.addRow("Оплата сверхурочных:", self.lbl_overtime)
        res_layout.addRow("Оплата выходных:", self.lbl_weekend)
        res_layout.addRow("ИТОГО к выплате:", self.lbl_total)

        layout.addWidget(res_group)

        # Кнопка расчета (можно обновлять автоматически при смене, но добавим кнопку)
        calc_btn = QPushButton("Рассчитать")
        calc_btn.clicked.connect(self.calculate_salary)
        layout.addWidget(calc_btn)

        layout.addStretch()

    # --- Методы для сотрудников ---
    def load_employees_table(self):
        employees = self.db.get_all_employees()
        self.emp_table.setRowCount(len(employees))
        for row, emp in enumerate(employees):
            self.emp_table.setItem(row, 0, QTableWidgetItem(emp.id))
            self.emp_table.setItem(row, 1, QTableWidgetItem(emp.name))
            self.emp_table.setItem(row, 2, QTableWidgetItem(emp.position or ""))
            self.emp_table.setItem(row, 3, QTableWidgetItem(f"{emp.salary:.2f}"))
        # Обновляем комбобоксы на других вкладках
        self.update_employee_combo_boxes()

    def update_employee_combo_boxes(self):
        employees = self.db.get_all_employees()
        names = [(emp.id, emp.name) for emp in employees]
        # Табель
        self.ts_emp_combo.clear()
        self.ts_emp_combo.addItem("Все сотрудники", None)
        for emp_id, name in names:
            self.ts_emp_combo.addItem(name, emp_id)
        # Расчет
        self.calc_emp_combo.clear()
        for emp_id, name in names:
            self.calc_emp_combo.addItem(name, emp_id)

    def add_employee(self):
        dialog = EmployeeDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            if not data["id"] or not data["name"]:
                QMessageBox.warning(self, "Ошибка", "ID и ФИО обязательны")
                return
            success, msg = self.db.add_employee(
                data["id"], data["name"], data["salary"], data["position"]
            )
            if success:
                self.load_employees_table()
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    def edit_employee(self):
        current = self.emp_table.currentRow()
        if current < 0:
            QMessageBox.information(
                self, "Информация", "Выберите сотрудника для редактирования"
            )
            return
        emp_id = self.emp_table.item(current, 0).text()
        emp = self.db.get_employee(emp_id)
        if not emp:
            return
        dialog = EmployeeDialog(self, employee=emp)
        if dialog.exec_():
            data = dialog.get_data()
            success = self.db.update_employee(
                emp_id, data["name"], data["salary"], data["position"]
            )
            if success:
                self.load_employees_table()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить сотрудника")

    def delete_employee(self):
        current = self.emp_table.currentRow()
        if current < 0:
            QMessageBox.information(
                self, "Информация", "Выберите сотрудника для удаления"
            )
            return
        emp_id = self.emp_table.item(current, 0).text()
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить сотрудника {emp_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.db.delete_employee(emp_id)
            self.load_employees_table()

    # --- Методы для табеля ---
    def load_timesheet_table(self):
        emp_id = self.ts_emp_combo.currentData()
        if emp_id is None:
            # Все сотрудники
            # Для простоты будем показывать все табели, объединив с именами
            timesheets = []
            employees = self.db.get_all_employees()
            for emp in employees:
                ts_list = self.db.get_timesheets_for_employee(emp.id)
                for ts in ts_list:
                    timesheets.append((emp.name, ts))
        else:
            timesheets = [
                (self.ts_emp_combo.currentText(), ts)
                for ts in self.db.get_timesheets_for_employee(emp_id)
            ]

        self.ts_table.setRowCount(len(timesheets))
        for row, (emp_name, ts) in enumerate(timesheets):
            self.ts_table.setItem(row, 0, QTableWidgetItem(str(ts.year)))
            self.ts_table.setItem(row, 1, QTableWidgetItem(str(ts.month)))
            self.ts_table.setItem(row, 2, QTableWidgetItem(f"{ts.norm_hours:.1f}"))
            self.ts_table.setItem(row, 3, QTableWidgetItem(f"{ts.regular_hours:.1f}"))
            self.ts_table.setItem(row, 4, QTableWidgetItem(f"{ts.overtime_hours:.1f}"))
            self.ts_table.setItem(row, 5, QTableWidgetItem(f"{ts.weekend_hours:.1f}"))
            # Сохраняем id табеля в скрытом столбце? Можно добавить, но пока не нужно

    def add_timesheet(self):
        emp_id = self.ts_emp_combo.currentData()
        if emp_id is None:
            QMessageBox.information(
                self,
                "Информация",
                "Выберите конкретного сотрудника для добавления табеля",
            )
            return
        emp = self.db.get_employee(emp_id)
        if not emp:
            return
        dialog = TimesheetDialog(self, employee_name=emp.name)
        if dialog.exec_():
            data = dialog.get_data()
            success, msg = self.db.add_timesheet(
                emp_id,
                data["year"],
                data["month"],
                data["norm_hours"],
                data["regular_hours"],
                data["overtime_hours"],
                data["weekend_hours"],
            )
            if success:
                self.load_timesheet_table()
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    def edit_timesheet(self):
        # Получить выбранную строку
        current = self.ts_table.currentRow()
        if current < 0:
            QMessageBox.information(
                self, "Информация", "Выберите запись табеля для редактирования"
            )
            return
        # Нужно определить employee_id и год/месяц
        # Сначала получаем сотрудника из комбобокса
        emp_id = self.ts_emp_combo.currentData()
        if emp_id is None:
            QMessageBox.information(
                self,
                "Информация",
                "Для редактирования выберите конкретного сотрудника в фильтре",
            )
            return
        year = int(self.ts_table.item(current, 0).text())
        month = int(self.ts_table.item(current, 1).text())
        ts = self.db.get_timesheet(emp_id, year, month)
        if not ts:
            return
        emp = self.db.get_employee(emp_id)
        dialog = TimesheetDialog(self, timesheet=ts, employee_name=emp.name)
        if dialog.exec_():
            data = dialog.get_data()
            # Удаляем старую и добавляем новую (т.к. уникальность по employee/year/month)
            self.db.delete_timesheet(ts.id)
            success, msg = self.db.add_timesheet(
                emp_id,
                data["year"],
                data["month"],
                data["norm_hours"],
                data["regular_hours"],
                data["overtime_hours"],
                data["weekend_hours"],
            )
            if success:
                self.load_timesheet_table()
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    def delete_timesheet(self):
        current = self.ts_table.currentRow()
        if current < 0:
            QMessageBox.information(
                self, "Информация", "Выберите запись табеля для удаления"
            )
            return
        emp_id = self.ts_emp_combo.currentData()
        if emp_id is None:
            QMessageBox.information(
                self,
                "Информация",
                "Для удаления выберите конкретного сотрудника в фильтре",
            )
            return
        year = int(self.ts_table.item(current, 0).text())
        month = int(self.ts_table.item(current, 1).text())
        ts = self.db.get_timesheet(emp_id, year, month)
        if not ts:
            return
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить табель за {month}.{year}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.db.delete_timesheet(ts.id)
            self.load_timesheet_table()

    # --- Методы для расчета ---
    def on_calc_employee_changed(self):
        # При смене сотрудника можно обновить доступные периоды, но пока просто очищаем поля
        self.clear_calc_fields()

    def on_calc_period_changed(self):
        self.clear_calc_fields()

    def clear_calc_fields(self):
        self.lbl_hourly_rate.clear()
        self.lbl_regular.clear()
        self.lbl_overtime.clear()
        self.lbl_weekend.clear()
        self.lbl_total.clear()

    def calculate_salary(self):
        emp_id = self.calc_emp_combo.currentData()
        if not emp_id:
            QMessageBox.information(self, "Информация", "Выберите сотрудника")
            return
        year = self.calc_year_spin.value()
        month = self.calc_month_spin.value()
        ts = self.db.get_timesheet(emp_id, year, month)
        if not ts:
            QMessageBox.warning(self, "Ошибка", "Табель за указанный месяц не найден")
            return
        emp = self.db.get_employee(emp_id)
        if not emp:
            return

        result = SalaryCalculator.calculate(
            emp.salary,
            ts.norm_hours,
            ts.regular_hours,
            ts.overtime_hours,
            ts.weekend_hours,
        )
        if result.get("error"):
            QMessageBox.warning(self, "Ошибка расчета", result["error"])
            return

        self.lbl_hourly_rate.setText(f"{result['hourly_rate']:.2f} руб.")
        self.lbl_regular.setText(f"{result['regular_payment']:.2f} руб.")
        self.lbl_overtime.setText(f"{result['overtime_payment']:.2f} руб.")
        self.lbl_weekend.setText(f"{result['weekend_payment']:.2f} руб.")
        self.lbl_total.setText(f"{result['total']:.2f} руб.")

    def closeEvent(self, event):
        self.db.close()
        event.accept()
