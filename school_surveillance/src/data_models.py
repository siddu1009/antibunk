from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class Student:
    id: str
    name: str
    image_path: str
    parent_email: str = ""

@dataclass
class Schedule:
    student_id: str
    period: int
    classroom_id: str

@dataclass
class Zone:
    id: str
    name: str
    allowed_periods: List[int]

@dataclass
class Violation:
    student_id: str
    zone_id: str
    timestamp: datetime
    grace_period_expired: bool = False
    alert_sent: bool = False