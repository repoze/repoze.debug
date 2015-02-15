import unittest


class RequestTests(unittest.TestCase):

    def _getTargetClass(self):
        from ..requestprofiler import Request
        return Request

    def _makeOne(self):
        return self._getTargetClass()()

    def _orig_state(self, request):
        self.assertEqual(request.url, None)
        self.assertEqual(request.start, None)
        self.assertEqual(request.method, None)
        self.assertEqual(request.t_recdinput, None)
        self.assertEqual(request.isize, 0)
        self.assertEqual(request.t_recdoutput, None)
        self.assertEqual(request.osize, None)
        self.assertEqual(request.httpcode, None)
        self.assertEqual(request.t_end, None)
        self.assertEqual(request.elapsed, None)
        self.assertEqual(request.active, 0)

    def test_ctor_defaults(self):
        request = self._makeOne()
        self._orig_state(request)

    def test_put_w_invalid_code(self):
        request = self._makeOne()
        self.assertRaises(ValueError, request.put, 'X', 123, 'XXX')

    def test_put_w_I(self):
        request = self._makeOne()
        # 'I' is a no-op
        request.put('I', 123, 'whatever')
        self._orig_state(request)

    def test_put_w_B(self):
        request = self._makeOne()
        request.put('B', 123, ' GET /foo/bar ')
        self.assertEqual(request.start, 123)
        self.assertEqual(request.method, 'GET')
        self.assertEqual(request.url, '/foo/bar')

    def test_put_w_A(self):
        request = self._makeOne()
        request.put('A', 123, ' 200 4567 ')
        self.assertEqual(request.t_recdinput, 123)
        self.assertEqual(request.t_recdinput, 123)
        self.assertEqual(request.httpcode, '200')
        self.assertEqual(request.osize, '4567')

    def test_put_w_E(self):
        request = self._makeOne()
        request.start = 100
        request.put('E', 123, 'whatever')
        self.assertEqual(request.t_end, 123)
        self.assertEqual(request.elapsed, 23)

    def test_is_finished_no_elapsed(self):
        request = self._makeOne()
        self.assertFalse(request.isfinished())

    def test_is_finished_w_elapsed(self):
        request = self._makeOne()
        request.elapsed = 23
        self.assertTrue(request.isfinished())

    def test_prettystart_na(self):
        request = self._makeOne()
        self.assertEqual(request.prettystart(), 'NA')

    def test_prettystart_w_start(self):
        import time
        request = self._makeOne()
        request.start = time.mktime((2014, 12, 14, 19, 6, 23, 6, 348, 0))
        self.assertEqual(request.prettystart(), '2014-12-14T19:06:23')

    def test_shortprettystart_na(self):
        request = self._makeOne()
        self.assertEqual(request.shortprettystart(), -1)

    def test_shortprettystart_w_start(self):
        import time
        request = self._makeOne()
        request.start = time.mktime((2014, 12, 14, 19, 6, 23, 6, 348, 0))
        self.assertEqual(request.shortprettystart(), '19:06:23')

    def test_win_na(self):
        request = self._makeOne()
        self.assertEqual(request.win(), -1)

    def test_win_w_start_wo_t_recdinput(self):
        request = self._makeOne()
        request.start = 123
        self.assertEqual(request.win(), -1)

    def test_win_wo_start_w_t_recdinput(self):
        request = self._makeOne()
        request.t_recdinput = 123
        self.assertEqual(request.win(), -1)

    def test_win_w_start_w_t_recdinput(self):
        request = self._makeOne()
        request.start = 123
        request.t_recdinput = 234
        self.assertEqual(request.win(), 111)

    def test_wout_na(self):
        request = self._makeOne()
        self.assertEqual(request.wout(), -1)

    def test_wout_w_t_recdinput_wo_t_recdoutput(self):
        request = self._makeOne()
        request.t_recdinput = 123
        self.assertEqual(request.wout(), -1)

    def test_wout_wo_t_recdinput_w_t_recdoutput(self):
        request = self._makeOne()
        request.t_recdoutput = 123
        self.assertEqual(request.wout(), -1)

    def test_wout_w_t_recdinput_w_t_recdoutput(self):
        request = self._makeOne()
        request.t_recdinput = 234
        request.t_recdoutput = 345
        self.assertEqual(request.wout(), 111)

    def test_wend_na(self):
        request = self._makeOne()
        self.assertEqual(request.wend(), -1)

    def test_wend_w_t_recdoutput_wo_t_end(self):
        request = self._makeOne()
        request.t_recdoutput = 123
        self.assertEqual(request.wend(), -1)

    def test_wend_wo_t_recdoutput_w_t_end(self):
        request = self._makeOne()
        request.t_end = 123
        self.assertEqual(request.wend(), -1)

    def test_wend_w_t_recdoutput_w_t_end(self):
        request = self._makeOne()
        request.t_recdoutput = 345
        request.t_end = 456
        self.assertEqual(request.wend(), 111)

    def test_endstage_na(self):
        request = self._makeOne()
        self.assertEqual(request.endstage(), "B")

    def test_endstage_w_t_recdinput(self):
        request = self._makeOne()
        request.t_recdinput = 123
        self.assertEqual(request.endstage(), "I")

    def test_endstage_w_t_recdoutput(self):
        request = self._makeOne()
        request.t_recdoutput = 345
        self.assertEqual(request.endstage(), "A")

    def test_endstage_w_t_end(self):
        request = self._makeOne()
        request.t_end = 456
        self.assertEqual(request.endstage(), "E")

    def test_total_na(self):
        request = self._makeOne()
        self.assertEqual(request.total(), 0)

    def test_total_w_t_recdinput(self):
        request = self._makeOne()
        request.start = 123
        request.t_recdinput = 234
        self.assertEqual(request.total(), 111)

    def test_total_w_t_recdoutput(self):
        request = self._makeOne()
        request.start = 123
        request.t_recdoutput = 345
        self.assertEqual(request.total(), 222)

    def test_total_w_t_end(self):
        request = self._makeOne()
        request.start = 123
        request.t_end = 456
        request.elapsed = 333
        self.assertEqual(request.total(), 333)

    def test_prettyisize_na(self):
        request = self._makeOne()
        request.isize = None
        self.assertEqual(request.prettyisize(), -1)

    def test_prettyisize_w_isize(self):
        request = self._makeOne()
        request.isize = 123
        self.assertEqual(request.prettyisize(), 123)

    def test_prettyosize_na(self):
        request = self._makeOne()
        self.assertEqual(request.prettyosize(), -1)

    def test_prettyosize_w_osize(self):
        request = self._makeOne()
        request.osize = 123
        self.assertEqual(request.prettyosize(), 123)

    def test_prettyhttpcode_na(self):
        request = self._makeOne()
        self.assertEqual(request.prettyhttpcode(), "NA")

    def test_prettyhttpcode_w_httpcode(self):
        request = self._makeOne()
        request.httpcode = "200"
        self.assertEqual(request.prettyhttpcode(), "200")


