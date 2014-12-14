import unittest

class RequestTests(unittest.TestCase):

    def _getTargetClass(self):
        from ..requestprofiler import Request
        return Request

    def _makeOne(self):
        return self._getTargetClass()()

    def test_ctor_defaults(self):
        request = self._makeOne()
