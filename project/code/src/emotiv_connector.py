import os
import time

import emokit
from emokit.emotiv import Emotiv

from util.eeg_data_source import EEGTablePacketSource


scriptPath = os.path.dirname(os.path.abspath(__file__))

emokit.emotiv.DEVICE_POLL_INTERVAL = 0.001

class EmotivConnector(object):

    def __init__(self, display_output=False, write=True, verbose=False, output_path="."):
        self._initEmotiv(display_output, write, verbose, output_path)

    def _initEmotiv(self, display_output, write, verbose, output_path):
        self.emotiv = Emotiv(display_output=display_output, write=write, verbose=verbose, output_path=output_path)
        if not self._isEmotivConnected():
            self.close()
            self._loadDummyData()

    def _isEmotivConnected(self):
        return self.emotiv.running

    def _loadDummyData(self):
        filePath = scriptPath + "/../../captured_data/janis/parts/2016-07-12-11-15_EEG_4096.csv"
        self.emotiv = EEGTablePacketSource(filePath)
        self.emotiv.convert()

    def dequeue(self):
        return self.emotiv.dequeue()

    def stop(self):
        try:
            self.emotiv.stop()
        except Exception as e:
            print "Error while shutting down", e

    def close(self):
        self.stop()

if __name__ == "__main__":
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    output_path = scriptPath + "/../data/"

    headset = EmotivConnector(display_output=False, write=True, verbose=True, output_path=output_path)
    print("Serial Number: %s" % headset.emotiv.serial_number)

    while headset.emotiv.running:
        try:
            packet = headset.dequeue()
        except Exception:
            headset.stop()
        time.sleep(0.0001)
    headset.stop()
