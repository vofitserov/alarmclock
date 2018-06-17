
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

import urlparse
import threading
import getpass

from config import *
from sound import *

# Named global logger from config
logger = logging.getLogger("alarmclock")

html = """
<!DOCTYPE html>
<html>
<body>
<h1>%s</h1>
%s
<br>
<form action="/">
  <input type="submit" name="action" value="Play">
  <input type="submit" name="action" value="Set">
  <input type="submit" name="action" value="Off">
</form>

<br>
<br>

</body>
</html>
"""

class HTTPAlarmClockHandler(BaseHTTPRequestHandler):

    def config(self):
        html = ""
        module = globals()
        html += "<table border=0>\n"
        for (key, value) in module.iteritems():
            if key.startswith('html') or key.startswith('_'): continue
            if not isinstance(value, str) and not isinstance(value, int): continue
            html += "<tr><td>%s</td><td>%s</td></tr>\n" % (key, str(value))
            pass
        html += "</table>\n"
        return html

    def respond(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html % (message, self.config()))
        self.wfile.close()
        return

    def log_message(self, format, *args):
        return logger.info(self.address_string() + " - " + (format % args))
    
    def do_GET(self):
        # Instance of global GarageDoor object is on server.
        parsed = urlparse.urlparse(self.path)
        if parsed.path != '/':
            self.send_response(404)
            self.end_headers()
            return
        params = urlparse.parse_qs(parsed.query)
        action = params["action"][0].lower() if "action" in params else "ok"
        # Get alarm object from the server.
        alarm = self.server.alarm_clock.alarm
        if action == "set":
            alarm.set_on()
        elif action == "off":
            alarm.set_off()
        elif action == "play":
            self.server.player.play(SOUND_FILE)
            pass
        if alarm.set:
            status = "Alarm clock is SET for %d:%d" % \
                     (alarm.hour, alarm.minute)
        else:
            status = "Alarm clock is OFF."
        return self.respond(status)

class HTTPAlarmClockServer(HTTPServer):
    def __init__(self, alarm_clock, address, handler_class):
        HTTPServer.__init__(self, address, handler_class)
        self.alarm_clock = alarm_clock
        self.player = Player()
        return

class HTTPAlarmClockController(threading.Thread):
    def __init__(self, alarm_clock):
        threading.Thread.__init__(self)
        logger.info("created http door controller: %s" % getpass.getuser())
        self.alarm_clock = alarm_clock
        logger.info("starting HTTP server: %s:%d" % (HTTP_HOST, HTTP_PORT))
        self.httpserver = HTTPAlarmClockServer(self.alarm_clock,
                                               (HTTP_HOST, HTTP_PORT), HTTPAlarmClockHandler)
        return
    
    def run(self):
        logger.info("starting serve forever...")
        self.httpserver.serve_forever()
        logger.info("...done serve forever")
        return

    def shutdown(self):
        self.httpserver.shutdown()
        return
