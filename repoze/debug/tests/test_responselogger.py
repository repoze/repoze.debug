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
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 0, 10, vlogger, tlogger)
        environ = self._makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(''.join(list(app_iter)), 'thebody')
        self.assertEqual(len(vlogger.logged), 2)
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(len(start_response.headers), 1)
        self.assertEqual(start_response.headers[0], ('HeaderKey','headervalue'))
        self.assertEqual(start_response.exc_info, None)
        self.assertEqual(app.called, True)

    def test_call_nologgers(self):
        body = ['thebody']
        app = DummyApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        mw = self._makeOne(app, 0, 10, None, None)
        environ = self._makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(''.join(list(app_iter)), 'thebody')
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(len(start_response.headers), 1)
        self.assertEqual(start_response.headers[0], ('HeaderKey','headervalue'))
        self.assertEqual(start_response.exc_info, None)
        self.assertEqual(app.called, True)

    def test_call_overmaxbodylen(self):
        body = ['thebody']
        app = DummyApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        environ = self._makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(''.join(app_iter), 'thebody')
        self.assertEqual(len(vlogger.logged), 2)
        self.failUnless('(truncated at 1 bytes)' in vlogger.logged[1])

    def test_call_contentlengthwrong(self):
        body = ['thebody']
        app = DummyApp(body, '200 OK', [('Content-Length', '1')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        environ = self._makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(''.join(app_iter), 'thebody')
        self.assertEqual(len(vlogger.logged), 2)
        self.failUnless('WARNING-1' in vlogger.logged[1])

    def test_call_sourceurl_in_response(self):
        body = ['thebody']
        app = DummyApp(body, '200 OK', [('Content-Length', '1')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        environ = self._makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(''.join(app_iter), 'thebody')
        self.assertEqual(len(vlogger.logged), 2)
        self.failUnless('URL: GET http://localhost' in vlogger.logged[1])

    def test_entry_created(self):
        body = ['thebody']
        app = DummyApp(body, '200 OK', [('Content-Length', '1')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        start_response = FakeStartResponse()
        environ = self._makeEnviron()
        app_iter = mw(environ, start_response)
        self.assertEqual(''.join(app_iter), 'thebody')
        self.assertEqual(len(mw.entries), 1)
        entry = mw.entries[0]
        self.assertEqual(entry['response']['status'], '200 OK')
        self.failUnless(isinstance(entry['request']['begin'], float))
        self.failUnless(isinstance(entry['response']['begin'], float))
        self.failUnless(isinstance(entry['response']['end'], float))
        self.assertEqual(entry['response']['headers'],
                         [('Content-Length', '1')])
        self.assertEqual(entry['request']['url'], 'http://localhost')
        self.assertEqual(entry['response']['content-length'], 1)
        self.assertEqual(len(entry['request']['cgi_variables']), 2)
        self.assertEqual(len(entry['request']['wsgi_variables']), 2)
        self.failUnless(isinstance(entry['id'], int))

    def test_trace_logging(self):
        import time
        body = ['thebody']
        app = DummyApp(body, '200 OK', [('Content-Length', '7')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        start_response = FakeStartResponse()
        environ = self._makeEnviron()
        mw.pid = 0
        app_iter = mw(environ, start_response)
        self.assertEqual(''.join(app_iter), 'thebody')
        self.assertEqual(len(tlogger.logged), 4)
        logged = tlogger.logged
        entry = mw.entries[0]
        rid = entry['id']
        begin = entry['request']['begin']
        
        result = logged[0].split(' ', 4)
        self.assertEqual(result[0], 'U')
        self.assertEqual(result[1], str(mw.pid))
        self.assertEqual(result[2], str(rid))
        self.assertEqual(result[3], str(begin))

        result = logged[1].split(' ', 4)
        self.assertEqual(result[0], 'B')
        self.assertEqual(result[1], str(mw.pid))
        self.assertEqual(result[2], str(rid))
        self.assertEqual(result[3], str(begin))
        self.assertEqual(result[4], 'GET http://localhost')
                         
        result = logged[2].split(' ', 4)
        self.assertEqual(result[0], 'A')
        self.assertEqual(result[1], str(mw.pid))
        self.assertEqual(result[2], str(rid))
        self.assertEqual(result[3], str(begin))
        self.assertEqual(result[4], '200 7')

        result = logged[3].split(' ', 4)
        self.assertEqual(result[0], 'E')
        self.assertEqual(result[1], str(mw.pid))
        self.assertEqual(result[2], str(rid))
        self.assertEqual(result[3], str(begin))
        self.assertEqual(result[4], '7')

class TestMakeResponseLoggingMiddleware(unittest.TestCase):
    def _getFUT(self):
        from repoze.debug.responselogger import make_middleware
        return make_middleware

    def test_make_middleware_defaults(self):
        f = self._getFUT()
        app = DummyApp(None, None, None)
        global_conf = {}
        import tempfile
        fn = tempfile.mktemp()
        mw = f(app, global_conf)
        self.assertEqual(mw.verbose_logger, None)
        self.assertEqual(mw.max_bodylen, 3072)
        self.assertEqual(mw.keep, 100)

    def test_make_middleware_nondefaults(self):
        f = self._getFUT()
        app = DummyApp(None, None, None)
        global_conf = {}
        import tempfile
        vfn = tempfile.mktemp()
        tfn = tempfile.mktemp()
        mw = f(app, global_conf, vfn, tfn, '0', '0', '0', '0')
        self.assertEqual(len(mw.verbose_logger.handlers), 1)
        self.assertEqual(len(mw.trace_logger.handlers), 1)
        self.assertEqual(mw.max_bodylen, 0)
        self.assertEqual(mw.keep, 0)

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
    
