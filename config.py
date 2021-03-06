
import logging
import logging.handlers

# daemon log and lock
LOGFILE = "/var/log/alarmclock-daemon.log"
PIDFILE = "/var/run/alarmclock-daemon.pid"

# http host and port to start http server
HTTP_HOST = "" # "clockpi.local"
HTTP_PORT = 80

BRIGHTNESS = 50

BASE_DIR = "/home/pi/alarmclock/"

SOUND_DEVICE = "default"
SOUND_FILE = BASE_DIR + "sounds/Xylo1.wav"
SOUND_VOLUME = 80

logger = logging.getLogger("alarmclock")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

