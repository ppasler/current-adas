'''
Created on 13.06.2016

@author: Paul Pasler
'''
import os
import sys
from time import strftime, localtime

from default_chain import ProcessingChain
from util.eeg_table_to_packet_converter import EEGTableToPacketUtil
from util.eeg_table_util import EEGTableFileUtil


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

PATH = os.path.dirname(os.path.abspath(__file__)) +  "/../../data/"


class Chain(object):

    def __init__(self): 
        self.chain = ProcessingChain()
        self.readData()
    
    def readData(self):
        self.data = EEGTableToPacketUtil()._buildFullDataStructure()
    
    def main(self, filePath):
        eeg, gyro = self.chain.process(self.data)
        eeg.update(gyro)
        
        EEGTableFileUtil().writeStructredFile(filePath, eeg)
    
if __name__ == "__main__":
    time = strftime("%y-%M-%d_%H-%M", localtime())
    filePath = PATH + "chain_" + time + ".csv"

    c = Chain()
    c.main(filePath)
    