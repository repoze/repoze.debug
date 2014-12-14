import datetime
import sys

import traceback

import webob

from repoze.debug._compat import thread
from repoze.debug._compat import TEXT

_NOW = None
def _now():
    if _NOW is not None:
        return _NOW
    return datetime.datetime.now()  #pragma NO COVER

def dump_threads(frames=None,       # testing hook
                 thread_id=None,    #    "     "
                ):
    """Dump running threads

    Returns a string with the tracebacks.
    """
    if frames is None:
        frames = sys._current_frames()
    if thread_id is None:
        thread_id = thread.get_ident()
    res = ["Threads traceback dump at %s\n"
            % _now().strftime("%Y-%m-%d %H:%M:%S")
          ]
    for f_tid, frame in frames.items():
        if f_tid != thread_id: #pragma NO COVER
            res.append("Thread %s:\n%s" %
                (f_tid, traceback.format_stack(frame)))
    frames = None
    res.append("End of dump")
    return '\n'.join(res)

class MonitoringMiddleware(object):
    """The monitoring middleware intercepts requests for the path
    '/debug_threads' and returns a plain-text thread dump."""
    
    _frames = _thread_id = None  # testing hooks

    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        request = webob.Request(environ)

        if request.path == '/debug_threads':
            response = webob.Response(request=request)
            response.content_type = 'text/plain'
            t = dump_threads(self._frames, self._thread_id)
            if isinstance(t, TEXT):  # pragma NO COVER Py3k
                response.text = t
            else:
                response.body = t
        else:
            response = request.get_response(self.app, catch_exc_info=True)
            
        return response(environ, start_response)

def make_middleware(app, global_conf):
    return MonitoringMiddleware(app)
