from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from .data_models import Student, Schedule, Zone, Violation
from .database import save_violation

class RuleEngine:
    def __init__(self, students: List[Student], schedules: List[Schedule], zones: List[Zone], grace_period_minutes: int = 2):
        self.students = {s.id: s for s in students}
        self.schedules = schedules
        self.zones = {z.id: z for z in zones}
        self.active_violations: Dict[str, Violation] = {}
        self.grace_period = timedelta(minutes=grace_period_minutes)
        self.last_seen_location: Dict[str, Tuple[str, datetime]] = {}
        self.bunking_score: Dict[str, int] = {s.id: 0 for s in students}

    def get_current_period(self):
        now = datetime.now()
        if 8 <= now.hour < 9:
            return 1
        elif 9 <= now.hour < 10:
            return 2
        elif 10 <= now.hour < 11:
            return 3
        elif 11 <= now.hour < 12:
            return 4
        elif 13 <= now.hour < 14:
            return 5
        elif 14 <= now.hour < 15:
            return 6
        elif 15 <= now.hour < 16:
            return 7
        else:
            return None

    def is_student_allowed_in_zone(self, student_id: str, zone_id: str) -> bool:
        current_period = self.get_current_period()
        if not current_period:
            return True  # Outside of school hours

        student_schedule = [s for s in self.schedules if s.student_id == student_id and s.period == current_period]
        if not student_schedule:
            return True

        classroom_id = student_schedule[0].classroom_id

        if zone_id == classroom_id:
            if student_id in self.active_violations:
                print(f"[✅] Student {student_id} returned to classroom. Violation revoked.")
                del self.active_violations[student_id]
            return True

        zone = self.zones.get(zone_id)
        if zone and current_period in zone.allowed_periods:
            return True

        return False

    def process_violation(self, student_id: str, current_zone_id: str):
        self.last_seen_location[student_id] = (current_zone_id, datetime.now())

        if self.is_student_allowed_in_zone(student_id, current_zone_id):
            return

        if student_id not in self.active_violations:
            self.active_violations[student_id] = Violation(student_id, current_zone_id, datetime.now())
            print(f"[⏰] Rule Triggered: {datetime.now().strftime('%I:%M %p')} Attendance Window")
            print(f"[👁] Student {student_id} detected outside permitted zone ({current_zone_id}). Grace period started.")
        else:
            violation = self.active_violations[student_id]
            if not violation.grace_period_expired and datetime.now() - violation.timestamp > self.grace_period:
                violation.grace_period_expired = True
                print(f"[⚖️] Student {student_id} has not returned within the grace period. Violation confirmed.")
                self.bunking_score[student_id] += 1
                save_violation(violation) # Save to database
            
            if violation.grace_period_expired and not violation.alert_sent:
                print(f"[🔔] NOTIFICATION: Student {student_id} marked absent. Bunking Score: {self.bunking_score[student_id]}")
                violation.alert_sent = True