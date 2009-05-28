import pdb
import sys
import paste.httpexceptions

# stolen partly from z3c.evalexception
def PostMortemDebug(application, *ignore_exc):
    """Middleware that catches exceptions and invokes pdb's
    post-mortem debugging facility."""
    def middleware(environ, start_response):
        try:
            return application(environ, start_response)
        except ignore_exc:
            raise
        except:
            pdb.post_mortem(sys.exc_info()[2])
            raise

    return middleware

def make_middleware(app, global_conf, ignore_http_exceptions=True):
    if ignore_http_exceptions:
        return PostMortemDebug(app, paste.httpexceptions.HTTPException)
    return PostMortemDebug(app)
    

