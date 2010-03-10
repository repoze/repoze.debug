import itertools
import os
import time
import threading

from paste.exceptions.errormiddleware import Supplement
from paste.response import header_value
from repoze.debug.ui import is_gui_url
from repoze.debug.ui import DebugGui

class ResponseLoggingMiddleware:
    def __init__(self, app, max_bodylen, keep, verbose_logger, trace_logger):
        self.application = app
        self.max_bodylen = max_bodylen
        self.verbose_logger = verbose_logger
        self.trace_logger = trace_logger
        self.keep = keep
        self.entries = []
        self.lock = threading.Lock()
        self.first_request = True
        if hasattr(os, 'getpid'): # pragma: no cover
            self.pid = os.getpid()
        else:
            self.pid = 0 # pragma: no cover

    def __call__(self, environ, start_response):
        now = time.time()

        if is_gui_url(environ):
            gui = DebugGui(self)
            return gui(environ, start_response)

        request_id = id(environ)
        request_info = self.get_request_info(environ)
        request_info['begin'] = now
        self.log_request_begin(request_id, request_info)

        entry = {}
        entry['id'] = request_id
        entry['request'] = request_info

        if self.keep:
            self.lock.acquire()
            try:
                if len(self.entries) >= self.keep:
                    self.entries.pop(0)
                self.entries.append(entry)
            finally:
                self.lock.release()

        catch_response = []
        written = []

        def replace_start_response(status, headers, exc_info=None):
            catch_response.append([status, headers])
            start_response(status, headers, exc_info)
            return written.append

        app_iter = self.application(environ, replace_start_response)
        received_response = time.time()

        if catch_response:
            status, headers = catch_response[0]
        else:
            status = '500 Start Response Not Called'
            headers = []

        response_info = self.get_response_info(status, headers)
        response_info['begin'] = received_response

        entry['response'] = response_info

        close = getattr(app_iter, 'close', None)

        body = itertools.chain(written, app_iter)
        body = self.log_response(request_id, request_info, response_info, body,
                                 close)

        return body

    def get_request_info(self, environ):
        info = {}
        supplement = Supplement(self, environ)
        request_data = supplement.extraData()
        method = environ.get('REQUEST_METHOD', 'GET')
        info['method'] = method
        info['url'] = supplement.source_url
        info['cgi_variables'] = []
        info['wsgi_variables'] = []
        for k, v in sorted(request_data[('extra', 'CGI Variables')].items()):
            info['cgi_variables'].append((k, v))
        for k, v in sorted(request_data[('extra', 'WSGI Variables')].items()):
            if not 'repoze.debug' in k:
                info['wsgi_variables'].append((k, v))
        return info

    def log_request_begin(self, request_id, info):
        out = []
        begin = info['begin']
        t = time.ctime(begin)
        out.append('--- begin REQUEST for %s at %s ---' % (request_id, t))
        method_and_url = '%s %s' % (info['method'], info['url'])
        out.append('URL: %s' % method_and_url)
        out.append('CGI Variables')
        for k, v in info['cgi_variables']:
            out.append('  %s: %s' % (k, v))
        out.append('WSGI Variables')
        for k, v in info['wsgi_variables']:
            out.append('  %s: %s' % (k, v))
        out.append('--- end REQUEST for %s ---' % request_id)
        self.verbose_logger and self.verbose_logger.info('\n'.join(out))
        self.lock.acquire()
        try:
            if self.first_request:
                if self.trace_logger is not None:
                    info = 'U %s %s %s' % (self.pid, request_id, begin)
                    self.trace_logger.info(info)
                self.first_request = False
        finally:
            self.lock.release()
        if self.trace_logger is not None:
            info = 'B %s %s %s %s' % (self.pid, request_id, begin,
                                      method_and_url)
            self.trace_logger.info(info)

    def get_response_info(self, status, headers):
        info = {}
        cl = header_value(headers, 'content-length')
        info['headers'] = list(headers)
        try:
            cl = int(cl)
        except (TypeError, ValueError):
            cl = None
        info['content-length'] = cl
        info['status'] = status
        return info

    def log_response(self, request_id, request_info, response_info, body,close):
        out = []
        begin = response_info['begin']
        t = time.ctime(begin)
        status = response_info['status'].split(' ', 1)[0]
        cl = response_info['content-length']
        if self.trace_logger is not None:
            info = 'A %s %s %s %s %s' % (self.pid, request_id, begin,
                                         status, cl)
            self.trace_logger.info(info)
        out.append('--- begin RESPONSE for %s at %s ---' % (request_id, t))
        out.append('URL: %s %s' % (request_info['method'], request_info['url']))
        out.append('Status: %s' % response_info['status'])
        out.append('Response Headers')
        for k, v in response_info['headers']:
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
            bodyout += ' ... (truncated at %s bytes)' % self.max_bodylen
        out.append('Body:\n' + bodyout)
        out.append('Bodylen: %s' % bodylen)
        if cl is not None:
            if bodylen != cl:
                out.append(
                    'WARNING-1: bodylen (%s) != Content-Length '
                    'header value (%s)' % (bodylen, cl))
        response_info['body'] = bodyout
        end = response_info['end'] = time.time()
        duration = response_info['end'] - request_info['begin']
        out.append('--- end RESPONSE for %s (%0.2f seconds) ---' % (
            request_id, duration))
        self.verbose_logger and self.verbose_logger.info('\n'.join(out))
        if self.trace_logger is not None:
            info = 'E %s %s %s %s' % (self.pid, request_id, end, bodylen)
            self.trace_logger.info(info)
        if close is not None:
            close()

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

def make_middleware(app,
                    global_conf,
                    verbose_log=None,
                    trace_log=None,
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

    if verbose_log:
        handler = RotatingFileHandler(verbose_log, maxBytes=max_logsize,
                                        backupCount=backup_count)
        verbose_log = Logger('repoze.debug.verboselogger')
        verbose_log.handlers = [handler]

    if trace_log:
        handler = RotatingFileHandler(trace_log, maxBytes=max_logsize,
                                        backupCount=backup_count)
        trace_log = Logger('repoze.debug.tracelogger')
        trace_log.handlers = [handler]

    return ResponseLoggingMiddleware(app, max_bodylen, keep, verbose_log,
                                     trace_log)
