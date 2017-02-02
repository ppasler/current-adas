#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.02.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

import sys, os
import threading
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from posdbos.source.emotiv_connector import EmotivConnector
from posdbos.network.http_data_provider import HttpEEGDataProvider
from posdbos.source.dummy_data_source import DummyDataSource

scriptPath = os.path.dirname(os.path.abspath(__file__))

def test():
    source = DummyDataSource()
    server = HttpEEGDataProvider(source = source)
    try:
        print "starting server and emotiv"
        t = threading.Thread(target=server.run)
        t.start()

        time.sleep(1)

        print "closing server and emotiv"
        server.stop()
    except (KeyboardInterrupt, SystemExit) as e:
        print e.getMessage()
        server.stop()
    finally:
        print "exit now..."
        t.join()
        print "...really"

def run():
    output_path = scriptPath + "/../../data/"
    emotiv = EmotivConnector(display_output=False, output_path=output_path)
    server = HttpEEGDataProvider()
    try:
        print "starting server and emotiv"
        t = threading.Thread(target=server.run)
        t.start()
    
        time.sleep(1)
    
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


if __name__ == "__main__":
    test()