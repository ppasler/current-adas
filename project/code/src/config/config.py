import ConfigParser
from os.path import dirname, abspath
from ast import literal_eval

scriptPath = dirname(abspath(__file__))

DEFCONFIG = scriptPath + '/default.cfg'

def getInstance(relative=""):
    global instance
    if instance is None:
        instance = ConfigProvider(relative)
    return instance
instance = None


class ConfigProvider(object):

    def __init__(self, relative=""):
        self.relative = relative
        self.defaultConfig = ConfigParser.SafeConfigParser()
        self.defaultConfig.optionxform = str
        self.defaultConfig.read(DEFCONFIG)

    def getCollectorConfig(self):
        return self.getConfig("collector")

    def getConfig(self, section):
        try:
            d = dict(self.defaultConfig.items(section))
            return {x: literal_eval(d[x]) for x in d}
        except ConfigParser.NoSectionError:
            print "No config found for '%s'" % section
            raise 

if __name__ == "__main__":
    config = ConfigProvider()
    
    print config.getCollectorConfig()