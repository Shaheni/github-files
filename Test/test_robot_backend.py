"""
Test suite for robot backend integration with Arduino.

Tests validate:
- Packet generation
- Servo validation
- API contracts
- Motion execution flow
- Serial communication (when Arduino is connected)
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import unittest
from services.command_mapper import (
    validate_servo_values,
    build_packet,
    process_robot_command
)
from services.motion_engine import (
    get_motion_status,
    ExecutionState
)

# ==========================================
# TEST SERVO VALIDATION
# ==========================================

class TestServoValidation(unittest.TestCase):
    """Tests for servo value validation."""
    
    def test_valid_servo_values(self):
        """Test valid servo values pass validation."""
        data = {
            "servo1": 90,
            "servo2": 90,
            "servo3": 90,
            "servo4": 90,
            "servo5": 90,
            "servo6": 90
        }
        valid, result = validate_servo_values(data)
        self.assertTrue(valid)
        self.assertEqual(result, [90, 90, 90, 90, 90, 90])
    
    def test_servo_min_values(self):
        """Test servo minimum values are accepted."""
        data = {
            "servo1": 0,
            "servo2": 10,
            "servo3": 10,
            "servo4": 0,
            "servo5": 0,
            "servo6": 0
        }
        valid, result = validate_servo_values(data)
        self.assertTrue(valid)
        self.assertEqual(result, [0, 10, 10, 0, 0, 0])
    
    def test_servo_max_values(self):
        """Test servo maximum values are accepted."""
        data = {
            "servo1": 180,
            "servo2": 170,
            "servo3": 170,
            "servo4": 180,
            "servo5": 180,
            "servo6": 180
        }
        valid, result = validate_servo_values(data)
        self.assertTrue(valid)
        self.assertEqual(result, [180, 170, 170, 180, 180, 180])
    
    def test_servo_out_of_bounds_low(self):
        """Test servo value below minimum is rejected."""
        data = {
            "servo1": -1,
            "servo2": 90,
            "servo3": 90,
            "servo4": 90,
            "servo5": 90,
            "servo6": 90
        }
        valid, result = validate_servo_values(data)
        self.assertFalse(valid)
        self.assertIn("out of bounds", result)
    
    def test_servo_out_of_bounds_high(self):
        """Test servo value above maximum is rejected."""
        data = {
            "servo1": 90,
            "servo2": 171,  # servo2 max is 170
            "servo3": 90,
            "servo4": 90,
            "servo5": 90,
            "servo6": 90
        }
        valid, result = validate_servo_values(data)
        self.assertFalse(valid)
        self.assertIn("out of bounds", result)
    
    def test_missing_servo_value(self):
        """Test missing servo value is rejected."""
        data = {
            "servo1": 90,
            "servo2": 90,
            # Missing servo3-servo6
        }
        valid, result = validate_servo_values(data)
        self.assertFalse(valid)
        self.assertIn("Missing", result)
    
    def test_non_integer_servo_value(self):
        """Test non-integer servo value is rejected."""
        data = {
            "servo1": "ninety",
            "servo2": 90,
            "servo3": 90,
            "servo4": 90,
            "servo5": 90,
            "servo6": 90
        }
        valid, result = validate_servo_values(data)
        self.assertFalse(valid)
        self.assertIn("must be an integer", result)

# ==========================================
# TEST PACKET BUILDING
# ==========================================

class TestPacketBuilding(unittest.TestCase):
    """Tests for Arduino packet generation."""
    
    def test_packet_format(self):
        """Test packet is in correct format."""
        angles = [90, 90, 90, 90, 90, 90]
        packet = build_packet(angles)
        self.assertEqual(packet, "90,90,90,90,90,90\n")
    
    def test_packet_with_different_values(self):
        """Test packet generation with varied angles."""
        angles = [0, 10, 45, 90, 170, 180]
        packet = build_packet(angles)
        self.assertEqual(packet, "0,10,45,90,170,180\n")
    
    def test_packet_ends_with_newline(self):
        """Test packet always ends with newline."""
        angles = [90, 90, 90, 90, 90, 90]
        packet = build_packet(angles)
        self.assertTrue(packet.endswith("\n"))
    
    def test_packet_wrong_length_raises_error(self):
        """Test packet with wrong number of angles raises error."""
        angles = [90, 90, 90]  # Only 3 angles
        with self.assertRaises(ValueError):
            build_packet(angles)

# ==========================================
# TEST COMMAND MAPPING
# ==========================================

class TestCommandMapping(unittest.TestCase):
    """Tests for command mapping logic."""
    
    def test_valid_command_processing(self):
        """Test valid command is processed successfully."""
        data = {
            "servo1": 90,
            "servo2": 90,
            "servo3": 90,
            "servo4": 90,
            "servo5": 90,
            "servo6": 90
        }
        result = process_robot_command(data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['packet'], "90,90,90,90,90,90\n")
        self.assertEqual(result['angles'], [90, 90, 90, 90, 90, 90])
        self.assertIsNone(result['error'])
    
    def test_invalid_command_processing(self):
        """Test invalid command returns error."""
        data = {
            "servo1": 200,  # Out of bounds
            "servo2": 90,
            "servo3": 90,
            "servo4": 90,
            "servo5": 90,
            "servo6": 90
        }
        result = process_robot_command(data)
        
        self.assertFalse(result['success'])
        self.assertIsNone(result['packet'])
        self.assertIsNotNone(result['error'])
        self.assertIn("out of bounds", result['error'])

# ==========================================
# TEST MOTION ENGINE STATE
# ==========================================

class TestMotionEngineState(unittest.TestCase):
    """Tests for motion engine state management."""
    
    def test_motion_status_on_idle(self):
        """Test motion status reflects idle state."""
        status = get_motion_status()
        
        self.assertEqual(status['state'], ExecutionState.IDLE)
        self.assertEqual(status['queue_size'], 0)
        self.assertIsNone(status['last_command'])

# ==========================================
# RUN TESTS
# ==========================================

if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
