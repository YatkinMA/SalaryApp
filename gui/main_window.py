# gui/main_window.py
import sys
from tkinter.font import names
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QMessageBox, QTabWidget, QHeaderView,
                             QGroupBox, QFormLayout, QLineEdit, QDoubleSpinBox,
                             QComboBox, QDateEdit, QSpinBox, QFileDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QSpinBox, QDoubleSpinBox, QGridLayout, QGroupBox
from calendar import monthrange

from db import Database
from salary_calc import SalaryCalculator
from gui.employee_dialog import EmployeeDialog
from gui.timesheet_dialog import TimesheetDialog
from gui.styles import APP_STYLE

import csv

month_names = {
    1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
    5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
    9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Табель + Начисление зарплаты")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(APP_STYLE)
        
        tabs = QTabWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.addWidget(tabs)
        
        # Вкладка "Дневной табель"
        self.day_tab = QWidget()

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Вкладки
        self.day_tab = QWidget()
        tabs.addTab(self.day_tab, "Дневной табель")
        self.setup_day_timesheet_tab()

        # Вкладка "Сотрудники"
        self.emp_tab = QWidget()
        tabs.addTab(self.emp_tab, "Сотрудники")
        self.setup_employees_tab()


        # Вкладка "Расчет зарплаты"
        self.calc_tab = QWidget()
        tabs.addTab(self.calc_tab, "Расчет зарплаты")
        self.setup_calc_tab()

        # Загрузка данных
        self.load_employees_table()
        self.load_timesheet_table()
        self.load_history_table()

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
        self.export_emp_btn = QPushButton("Выгрузить CSV")
        self.export_emp_btn.clicked.connect(self.export_employees_csv)
        btn_layout.addWidget(self.add_emp_btn)
        btn_layout.addWidget(self.edit_emp_btn)
        btn_layout.addWidget(self.del_emp_btn)
        btn_layout.addWidget(self.export_emp_btn)
        btn_layout.addWidget(self.import_emp_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        self.import_emp_btn = QPushButton("Загрузить CSV")
        self.import_emp_btn.clicked.connect(self.import_employees_csv)

        # Таблица сотрудников
        self.emp_table = QTableWidget()
        self.emp_table.setColumnCount(4)
        self.emp_table.setHorizontalHeaderLabels(["ID", "ФИО", "Должность", "Оклад, руб."])
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
        self.export_ts_btn = QPushButton("Выгрузить CSV")
        self.export_ts_btn.clicked.connect(self.export_timesheet_csv)
        btn_layout.addWidget(self.add_ts_btn)
        btn_layout.addWidget(self.edit_ts_btn)
        btn_layout.addWidget(self.del_ts_btn)
        btn_layout.addWidget(self.export_ts_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Таблица табелей
        self.ts_table = QTableWidget()
        self.ts_table.setColumnCount(6)
        self.ts_table.setHorizontalHeaderLabels(["Год", "Месяц", "Норма, ч", "Обычные, ч", "Сверхурочные, ч", "Выходные, ч"])
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

        # Кнопка расчета
        calc_btn = QPushButton("Рассчитать")
        calc_btn.clicked.connect(self.calculate_salary)
        layout.addWidget(calc_btn)

        # --- История расчётов ---
        history_group = QGroupBox("Сохранённые расчёты")
        history_layout = QVBoxLayout(history_group)

        hist_btn_layout = QHBoxLayout()
        self.save_calc_btn = QPushButton("Добавить текущий расчёт в таблицу")
        self.save_calc_btn.clicked.connect(self.save_current_calculation)
        self.refresh_history_btn = QPushButton("Обновить")
        self.refresh_history_btn.clicked.connect(self.load_history_table)
        self.export_history_btn = QPushButton("Выгрузить CSV")
        self.export_history_btn.clicked.connect(self.export_history_csv)
        hist_btn_layout.addWidget(self.save_calc_btn)
        hist_btn_layout.addWidget(self.refresh_history_btn)
        hist_btn_layout.addWidget(self.export_history_btn)
        hist_btn_layout.addStretch()
        history_layout.addLayout(hist_btn_layout)

        # Таблица истории (с hidden столбцом ID)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(["Год", "Месяц", "Оплата обычных", "Оплата сверхурочных", "Оплата выходных", "Итого", "ID"])
        self.history_table.setColumnHidden(6, True)  # скрываем ID
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        history_layout.addWidget(self.history_table)

        # Кнопка удаления
        self.del_history_btn = QPushButton("Удалить выбранный расчёт")
        self.del_history_btn.clicked.connect(self.delete_selected_calculation)
        history_layout.addWidget(self.del_history_btn)

        layout.addWidget(history_group)
        layout.addStretch()

    def setup_day_timesheet_tab(self):
        layout = QVBoxLayout(self.day_tab)

        # Выбор сотрудника и месяца
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Сотрудник:"))
        self.dt_emp_combo = QComboBox()
        self.dt_emp_combo.currentIndexChanged.connect(self.on_dt_employee_changed)
        filter_layout.addWidget(self.dt_emp_combo)

        filter_layout.addWidget(QLabel("Год:"))
        self.dt_year_spin = QSpinBox()
        self.dt_year_spin.setRange(2020, 2030)
        self.dt_year_spin.setValue(QDate.currentDate().year())
        self.dt_year_spin.valueChanged.connect(self.load_day_timesheet_table)
        filter_layout.addWidget(self.dt_year_spin)

        filter_layout.addWidget(QLabel("Месяц:"))
        self.dt_month_spin = QSpinBox()
        self.dt_month_spin.setRange(1, 12)
        self.dt_month_spin.setValue(QDate.currentDate().month())
        self.dt_month_spin.valueChanged.connect(self.load_day_timesheet_table)
        filter_layout.addWidget(self.dt_month_spin)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Норма часов за месяц
        norm_layout = QHBoxLayout()
        norm_layout.addWidget(QLabel("Норма часов в месяце:"))
        self.norm_spin = QDoubleSpinBox()
        self.norm_spin.setRange(0, 500)
        self.norm_spin.setSuffix(" ч")
        self.norm_spin.valueChanged.connect(self.save_norm)
        norm_layout.addWidget(self.norm_spin)
        norm_layout.addStretch()
        layout.addLayout(norm_layout)

        # Таблица дней (динамическая)
        self.day_table = QTableWidget()
        self.day_table.setColumnCount(4)
        self.day_table.setHorizontalHeaderLabels(["День", "Обычные часы", "Сверхурочные", "Выходные"])
        self.day_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.day_table)

        # Кнопки действий
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить все изменения")
        save_btn.clicked.connect(self.save_day_timesheet)
        export_btn = QPushButton("Выгрузить CSV")
        export_btn.clicked.connect(self.export_day_timesheet_csv)
        import_btn = QPushButton("Загрузить CSV")
        import_btn.clicked.connect(self.import_day_timesheet_csv)
        clear_btn = QPushButton("Очистить месяц")
        clear_btn.clicked.connect(self.clear_day_timesheet)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(import_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    # --- Методы для сотрудников ---
    def load_employees_table(self):
        employees = self.db.get_all_employees()
        self.emp_table.setRowCount(len(employees))
        for row, emp in enumerate(employees):
            self.emp_table.setItem(row, 0, QTableWidgetItem(emp.id))
            self.emp_table.setItem(row, 1, QTableWidgetItem(emp.name))
            self.emp_table.setItem(row, 2, QTableWidgetItem(emp.position or ''))
            self.emp_table.setItem(row, 3, QTableWidgetItem(f"{emp.salary:.2f}"))
        # Обновляем комбобоксы на других вкладках
        self.update_employee_combo_boxes()

    def update_employee_combo_boxes(self):
        employees = self.db.get_all_employees()
        names = [(emp.id, emp.name) for emp in employees]

        # Для дневного табеля
        self.dt_emp_combo.clear()
        for emp_id, name in names:
            self.dt_emp_combo.addItem(name, emp_id)

        # Для расчёта зарплаты
        self.calc_emp_combo.clear()
        for emp_id, name in names:
            self.calc_emp_combo.addItem(name, emp_id)

    def add_employee(self):
        dialog = EmployeeDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            if not data['id'] or not data['name']:
                QMessageBox.warning(self, "Ошибка", "ID и ФИО обязательны")
                return
            success, msg = self.db.add_employee(data['id'], data['name'], data['salary'], data['position'])
            if success:
                self.load_employees_table()
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    def edit_employee(self):
        current = self.emp_table.currentRow()
        if current < 0:
            QMessageBox.information(self, "Информация", "Выберите сотрудника для редактирования")
            return
        emp_id = self.emp_table.item(current, 0).text()
        emp = self.db.get_employee(emp_id)
        if not emp:
            return
        dialog = EmployeeDialog(self, employee=emp)
        if dialog.exec_():
            data = dialog.get_data()
            success = self.db.update_employee(emp_id, data['name'], data['salary'], data['position'])
            if success:
                self.load_employees_table()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить сотрудника")

    def delete_employee(self):
        current = self.emp_table.currentRow()
        if current < 0:
            QMessageBox.information(self, "Информация", "Выберите сотрудника для удаления")
            return
        emp_id = self.emp_table.item(current, 0).text()
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить сотрудника {emp_id}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_employee(emp_id)
            self.load_employees_table()

    def export_employees_csv(self):
        employees = self.db.get_all_employees()
        if not employees:
            QMessageBox.information(self, "Информация", "Нет данных для выгрузки")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV", "", "CSV files (*.csv)")
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["ID", "ФИО", "Должность", "Оклад"])
                for emp in employees:
                    writer.writerow([emp.id, emp.name, emp.position or '', emp.salary])
            QMessageBox.information(self, "Успех", f"Выгружено в {filename}")

    def import_employees_csv(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Загрузить CSV", "", "CSV files (*.csv)")
        if not filename:
            return
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter=';')
                header = next(reader)  # пропускаем заголовок
                for row in reader:
                    if len(row) < 4:
                        continue
                    emp_id, name, position, salary_str = row[0], row[1], row[2], row[3]
                    salary = float(salary_str)
                    existing = self.db.get_employee(emp_id)
                    if existing:
                        self.db.update_employee(emp_id, name=name, salary=salary, position=position)
                    else:
                        self.db.add_employee(emp_id, name, salary, position)
            self.load_employees_table()
            QMessageBox.information(self, "Успех", "Сотрудники загружены")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {str(e)}")

    # --- Методы для табеля ---
    def load_timesheet_table(self):
        emp_id = self.ts_emp_combo.currentData()
        if emp_id is None:
            # Все сотрудники
            timesheets = []
            employees = self.db.get_all_employees()
            for emp in employees:
                ts_list = self.db.get_timesheets_for_employee(emp.id)
                for ts in ts_list:
                    timesheets.append((emp.name, ts))
        else:
            timesheets = [(self.ts_emp_combo.currentText(), ts) for ts in self.db.get_timesheets_for_employee(emp_id)]

        self.ts_table.setRowCount(len(timesheets))
        for row, (emp_name, ts) in enumerate(timesheets):
            self.ts_table.setItem(row, 0, QTableWidgetItem(str(ts.year)))
            self.ts_table.setItem(row, 1, QTableWidgetItem(month_names[ts.month]))
            self.ts_table.setItem(row, 2, QTableWidgetItem(f"{ts.norm_hours:.1f}"))
            self.ts_table.setItem(row, 3, QTableWidgetItem(f"{ts.regular_hours:.1f}"))
            self.ts_table.setItem(row, 4, QTableWidgetItem(f"{ts.overtime_hours:.1f}"))
            self.ts_table.setItem(row, 5, QTableWidgetItem(f"{ts.weekend_hours:.1f}"))

    def add_timesheet(self):
        emp_id = self.ts_emp_combo.currentData()
        if emp_id is None:
            QMessageBox.information(self, "Информация", "Выберите конкретного сотрудника для добавления табеля")
            return
        emp = self.db.get_employee(emp_id)
        if not emp:
            return
        dialog = TimesheetDialog(self, employee_name=emp.name)
        if dialog.exec_():
            data = dialog.get_data()
            success, msg = self.db.add_timesheet(
                emp_id, data['year'], data['month'],
                data['norm_hours'], data['regular_hours'],
                data['overtime_hours'], data['weekend_hours']
            )
            if success:
                self.load_timesheet_table()
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    def edit_timesheet(self):
        current = self.ts_table.currentRow()
        if current < 0:
            QMessageBox.information(self, "Информация", "Выберите запись табеля для редактирования")
            return
        emp_id = self.ts_emp_combo.currentData()
        if emp_id is None:
            QMessageBox.information(self, "Информация", "Для редактирования выберите конкретного сотрудника в фильтре")
            return
        year = int(self.ts_table.item(current, 0).text())
        month_num = None
        # Находим номер месяца по названию
        month_name = self.ts_table.item(current, 1).text()
        for num, name in month_names.items():
            if name == month_name:
                month_num = num
                break
        if month_num is None:
            return
        ts = self.db.get_timesheet(emp_id, year, month_num)
        if not ts:
            return
        emp = self.db.get_employee(emp_id)
        dialog = TimesheetDialog(self, timesheet=ts, employee_name=emp.name)
        if dialog.exec_():
            data = dialog.get_data()
            # Удаляем старую и добавляем новую (т.к. уникальность по employee/year/month)
            self.db.delete_timesheet(ts.id)
            success, msg = self.db.add_timesheet(
                emp_id, data['year'], data['month'],
                data['norm_hours'], data['regular_hours'],
                data['overtime_hours'], data['weekend_hours']
            )
            if success:
                self.load_timesheet_table()
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    def delete_timesheet(self):
        current = self.ts_table.currentRow()
        if current < 0:
            QMessageBox.information(self, "Информация", "Выберите запись табеля для удаления")
            return
        emp_id = self.ts_emp_combo.currentData()
        if emp_id is None:
            QMessageBox.information(self, "Информация", "Для удаления выберите конкретного сотрудника в фильтре")
            return
        year = int(self.ts_table.item(current, 0).text())
        month_name = self.ts_table.item(current, 1).text()
        month_num = None
        for num, name in month_names.items():
            if name == month_name:
                month_num = num
                break
        if month_num is None:
            return
        ts = self.db.get_timesheet(emp_id, year, month_num)
        if not ts:
            return
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить табель за {month_name} {year}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_timesheet(ts.id)
            self.load_timesheet_table()

    def export_timesheet_csv(self):
        emp_id = self.ts_emp_combo.currentData()
        if emp_id is None:
            # Все сотрудники
            data = []
            employees = self.db.get_all_employees()
            for emp in employees:
                ts_list = self.db.get_timesheets_for_employee(emp.id)
                for ts in ts_list:
                    data.append([
                        emp.id, emp.name,
                        ts.year, month_names[ts.month],
                        ts.norm_hours, ts.regular_hours, ts.overtime_hours, ts.weekend_hours
                    ])
        else:
            emp = self.db.get_employee(emp_id)
            if not emp:
                return
            ts_list = self.db.get_timesheets_for_employee(emp_id)
            data = []
            for ts in ts_list:
                data.append([
                    emp.id, emp.name,
                    ts.year, month_names[ts.month],
                    ts.norm_hours, ts.regular_hours, ts.overtime_hours, ts.weekend_hours
                ])

        if not data:
            QMessageBox.information(self, "Информация", "Нет данных для выгрузки")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV", "", "CSV files (*.csv)")
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["ID", "ФИО", "Год", "Месяц", "Норма, ч", "Обычные, ч", "Сверхурочные, ч", "Выходные, ч"])
                writer.writerows(data)
            QMessageBox.information(self, "Успех", f"Выгружено в {filename}")

    def on_dt_employee_changed(self):
    self.load_day_timesheet_table()

def load_day_timesheet_table(self):
    emp_id = self.dt_emp_combo.currentData()
    if not emp_id:
        self.day_table.setRowCount(0)
        return
    year = self.dt_year_spin.value()
    month = self.dt_month_spin.value()
    # Загружаем норму
    norm = self.db.get_monthly_norm(emp_id, year, month)
    self.norm_spin.setValue(norm if norm is not None else 0)
    # Загружаем дни
    entries = self.db.get_day_entries(emp_id, year, month)
    days_in_month = monthrange(year, month)[1]
    self.day_table.setRowCount(days_in_month)
    for day in range(1, days_in_month + 1):
        # День
        self.day_table.setItem(day-1, 0, QTableWidgetItem(str(day)))
        # Обычные
        regular = entries.get(day, (0,0,0))[0]
        regular_spin = QDoubleSpinBox()
        regular_spin.setRange(0, 24)
        regular_spin.setValue(regular)
        regular_spin.setDecimals(1)
        self.day_table.setCellWidget(day-1, 1, regular_spin)
        # Сверхурочные
        overtime = entries.get(day, (0,0,0))[1]
        overtime_spin = QDoubleSpinBox()
        overtime_spin.setRange(0, 24)
        overtime_spin.setValue(overtime)
        overtime_spin.setDecimals(1)
        self.day_table.setCellWidget(day-1, 2, overtime_spin)
        # Выходные
        weekend = entries.get(day, (0,0,0))[2]
        weekend_spin = QDoubleSpinBox()
        weekend_spin.setRange(0, 24)
        weekend_spin.setValue(weekend)
        weekend_spin.setDecimals(1)
        self.day_table.setCellWidget(day-1, 3, weekend_spin)

def save_norm(self):
    emp_id = self.dt_emp_combo.currentData()
    if not emp_id:
        return
    year = self.dt_year_spin.value()
    month = self.dt_month_spin.value()
    norm = self.norm_spin.value()
    self.db.set_monthly_norm(emp_id, year, month, norm)

def save_day_timesheet(self):
    emp_id = self.dt_emp_combo.currentData()
    if not emp_id:
        QMessageBox.warning(self, "Ошибка", "Выберите сотрудника")
        return
    year = self.dt_year_spin.value()
    month = self.dt_month_spin.value()
    days_in_month = monthrange(year, month)[1]
    for row in range(days_in_month):
        day = row + 1
        regular = self.day_table.cellWidget(row, 1).value()
        overtime = self.day_table.cellWidget(row, 2).value()
        weekend = self.day_table.cellWidget(row, 3).value()
        self.db.save_day_entry(emp_id, year, month, day, regular, overtime, weekend)
    QMessageBox.information(self, "Успех", "Табель сохранён")

def clear_day_timesheet(self):
    emp_id = self.dt_emp_combo.currentData()
    if not emp_id:
        return
    year = self.dt_year_spin.value()
    month = self.dt_month_spin.value()
    reply = QMessageBox.question(self, "Подтверждение", f"Очистить весь табель за {month}.{year}?",
                                 QMessageBox.Yes | QMessageBox.No)
    if reply == QMessageBox.Yes:
        self.db.clear_month_timesheet(emp_id, year, month)
        self.load_day_timesheet_table()

def export_day_timesheet_csv(self):
    emp_id = self.dt_emp_combo.currentData()
    if not emp_id:
        QMessageBox.warning(self, "Ошибка", "Выберите сотрудника")
        return
    emp = self.db.get_employee(emp_id)
    if not emp:
        return
    year = self.dt_year_spin.value()
    month = self.dt_month_spin.value()
    entries = self.db.get_day_entries(emp_id, year, month)
    filename, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV", "", "CSV files (*.csv)")
    if filename:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(["День", "Обычные часы", "Сверхурочные часы", "Выходные часы"])
            days_in_month = monthrange(year, month)[1]
            for day in range(1, days_in_month+1):
                regular, overtime, weekend = entries.get(day, (0,0,0))
                writer.writerow([day, regular, overtime, weekend])
        QMessageBox.information(self, "Успех", f"Выгружено в {filename}")

def import_day_timesheet_csv(self):
    emp_id = self.dt_emp_combo.currentData()
    if not emp_id:
        QMessageBox.warning(self, "Ошибка", "Выберите сотрудника")
        return
    filename, _ = QFileDialog.getOpenFileName(self, "Загрузить CSV", "", "CSV files (*.csv)")
    if not filename:
        return
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            header = next(reader)  # пропускаем заголовок
            for row in reader:
                if len(row) < 4:
                    continue
                day = int(row[0])
                regular = float(row[1])
                overtime = float(row[2])
                weekend = float(row[3])
                self.db.save_day_entry(emp_id, self.dt_year_spin.value(), self.dt_month_spin.value(), day, regular, overtime, weekend)
        self.load_day_timesheet_table()
        QMessageBox.information(self, "Успех", "Данные загружены")
    except Exception as e:
        QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить: {str(e)}")

    # --- Методы для расчета ---
    def on_calc_employee_changed(self):
        self.clear_calc_fields()
        self.load_history_table()

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
        # Получаем норму
        norm = self.db.get_monthly_norm(emp_id, year, month)
        if norm is None:
            QMessageBox.warning(self, "Ошибка", "Норма часов за месяц не задана. Задайте на вкладке 'Дневной табель'.")
            return
        # Получаем дневные записи
        entries = self.db.get_day_entries(emp_id, year, month)
        if not entries:
            QMessageBox.warning(self, "Ошибка", "Нет данных за этот месяц. Введите табель.")
            return
        emp = self.db.get_employee(emp_id)
        if not emp:
            return

        result = SalaryCalculator.calculate(emp.salary, norm, entries)
        if result.get('error'):
            QMessageBox.warning(self, "Ошибка расчета", result['error'])
            return

        self.lbl_hourly_rate.setText(f"{result['hourly_rate']:.2f} руб.")
        self.lbl_regular.setText(f"{result['regular_payment']:.2f} руб.")
        self.lbl_overtime.setText(f"{result['overtime_payment']:.2f} руб.")
        self.lbl_weekend.setText(f"{result['weekend_payment']:.2f} руб.")
        self.lbl_total.setText(f"{result['total']:.2f} руб.")

    # --- История расчётов ---
    def save_current_calculation(self):
        emp_id = self.calc_emp_combo.currentData()
        if not emp_id:
            QMessageBox.information(self, "Информация", "Выберите сотрудника")
            return
        year = self.calc_year_spin.value()
        month = self.calc_month_spin.value()
        if not self.lbl_total.text():
            QMessageBox.information(self, "Информация", "Сначала выполните расчёт (кнопка Рассчитать)")
            return
        total_text = self.lbl_total.text().replace(" руб.", "")
        regular_text = self.lbl_regular.text().replace(" руб.", "")
        overtime_text = self.lbl_overtime.text().replace(" руб.", "")
        weekend_text = self.lbl_weekend.text().replace(" руб.", "")
        try:
            total = float(total_text)
            regular = float(regular_text) if regular_text else 0
            overtime = float(overtime_text) if overtime_text else 0
            weekend = float(weekend_text) if weekend_text else 0
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить сумму")
            return

        self.db.add_salary_calculation(emp_id, year, month, regular, overtime, weekend, total)
        QMessageBox.information(self, "Успех", "Расчёт сохранён")
        self.load_history_table()

    def load_history_table(self):
        emp_id = self.calc_emp_combo.currentData()
        if not emp_id:
            self.history_table.setRowCount(0)
            return
        calculations = self.db.get_salary_calculations_for_employee(emp_id)
        self.history_table.setRowCount(len(calculations))
        for row, calc in enumerate(calculations):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(calc.year)))
            self.history_table.setItem(row, 1, QTableWidgetItem(month_names[calc.month]))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"{calc.regular_payment:.2f}"))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{calc.overtime_payment:.2f}"))
            self.history_table.setItem(row, 4, QTableWidgetItem(f"{calc.weekend_payment:.2f}"))
            self.history_table.setItem(row, 5, QTableWidgetItem(f"{calc.total:.2f}"))
            self.history_table.setItem(row, 6, QTableWidgetItem(str(calc.id)))

    def delete_selected_calculation(self):
        current = self.history_table.currentRow()
        if current < 0:
            QMessageBox.information(self, "Информация", "Выберите запись для удаления")
            return
        calc_id = int(self.history_table.item(current, 6).text())
        self.db.delete_salary_calculation(calc_id)
        self.load_history_table()

    def export_history_csv(self):
        emp_id = self.calc_emp_combo.currentData()
        if not emp_id:
            QMessageBox.information(self, "Информация", "Выберите сотрудника")
            return
        emp = self.db.get_employee(emp_id)
        if not emp:
            return
        calculations = self.db.get_salary_calculations_for_employee(emp_id)
        if not calculations:
            QMessageBox.information(self, "Информация", "Нет сохранённых расчётов для этого сотрудника")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV", "", "CSV files (*.csv)")
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["Год", "Месяц", "Оплата обычных", "Оплата сверхурочных", "Оплата выходных", "Итого"])
                for calc in calculations:
                    writer.writerow([calc.year, month_names[calc.month], calc.regular_payment, calc.overtime_payment, calc.weekend_payment, calc.total])
            QMessageBox.information(self, "Успех", f"Выгружено в {filename}")

    def closeEvent(self, event):
        self.db.close()
        event.accept()
        