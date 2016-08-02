#!/usr/bin/python

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import ConfigParser
import unittest

from config.config import ConfigProvider


class ConfigTest(unittest.TestCase):

    def setUp(self):
        self.config = ConfigProvider()

    def test_getConfig(self):
        cfg = self.config.getConfig("test")
        
        self.assertEqual(type(cfg["int"]), int)
        self.assertEqual(type(cfg["float"]), float)
        self.assertEqual(type(cfg["bool"]), bool)
        self.assertEqual(type(cfg["str"]), str)
        self.assertEqual(type(cfg["list"]), list)
        self.assertEqual(type(cfg["dict"]), dict)

    def test_getUnknownConfig(self):
        with self.assertRaises(ConfigParser.NoSectionError):
            self.config.getConfig("unknown")

    def test_getInvalidConfig(self):
        with self.assertRaises(ValueError):
            self.config.getConfig("fail")
        
if __name__ == '__main__':
    unittest.main()