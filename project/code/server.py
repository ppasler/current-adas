#!/usr/bin/python

import BaseHTTPServer
import SocketServer
import errno
import socket
import threading
import json
import xmlrpclib
import time


from emokit.emotiv import Emotiv

emotiv = None

class EpocHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def _add_success(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def _add_error(self):
        self.send_response(501)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_HEAD(self):
        self._add_success()
        
    def do_POST(self):
        """Respond to a POST request, used to stop the server with a ping."""

    def do_GET(self):
        """Respond to a GET request."""
        print self

        global emotiv
        packet = emotiv.dequeue()
        if packet != None:
            print packet

            self._add_success()

            data = packet.sensors
            
            data.pop("Unknown",None)
            data["UNIX_TIME"] = time.time()
            if(self.path == "/header"):
                data = epoc_data.keys()
            self.wfile.write(json.dumps(data))
        else:
            self._add_error()

class EpocServer(object):
    def __init__(self, host="localhost", port=9000):      
        self.server_address = (host, port)
        self.run_server = True
        self.handler_class = EpocHandler
        self.server_class = BaseHTTPServer.HTTPServer

    def stop(self):
        self.run_server = False
        self._stop()

    def _stop(self):
        server = xmlrpclib.Server('http://%s:%s' % self.server_address)
        try:
            server.ping()
        except Exception:
            print "Ignore, 1 ping is enough"
            

    def run(self):
        self.httpd = self.server_class(self.server_address, self.handler_class)
        print time.asctime(), "Server Starts - %s:%s" % self.server_address
        while self.run_server:
            try:
                self.httpd.handle_request()
            except KeyboardInterrupt, SystemExit:
                print "STOP in the name of love"
                self.stop()
                raise
            

        print time.asctime(), "Server Stops - %s:%s" % self.server_address
        self.httpd.server_close();



if __name__ == "__main__":
    emotiv = Emotiv(display_output=False)
    server = EpocServer()
    try:
        threading.Thread(target=server.run).start()
        emotiv.setup()
    except KeyboardInterrupt, SystemExit:
        print "STOP this shit"
        emotiv.close()
        server.stop()
