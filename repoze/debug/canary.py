class CanaryMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['repoze.debug.canary'] = Canary()
        return self.app(environ, start_response)

class Canary(object):
    pass

def make_middleware(app, global_conf):
    """ Paste filter-app converter """
    return CanaryMiddleware(app)
