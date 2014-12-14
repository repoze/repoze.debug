import unittest

class _Base(unittest.TestCase):

    _old_NOW = None

    def tearDown(self):
        super(_Base, self).tearDown()
        if self._old_NOW is not None:
            self._setNOW(self._old_NOW)

    def _setNOW(self, value):
        from repoze.debug import threads
        self._old_NOW, threads._NOW = threads._NOW, value

class Test_dump_threads(_Base):

    def _callFUT(self, frames=None, thread_id=None):
        from ..threads import dump_threads
        return dump_threads(frames=frames, thread_id=thread_id)

    def test_wo_other_threads(self):
        import datetime
        now = datetime.datetime(2013, 11, 21, 21, 5, 37)
        self._setNOW(now)
        lines = self._callFUT().splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0],
                         "Threads traceback dump at 2013-11-21 21:05:37")
        self.assertEqual(lines[1], "")
        self.assertEqual(lines[2], "End of dump")

    def test_w_other_threads(self):
        import datetime
        class Dummy(object):
            def __init__(self, **kw):
                self.__dict__.update(kw)
        f_code = Dummy(co_name='publish',
                       co_filename='/path/to/publisher/publish.py',
                      )
        f_locals = {'request': {'REQEUEST_METHOD': 'GET',
                                'PATH_INFO': '/url/path',
                                'QUERY_STRING': 'foo=bar&baz=1',
                               },
                   }
        frames = {'tid1': Dummy(), #ignored
                  'tid2': Dummy(f_code=f_code,
                                f_locals=f_locals,
                                f_lineno=123,
                                f_globals={},
                                f_back=None,
                               ),
                 }
        now = datetime.datetime(2013, 11, 21, 21, 5, 37)
        self._setNOW(now)
        lines = self._callFUT(frames, 'tid1').splitlines()
        self.assertEqual(len(lines), 5)
        self.assertEqual(lines[0],
                         "Threads traceback dump at 2013-11-21 21:05:37")
        self.assertEqual(lines[1], "")
        self.assertEqual(lines[2], "Thread tid2:")
        self.assertEqual(lines[3],
            """['  File "/path/to/publisher/publish.py", line 123,"""
                """ in publish\\n']""")
        self.assertEqual(lines[4], "End of dump")


class MonitoringMiddlewareTests(_Base):

    def _getTargetClass(self):
        from repoze.debug.threads import MonitoringMiddleware
        return MonitoringMiddleware

    def _makeOne(self, app):
        return self._getTargetClass()(app)

    def test_ctor(self):
        app = DummyApp()
        mw = self._makeOne(app)
        self.assertTrue(mw.app is app)

    def test___call___w_debug(self):
        import datetime
        now = datetime.datetime(2013, 11, 21, 21, 5, 37)
        self._setNOW(now)
        _environ = {'PATH_INFO': '/debug_threads',
                    'REQUEST_METHOD': 'GET',
                   }
        _started = []
        _body = []
        def _start_response(status, response_headers, exc_info=None):
            _started.append((status, response_headers, exc_info))
            return _body.append
        app = DummyApp()
        mw = self._makeOne(app)
        chunks = list(mw(_environ, _start_response))
        self.assertEqual(_started,
                        [('200 OK',
                          [('Content-Type', 'text/plain; charset=UTF-8'),
                           ('Content-Length', '58'),
                          ],
                          None)])
        self.assertTrue(app._environ is None)
        self.assertEqual(len(chunks), 1)
        lines = chunks[0].splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0],
                         b"Threads traceback dump at 2013-11-21 21:05:37")
        self.assertEqual(lines[1], b"")
        self.assertEqual(lines[2], b"End of dump")

    def test___call___not_debug(self):
        _environ = {'PATH_INFO': '/path/info',
                    'REQUEST_METHOD': 'GET',
                   }
        _started = []
        _body = []
        def _start_response(status, response_headers, exc_info=None):
            _started.append((status, response_headers, exc_info))
            return _body.append
        app = DummyApp()
        mw = self._makeOne(app)
        chunks = list(mw(_environ, _start_response))
        self.assertEqual(app._environ, _environ)
        self.assertEqual(chunks, ['body'])
        self.assertEqual(_started,
                        [('200 OK',
                          [('Content-Type', 'text/html; charset=UTF-8')],
                          None)])


class Test_make_middleware(_Base):

    def _callFUT(self, app, global_conf):
        from repoze.debug.threads import make_middleware
        return make_middleware(app, global_conf)

    def test_it(self):
        app = DummyApp()
        mw = self._callFUT(app, {})
        self.assertTrue(mw.app is app)


class DummyApp(object):
    _environ = None

    def __call__(self, environ, start_response):
        self._environ = environ
        start_response(200, [])
        return ['body']
