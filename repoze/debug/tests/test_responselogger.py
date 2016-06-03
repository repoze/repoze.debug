# -*- encoding: utf-8 -*-
import unittest


class ResponseLoggingMiddlewareTests(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.debug.responselogger import ResponseLoggingMiddleware
        return ResponseLoggingMiddleware

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_call(self):
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 0, 10, vlogger, tlogger)
        environ = _makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(b''.join(list(app_iter)), b'thebody')
        self.assertEqual(len(vlogger.logged), 2)
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(len(start_response.headers), 1)
        self.assertEqual(start_response.headers[0], ('HeaderKey','headervalue'))
        self.assertEqual(start_response.exc_info, None)
        self.assertEqual(app.called, True)

    def test_call_gui_url(self):
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 0, 10, vlogger, tlogger)
        environ = _makeEnviron()
        environ['PATH_INFO'] = '/__repoze.debug/feed.xml'
        environ['REQUEST_METHOD'] = 'GET'
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)

    def test_call_umlaut_url(self):
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 0, 10, vlogger, tlogger)
        environ = _makeEnviron()
        # Having special characters in url lacking
        # proper url encoding obviously is invalid,
        # but we should be graceful though.
        environ['PATH_INFO'] = '/äöü'
        environ['QUERY_STRING'] = 'some_value=äöü'
        environ['REQUEST_METHOD'] = 'GET'
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)

    def test_call_nologgers(self):
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        mw = self._makeOne(app, 0, 10, None, None)
        environ = _makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(b''.join(list(app_iter)), b'thebody')
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(len(start_response.headers), 1)
        self.assertEqual(start_response.headers[0], ('HeaderKey','headervalue'))
        self.assertEqual(start_response.exc_info, None)
        self.assertEqual(app.called, True)

    def test_call_overmaxbodylen(self):
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        environ = _makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(b''.join(app_iter), b'thebody')
        self.assertEqual(len(vlogger.logged), 2)
        self.assertTrue('(truncated at 1 bytes)' in vlogger.logged[1])

    def test_call_overkeep(self):
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 1, vlogger, tlogger)
        mw.entries = ['a']
        environ = _makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(len(mw.entries), 1)

    def test_call_keep_zero_doesnt_append_entry(self):
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 0, vlogger, tlogger)
        mw.entries = []
        environ = _makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(len(mw.entries), 0)

    def test_call_start_response_not_called(self):
        body = [b'thebody']
        app = DummyBrokenApp(body, '200 OK', [('HeaderKey', 'headervalue')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 1, vlogger, tlogger)
        environ = _makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(mw.entries[-1]['response']['status'],
                         '500 Start Response Not Called')

    def test_call_app_iter_close(self):
        class Iterable(object):
            def __init__(self, data):
                self.data = data
            def close(self):
                self.closed = True
            def __iter__(self):
                return self
            def next(self):
                if not self.data:
                    raise StopIteration
                return self.data.pop(0)
            __next__ = next
        iterable = Iterable([b'1', b'2'])
        app = DummyBrokenApp(iterable, '200 OK', [('HeaderKey', 'headervalue')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 1, vlogger, tlogger)
        environ = _makeEnviron()
        start_response = FakeStartResponse()
        app_iter = list(mw(environ, start_response))
        self.assertEqual(iterable.closed, True)

    def test_call_input_non_rewindable(self):
        BODY = b"Don't bother rewinding me!"
        class _NoRewind(object):
            def read(self, *args):
                return BODY
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('Content-Length', str(len(body[0])))])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        environ = _makeEnviron()
        environ['wsgi.input'] = _NoRewind()
        environ['CONTENT_LENGTH'] = str(len(body))
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(b''.join(app_iter), b'thebody')
        self.assertEqual(len(vlogger.logged), 2)
        self.assertFalse('WARNING-1' in vlogger.logged[1])

    def test_call_contentlengthmissing(self):
        import io
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        environ = _makeEnviron()
        environ['wsgi.input'] = io.BytesIO()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(b''.join(app_iter), b'thebody')
        self.assertEqual(len(vlogger.logged), 2)
        self.assertFalse('WARNING-1' in vlogger.logged[1])

    def test_call_contentlengthemptyvalue(self):
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('Content-Length', '')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        environ = _makeEnviron()
        environ['CONTENT_LENGTH'] = ''
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        entry = mw.entries[0]
        self.assertEqual(b''.join(app_iter), b'thebody')
        self.assertEqual(len(vlogger.logged), 2)
        self.assertEqual(entry['response']['content-length'], None)
        self.assertEqual(entry['response']['headers'],
                         [('Content-Length', '')])

    def test_call_contentlengthwrong(self):
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('Content-Length', '1')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        environ = _makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(b''.join(app_iter), b'thebody')
        self.assertEqual(len(vlogger.logged), 2)
        self.assertTrue('WARNING-1' in vlogger.logged[1])

    def test_call_sourceurl_in_response(self):
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('Content-Length', '1')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        environ = _makeEnviron()
        start_response = FakeStartResponse()
        app_iter = mw(environ, start_response)
        self.assertEqual(b''.join(app_iter), b'thebody')
        self.assertEqual(len(vlogger.logged), 2)
        self.assertTrue('URL: GET http://localhost' in vlogger.logged[1])

    def test_entry_created(self):
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('Content-Length', '1')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        start_response = FakeStartResponse()
        environ = _makeEnviron()
        app_iter = mw(environ, start_response)
        self.assertEqual(b''.join(app_iter), b'thebody')
        self.assertEqual(len(mw.entries), 1)
        entry = mw.entries[0]
        self.assertEqual(entry['response']['status'], '200 OK')
        self.assertTrue(isinstance(entry['request']['begin'], float))
        self.assertTrue(isinstance(entry['response']['begin'], float))
        self.assertTrue(isinstance(entry['response']['end'], float))
        self.assertEqual(entry['response']['headers'],
                         [('Content-Length', '1')])
        self.assertEqual(entry['request']['url'], 'http://localhost')
        self.assertEqual(entry['request']['body'], b'hello world')
        self.assertEqual(entry['response']['content-length'], 1)
        self.assertEqual(len(entry['request']['cgi_variables']), 2)
        self.assertEqual(len(entry['request']['wsgi_variables']), 2)
        self.assertEqual(entry['id'], id(environ))

    def test_trace_logging(self):
        import time
        body = [b'thebody']
        app = DummyApp(body, '200 OK', [('Content-Length', '7')])
        vlogger = FakeLogger()
        tlogger = FakeLogger()
        mw = self._makeOne(app, 1, 10, vlogger, tlogger)
        start_response = FakeStartResponse()
        environ = _makeEnviron()
        mw.pid = 0
        mw._now = now = time.time()
        app_iter = mw(environ, start_response)
        self.assertEqual(b''.join(app_iter), b'thebody')
        self.assertEqual(len(tlogger.logged), 4)
        logged = tlogger.logged
        entry = mw.entries[0]
        rid = entry['id']
        begin = entry['request']['begin']
        self.assertEqual(begin, now)

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


