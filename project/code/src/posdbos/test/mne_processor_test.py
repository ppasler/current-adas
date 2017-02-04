#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from Queue import Queue

from posdbos.processor.mne_processor import MNEProcessor
from posdbos.util.mne_util import MNEUtil
from mne.viz.utils import plt_show
from posdbos.test.posdbos_test_factory import TestFactory

@unittest.skip("work in progress")
class TestMNEProcessor(BaseTest):

    def setUp(self):
        self.queue = Queue()
        self.collector = TestFactory.createDemoDataCollector(self.getData1024CSV(), self.queue)
        self.collector.collectData()
        self.processor = MNEProcessor()

    def test_all(self):
        window = self.queue.get()
        preProc, _ = self.processor.process(window)

    #def test_preProc(self):
    #    window = self.queue.get()
    #    preProc = self.processor.preProcessor.process(window)

if __name__ == "__main__":
    unittest.main()