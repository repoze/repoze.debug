import unittest

class TestCanaryMiddleware(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.debug.canary import CanaryMiddleware
        return CanaryMiddleware

    def _makeOne(self, app):
        klass = self._getTargetClass()
        return klass(app)

    def test_call(self):
        def app(environ, start_response):
            environ['app_saw'] = True
            return True
        mw = self._makeOne(app)
        environ = {}
        result = mw(environ, None)
        self.assertEqual(result, True)
        from repoze.debug.canary import Canary
        self.failUnless(isinstance(environ['repoze.debug.canary'], Canary))
        self.assertEqual(environ['app_saw'], True)
        
class TestMakeCanaryMiddleware(unittest.TestCase):
    def _getFUT(self):
        from repoze.debug.canary import make_middleware
        return make_middleware

    def test_maker(self):
        f = self._getFUT()
        mw = f(None, None)
        self.assertEqual(mw.app, None)
        
        


        
        
