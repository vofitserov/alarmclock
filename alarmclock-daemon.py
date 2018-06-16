#!/usr/bin/env python

import signal
import sys
import logging
import getpass

from daemon import runner

from config import *
from httpserver import *
from alarmclock import *

# Named global logger from config
logger = logging.getLogger("alarmclock")

class AlarmClockDaemon:
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/var/log/alarmclock-daemon.out'
        self.stderr_path = '/var/log/alarmclock-daemon.err'
        self.pidfile_path = PIDFILE
        self.pidfile_timeout = 10
        return
    
    def run(self):
        # signal handler can be set only in main thread
        signal.signal(signal.SIGTERM, self.shutdown)    
        signal.signal(signal.SIGINT, self.shutdown)    

        logging.info("running as user %s", getpass.getuser())
        
        self.alarm_clock = AlarmClock()
        
        self.httpserver = HTTPAlarmClockController(self.alarm_clock)
        self.httpserver.setDaemon(True)
        self.httpserver.start()

        self.alarm_clock.setDaemon(True)
        self.alarm_clock.start()

        # join() with is_alive() is only way catch signals
        while self.httpserver.is_alive():
            self.httpserver.join(2**31)
            pass
            
        logger.critical("staring door shutdown, gpio cleanup")
        self.alarm_clock.shutdown()
        return

    def shutdown(self, signum, frame):
        logger.critical("starting shutdown by %d" % signum)
        self.httpserver.shutdown()
        logger.critical("finished shutdown by %d" % signum)
        return
    
try:
    alarmclock_daemon = AlarmClockDaemon()
    if sys.argv[1] == "test":
        stderrHandler = logging.StreamHandler(sys.stderr)
        stderrHandler.setFormatter(formatter)
        logger.addHandler(stderrHandler)
        logger.info("running in test mode, logging to stderr")
        alarmclock_daemon.run()
    else:
        daemonHandler = logging.handlers.RotatingFileHandler(
            LOGFILE, maxBytes=100000, backupCount=5)
        daemonHandler.setFormatter(formatter)
        logger.addHandler(daemonHandler)
        daemon_runner = runner.DaemonRunner(alarmclock_daemon)
        daemon_runner.daemon_context.files_preserve = [daemonHandler.stream]
        daemon_runner.do_action()
        pass
    
except Exception as e:
    logger.error("failed: \"%s\"" % str(e))
    pass

