#!/usr/bin/env python

import time

class Alarm:
    WAIT = 1
    NOISE = 2
    SILENCE = 3
    
    def __init__(self, hour, minute):
        self.hour = hour
        self.minute = minute
        self.state = Alarm.WAIT
        return

    def see_noise(self, local_time):
        if self.state == WAIT:
            if local_time.tm_hour == self.hour and local_time.tm_min == self.minute:
                self.start_noise()
                self.state = Alarm.NOISE
                pass
        elif self.state == NOISE:
            if local_time.tm_hour != self.hour or local_time.tm_min != self.minute:
                self.stop_noise()
                self.state = Alarm.WAIT
                pass
        elif self.state == SILENCE:
            if local_time.tm_hour != self.hour or local_time.tm_min != self.minute:
                self.state = Alarm.WAIT
                pass
        else:
            print "Unexpected state=", self.state

        return

    def silence(self):
        self.stop_noise()
        self.state = Alarm.SILENCE
        return

    def start_noise(self):

        return

    def stop_noise(self):

        return

    def change_up(self, m = 15):
        self.minute = self.minute + m
        if self.minute >= 60:
            self.hour = self.hour + 1
            self.minute = 0
            pass
        if self.hour == 24:
            self.hour = 0
            pass
        return
    
    def change_down(self, m = 15):
        self.minute = self.minute - m
        if self.minute < 0:
            self.hour = self.hour - 1
            self.minute = 60 - m
            pass
        if self.hour < 0:
            self.hour = 23
        return
