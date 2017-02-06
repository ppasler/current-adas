#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport
from time import sleep
import threading
from posdbos.test.test_factory import TestFactory


class AppTest(BaseTest):

    def setUp(self):
        self.app = TestFactory.getForTesting()

    # TODO sths wrong here
    def test_run(self):
        pt = threading.Thread(target=self.app.run)
        pt.start()
        sleep(2)
        self.app.close()
        pt.join()


if __name__ == '__main__':
    unittest.main()