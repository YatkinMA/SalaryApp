# db.py
from models import init_db, Employee, DayTimesheet, MonthlyNorm, SalaryCalculation
from sqlalchemy.exc import IntegrityError

class Database:
    def __init__(self, db_path='salary.db'):
        self.session = init_db(db_path)

    # ---- Сотрудники (без изменений) ----
    def add_employee(self, emp_id, name, salary, position=''):
        emp = Employee(id=emp_id, name=name, salary=salary, position=position)
        try:
            self.session.add(emp)
            self.session.commit()
            return True, None
        except IntegrityError:
            self.session.rollback()
            return False, 'Сотрудник с таким ID уже существует'

    def get_all_employees(self):
        return self.session.query(Employee).order_by(Employee.name).all()

    def get_employee(self, emp_id):
        return self.session.query(Employee).filter(Employee.id == emp_id).first()

    def update_employee(self, emp_id, name=None, salary=None, position=None):
        emp = self.get_employee(emp_id)
        if emp:
            if name is not None:
                emp.name = name
            if salary is not None:
                emp.salary = salary
            if position is not None:
                emp.position = position
            self.session.commit()
            return True
        return False

    def delete_employee(self, emp_id):
        emp = self.get_employee(emp_id)
        if emp:
            self.session.delete(emp)
            self.session.commit()
            return True
        return False

    # ---- Норма часов за месяц ----
    def set_monthly_norm(self, employee_id, year, month, norm_hours):
        norm = self.session.query(MonthlyNorm).filter(
            MonthlyNorm.employee_id == employee_id,
            MonthlyNorm.year == year,
            MonthlyNorm.month == month
        ).first()
        if norm:
            norm.norm_hours = norm_hours
        else:
            norm = MonthlyNorm(employee_id=employee_id, year=year, month=month, norm_hours=norm_hours)
            self.session.add(norm)
        self.session.commit()
        return True

    def get_monthly_norm(self, employee_id, year, month):
        norm = self.session.query(MonthlyNorm).filter(
            MonthlyNorm.employee_id == employee_id,
            MonthlyNorm.year == year,
            MonthlyNorm.month == month
        ).first()
        return norm.norm_hours if norm else None

    # ---- Дневной табель ----
    def save_day_entry(self, employee_id, year, month, day, regular_hours, overtime_hours, weekend_hours):
        entry = self.session.query(DayTimesheet).filter(
            DayTimesheet.employee_id == employee_id,
            DayTimesheet.year == year,
            DayTimesheet.month == month,
            DayTimesheet.day == day
        ).first()
        if entry:
            entry.regular_hours = regular_hours
            entry.overtime_hours = overtime_hours
            entry.weekend_hours = weekend_hours
        else:
            entry = DayTimesheet(
                employee_id=employee_id, year=year, month=month, day=day,
                regular_hours=regular_hours, overtime_hours=overtime_hours, weekend_hours=weekend_hours
            )
            self.session.add(entry)
        self.session.commit()
        return True

    def get_day_entries(self, employee_id, year, month):
        entries = self.session.query(DayTimesheet).filter(
            DayTimesheet.employee_id == employee_id,
            DayTimesheet.year == year,
            DayTimesheet.month == month
        ).all()
        # возвращаем словарь {день: (regular, overtime, weekend)}
        result = {}
        for e in entries:
            result[e.day] = (e.regular_hours, e.overtime_hours, e.weekend_hours)
        return result

    def clear_month_timesheet(self, employee_id, year, month):
        self.session.query(DayTimesheet).filter(
            DayTimesheet.employee_id == employee_id,
            DayTimesheet.year == year,
            DayTimesheet.month == month
        ).delete()
        self.session.commit()

    # ---- Расчёты (история) ----
    def add_salary_calculation(self, employee_id, year, month, regular_payment, overtime_payment, weekend_payment, total):
        calc = SalaryCalculation(
            employee_id=employee_id, year=year, month=month,
            regular_payment=regular_payment, overtime_payment=overtime_payment,
            weekend_payment=weekend_payment, total=total
        )
        self.session.add(calc)
        self.session.commit()
        return calc.id

    def get_salary_calculations_for_employee(self, employee_id):
        return self.session.query(SalaryCalculation).filter(
            SalaryCalculation.employee_id == employee_id
        ).order_by(SalaryCalculation.year, SalaryCalculation.month).all()

    def delete_salary_calculation(self, calc_id):
        calc = self.session.query(SalaryCalculation).get(calc_id)
        if calc:
            self.session.delete(calc)
            self.session.commit()
            return True
        return False

    def close(self):
        self.session.close()
        