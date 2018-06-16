#!/usr/bin/env python

import time

from config import *

class Alarm:
    def __init__(self, hour, minute, player):
        self.hour = hour
        self.minute = minute
        self.silenced = False
        self.set = False
        self.player = player
        return

    def check(self, local_time):
        if local_time.tm_hour == self.hour \
                and local_time.tm_min == self.minute:
            if self.set and not self.silenced:
                self.player.play(SOUND_FILE)
                pass
        else:
            self.silenced = False
            pass

        return

    def set_on(self):
        self.set = True
        return

    def set_off(self):
        self.set = False
        return

    def silence(self):
        self.player.stop()
        self.silenced = True
        return

    def change_up(self, m = 15):
        self.set = True
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
        self.set = True
        self.minute = self.minute - m
        if self.minute < 0:
            self.hour = self.hour - 1
            self.minute = 60 - m
            pass
        if self.hour < 0:
            self.hour = 23
        return
