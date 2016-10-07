import os
import gevent


from emokit.emotiv import Emotiv
from util.eeg_data_source import EEGTablePacketSource

scriptPath = os.path.dirname(os.path.abspath(__file__))

import emokit
emokit.emotiv.DEVICE_POLL_INTERVAL = 0.001

class EmotivConnector(object):

    def __init__(self, display_output=False, write_to_file=True):
        self._initEmotiv(display_output, write_to_file)

    def _initEmotiv(self, display_output, write_to_file):
        self.emotiv = Emotiv(display_output, write_to_file)
        gevent.spawn(self.emotiv.setup)
        gevent.sleep(0)
        if not self._isEmotivConnected():
            self.emotiv.close()
            self._loadDummyData()

    def _isEmotivConnected(self):
        return self.emotiv.serial_number

    def _loadDummyData(self):
        filePath = scriptPath + "/../../captured_data/janis/parts/2016-07-12-11-15_EEG_4096.csv"
        self.emotiv = EEGTablePacketSource(filePath)
        self.emotiv.convert()

    def dequeue(self):
        return self.emotiv.dequeue()

    def close(self):
        self.emotiv.close()

if __name__ == "__main__":
    a = EmotivConnector(display_output=True, write_to_file=False)
    try:
        print "packet", a.dequeue()
    except KeyboardInterrupt:
        a.close()
    a.close()
