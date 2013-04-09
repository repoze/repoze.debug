import unittest

class Test_is_gui_url(unittest.TestCase):

    def _callFUT(self, environ):
        from repoze.debug.ui import is_gui_url
        return is_gui_url(environ)

    def test_no_PATH_INFO(self):
        self.assertFalse(self._callFUT({}))

    def test_w_PATH_INFO_not_gui_flag(self):
        self.assertFalse(self._callFUT({'PATH_INFO': 'something'}))

    def test_w_PATH_INFO_w_gui_flag(self):
        self.assertTrue(self._callFUT({'PATH_INFO': '__repoze.debug/foo'}))

class Test_get_mimetype(unittest.TestCase):

    def _callFUT(self, filename):
        from repoze.debug.ui import get_mimetype
        return get_mimetype(filename)

    def test_known_type(self):
        self.assertEqual(self._callFUT('foo.txt'), 'text/plain')

    def test_unknown_type(self):
        self.assertEqual(self._callFUT('foo.weird'),
                         'application/octet-stream')

    def test_unknown_type_XUL(self):
        self.assertEqual(self._callFUT('foo.bar.xul'),
                         'application/vnd.mozilla.xul+xml')

class DebugGuiTests(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.debug.ui import DebugGui
        return DebugGui

    def _makeOne(self, middleware):
        return self._getTargetClass()(middleware)

    def _makeEnviron(self, **kw):
        environ = {'PATH_INFO': '/',
                   'REQUEST_METHOD': 'GET',
                  }
        environ.update(kw)
        return environ

    def _make_start_response(self):
        _started = []
        def _start_response(*args):
            _started.append(args)
        return _started, _start_response

    def test___call___static_missing(self):
        environ = self._makeEnviron(PATH_INFO='/static/nonesuch.html')
        _started, _start_response = self._make_start_response()
        gui = self._makeOne(None)
        self.assertRaises(ValueError, gui, environ, _start_response)

    def test___call___static_not_missing(self):
        environ = self._makeEnviron(PATH_INFO='/static/debugui.html')
        _started, _start_response = self._make_start_response()
        gui = self._makeOne(None)
        app_iter =  gui(environ, _start_response)
        self.assertEqual(len(_started), 1)
        self.assertEqual(_started[0][0], '200 OK')
        headers = _started[0][1]
        self.assertTrue(('Content-Type', 'text/html; charset=UTF-8')
                            in headers)
        self.assertTrue(b'<html' in b''.join(list(app_iter)))
        # XXX need more assertions?  Damn trying to test rendered output!

    def test___call___unknown(self):
        environ = self._makeEnviron(PATH_INFO='/nonesuch.html')
        _started, _start_response = self._make_start_response()
        gui = self._makeOne(None)
        self.assertRaises(ValueError, gui, environ, _start_response)

    def test___call___w_feed_xml(self):
        environ = self._makeEnviron(PATH_INFO='/__repoze.debug/feed.xml')
        _started, _start_response = self._make_start_response()
        mw = DummyModel(entries=[], pid=1234)
        gui = self._makeOne(mw)
        app_iter =  gui(environ, _start_response)
        self.assertEqual(len(_started), 1)
        self.assertEqual(_started[0][0], '200 OK')
        headers = _started[0][1]
        self.assertTrue(('Content-Type', 'application/atom+xml; charset=UTF-8')
                            in headers)
        self.assertTrue(b'<atom:feed' in b''.join(list(app_iter)))
        # XXX need more assertions?  Damn trying to test rendered output!

    def test_getStatic_miss(self):
        gui = self._makeOne(None)
        self.assertRaises(ValueError, gui.getStatic, 'nonesuch.html')

    def test_getStatic_hit(self):
        from webob import Response
        gui = self._makeOne(None)
        response = gui.getStatic('debugui.html')
        self.assertTrue(isinstance(response, Response))
        self.assertEqual(response.content_type, 'text/html')
        self.assertEqual(response.charset, 'UTF-8')
        # XXX need more assertions?  Damn trying to test rendered output!

    def test_getFeed_empty(self):
        from webob import Response
        mw = DummyModel(entries=[], pid=1234)
        gui = self._makeOne(mw)
        response = gui.getFeed()
        self.assertTrue(isinstance(response, Response))
        self.assertEqual(response.content_type, 'application/atom+xml')
        # XXX need more assertions?  Damn trying to test rendered output!

    def test_getFeed_non_empty_no_response(self):
        from webob import Response
        entries = [
            {'id': 'aaaa',
             'request': {
                'begin': 1234,
                'method': 'GET',
                'url': '/foo',
                'cgi_variables': [('cgi_a', 'CGI_A')],
                'wsgi_variables': [('wsgi_a', 'WSGI_A')],
                'body': '',
                },
             #'response': {},
            },
        ]
        mw = DummyModel(entries=entries, pid=1234)
        gui = self._makeOne(mw)
        response = gui.getFeed()
        self.assertTrue(isinstance(response, Response))
        self.assertEqual(response.content_type, 'application/atom+xml')
        # XXX need more assertions?  Damn trying to test rendered output!

    def test_getFeed_non_empty_no_response_long_url(self):
        from webob import Response
        entries = [
            {'id': 'aaaa',
             'request': {
                'begin': 1234,
                'method': 'GET',
                'url': '/foo/%s' % '/'.join(['bbb' * 40]),
                'cgi_variables': [('cgi_a', 'CGI_A')],
                'wsgi_variables': [('wsgi_a', 'WSGI_A')],
                'body': '',
                },
             #'response': {},
            },
        ]
        mw = DummyModel(entries=entries, pid=1234)
        gui = self._makeOne(mw)
        response = gui.getFeed()
        self.assertTrue(isinstance(response, Response))
        self.assertEqual(response.content_type, 'application/atom+xml')
        # XXX need more assertions?  Damn trying to test rendered output!

    def test_getFeed_non_empty_w_response(self):
        from webob import Response
        entries = [
            {'id': 'aaaa',
             'request': {
                'begin': 1234,
                'method': 'GET',
                'url': '/foo',
                'cgi_variables': [('cgi_a', 'CGI_A')],
                'wsgi_variables': [('wsgi_a', 'WSGI_A')],
                'body': '',
                },
             'response': {
                'begin': 1235,
                'end': 1236,
                'status': '200 OK',
                'content-length': 57,
                'headers': [('header_a', 'HEADER_A')],
                'body': 'X' * 57,
                },
            },
        ]
        mw = DummyModel(entries=entries, pid=1234)
        gui = self._makeOne(mw)
        response = gui.getFeed()
        self.assertTrue(isinstance(response, Response))
        self.assertEqual(response.content_type, 'application/atom+xml')
        # XXX need more assertions?  Damn trying to test rendered output!

class DummyModel:
    def __init__(self, **kw):
        self.__dict__.update(kw)
