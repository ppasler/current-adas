'''
Created on 30.05.2016

@author: Paul Pasler
'''
from classification.neural_network import NeuralNetwork
from config.config import ConfigProvider
from feature_extractor import FeatureExtractor

class PoSDBoS(object):
    
    def __init__(self, networkFile=None):
        '''Main class for drowsiness detection
        
        :param string networkFile: file name of the saved neural network (path: "/../../data/<networkFile>.nn")
        '''
        self.running = True
        self.config = ConfigProvider()
        self._initNeuralNetwork(networkFile)
        self._initFeatureExtractor()
        
    def _initNeuralNetwork(self, networkFile):
        nn_conf = self.config.getNeuralNetworkConfig()
        if networkFile == None:
            self.nn = NeuralNetwork().createNew(nn_conf["nInputs"], nn_conf["nHiddenLayers"], nn_conf["nOutput"], nn_conf["bias"])
        else:
            self.nn = NeuralNetwork().load(networkFile)

    def _initFeatureExtractor(self):
        self.fe = FeatureExtractor()

    def close(self):
        self.running = False

    def run(self):
        while self.running:
            pass
        self.fe.close()

if __name__ == '__main__':
    pass