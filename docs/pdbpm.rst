:mod:`repoze.debug` pdbpm middleware
====================================

If installed in the WSGI pipeline, the ``pdbpm`` middleware monitors your
application for uncaught exceptions:  when one occurs, it drops your
(foregrounded) server process into the pdb post-mortem debugger to allow
you to debug the error.


Configuration via Python
------------------------

Wire up the middleware in your application:

.. code-block:: python

 from repoze.debug.pdbpm import PostMortemDebug
 middleware = PostMortemDebug(app)


Configuration via Paste
------------------------

Use the 'egg:repoze.debug#pdbpm' entry point in your Paste
configuration, e.g.:

.. code-block:: ini

      [pipeline:main]
      pipeline = egg:Paste#cgitb
                 egg:repoze.debug#pdbpm
                 myapp


Ignored Exceptions
------------------

By default, the ``pdbpm`` middleware ignores exceptions from the
:mod:`paste.httpexceptions` package.  To disable this feature, configure
the middlware using the ``ignore_http_exceptions`` flag (set to ``False``).
