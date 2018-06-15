#!/usr/bin/env python
import time
import threading
import getpass

import RPi.GPIO as GPIO

from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions

from alarm import *
from config import *
from sound import *

logger = logging.getLogger("alarmclock")

SENSOR = 12
UP = 16
DOWN = 20
SOUND = 26 

class AlarmClock(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        # Setup GPIO buttons
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(SOUND, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.font_day = graphics.Font()
        self.font_day.LoadFont(BASE_DIR + "fonts/4x6.bdf")
        self.font_time = graphics.Font()
        self.font_time.LoadFont(BASE_DIR + "fonts/5x8.bdf")
        self.color_day = graphics.Color(255, 179, 0)
        self.color_time = graphics.Color(154, 240, 0)
        self.color_pixel = graphics.Color(0, 149, 67)
        self.alarm = Alarm(7, 30)
        self.font_alarm = graphics.Font()
        self.font_alarm.LoadFont(BASE_DIR + "fonts/7x13.bdf")
        self.color_alarm = graphics.Color(234, 0, 52)
        self.color_alarm_colon = graphics.Color(255, 130, 42)

        self.player = Player()
        self.done = False
        return
        
    def set_pixel(self, x, y, color):
        self.matrix.SetPixel(x, y, color[0],color[1],color[2])
        return

    def shutdown(self):
        logger.info("AlarmClock is shutting down")
        self.done = True
        time.sleep(2)
        pass

    def setup(self):
        logger.info("setting up the matrix: %s", getpass.getuser())
        options = RGBMatrixOptions()
        options.rows = 16
        options.chain_length = 1
        options.brightness = BRIGHTNESS
        self.matrix = RGBMatrix(options = options)
        return
        
    def run(self):
        self.setup()
        logger.info("AlarmClock is running")
        self.color_black = graphics.Color(0,0,0)
        while not self.done:
            # handle sound play
            if GPIO.input(SOUND) == 0:
                self.player.play(SOUND_FILE)
            elif GPIO.input(SOUND) == 1:
                self.player.stop()
                pass

            # handle buttons
            self.matrix.Clear()
            if GPIO.input(SENSOR) == 0:
                if GPIO.input(UP) == 0:
                    self.alarm.change_up()
                    pass
                if GPIO.input(DOWN) == 0:
                    self.alarm.change_down()
                    pass
                alarm_hour = "%2d" % (self.alarm.hour)
                alarm_minute = "%02d" % (self.alarm.minute)
                self.alarm_dot(0, 12, alarm_hour, alarm_minute)
            else:
                local_time = time.localtime()
                local_hour = "%2d" % (local_time.tm_hour)
                local_minute = "%02d" % (local_time.tm_min)
                local_sec = "%02d" % (local_time.tm_sec)
                self.time_dot(0, 15, local_hour, local_minute, local_sec)
                local_day = time.strftime("%a%d%b%y",local_time)
                self.day_text(0, 6, local_day)
                pass
            time.sleep(1)
            pass
        GPIO.cleanup()
        logger.info("GPIO cleanup is done")
        self.player.shutdown()
        return
    
      
    def pixel(self, x, y, color):
        self.matrix.SetPixel(x, y-1, color.red, color.green, color.blue)
        self.matrix.SetPixel(x-1, y-1, color.red, color.green, color.blue)
        self.matrix.SetPixel(x, y-2, color.red, color.green, color.blue)
        self.matrix.SetPixel(x-1, y-2, color.red, color.green, color.blue)
        return 1

    def colon(self, x, y, color):
        self.pixel(x, y, color)
        self.pixel(x, y-4,color)
        return 1

    def alarm_colon(self, x, y, color):
        self.pixel(x, y-1, color)
        self.pixel(x, y-6,color)
        return 1
        
    def time_dot(self, x, y, hour, minute, sec):
        cx = x
        l = graphics.DrawText(self.matrix, self.font_time, cx, y, self.color_time, hour)
        cx = cx + l
        self.colon(cx, y, self.color_pixel) 
        cx = cx + 1
        l = graphics.DrawText(self.matrix, self.font_time, cx, y, self.color_time, minute)
        cx = cx + l
        self.pixel(cx, y, self.color_pixel)
        cx = cx + 1
        l = graphics.DrawText(self.matrix, self.font_time, cx, y, self.color_time, sec)
        return    

    def time_text(self, x, y, text):
        graphics.DrawText(self.matrix, self.font_time, x, y, self.color_time, text)
        return
        
    def day_text(self, x, y, text):
        graphics.DrawText(self.matrix, self.font_day, x, y, self.color_day, text)
        return
    
    def alarm_dot(self, x, y, hour, minute):
       cx = x
       l = graphics.DrawText(self.matrix, self.font_alarm, cx, y, self.color_alarm, hour)
       cx = cx + l
       self.alarm_colon(cx, y, self.color_alarm_colon)
       cx = cx + 1
       #cx = cx + l - 2
       #l = graphics.DrawText(self.matrix, self.font_alarm, cx, y-1, self.color_alarm_pixel, ":")
       #cx = cx + l - 1
       l = graphics.DrawText(self.matrix, self.font_alarm, cx, y, self.color_alarm, minute)
       return


