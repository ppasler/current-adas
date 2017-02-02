#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport
from posdbos_test_factory import TestFactory


class AppTest(BaseTest):

    def setUp(self):
        self.app = TestFactory.getForTesting()

    def test_run(self):
        self.app.run()


if __name__ == '__main__':
    unittest.main()