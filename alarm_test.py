import time
import unittest
from unittest.mock import MagicMock

from alarm import *
from config import *

class MockPlayer:
    def __init__(self):
        self.play = MagicMock()
        self.stop = MagicMock()
        return
    pass

class TestAlarm(unittest.TestCase):

    # Tests that alarm is not set on init.
    def test_init(self):
        alarm = Alarm(7, 30, MockPlayer())
        self.assertEqual(alarm.set, False)
        self.assertEqual(alarm.silenced, False)
        pass

    # Test change_up() rolls over the hour.
    def test_change_up(self):
        alarm = Alarm(7, 30, MockPlayer())
        alarm.change_up(15)
        self.assertEqual(alarm.hour, 7)
        self.assertEqual(alarm.minute, 45)
        alarm.change_up(15)
        self.assertEqual(alarm.hour, 8)
        self.assertEqual(alarm.minute, 0)
        pass

    # Test change_up() rolls over the day.
    def test_change_up_day(self):
        alarm = Alarm(23, 45, MockPlayer())
        alarm.change_up(15)
        self.assertEqual(alarm.hour, 0)
        self.assertEqual(alarm.minute, 0)
        pass

    # Test change_down() rolls over the hour.
    def test_change_down(self):
        alarm = Alarm(7, 30, MockPlayer())
        alarm.change_down(15)
        self.assertEqual(alarm.hour, 7)
        self.assertEqual(alarm.minute, 15)
        alarm.change_down(15)
        self.assertEqual(alarm.hour, 7)
        self.assertEqual(alarm.minute, 0)
        alarm.change_down(15)
        self.assertEqual(alarm.hour, 6)
        self.assertEqual(alarm.minute, 45)
        pass

    # Test change_down() rolls over the day.
    def test_change_down_day(self):
        alarm = Alarm(0, 0, MockPlayer())
        alarm.change_down(15)
        self.assertEqual(alarm.hour, 23)
        self.assertEqual(alarm.minute, 45)
        pass

    # Test play sound on right time.
    def test_play(self):
        player = MockPlayer()
        alarm = Alarm(7, 30, player)
        alarm.set_on()
        local_time = time.gmtime(1529134216)
        self.assertEqual(local_time.tm_hour, 7)
        self.assertEqual(local_time.tm_min, 30)
        alarm.check(local_time)
        player.play.assert_called_with(SOUND_FILE)
        pass

    def test_silence(self):
        player = MockPlayer()
        alarm = Alarm(7, 30, player)
        alarm.set_on()
        local_time = time.gmtime(1529134216)
        self.assertEqual(local_time.tm_hour, 7)
        self.assertEqual(local_time.tm_min, 30)

        # Test that silence stops the play.
        alarm.check(local_time)
        player.play.assert_called_with(SOUND_FILE)
        alarm.silence()
        player.stop.assert_called_with()
        self.assertEqual(alarm.silenced, True)

        # Test that silence is reset on next minute.
        local_time = time.gmtime(1529134216 + 60)
        self.assertEqual(local_time.tm_hour, 7)
        self.assertEqual(local_time.tm_min, 31)
        alarm.check(local_time)
        self.assertEqual(alarm.silenced, False)
        pass


if __name__ == '__main__':
    unittest.main()
