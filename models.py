# models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False)
    position = Column(String(100))

class Timesheet(Base):
    __tablename__ = 'timesheets'
    __table_args__ = (UniqueConstraint('employee_id', 'year', 'month', name='uq_timesheet'),)
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    norm_hours = Column(Float, nullable=False)
    regular_hours = Column(Float, default=0)
    overtime_hours = Column(Float, default=0)
    weekend_hours = Column(Float, default=0)

def init_db(db_path='salary.db'):
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
