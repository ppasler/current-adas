#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from posdbos_factory import PoSDBoSFactory


class TestPoSDBoS(BaseTest):

    def setUp(self):
        self.posdbos = PoSDBoSFactory.getForTesting()

    def test_run(self):
        self.posdbos.run()


if __name__ == '__main__':
    unittest.main()