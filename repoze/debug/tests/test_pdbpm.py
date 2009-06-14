import unittest

class TestPDBPM(unittest.TestCase):
    def _getFUT(self):
        from repoze.debug.pdbpm import PostMortemDebug
        return PostMortemDebug

    def _makeOne(self, app, *ignore_exc):
        f = self._getFUT()
        return f(app, *ignore_exc)

    def test_post_mortem_withexc(self):
        app = DummyApplication(KeyError)
        mw = self._makeOne(app)
        fake_pdb = FakePDB()
        try:
            import repoze.debug.pdbpm
            old_pdb = repoze.debug.pdbpm.pdb
            repoze.debug.pdbpm.pdb = fake_pdb
            environ = {}
            self.assertRaises(KeyError, mw, environ, None)
        finally:
            repoze.debug.pdb = old_pdb
        self.assertEqual(fake_pdb.called, True)

    def test_post_mortem_noexc(self):
        app = DummyApplication()
        mw = self._makeOne(app)
        fake_pdb = FakePDB()
        try:
            import repoze.debug.pdbpm
            old_pdb = repoze.debug.pdbpm.pdb
            repoze.debug.pdbpm.pdb = fake_pdb
            environ = {}
            result = mw(environ, None)
        finally:
            repoze.debug.pdbpm.pdb = old_pdb
        self.assertEqual(fake_pdb.called, False)
        self.assertEqual(result, ['hello world'])

    def test_post_mortem_ignore_exc(self):
        app = DummyApplication(KeyError)
        mw = self._makeOne(app, KeyError)
        fake_pdb = FakePDB()
        try:
            import repoze.debug.pdbpm
            old_pdb = repoze.debug.pdbpm.pdb
            repoze.debug.pdbpm.pdb = fake_pdb
            environ = {}
            self.assertRaises(KeyError, mw, environ, None)
        finally:
            repoze.debug.pdb = old_pdb
        self.assertEqual(fake_pdb.called, False)

class TestMakeMiddleware(unittest.TestCase):
    def _callFUT(self, app, global_conf=None, ignore_http_exceptions=True):
        from repoze.debug.pdbpm import make_middleware
        return make_middleware(app, global_conf, ignore_http_exceptions)

    def test_paste_constructor_ignore_http_exceptions(self):
        app = DummyApplication() 
        mw = self._callFUT(app, None)
        self.assertEqual(mw.__name__, 'middleware')

    def test_paste_constructor_ignore_http_exceptions_False(self):
        app = DummyApplication() 
        mw = self._callFUT(app, None, False)
        self.assertEqual(mw.__name__, 'middleware')
    

class FakePDB:
    called = False
    def post_mortem(self, *args):
        self.called = True

class DummyApplication:
    def __init__(self, exc=None):
        self.exc = exc

    def __call__(self, environ, start_response):
        if self.exc:
            raise self.exc
        self.environ = environ
        self.start_response = start_response
        return ['hello world']

class DummyException(Exception):
    pass
