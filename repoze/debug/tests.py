import unittest

class TestResponseLoggingMiddleware(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.debug.responselogger import ResponseLoggingMiddleware
        return ResponseLoggingMiddleware

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def _makeEnviron(self):
        environ = {
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'80',
            'wsgi.version':(1,0),
            'wsgi.multiprocess':False,
            'wsgi.multithread':True,
            'wsgi.run_once':False,
            'wsgi.url_scheme':'http',
            }
        return environ

    def test_call(self):
        body = ['thebody']
        app = DummyApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        logger = FakeLogger()
        mw = self._makeOne(app, 0, logger)
        environ = self._makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(''.join(app_iter), 'thebody')
        self.assertEqual(len(logger.logged), 2)
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(len(start_response.headers), 1)
        self.assertEqual(start_response.headers[0], ('HeaderKey','headervalue'))
        self.assertEqual(start_response.exc_info, None)
        self.assertEqual(app.called, True)

    def test_call_overmaxbodylen(self):
        body = ['thebody']
        app = DummyApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        logger = FakeLogger()
        mw = self._makeOne(app, 1, logger)
        environ = self._makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(''.join(app_iter), 'thebody')
        self.assertEqual(len(logger.logged), 2)
        self.failUnless('(truncated)' in logger.logged[1])

class TestMakeMiddleware(unittest.TestCase):
    def _getFUT(self):
        from repoze.debug.responselogger import make_middleware
        return make_middleware

    def test_make_middleware_defaults(self):
        f = self._getFUT()
        app = DummyApp(None, None, None)
        global_conf = {}
        import tempfile
        fn = tempfile.mktemp()
        mw = f(app, global_conf, fn)
        self.assertEqual(len(mw.logger.handlers), 1)
        self.assertEqual(mw.max_bodylen, 0)

    def test_make_middleware_nondefaults(self):
        f = self._getFUT()
        app = DummyApp(None, None, None)
        global_conf = {}
        import tempfile
        fn = tempfile.mktemp()
        mw = f(app, global_conf, fn, '0', '0')
        self.assertEqual(len(mw.logger.handlers), 1)

class FakeStartResponse:
    def __call__(self, status, headers, exc_info=None):
        self.status = status
        self.headers = headers
        self.exc_info = exc_info

class FakeLogger:
    def __init__(self):
        self.logged = []
        
    def info(self, msg):
        self.logged.append(msg)

class DummyApp:
    def __init__(self, body, status, headers):
        self.body = body
        self.status = status
        self.headers = headers
        
    def __call__(self, environ, start_response):
        start_response(self.status, self.headers)
        self.called = True
        return self.body
    
