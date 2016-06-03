Changelog
=========

1.1 (2016-06-03)
----------------

- PR #8:  Tolerate empty value for ``Content-Length`` header.

- PR #7:  Suppress ``UnicodeDecodeError`` when query strings contain non
  ASCII characters..

- PR #5:  Avoid breaking when ``wsgi.input`` has no ``seek()`` method.

- Add support for testing under Travis.

- Drop support for Python 2.6, 3.2.

- Add support for Python 3.4, 3,5, and PyPy3.

1.0.2 (2013-07-02)
------------------

- Fix reponse logger handling of WSGI app_iter-as-bytes under Py3k.

1.0.1 (2013-05-17)
------------------

- Work around URLs which contain invalid (unquoted) characters.

- Restored 100% unit test coverage.

1.0 (2013-04-09)
----------------

- Added support for recording, logging and displaying the request body
  (thanks to Andreas Motl for the patch).

1.0b1 (2013-01-30)
------------------

- Add support for bulding docs and testing doctest snippets under ``tox``.

- Add ``setup.py docs`` alias (installs Sphinx).

- Add support for Python 3.2 / 3.3.

- Drop support for Python 2.4 / 2.5.

- Some typo fixes and enhancements to xsl stylesheet

0.7.3 (2012-03-29)
------------------

- This release is the last which will maintain support for Python 2.4 /
  Python 2.5.

- Added support for continuous integration using ``tox`` and ``jenkins``.

- Added 'setup.py dev' alias (runs ``setup.py develop`` plus installs
  ``nose`` and ``coverage``).

0.7.2 (2011-04-18)
------------------

- Don't require 'threadframe' module in Python >= 2.5 (thanks, Jonathan
  Ballet).  Closes http://bugs.repoze.org/issue162.

- Don't crash if unicode values are present in threads' state (thanks,
  Jonathan Ballet).  Closes http://bugs.repoze.org/issue162.

0.7.1 (2010-03-11)
------------------

- Sphinxified docs.

- Don't compute tracelog records unless we are going to write them.


0.7 (2009/09/06)
----------------

- The iterator returned by an application was closed too soon when
  using the responselogger middleware, resulting in, e.g. errors from
  paste.fileapp complaining about "file already closed".

- If the ``keep`` parameter in the "responselogger" middleware is set
  to zero, no entries are logged (not even one, as previously may have
  happened).

- Better test coverage.

- Ignore HTTP errors in post-mortem debug middleware. The exceptions
  we want to catch here are application-level. A configuration option
  has been added to keep the old behavior.

- Added middleware "threads" to debug threads (based on an adaptation
  of Florent Guillaume's "DeadlockDebugger" product for Zope 2).

0.6.2 (2008/07/03)
------------------

- Show a "short" URL in the debug UI.

0.6.1 (2008/07/03)
------------------

- Fix debug UI bug: show escaped body regardless of content-type.

0.6 (2008/07/02)
----------------

- Fix logging bug.  Symptom: AttributeError: 'NoneType' object has no
  attribute 'info'

0.5 (2008/06/30)
----------------

- Make debug request id reflect approximate UNIX time rather than a
  random debug id.

- Deal with responses via a generator; don't unwind response bodies
  into memory.

- Default max_bodysize is now 3K rather than the entire response
  body.

- User interface; keep entries around to show in GUI.  See
  /__repoze.debug/static/debugui.html.

- We now write two logs: a verbose log, and a trace log.  The verbose
  log contains information about headers, request information,
  response bodies, etc.  The trace log is more compact and is written
  in essence to be parsed by a tool.

- The 'filename' option in Paste config is now 'verbose_log'.

- Port Zope's 'requestprofiler' script to WSGI.  Invoke via
  'wsgirequestprofiler' to see help; operates against 'trace' log.

0.4 (2008/06/25)
----------------

- Add pdbpm middleware for dropping into the post-mortem debugger upon
  an exception (copied from repoze.errorlog).

0.3 (2008/06/25)
----------------

- Add 'canary' middleware for detecting environment dictionary leaks.
  Add to your Paste config via 'egg:repoze.debug#canary'; it takes no
  arguments.  If refcounts to repoze.debug.canary.Canary grow without
  bound, you know you are leaking WSGI environment dictionaries.

- Add source url to response logging.

0.2 (2008/06/14)
----------------

- Add warning if content-length != body length.

0.1 (2008/06/13)
----------------

- Initial release.

