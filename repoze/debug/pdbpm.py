import pdb
import sys

# stolen partly from z3c.evalexception
def PostMortemDebug(application):
    """Middleware that catches exceptions and invokes pdb's
    post-mortem debugging facility."""
    def middleware(environ, start_response):
        try:
            return application(environ, start_response)
        except:
            pdb.post_mortem(sys.exc_info()[2])
            raise

    return middleware

def make_middleware(app, global_conf):
    return PostMortemDebug(app)

