import thread
import traceback
import time
from cStringIO import StringIO

import threadframe
import webob

def dump_threads():
    """Dump running threads

    Returns a string with the tracebacks.
    """

    frames = threadframe.dict()
    this_thread_id = thread.get_ident()
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    res = ["Threads traceback dump at %s\n" % now]
    for thread_id, frame in frames.iteritems():
        if thread_id == this_thread_id:
            continue

        # Find request in frame
        reqinfo = ''
        f = frame
        while f is not None:
            co = f.f_code

           #reqinfo += '\n\t ' + co.co_name + '\t ' + co.co_filename

            if (co.co_name == 'publish' and
               co.co_filename.endswith('publisher/publish.py')):
                request = f.f_locals.get('request')
                if request is not None:
                    reqinfo += (request.get('REQUEST_METHOD', '') + ' ' +
                               request.get('PATH_INFO', ''))
                    qs = request.get('QUERY_STRING')
                    if qs:
                        reqinfo += '?'+qs
                break
            f = f.f_back
        if reqinfo:
            reqinfo = " (%s)" % reqinfo

        output = StringIO()
        traceback.print_stack(frame, file=output)
        res.append("Thread %s%s:\n%s" %
            (thread_id, reqinfo, output.getvalue()))

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
            response.body = dump_threads()
        else:
            response = request.get_response(self.app, catch_exc_info=True)
            
        return response(environ, start_response)

def make_middleware(app, global_conf):
    return MonitoringMiddleware(app)
