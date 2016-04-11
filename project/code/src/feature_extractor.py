from emokit.emotiv import Emotiv
from data_collector import DataCollector
from config.config import ConfigProvider
from time import sleep


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
        
        self.extract = True
        
    def main(self):
        print "start"
        # TODO blocking
        self.collector.collectData()
        print "gole"
        sleep(2)
        self.collector.close()
        print "close"    
        
if __name__ == "__main__":
    extractor = FeatureExtractor()
    extractor.main()