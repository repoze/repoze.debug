"""GUI for presenting ways to look at the repoze.debug data

"""

import cgi
import mimetypes
import os
import pprint
import time

from webob import exc
from webob import Request
from webob import Response

_HERE = os.path.abspath(os.path.dirname(__file__))
gui_flag = '__repoze.debug'

def is_gui_url(environ):
    return gui_flag in environ.get('PATH_INFO', '')

def get_mimetype(filename):
    type, encoding = mimetypes.guess_type(filename)
    if type is None and filename.endswith(".xul"):
        return 'application/vnd.mozilla.xul+xml'
    return type or 'application/octet-stream'

class DebugGui(object):

    def __init__(self, middleware):
        self.middleware = middleware
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

        return resp(environ, start_response)

    def getStatic(self, req):

        fn = req.url.split("/")[-1]
        filename = os.path.join(self.static_dir, fn)
        res = Response(content_type=get_mimetype(filename))
        res.body = open(filename, 'rb').read()

        return res

    def _generateFeedTagURI(self, when, pid):
        """ See http//www.taguri.org """
        date = time.strftime('%Y-%m-%d', time.localtime(when))
        pid = self.middleware.pid
        return 'tag:repoze.org,%s:%s' % (date, pid)

    def _generateEntryTagURI(self, entry):
        """ See http//www.taguri.org """
        date = time.strftime('%Y-%m-%d', time.localtime(
            entry['request']['begin']))
        pid = self.middleware.pid
        return 'tag:repoze.org,%s:%s-%s' % (date, entry['id'], pid)

    def getFeed(self, req):
        """Get XML representing information in the middleware"""

        entries_xml = []

        for entry in self.middleware.entries:
            request = entry['request']
            begin = time.localtime(request['begin'])
            entry_id = self._generateEntryTagURI(entry)
            entry_title = '%s %s ' % (request['method'], request['url'])
            entry_xml = entryfmt % {
                'entry_id':entry_id,
                'entry_title':cgi.escape(entry_title),
                'updated':time.strftime('%Y-%m-%dT%H:%M:%SZ', begin),
                'summary':cgi.escape(pprint.pformat(entry)),
                }
            entries_xml.append(entry_xml)

        now = time.time()

        body = feedfmt % {
            'title':'repoze.debug feed for pid %s' % self.middleware.pid,
            'entries':'\n'.join(entries_xml),
            'feed_id':self._generateFeedTagURI(now, self.middleware.pid),
            'updated':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(now)),
            }

        resp = Response(content_type='application/atom+xml', body=body)
        return resp

feedfmt = """\
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

  <title>%(title)s</title>
  <link href="http://example.org/"/>
  <updated>%(updated)s</updated>
  <author>
    <name></name>
  </author>
  <id>%(feed_id)s</id>
  %(entries)s
</feed>
"""

entryfmt = """\
  <entry>
    <id>%(entry_id)s</id>
    <title>%(entry_title)s</title>
    <link href="http://example.org/2003/12/13/atom03"/>
    <updated>%(updated)s</updated>
    <summary>%(summary)s</summary>
  </entry>
"""

