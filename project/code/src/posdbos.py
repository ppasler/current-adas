'''
Created on 30.05.2016

@author: Paul Pasler
'''
from Queue import Empty
import random
import threading
from time import sleep

from classification.neural_network import NeuralNetwork
from config.config import ConfigProvider
from feature_extractor import FeatureExtractor
from output.drowsiness_monitor import DrowsinessMonitor


class PoSDBoS(object):
    
    def __init__(self, networkFile=None):
        '''Main class for drowsiness detection
        
        :param string networkFile: file name of the saved neural network (path: "/../../data/<networkFile>.nn")
        '''
        self.running = True
        self.config = ConfigProvider()
        self._initNeuralNetwork(networkFile)
        self._initFeatureExtractor()
        self.dm = DrowsinessMonitor()

    def _initNeuralNetwork(self, networkFile):
        nn_conf = self.config.getNeuralNetworkConfig()
        if networkFile == None:
            self.nn = NeuralNetwork().createNew(nn_conf["nInputs"], nn_conf["nHiddenLayers"], nn_conf["nOutput"], nn_conf["bias"])
        else:
            self.nn = NeuralNetwork().load(networkFile)

    def _initFeatureExtractor(self):
        self.fe = FeatureExtractor()
        self.inputQueue = self.fe.outputQueue

    def close(self):
        self.running = False

    def run(self):
        self.fe.start()
        dmt = threading.Thread(target=self.dm.run)
        dmt.start()
        while self.running and dmt.is_alive():
            try:
                data = self.inputQueue.get(timeout=1)
                # TODO activate classification
                #self.nn.activate(data)
                
                n = random.randint(1, 10)
                self.dm.setStatus(n%2)
                sleep(0.1)
            except Empty:
                pass
            except KeyboardInterrupt:
                self.close()
            except Exception as e:
                print e.message
                self.close()
        self.fe.close()
        self.dm.close()
        dmt.join()

if __name__ == '__main__':
    p = PoSDBoS()
    print "START"
    pt = threading.Thread(target=p.run)
    pt.start()
    #sleep(3)
    #p.close()
    pt.join()
    print "END"