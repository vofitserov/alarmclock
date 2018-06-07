
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

import urlparse
import threading
import getpass

from config import *

# Named global logger from config
logger = logging.getLogger("alarmclock")

html = """
<!DOCTYPE html>
<html>
<body>

<h1>%s</h1>

<form action="/">
  <input type="submit" name="action" value="Open">
  <input type="submit" name="action" value="Close">
  <input type="submit" name="action" value="Refresh">
</form>

<br>
<br>

</body>
</html>
"""

class HTTPAlarmClockHandler(BaseHTTPRequestHandler):
    def respond(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html % (message))
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
        return self.respond("Alarm Clock is " + action)

class HTTPAlarmClockServer(HTTPServer):
    def __init__(self, alarm_clock, address, handler_class):
        HTTPServer.__init__(self, address, handler_class)
        self.alarm_clock = alarm_clock
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
