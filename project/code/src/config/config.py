import ConfigParser
from os.path import dirname, abspath
from ast import literal_eval
import logging

scriptPath = dirname(abspath(__file__))

DEFCONFIG = scriptPath + '/default.cfg'

class ConfigProvider(object):
    '''Loads config file and groups them by section'''

    def __init__(self, relative=""):
        '''Loading default config'''
        self.defaultConfig = ConfigParser.SafeConfigParser()
        self.defaultConfig.optionxform = str
        logging.debug("%s: reading configfile <%s>" % (self.__class__.__name__, DEFCONFIG))
        self.defaultConfig.read(DEFCONFIG)

    def getCollectorConfig(self):
        '''get config for DataCollector '''
        return self.getConfig("collector")
    
    def getProcessingConfig(self):
        '''get config for ProcessingChain '''
        return self.getConfig("processing")
    
    def getEmotivConfig(self):
        '''get config for ProcessingChain '''
        return self.getConfig("emotiv")

    def getNNInitConfig(self):
        '''get config for Neural Network Initialization '''
        return self.getConfig("nnInit")

    def getNNTrainConfig(self):
        '''get config for Neural Network Training '''
        return self.getConfig("nnTrain")

    def getExperimentConfig(self):
        '''get config for experimental data '''
        return self.getConfig("experiment")

    def getClassConfig(self):
        '''get config for classes'''
        return self.getConfig("class")

    def getPoSDBoSConfig(self):
        '''get config for PoSDBoS'''
        return self.getConfig("posdbos")

    def getConfig(self, section):
        '''get config for section '''
        try:
            d = dict(self.defaultConfig.items(section))
            return {x: literal_eval(d[x]) for x in d}
        except ConfigParser.NoSectionError:
            logging.warn("No config found for '%s'" % section)
            raise 