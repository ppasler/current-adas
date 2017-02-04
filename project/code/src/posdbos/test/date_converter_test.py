#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from posdbos.util.date_converter import DateConverter


class DateConverterTest(BaseTest):

    def setUp(self):
        self.dc = DateConverter('%d/%m/%Y %H:%M:%S.%f', 1)

    def test_convert(self):
        self.assertEqual(self.dc.convertDate("05/12/2016 13:58:59.407"), 1480942739.407)

        self.dc.setPattern("%Y-%m-%d %H:%M:%S.%f")
        self.assertEqual(self.dc.convertDate("2016-12-05 13:58:59.407"), 1480942739.407)

if __name__ == '__main__':
    unittest.main()