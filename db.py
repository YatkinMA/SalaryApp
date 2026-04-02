# db.py
from models import init_db, Employee, Timesheet, SalaryCalculation
from sqlalchemy.exc import IntegrityError

class Database:
    def __init__(self, db_path='salary.db'):
        self.session = init_db(db_path)

    # --- Сотрудники ---
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

    # --- Табель ---
    def add_timesheet(self, employee_id, year, month, norm_hours, regular_hours, overtime_hours, weekend_hours):
        ts = Timesheet(
            employee_id=employee_id,
            year=year,
            month=month,
            norm_hours=norm_hours,
            regular_hours=regular_hours,
            overtime_hours=overtime_hours,
            weekend_hours=weekend_hours
        )
        try:
            self.session.add(ts)
            self.session.commit()
            return True, None
        except IntegrityError:
            self.session.rollback()
            return False, 'Табель за этот месяц уже существует'

    def get_timesheet(self, employee_id, year, month):
        return self.session.query(Timesheet).filter(
            Timesheet.employee_id == employee_id,
            Timesheet.year == year,
            Timesheet.month == month
        ).first()

    def get_timesheets_for_employee(self, employee_id):
        return self.session.query(Timesheet).filter(Timesheet.employee_id == employee_id).order_by(Timesheet.year, Timesheet.month).all()

    def delete_timesheet(self, timesheet_id):
        ts = self.session.query(Timesheet).get(timesheet_id)
        if ts:
            self.session.delete(ts)
            self.session.commit()
            return True
        return False

    # --- История расчётов ---
    def add_salary_calculation(self, employee_id, year, month, regular_payment, overtime_payment, weekend_payment, total):
        calc = SalaryCalculation(
            employee_id=employee_id,
            year=year,
            month=month,
            regular_payment=regular_payment,
            overtime_payment=overtime_payment,
            weekend_payment=weekend_payment,
            total=total
        )
        self.session.add(calc)
        self.session.commit()
        return calc.id

    def get_salary_calculations_for_employee(self, employee_id):
        return self.session.query(SalaryCalculation).filter(SalaryCalculation.employee_id == employee_id).order_by(SalaryCalculation.year, SalaryCalculation.month).all()

    def delete_salary_calculation(self, calc_id):
        calc = self.session.query(SalaryCalculation).get(calc_id)
        if calc:
            self.session.delete(calc)
            self.session.commit()
            return True
        return False

    def close(self):
        self.session.close()
        