class CumulativeTests(unittest.TestCase):

    def _getTargetClass(self):
        from ..requestprofiler import Cumulative
        return Cumulative

    def _makeOne(self, url):
        return self._getTargetClass()(url)

    def test_ctor_defaults(self):
        cumulative = self._makeOne('/path/info')
        self.assertEqual(cumulative.url, '/path/info')
        self.assertEqual(cumulative.times, [])
        self.assertEqual(cumulative.hangs, 0)
        self.assertEqual(cumulative.hits(), 0)
        self.assertEqual(cumulative.max(), 0)
        self.assertEqual(cumulative.min(), 0)
        self.assertEqual(cumulative.mean(), 0)
        self.assertEqual(cumulative.median(), 0)
        self.assertEqual(cumulative.total(), 0)

    def test_put_request_wo_elapsed(self):
        class Request(object):
            elapsed = None
        cumulative = self._makeOne('/path/info')
        cumulative.put(Request())
        self.assertEqual(cumulative.hangs, 1)
        self.assertEqual(cumulative.times, [])
        self.assertEqual(cumulative.all(), [])
        self.assertEqual(cumulative.hits(), 0)
        self.assertEqual(cumulative.max(), 0)
        self.assertEqual(cumulative.min(), 0)
        self.assertEqual(cumulative.mean(), 0)
        self.assertEqual(cumulative.median(), 0)
        self.assertEqual(cumulative.total(), 0)

    def test_put_request_w_elapsed(self):
        class Request(object):
            def __init__(self, elapsed):
                self.elapsed = elapsed
        cumulative = self._makeOne('/path/info')
        cumulative.put(Request(234))
        cumulative.put(Request(123))
        self.assertEqual(cumulative.hangs, 0)
        self.assertEqual(cumulative.times, [234, 123])
        self.assertEqual(cumulative.all(), [123, 234])
        self.assertEqual(cumulative.hits(), 2)
        self.assertEqual(cumulative.max(), 234)
        self.assertEqual(cumulative.min(), 123)
        self.assertEqual(cumulative.mean(), float(123+234)/2)
        self.assertEqual(cumulative.median(), float(123+234)/2)
        self.assertEqual(cumulative.total(), float(123 + 234))

    def test_median_one(self):
        cumulative = self._makeOne('/path/info')
        cumulative.times = [14]
        self.assertEqual(cumulative.median(), 14)

    def test_median_odd(self):
        cumulative = self._makeOne('/path/info')
        cumulative.times = [1, 21, 14]
        self.assertEqual(cumulative.median(), 14)

    def test_median_odd_w_dupes(self):
        cumulative = self._makeOne('/path/info')
        cumulative.times = [1, 21, 14, 21, 7]
        self.assertEqual(cumulative.median(), 14)


