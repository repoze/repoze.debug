import datetime
import sys
try:
    import thread
except ImportError:                 #pragma NO COVER Python 3.x
    import _thread as thread

import traceback

import webob

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
    
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        request = webob.Request(environ)

        if request.path == '/debug_threads':
            response = webob.Response(request=request)
            response.content_type = 'text/plain'
            t = dump_threads()
            if isinstance(t, unicode):
                response.unicode_body = t
            else:
                response.body = t
        else:
            response = request.get_response(self.app, catch_exc_info=True)
            
        return response(environ, start_response)

def make_middleware(app, global_conf):
    return MonitoringMiddleware(app)