class Test_make_middleware(unittest.TestCase):

    def _callFUT(self, app, global_conf, *args):
        from repoze.debug.responselogger import make_middleware
        return make_middleware(app, global_conf, *args)

    def test_make_middleware_defaults(self):
        import tempfile
        app = DummyApp(None, None, None)
        global_conf = {}
        fn = tempfile.mktemp()
        mw = self._callFUT(app, global_conf)
        self.assertEqual(mw.verbose_logger, None)
        self.assertEqual(mw.max_bodylen, 3072)
        self.assertEqual(mw.keep, 100)

    def test_make_middleware_nondefaults(self):
        import tempfile
        app = DummyApp(None, None, None)
        global_conf = {}
        vfn = tempfile.mktemp()
        tfn = tempfile.mktemp()
        mw = self._callFUT(app, global_conf, vfn, tfn, '0', '0', '0', '0')
        self.assertEqual(len(mw.verbose_logger.handlers), 1)
        self.assertEqual(len(mw.trace_logger.handlers), 1)
        self.assertEqual(mw.max_bodylen, 0)
        self.assertEqual(mw.keep, 0)
        mw.verbose_logger.handlers[0].close()
        mw.trace_logger.handlers[0].close()


class SupplementTests(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.debug.responselogger import Supplement
        return Supplement

    def _makeOne(self, middleware, environ):
        klass = self._getTargetClass()
        return klass(middleware, environ)

    def test_ctor(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron()
        supplement = self._makeOne(middleware, environ)
        self.assertTrue(supplement.middleware is middleware)
        self.assertTrue(supplement.environ is environ)
        self.assertEqual(supplement.source_url, 'http://localhost')

    def test_extraData_non_concurrent(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron({'wsgi.multiprocess': 0,
                                'wsgi.multithread': 0,
                                'wsgi.run_once': 0,
                               })
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(data[('extra', 'WSGI Variables')]['wsgi process'],
                         'Non-concurrent server')

    def test_extraData_multithreaded(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron({'wsgi.multiprocess': 0,
                                'wsgi.multithread': 1,
                                'wsgi.run_once': 0,
                               })
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(data[('extra', 'WSGI Variables')]['wsgi process'],
                         'Multithreaded')

    def test_extraData_multiprocess(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron({'wsgi.multiprocess': 1,
                                'wsgi.multithread': 0,
                                'wsgi.run_once': 0,
                               })
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(data[('extra', 'WSGI Variables')]['wsgi process'],
                         'Multiprocess')

    def test_extraData_multiprocess_and_threads(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron({'wsgi.multiprocess': 1,
                                'wsgi.multithread': 1,
                                'wsgi.run_once': 0,
                               })
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(data[('extra', 'WSGI Variables')]['wsgi process'],
                         'Multi process AND threads (?)')

    def test_extraData_non_concurrent_CGI(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron({'wsgi.multiprocess': 0,
                                'wsgi.multithread': 0,
                                'wsgi.run_once': 1,
                               })
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(data[('extra', 'WSGI Variables')]['wsgi process'],
                         'Non-concurrent CGI')

    def test_extraData_multithread_CGI(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron({'wsgi.multiprocess': 0,
                                'wsgi.multithread': 1,
                                'wsgi.run_once': 1,
                               })
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(data[('extra', 'WSGI Variables')]['wsgi process'],
                         'Multithread CGI (?)')

    def test_extraData_CGI(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron({'wsgi.multiprocess': 1,
                                'wsgi.multithread': 0,
                                'wsgi.run_once': 1,
                               })
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(data[('extra', 'WSGI Variables')]['wsgi process'],
                         'CGI')

    def test_extraData_multithread_process_CGI(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron({'wsgi.multiprocess': 1,
                                'wsgi.multithread': 1,
                                'wsgi.run_once': 1,
                               })
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(data[('extra', 'WSGI Variables')]['wsgi process'],
                         'Multi thread/process CGI (?)')

    def test_extraData_no_unhidden_vars(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron()
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(sorted(data),
                         [('extra', 'CGI Variables'),
                          ('extra', 'WSGI Variables'),
                         ])
        self.assertEqual(data[('extra', 'CGI Variables')],
                         {'SERVER_NAME': 'localhost',
                          'SERVER_PORT': '80',
                         }
                        )
        self.assertEqual(data[('extra', 'WSGI Variables')],
                         {'application': app,
                          'wsgi process': 'Multithreaded',
                         })

    def test_extraData_w_unhidden_vars(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron({'x-other': 'foo'})
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(sorted(data),
                         [('extra', 'CGI Variables'),
                          ('extra', 'WSGI Variables'),
                         ])
        self.assertEqual(data[('extra', 'CGI Variables')],
                         {'SERVER_NAME': 'localhost',
                          'SERVER_PORT': '80',
                         }
                        )
        self.assertEqual(data[('extra', 'WSGI Variables')],
                         {'application': app,
                          'wsgi process': 'Multithreaded',
                          'x-other': 'foo',
                         })

    def test_extraData_w_non_default_wsgi_version(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron({'wsgi.version': (3, 0)})
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(sorted(data),
                         [('extra', 'CGI Variables'),
                          ('extra', 'WSGI Variables'),
                         ])
        self.assertEqual(data[('extra', 'CGI Variables')],
                         {'SERVER_NAME': 'localhost',
                          'SERVER_PORT': '80',
                         }
                        )
        self.assertEqual(data[('extra', 'WSGI Variables')],
                         {'application': app,
                          'wsgi process': 'Multithreaded',
                          'wsgi.version': (3, 0),
                         })

    def test_extraData_w_paste_config(self):
        app = object()
        middleware = DummyMiddleware(app)
        environ = _makeEnviron({'paste.config': {'foo': 'bar'}})
        supplement = self._makeOne(middleware, environ)
        data = supplement.extraData()
        self.assertEqual(sorted(data),
                         [('extra', 'CGI Variables'),
                          ('extra', 'Configuration'),
                          ('extra', 'WSGI Variables'),
                         ])
        self.assertEqual(data[('extra', 'Configuration')], {'foo': 'bar'})
        self.assertEqual(data[('extra', 'CGI Variables')],
                         {'SERVER_NAME': 'localhost',
                          'SERVER_PORT': '80',
                         }
                        )
        self.assertEqual(data[('extra', 'WSGI Variables')],
                         {'application': app,
                          'wsgi process': 'Multithreaded',
                         })


class Test_construct_url(unittest.TestCase):

    def _callFUT(self, environ):
        from repoze.debug.responselogger import construct_url
        return construct_url(environ)

    def test_w_HTTP_HOST_wo_port(self):
        environ = _makeEnviron({'HTTP_HOST': 'example.com'})
        self.assertEqual(self._callFUT(environ), 'http://example.com')

    def test_w_HTTP_HOST_w_default_http_port(self):
        environ = _makeEnviron({'HTTP_HOST': 'example.com:80'})
        self.assertEqual(self._callFUT(environ), 'http://example.com')

    def test_w_HTTP_HOST_w_non_default_http_port(self):
        environ = _makeEnviron({'HTTP_HOST': 'example.com:8080'})
        self.assertEqual(self._callFUT(environ), 'http://example.com:8080')

    def test_w_HTTP_HOST_w_default_https_port(self):
        environ = _makeEnviron({'HTTP_HOST': 'example.com:443',
                                'wsgi.url_scheme': 'https',
                               })
        self.assertEqual(self._callFUT(environ), 'https://example.com')

    def test_w_HTTP_HOST_w_non_default_https_port(self):
        environ = _makeEnviron({'HTTP_HOST': 'example.com:4443',
                                'wsgi.url_scheme': 'https',
                               })
        self.assertEqual(self._callFUT(environ), 'https://example.com:4443')

    def test_wo_HTTP_HOST_w_default_http_port(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '80',
                               })
        self.assertEqual(self._callFUT(environ), 'http://example.com')

    def test_wo_HTTP_HOST_w_non_default_http_port(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '8080',
                               })
        self.assertEqual(self._callFUT(environ), 'http://example.com:8080')

    def test_wo_HTTP_HOST_w_default_https_port(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '443',
                                'wsgi.url_scheme': 'https',
                               })
        self.assertEqual(self._callFUT(environ), 'https://example.com')

    def test_wo_HTTP_HOST_w_non_default_https_port(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '4443',
                                'wsgi.url_scheme': 'https',
                               })
        self.assertEqual(self._callFUT(environ), 'https://example.com:4443')

    def test_w_SCRIPT_NAME(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '80',
                                'SCRIPT_NAME': '/script/name',
                               })
        self.assertEqual(self._callFUT(environ),
                         'http://example.com/script/name')

    def test_w_PATH_INFO(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '80',
                                'PATH_INFO': '/path/info',
                               })
        self.assertEqual(self._callFUT(environ),
                         'http://example.com/path/info')

    def test_w_SCRIPT_NAME_and_PATH_INFO(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '80',
                                'SCRIPT_NAME': '/script/name',
                                'PATH_INFO': '/path/info',
                               })
        self.assertEqual(self._callFUT(environ),
                         'http://example.com/script/name/path/info')

    def test_w_QUERY_STRING(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '80',
                                'QUERY_STRING': 'foo=bar&qux=spam',
                               })
        self.assertEqual(self._callFUT(environ),
                         'http://example.com?foo=bar&qux=spam')


class Test_header_value(unittest.TestCase):

    def _callFUT(self, headers, name):
        from repoze.debug.responselogger import header_value
        return header_value(headers, name)

    def test_miss(self):
        self.assertEqual(self._callFUT([], 'nonesuch'), None)

    def test_hit_simple(self):
        self.assertEqual(
            self._callFUT([('Header-Name', 'Value')], 'Header-Name'), 'Value')

    def test_hit_multiple(self):
        self.assertEqual(
            self._callFUT([('Header-Name', 'Value1'),
                           ('Header-Name', 'Value2'),
                          ], 'Header-Name'), 'Value1,Value2')

    def test_case_insensitive(self):
        self.assertEqual(
            self._callFUT([('Header-Name', 'Value')], 'HEADER-NAME'), 'Value')
        self.assertEqual(
            self._callFUT([('HEADER-NAME', 'Value')], 'Header-Name'), 'Value')


class FakeStartResponse(object):

    def __call__(self, status, headers, exc_info=None):
        self.status = status
        self.headers = headers
        self.exc_info = exc_info


class FakeLogger(object):

    def __init__(self):
        self.logged = []

    def info(self, msg):
        self.logged.append(msg)


class DummyApp(object):

    def __init__(self, body, status, headers):
        self.body = body
        self.status = status
        self.headers = headers

    def __call__(self, environ, start_response):
        start_response(self.status, self.headers)
        self.called = True
        return self.body


class DummyBrokenApp(DummyApp):

    def __call__(self,environ, start_response):
        self.called = True
        return self.body


class DummyMiddleware(object):

    def __init__(self, application):
        self.application = application


def _makeEnviron(override=None):
    import io
    environ = {
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.multiprocess': False,
        'wsgi.multithread': True,
        'wsgi.run_once': False,
        'wsgi.url_scheme': 'http',
        'wsgi.input': io.BytesIO(b'hello world'),
        }
    if override is not None:
        environ.update(override)
    return environ
