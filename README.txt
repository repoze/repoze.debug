repoze.debug README
===================

Middleware which can help with in-production forensic debugging.
Currently the only middleware in this package is the responselogger
middleware, which logs requests and responses to a file for later
perusal.

Installation
------------

Install using setuptools, e.g. (within a virtualenv)::

 $ easy_install repoze.debug


Configuration via Python
------------------------

Wire up the middleware in your application::

 from repoze.debug.responselogger import ResponseLoggingMiddleware
 from logging import getLogger
 middleware = ResponseLoggingMiddleware(
                app,
                max_bodylen='3KB',
                logger=getLogger('foo')
               )

The configuration options are as follows::

 - ``max_bodylen`` should be the size in bytes (optionally followed by
   KB, MB, or GB) of the response body that should be logged.

 - ``logger`` is a PEP 282 logger instance (any).

Configuration via Paste
-----------------------

Wire the middleware into a pipeline in your Paste configuration, for
example::

 [filter:responselogger]
 use = egg:repoze.debug#responselogger
 filename = %(here)s/response.log
 # if max_bodylen is unset or is 0, it means do not limit body logging
 # default is 0
 max_bodylen = 3KB
 # if max_logsize is unset or is 0, it means do not limit logsize; default is
 # 100MB
 max_logsize = 100MB
 # if backup_count is 0, do not rotate the logfile.  Default is 10.
 backup_count = 10

 ...

 [pipeline:main]
 pipeline = egg:Paste#cgitb
            responselogger
            myapp

The middleware will log response data to ``filename``.

Operation
---------

Once the middleware is in the pipeline, it will log requests and
responses to the logger.  An example of the log output for a request
follows::

  --- REQUEST 860724193 at Fri Jun 13 18:40:47 2008 ---
  URL: http://localhost:9971/p_/pl
  CGI Variables
    ACTUAL_SERVER_PROTOCOL: HTTP/1.1
    AUTH_TYPE: Basic
    HTTP_ACCEPT: */*
    HTTP_ACCEPT_ENCODING: gzip, deflate
    HTTP_ACCEPT_LANGUAGE: en-us
    HTTP_CONNECTION: keep-alive
    HTTP_HOST: localhost:9971
    HTTP_REFERER: http://localhost:9971/manage_menu
    HTTP_USER_AGENT: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_2; en-us) AppleWebKit/525.18 (KHTML, like Gecko) Version/3.1.1 Safari/525.18
    PATH_INFO: /p_/pl
    REMOTE_ADDR: 127.0.0.1
    REMOTE_PORT: 51422
    REQUEST_METHOD: GET
    SERVER_NAME: vitaminf-2.local
    SERVER_PORT: 9971
    SERVER_PROTOCOL: HTTP/1.1
    SERVER_SOFTWARE: CherryPy/3.0.2 WSGI Server
  WSGI Variables
    repoze.debug.request_begin: 1213396847.41
    wsgi process: Multithreaded
    repoze.debug.id: 860724193
    application: <paste.httpexceptions.HTTPExceptionHandler object at 0x17a8fd0>
  --- end REQUEST 860724193 ---

Each request is tagged with a (random) identifier.  A response is also
written to the log, and can be matched up to the request that
generated it via the identifier.  Here's an example of a response in
the log::

  --- RESPONSE 860724193 at Fri Jun 13 18:40:47 2008 (0.0083 seconds) ---
  Status: 200 OK
  Response Headers
    Cache-Control: public,max-age=60
    Content-Length: 872
    Content-Type: image/gif
    Last-Modified: Thu, 06 Mar 2008 17:25:30 GMT
  Bodylen: 872
  Body:

  1?9p?:'~?? ?0a???q?J?(I?|;@@???????@?????!?,H? ?H?`?2t???K.LH?`D?
  --- end RESPONSE 860724193 ---

Reporting Bugs / Development Versions
-------------------------------------

Visit http://bugs.repoze.org to report bugs.  Visit
http://svn.repoze.org to download development or tagged versions.
