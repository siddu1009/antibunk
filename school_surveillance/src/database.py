import sqlite3
import json
from typing import List, Dict, Tuple
from datetime import datetime
from .data_models import Student, Schedule, Zone, Violation

DATABASE_NAME = "school_surveillance.db"

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT,
            image_path TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            student_id TEXT,
            period INTEGER,
            classroom_id TEXT,
            PRIMARY KEY (student_id, period),
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS zones (
            id TEXT PRIMARY KEY,
            name TEXT,
            allowed_periods TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            student_id TEXT,
            zone_id TEXT,
            timestamp TEXT,
            grace_period_expired INTEGER,
            alert_sent INTEGER,
            PRIMARY KEY (student_id, timestamp),
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()

def save_students(students: List[Student]):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM students")
    for student in students:
        c.execute("INSERT INTO students (id, name, image_path) VALUES (?, ?, ?)",
                  (student.id, student.name, student.image_path))
    conn.commit()
    conn.close()

def load_students() -> List[Student]:
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, image_path FROM students")
    students_data = c.fetchall()
    conn.close()
    return [Student(id=s[0], name=s[1], image_path=s[2]) for s in students_data]

def save_schedules(schedules: List[Schedule]):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM schedules")
    for schedule in schedules:
        c.execute("INSERT INTO schedules (student_id, period, classroom_id) VALUES (?, ?, ?)",
                  (schedule.student_id, schedule.period, schedule.classroom_id))
    conn.commit()
    conn.close()

def load_schedules() -> List[Schedule]:
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT student_id, period, classroom_id FROM schedules")
    schedules_data = c.fetchall()
    conn.close()
    return [Schedule(student_id=s[0], period=s[1], classroom_id=s[2]) for s in schedules_data]

def save_zones(zones: List[Zone]):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM zones")
    for zone in zones:
        c.execute("INSERT INTO zones (id, name, allowed_periods) VALUES (?, ?, ?)",
                  (zone.id, zone.name, json.dumps(zone.allowed_periods)))
    conn.commit()
    conn.close()

def load_zones() -> List[Zone]:
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, allowed_periods FROM zones")
    zones_data = c.fetchall()
    conn.close()
    return [Zone(id=z[0], name=z[1], allowed_periods=json.loads(z[2])) for z in zones_data]

def save_violation(violation: Violation):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO violations (student_id, zone_id, timestamp, grace_period_expired, alert_sent) VALUES (?, ?, ?, ?, ?)",
              (violation.student_id, violation.zone_id, violation.timestamp.isoformat(),
               int(violation.grace_period_expired), int(violation.alert_sent)))
    conn.commit()
    conn.close()

def load_violations() -> List[Violation]:
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT student_id, zone_id, timestamp, grace_period_expired, alert_sent FROM violations")
    violations_data = c.fetchall()
    conn.close()
    return [Violation(student_id=v[0], zone_id=v[1], timestamp=datetime.fromisoformat(v[2]),
                      grace_period_expired=bool(v[3]), alert_sent=bool(v[4])) for v in violations_data]