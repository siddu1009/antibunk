
import unittest
from unittest.mock import patch
from datetime import datetime

# Adjust the import path to match the project structure
# We are in tests, so we need to go up one level to school_surveillance and then into src
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_models import Student, Schedule, Zone
from src.rule_engine import RuleEngine

class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        """Set up mock data for tests."""
        self.students = [
            Student(id="101", name="John Doe", image_path="..."),
            Student(id="102", name="Jane Smith", image_path="...")
        ]
        self.schedules = [
            Schedule(student_id="101", period=1, classroom_id="CLASS-A"),
            Schedule(student_id="102", period=1, classroom_id="CLASS-B")
        ]
        self.zones = [
            Zone(id="CLASS-A", name="Classroom A", allowed_periods=[]),
            Zone(id="CLASS-B", name="Classroom B", allowed_periods=[]),
            Zone(id="HALLWAY-1", name="Main Hallway", allowed_periods=[1, 2, 3, 4, 5, 6, 7]),
            Zone(id="LIBRARY", name="Library", allowed_periods=[3, 4]),
            Zone(id="RESTRICTED-AREA", name="Staff Room", allowed_periods=[])
        ]
        self.rule_engine = RuleEngine(self.students, self.schedules, self.zones)

    @patch('src.rule_engine.RuleEngine.get_current_period')
    def test_student_allowed_in_correct_classroom(self, mock_get_current_period):
        """Test that a student is allowed in their scheduled classroom."""
        mock_get_current_period.return_value = 1  # Mocking current period to be 1
        
        student_id = "101"
        zone_id = "CLASS-A"
        
        is_allowed = self.rule_engine.is_student_allowed_in_zone(student_id, zone_id)
        self.assertTrue(is_allowed, f"Student {student_id} should be allowed in {zone_id} during period 1.")

    @patch('src.rule_engine.RuleEngine.get_current_period')
    def test_student_not_allowed_in_wrong_classroom(self, mock_get_current_period):
        """Test that a student is not allowed in a classroom that is not their scheduled one."""
        mock_get_current_period.return_value = 1
        
        student_id = "101"
        zone_id = "CLASS-B"
        
        is_allowed = self.rule_engine.is_student_allowed_in_zone(student_id, zone_id)
        self.assertFalse(is_allowed, f"Student {student_id} should not be allowed in {zone_id} during period 1.")

    @patch('src.rule_engine.RuleEngine.get_current_period')
    def test_student_allowed_in_common_area(self, mock_get_current_period):
        """Test that a student is allowed in a common area like a hallway."""
        mock_get_current_period.return_value = 1
        
        student_id = "101"
        zone_id = "HALLWAY-1"
        
        is_allowed = self.rule_engine.is_student_allowed_in_zone(student_id, zone_id)
        self.assertTrue(is_allowed, f"Student {student_id} should be allowed in {zone_id} during period 1.")

    @patch('src.rule_engine.RuleEngine.get_current_period')
    def test_student_not_allowed_in_restricted_zone(self, mock_get_current_period):
        """Test that a student is not allowed in a zone with no allowed periods."""
        mock_get_current_period.return_value = 1
        
        student_id = "101"
        zone_id = "RESTRICTED-AREA"
        
        is_allowed = self.rule_engine.is_student_allowed_in_zone(student_id, zone_id)
        self.assertFalse(is_allowed, f"Student {student_id} should not be allowed in {zone_id} at any time.")

    @patch('src.rule_engine.RuleEngine.get_current_period')
    def test_student_allowed_outside_school_hours(self, mock_get_current_period):
        """Test that rules are not applied outside of school hours."""
        mock_get_current_period.return_value = None  # Mocking time to be outside school hours
        
        student_id = "101"
        zone_id = "RESTRICTED-AREA" # Even a restricted area
        
        is_allowed = self.rule_engine.is_student_allowed_in_zone(student_id, zone_id)
        self.assertTrue(is_allowed, "All students should be allowed in any zone outside of school hours.")

if __name__ == '__main__':
    unittest.main()
