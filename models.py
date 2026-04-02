# models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False)
    position = Column(String(100))

class DayTimesheet(Base):
    __tablename__ = 'day_timesheets'
    __table_args__ = (UniqueConstraint('employee_id', 'year', 'month', 'day', name='uq_day_timesheet'),)
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    regular_hours = Column(Float, default=0)
    overtime_hours = Column(Float, default=0)
    weekend_hours = Column(Float, default=0)

class MonthlyNorm(Base):
    __tablename__ = 'monthly_norms'
    __table_args__ = (UniqueConstraint('employee_id', 'year', 'month', name='uq_monthly_norm'),)
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    norm_hours = Column(Float, nullable=False)

class SalaryCalculation(Base):
    __tablename__ = 'salary_calculations'
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    regular_payment = Column(Float, default=0)
    overtime_payment = Column(Float, default=0)
    weekend_payment = Column(Float, default=0)
    total = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db(db_path='salary.db'):
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
