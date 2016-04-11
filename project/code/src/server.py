#!/usr/bin/python

import BaseHTTPServer
import threading
import json
import xmlrpclib
import time


from emokit.emotiv import Emotiv

emotiv = None

class EpocHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''This Handles a request'''

    def _add_success(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def _add_error(self):
        self.send_response(500)
        self.send_header("Content-type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_HEAD(self):
        self._add_success()
        
    def do_POST(self):
        """Respond to a POST request, used to stop the server with a ping."""

    def _buildDataMap(self, packet):
        data = packet.sensors
        if "Unknown" in data:
            data.pop("Unknown",None)
        data["UNIX_TIME"] = time.time()
        return data
        

    def do_GET(self):
        """Respond to a GET request."""

        global emotiv
        packet = emotiv.dequeue()
        if packet != None:
            self._add_success()

            data = self._buildDataMap(packet)
            if(self.path == "/header"):
                self.wfile.write(json.dumps(data.keys()))
            else:
                self.wfile.write(json.dumps(data))
        else:
            self._add_error()
            self.wfile.write("No data found")


class EpocServer(object):
    '''
    Serve EPOC data on localhost:9000 by default
    /           returns a map of EPOC vales
    /header     returns a list of all data keys
    '''
    
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
            """Ignore, 1 ping is enough"""
            

    def run(self):
        '''Serve EPOC data until forever'''
        self.httpd = self.server_class(self.server_address, self.handler_class)
        print time.asctime(), "Server Starts - %s:%s" % self.server_address
        while self.run_server:
            try:
                self.httpd.handle_request()
            except (KeyboardInterrupt, SystemExit):
                self.stop()
                raise
            
        print time.asctime(), "Server Stops - %s:%s" % self.server_address
        self.httpd.server_close();



if __name__ == "__main__":
    emotiv = Emotiv(display_output=False)
    server = EpocServer()
    try:
        print "starting server and emotiv"
        t = threading.Thread(target=server.run)
        t.start()
        
        emotiv.setup()
        
        print "closing server and emotiv"
        emotiv.close()
        server.stop()
    except (KeyboardInterrupt, SystemExit) as e:
        print e.getMessage()
        emotiv.close()
        server.stop()
    finally:
        print "exit now..."
        t.join()
        print "...really"
