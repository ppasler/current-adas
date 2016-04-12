from data_collector import DataCollector
from config.config import ConfigProvider
from time import sleep
import threading
from util.signal_util import SignalUtil

from numpy import array


class ProcessingChain(object):
    
    def __init__(self):
        self.eegFields = ConfigProvider().getEmotivConfig()["eegFields"]
        self.gyroFields = ConfigProvider().getEmotivConfig()["gyroFields"]

        self.processingConfig = ConfigProvider().getProcessingConfig()
        self.signalUtil = SignalUtil()
    
    def splitData(self, data):
        '''split eeg and gyro data
        
        @param data: all values as dict
        
        @return: 
            eegData: eeg values as dict
            gyroData: gyro values as dict
        '''
        #TODO handle data except eeg and gyro?
        eegData = {x: data[x] for x in data if x in self.eegFields}
        gyroData = {x: data[x] for x in data if x in self.gyroFields}
        return eegData, gyroData
            
    def process(self, data):
        #TODO make me fast and nice
        eegData, gyroData = self.splitData(data)
        self.processEEGData(eegData)
        self.processGyroData(gyroData)
    
    def normalizeEEGSignals(self, eegData):
        return {x: self.signalUtil.normalize(array(eegData[x]["value"])) for x in eegData}
            
    def processEEGData(self, eegData):
        normalizedSignals = self.normalizeEEGSignals(eegData)
        print eegData
        print normalizedSignals
         
    def processGyroData(self, gyroData):
        pass#print gyroData

class FeatureExtractor(object):
    '''
    Controls the processing chain and fetches the values needed for the classificator
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.collectorConfig = ConfigProvider().getCollectorConfig()      
        self.collector = DataCollector(None, **self.collectorConfig)
        self.collectorThread = threading.Thread(target=self.collector.collectData)
        
        self.processor = ProcessingChain()
        
        self.extract = True
        
        
    def start(self):
        '''setting data handler and starts collecting'''
        print("%s: starting feature extractor" % self.__class__.__name__)   
        self.collector.setHandler(self.handleDataSet)  
        self.collectorThread.start()
    
    def handleDataSet(self, data):
        '''Handles the given data and starts the processing chain'''
        self.processor.process(data)
    
    def close(self):
        self.collector.close()
        self.collectorThread.join()
        print("%s: closing feature extractor" % self.__class__.__name__)     

        
if __name__ == "__main__":  # pragma: no cover
    extractor = FeatureExtractor()
    extractor.start()
    
    sleep(2)
    
    extractor.close()
