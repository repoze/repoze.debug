import time
import threading

from paste.exceptions.errormiddleware import Supplement
from repoze.debug.ui import is_gui_url
from repoze.debug.ui import DebugGui

class ResponseLoggingMiddleware:
    def __init__(self, app, max_bodylen, logger):
        self.application = app
        self.max_bodylen = max_bodylen
        self.logger = logger

    def __call__(self, environ, start_response):
        if is_gui_url(environ):
            gui = DebugGui(self)
            return gui(environ, start_response)

        now = time.time()
        request_id = get_request_id(now)

        debug = environ['repoze.debug'] = {}
        debug['id'] = request_id
        debug['begin'] = now

        self.log_request(environ)

        catch_response = []
        body = []

        def replace_start_response(status, headers, exc_info=None):
            catch_response.append([status, headers])
            start_response(status, headers, exc_info)
            return body.append

        app_iter = self.application(environ, replace_start_response)

        try:
            body.extend(app_iter)
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()

        body = ''.join(body)
        if catch_response:
            status, headers = catch_response[0]
        else:
            status = '500 Start Response Not Called'
            headers = []

        self.log_response(environ, status, headers, body)

        return [body]

    def log_request(self, environ):
        supplement = Supplement(self, environ)
        request_data = supplement.extraData()
        debug = environ['repoze.debug']
        request_id = debug['id']
        out = []
        t = time.ctime()
        out.append('--- REQUEST %s at %s ---' % (request_id, t))
        url = supplement.source_url
        debug['url'] = url
        out.append('URL: %s' % url)
        out.append('CGI Variables')
        items = request_data[('extra', 'CGI Variables')].items()
        items.sort()
        for k, v in items:
            out.append('  %s: %s' % (k, v))
        out.append('WSGI Variables')
        items = request_data[('extra', 'WSGI Variables')].items()
        for k, v in items:
            out.append('  %s: %s' % (k, v))
        out.append('--- end REQUEST %s ---' % request_id)
        self.logger.info('\n'.join(out))

    def log_response(self, environ, status, headers, body):
        debug = environ.get('repoze.debug', {})
        request_id = debug.get('id')
        out = [] 
        t = time.ctime()
        end = time.time()
        start = debug.get('begin')
        if start:
            duration = end - start
        else:
            duration = '??'
        out.append('--- RESPONSE %s at %s (%0.4f seconds) ---' % (
            request_id, t, duration))
        url = debug.get('url', '??')
        out.append('URL: %s' % url)
        out.append('Status: %s' % status)
        out.append('Response Headers')
        cl = None
        for header in headers:
            k, v = header
            if k.lower() == 'content-length':
                try:
                    cl = int(v)
                except (TypeError, ValueError):
                    cl = None
            out.append('  %s: %s' % (k, v))
        bodylen = len(body)
        out.append('Bodylen: %s' % bodylen)
        if cl is not None:
            if bodylen != cl:
                out.append(
                    'WARNING-1: bodylen (%s) != Content-Length '
                    'header value (%s)' % (bodylen, cl))
        out.append('Body:')
        out.append('')
        bodyout = body
        if self.max_bodylen:
            bodyout = body[:self.max_bodylen]
            if len(body) > self.max_bodylen:
                bodyout += ' ... (truncated)'
        out.append(bodyout)
        out.append('--- end RESPONSE %s ---' % request_id)
        self.logger.info('\n'.join(out))
        
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
                    max_bodylen='0KB', # all
                    max_logsize='100MB',
                    backup_count='10',
                    ):
    """ Paste filter-app converter """
    backup_count = int(backup_count)
    max_bytes = byte_size(max_logsize)
    max_bodylen = byte_size(max_bodylen)

    from logging import Logger
    from logging.handlers import RotatingFileHandler

    handler = RotatingFileHandler(filename, maxBytes=max_logsize,
                                  backupCount=backup_count)
    logger = Logger('repoze.debug.responselogger')
    logger.handlers = [handler]
    return ResponseLoggingMiddleware(app, max_bodylen, logger)
