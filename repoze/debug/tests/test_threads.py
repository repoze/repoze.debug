import unittest

class Test_dump_threads(unittest.TestCase):

    def tearDown(self):
        try:
            self._setNOW(self._old_NOW)
        except AttributeError:
            pass

    def _callFUT(self, frames=None, thread_id=None):
        from ..threads import dump_threads
        return dump_threads(frames=frames, thread_id=thread_id)

    def _setNOW(self, value):
        from repoze.debug import threads
        self._old_NOW, threads._NOW = threads._NOW, value

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
                  'tid2': Dummy(f_code=f_code, f_locals=f_locals),
                 }
        now = datetime.datetime(2013, 11, 21, 21, 5, 37)
        self._setNOW(now)
        lines = self._callFUT().splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0],
                         "Threads traceback dump at 2013-11-21 21:05:37")
        self.assertEqual(lines[1], "")
        self.assertEqual(lines[2], "End of dump")
