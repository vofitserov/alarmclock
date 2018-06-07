
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

logger = logging.getLogger("alarmclock")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler = logging.handlers.RotatingFileHandler(
                  LOGFILE, maxBytes=100000, backupCount=5)

handler.setFormatter(formatter)
logger.addHandler(handler)

