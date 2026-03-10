from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List
import re

app = FastAPI(title="Hospital Attendance System")

class ShiftType(str, Enum):
    MORNING = "MORNING"
    EVENING = "EVENING"

SHIFT_TIMES = {
    ShiftType.MORNING: ("08:00", "16:00"),
    ShiftType.EVENING: ("16:00", "22:00")
}

def to_minutes(t: str) -> int:
    h, m = map(int, t.split(":"))
    return h * 60 + m

def to_hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

class EmployeeAttendance(BaseModel):
    employee_id: int
    employee_name: str
    work_date: date
    shift: ShiftType
    check_in: str
    check_out: str

    @field_validator("check_in", "check_out")
    @classmethod
    def validate_time(cls, v):
        if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", v):
            raise ValueError("Time must be in HH:MM format")
        return v

class Visitor(BaseModel):
    visitor_id: int
    visitor_name: str
    visit_date: date

employees: List[EmployeeAttendance] = []
visitors: List[Visitor] = []

@app.post("/employee/attendance")
def add_employee_attendance(data: EmployeeAttendance):
    shift_start, shift_end = SHIFT_TIMES[data.shift]
    worked = to_minutes(data.check_out) - to_minutes(data.check_in)
    shift_minutes = to_minutes(shift_end) - to_minutes(shift_start)
    if worked < 0:
        worked += 1440
    overtime = max(0, worked - shift_minutes)
    employees.append(data)
    return {
        "employee_id": data.employee_id,
        "employee_name": data.employee_name,
        "shift": data.shift,
        "worked_hours": to_hhmm(worked),
        "overtime_hours": to_hhmm(overtime)
    }

@app.post("/visitor")
def add_visitor(visitor: Visitor):
    visitors.append(visitor)
    return visitor

@app.get("/reports/employees/shifts")
def employee_shifts():
    return [
        {
            "employee_id": e.employee_id,
            "employee_name": e.employee_name,
            "date": e.work_date,
            "shift": e.shift
        } for e in employees
    ]

@app.get("/reports/employees/overtime")
def employee_overtime():
    report = []
    for e in employees:
        shift_start, shift_end = SHIFT_TIMES[e.shift]
        worked = to_minutes(e.check_out) - to_minutes(e.check_in)
        if worked < 0:
            worked += 1440
        overtime = max(0, worked - (to_minutes(shift_end) - to_minutes(shift_start)))
        report.append({
            "employee_id": e.employee_id,
            "employee_name": e.employee_name,
            "overtime_hours": to_hhmm(overtime)
        })
    return report

@app.get("/reports/employees/monthly/{year}/{month}")
def monthly_employee_report(year: int, month: int):
    summary = {}
    for e in employees:
        if e.work_date.year == year and e.work_date.month == month:
            shift_start, shift_end = SHIFT_TIMES[e.shift]
            worked = to_minutes(e.check_out) - to_minutes(e.check_in)
            if worked < 0:
                worked += 1440
            overtime = max(0, worked - (to_minutes(shift_end) - to_minutes(shift_start)))
            if e.employee_id not in summary:
                summary[e.employee_id] = {
                    "employee_name": e.employee_name,
                    "worked": 0,
                    "overtime": 0
                }
            summary[e.employee_id]["worked"] += worked
            summary[e.employee_id]["overtime"] += overtime
    return {
        k: {
            "employee_name": v["employee_name"],
            "total_worked_hours": to_hhmm(v["worked"]),
            "total_overtime_hours": to_hhmm(v["overtime"])
        } for k, v in summary.items()
    }

@app.get("/reports/visitors/daily/{day}")
def daily_visitor_report(day: date):
    return [v for v in visitors if v.visit_date == day]