#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from posdbos.collector.window_dto import WindowDto
from numpy.testing.utils import assert_array_equal


class TestWindowDto(BaseTest):

    def setUp(self):
        self.winSize = 4
        self.header = ["X", "AF3"]
        self.dto = WindowDto(self.winSize, self.header)

    def _fillDto(self, start=0, count=2):
        for i in range(start, count):
            self.dto.addData({"X": {"value" : i, "quality": i*2}, "AF3": {"value" : i*3, "quality": i*4}})

    def test_init(self):
        self._fillDto(count=self.winSize)

    def test_len(self):
        self.assertEqual(len(self.dto), len(self.header))

    def test_shape(self):
        self.assertEqual(self.dto.shape(), (len(self.dto), len(self.header)))

    def test_contains(self):
        self.assertTrue("X" in self.dto)
        self.assertTrue("AF3" in self.dto)
        self.assertFalse("x" in self.dto)
        self.assertFalse("Y" in self.dto)

    def test_getitem(self):
        self._fillDto(count=self.winSize)
        self.assertEqual(self.dto["X"]["value"], range(self.winSize))

    def test_iter(self):
        for key in self.dto:
            self.assertTrue(key in self.header)

    def test_eq(self):
        self.assertNotEqual(self.dto, None)
        self.assertNotEqual(self.dto, 1)
        cp = self.dto.copy()
        cp.header = ["AF3", "X"]
        self.assertNotEqual(self.dto, cp)

        cp = self.dto.copy()
        self.assertEqual(cp, self.dto)
        self._fillDto(count=self.winSize)
        self.assertNotEqual(cp, self.dto)

    def test_cp(self):
        cp = self.dto.copy()
        self.assertEqual(cp, self.dto)
        self.assertNotEquals(id(cp), id(self.dto))

    def test_getField(self):
        self._fillDto(count=self.winSize)

        assert_array_equal(self.dto.getValue("X"), range(self.winSize))
        assert_array_equal(self.dto.getQuality("X"), np.array(range(self.winSize))*2)

        testVal = np.array([17])*self.winSize
        self.dto.addNewField("X", "test", testVal)
        assert_array_equal(self.dto.getField("X", "test"), testVal)

if __name__ == '__main__':
    unittest.main()