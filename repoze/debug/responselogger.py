import itertools
import time
import threading

from paste.exceptions.errormiddleware import Supplement
from paste.response import header_value
from repoze.debug.ui import is_gui_url
from repoze.debug.ui import DebugGui

class ResponseLoggingMiddleware:
    def __init__(self, app, max_bodylen, logger, keep):
        self.application = app
        self.max_bodylen = max_bodylen
        self.logger = logger
        self.keep = keep
        self.entries = []
        self.lock = threading.Lock()

    def __call__(self, environ, start_response):
        if is_gui_url(environ):
            self.lock.acquire()
            try:
                gui = DebugGui(self)
                return gui(environ, start_response)
            finally:
                self.lock.release()

        self.lock.acquire()
        try:
            if len(self.entries) > self.keep:
                self.entries.pop(0)
        finally:
            self.lock.release()

        now = time.time()
        request_id = get_request_id(now)

        debug = environ['repoze.debug'] = {}
        debug['id'] = request_id
        debug['begin'] = now

        self.log_request(environ)

        catch_response = []
        written = []

        def replace_start_response(status, headers, exc_info=None):
            catch_response.append([status, headers])
            start_response(status, headers, exc_info)
            return written.append

        app_iter = self.application(environ, replace_start_response)
        body = itertools.chain(written, app_iter)

        if catch_response:
            status, headers = catch_response[0]
        else:
            status = '500 Start Response Not Called'
            headers = []

        body = self.log_response(environ, status, headers, body)

        if hasattr(app_iter, 'close'):
            app_iter.close()

        return body

    def _add_request_data(self, environ):
        supplement = Supplement(self, environ)
        request_data = supplement.extraData()
        entry = environ['repoze.debug']
        entry['url'] = supplement.source_url
        entry['cgi_variables'] = []
        entry['wsgi_variables'] = []
        for k, v in sorted(request_data[('extra', 'CGI Variables')].items()):
            entry['cgi_variables'].append((k, v))
        for k, v in sorted(request_data[('extra', 'WSGI Variables')].items()):
            if not 'repoze.debug' in k:
                entry['wsgi_variables'].append((k, v))
        return entry

    def log_request(self, environ):
        entry = self._add_request_data(environ)
        request_id = entry['id']
        out = []
        t = time.ctime()
        out.append('--- REQUEST %s at %s ---' % (request_id, t))
        out.append('URL: %s' % entry['url'])
        out.append('CGI Variables')
        for k, v in entry['cgi_variables']:
            out.append('  %s: %s' % (k, v))
        out.append('WSGI Variables')
        for k, v in entry['wsgi_variables']:
            out.append('  %s: %s' % (k, v))
        out.append('--- end REQUEST %s ---' % request_id)
        self.logger.info('\n'.join(out))

    def _add_response_data(self, environ, status, headers):
        entry = environ.get('repoze.debug', {})
        end = time.time()
        entry['end'] = end
        cl = header_value(headers, 'content-length')
        entry['response_headers'] = list(headers)
        try:
            cl = int(cl)
        except (TypeError, ValueError):
            cl = None
        entry['content-length'] = cl
        entry['status'] = status
        method = environ.get('REQUEST_METHOD', 'GET')
        entry['title'] = '%s %s' % (method, entry.get('url', '??'))
        return entry

    def log_response(self, environ, status, headers, body):
        entry = self._add_response_data(environ, status, headers)
        request_id = entry.get('id')
        out = [] 
        start, end = entry.get('begin'), entry.get('end')
        if start and end:
            duration = end - start
        else:
            duration = '??'
        t = time.asctime(time.localtime(end))
        out.append('--- RESPONSE %s at %s (%0.4f seconds) ---' % (
            request_id, t, duration))
        out.append('URL: %s' % entry.get('url', '??'))
        out.append('Status: %s' % status)
        out.append('Response Headers')
        for k, v in entry['response_headers']:
            out.append('  %s: %s' % (k, v))
        bodyout = ''
        bodylen = 0
        remaining = None
        for chunk in body:
            if self.max_bodylen:
                remaining = max(0, self.max_bodylen - len(bodyout))
            bodyout += chunk[:remaining]
            bodylen += len(chunk)
            yield chunk
        if bodylen > self.max_bodylen:
            bodyout += ' ... (truncated)'
        out.append('Body:\n' + bodyout)
        out.append('Bodylen: %s' % bodylen)
        cl = entry['content-length']
        if cl is not None:
            if bodylen != cl:
                out.append(
                    'WARNING-1: bodylen (%s) != Content-Length '
                    'header value (%s)' % (bodylen, cl))
        out.append('--- end RESPONSE %s ---' % request_id)
        self.logger.info('\n'.join(out))
        self.lock.acquire()
        try:
            self.entries.append(entry)
        finally:
            self.lock.release()
        
class SuffixMultiplier:
    # d is a dictionary of suffixes to integer multipliers.  If no suffixes
    # match, default is the multiplier.  Matches are case insensitive.  Return
    # values are in the fundamental unit.
    def __init__(self, d, default=1):
        self._d = d
        self._default = default
        # all keys must be the same size
        self._keysz = None
        for k in d.keys():
            if self._keysz is None:
                self._keysz = len(k)
            else:
                assert self._keysz == len(k)

    def __call__(self, v):
        v = v.lower()
        for s, m in self._d.items():
            if v[-self._keysz:] == s:
                return int(v[:-self._keysz]) * m
        return int(v) * self._default

byte_size = SuffixMultiplier({'kb': 1024,
                              'mb': 1024*1024,
                              'gb': 1024*1024*1024L,})

_CURRENT_PERIOD = None
_PERIOD_COUNTER = 0

def get_request_id(when, period=.10, max=10000, lock=threading.Lock()):
    """
    We'd like to hand out a request id that is related to UNIX time
    but more unique than low-resolution timers (e.g. Windows) can give
    us.  To do so, we keep around 1/10 of a sec worth of history and
    we keep up to max slots for entries within this period,
    effectively limiting us to max / period items per second.  In the
    default configuration, this means we can hand out 100000 rids per
    second maximum.
    """
    this_period = when - (when % period)
    global _CURRENT_PERIOD
    global _PERIOD_COUNTER
    lock.acquire()
    try:
        if this_period != _CURRENT_PERIOD:
            _CURRENT_PERIOD = this_period
            _PERIOD_COUNTER = 0
        if _PERIOD_COUNTER > max:
            raise ValueError('> %s items within %s period' % (max, period))
        result = when + (_PERIOD_COUNTER / float(max))
        _PERIOD_COUNTER += 1
    finally:
        lock.release()
    return result

def make_middleware(app,
                    global_conf,
                    filename,
                    max_bodylen='3KB',
                    max_logsize='100MB',
                    backup_count='10',
                    keep='100',
                    ):
    """ Paste filter-app converter """
    backup_count = int(backup_count)
    max_bytes = byte_size(max_logsize)
    max_bodylen = byte_size(max_bodylen)
    keep = int(keep)

    from logging import Logger
    from logging.handlers import RotatingFileHandler

    handler = RotatingFileHandler(filename, maxBytes=max_logsize,
                                  backupCount=backup_count)
    logger = Logger('repoze.debug.responselogger')
    logger.handlers = [handler]
    return ResponseLoggingMiddleware(app, max_bodylen, logger, keep)
