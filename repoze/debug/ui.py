"""GUI for presenting ways to look at the repoze.debug data

"""

from webob import Request, Response
import mimetypes
from webob import exc
import os

_HERE = os.path.abspath(os.path.dirname(__file__))
gui_flag = '__repoze.debug'

def is_gui_url(environ):
    return gui_flag in environ.get('PATH_INFO', '')

def get_mimetype(filename):
    type, encoding = mimetypes.guess_type(filename)
    # We'll ignore encoding, even though we shouldn't really
    return type or 'application/octet-stream'


class FakeLogger(object):
    
    def getEntries(self):

        data = [
            {'id': '20323', 'title': 'My Entry'},
            {'id': '32736', 'title': 'Second Entry'},
            ]

        return data


class DebugGui(object):

    def __init__(self, logger):
        self.logger = logger
        self.static_dir = os.path.join(_HERE, 'static')

    def __call__(self, environ, start_response):
        """Pick apart this debug URL and return the correct response"""

        # Make WebOb versions of request and response
        req = Request(environ)

        try:
            # Process the request
            if req.url.find(gui_flag + "/static/") > -1:
                resp = self.getStatic(req)
            elif req.url.find(gui_flag + "feed.xml"):
                resp = self.getFeed(req)
        except ValueError, e:
            resp = exc.HTTPBadRequest(str(e))
        except exc.HTTPException, e:
            resp = e
        except:
            import traceback
            print traceback.format_exc()

        return resp(environ, start_response)

    def getStatic(self, req):

        fn = req.url.split("/")[-1]
        filename = os.path.join(self.static_dir, fn)
        res = Response(content_type=get_mimetype(filename))
        res.body = open(filename, 'rb').read()

        return res

    def getFeed(self, req):
        """Get XML representing information in the logger"""

        logger = FakeLogger()
        entries = logger.getEntries()

        feedfmt = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

  <title>Example Feed</title>
  <link href="http://example.org/"/>
  <updated>2003-12-13T18:30:02Z</updated>
  <author>
    <name>John Doe</name>
  </author>
  <id>urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6</id>
  %s
</feed>
"""

        entryfmt = """  <entry>
    <id>urn:uuid:%s</id>
    <title>%s</title>
    <link href="http://example.org/2003/12/13/atom03"/>
    <updated>2003-12-13T18:30:02Z</updated>
    <summary>Some text.</summary>
  </entry>
"""

        entriesstr = ''
        for e in entries:
            entriesstr = entriesstr + entryfmt % (e['id'], e['title'])

        body = feedfmt % entriesstr
        content_type = "application/atom+xml"
        resp = Response(
            content_type=content_type,
            body=body)

        return resp