class Test_parselogline(unittest.TestCase):

    def _callFUT(self, line):
        from ..requestprofiler import parselogline
        return parselogline(line)

    def test_w_empty(self):
        self.assertEqual(self._callFUT(''), None)

    def test_w_one(self):
        self.assertEqual(self._callFUT('a'), None)

    def test_w_two(self):
        self.assertEqual(self._callFUT('a b'), None)

    def test_w_three(self):
        self.assertEqual(self._callFUT('a b c'), None)

    def test_w_four(self):
        self.assertEqual(self._callFUT('a b c d'), ['a', 'b', 'c', 'd', ''])

    def test_w_five(self):
        self.assertEqual(self._callFUT('a b c d e'), ['a', 'b', 'c', 'd', 'e'])

    def test_w_six(self):
        self.assertEqual(self._callFUT('a b c d e f'),
                         ['a', 'b', 'c', 'd', 'e f'])

    def test_w_seven(self):
        self.assertEqual(self._callFUT('a b c d e f g'),
                         ['a', 'b', 'c', 'd', 'e f g'])


class Test_get_earliest_file_data(unittest.TestCase):

    def _callFUT(self, files):
        from ..requestprofiler import get_earliest_file_data
        return get_earliest_file_data(files)

    def test_w_empty_list(self):
        self.assertEqual(self._callFUT([]), None)

    def test_w_single_but_empty_file(self):
        from io import StringIO
        self.assertEqual(self._callFUT([StringIO()]), None)

    def test_w_single_but_bogus_file(self):
        from io import StringIO
        from ..._compat import TEXT
        BOGUS = TEXT('BOGUS 1\nBOGUS 2')
        self.assertEqual(self._callFUT([StringIO(BOGUS)]), None)

    def test_w_single_valid_file(self):
        from io import StringIO
        from ..._compat import TEXT
        VALID = TEXT('CODE PID ID 123.45 DESC')
        buf = StringIO(VALID)
        code, pid, id_, fromepoch, desc = self._callFUT([buf])
        self.assertEqual(code, TEXT('CODE'))
        self.assertEqual(pid, TEXT('PID'))
        self.assertEqual(id_, TEXT('ID'))
        self.assertEqual(fromepoch, 123.45)
        self.assertEqual(desc, TEXT('DESC'))
        self.assertEqual(buf.tell(), len(VALID))

    def test_w_multiple_files(self):
        from io import StringIO
        from ..._compat import TEXT
        VALID1 = TEXT('CODE1 PID1 ID1 234.56 DESC1\n'
                      'CODE3 PID3 ID3 345.67 DESC3\n'
                     )
        buf1 = StringIO(VALID1)
        VALID2 = TEXT('CODE2 PID2 ID2 123.45 DESC2')
        buf2 = StringIO(VALID2)
        code, pid, id_, fromepoch, desc = self._callFUT([buf1, buf2])
        self.assertEqual(code, TEXT('CODE2'))
        self.assertEqual(pid, TEXT('PID2'))
        self.assertEqual(id_, TEXT('ID2'))
        self.assertEqual(fromepoch, 123.45)
        self.assertEqual(desc, TEXT('DESC2'))
        # selected line is consumed, others are pushed back
        self.assertEqual(buf1.tell(), 0)
        self.assertEqual(buf2.tell(), len(VALID2))


class Test_get_requests(unittest.TestCase):

    def _callFUT(self, files, *args, **kw):
        from ..requestprofiler import get_requests
        return get_requests(files, *args, **kw)

    def test_wo_readstats_w_empty_files_list(self):
        self.assertEqual(self._callFUT([]), [])

    def test_wo_readstats_w_valid_file_start_after(self):
        from io import StringIO
        from ..._compat import TEXT
        VALID = TEXT('CODE PID ID 123.45 DESC')
        buf = StringIO(VALID)
        self.assertEqual(self._callFUT([buf], start=234.56), [])

    def test_wo_readstats_w_valid_file_end_before(self):
        from io import StringIO
        from ..._compat import TEXT
        VALID = TEXT('CODE PID ID 234.56 DESC')
        buf = StringIO(VALID)
        self.assertEqual(self._callFUT([buf], end=123.45), [])
