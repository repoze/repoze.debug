:mod:`repoze.debug` threads middleware
======================================

The ``threads`` middleware, when put into the pipeline, allows you to
visit a ``/debug_threads`` URL, which provides a plaintext report
representing the state of each currently running thread in the
process.  This is useful for debugging deadlocks.  The ``threads``
middleware uses code from the `Deadlock Debugger
<http://www.zope.org/Members/nuxeo/Products/DeadlockDebugger>`_
package by Florent Guillame.

Configuration via Python
------------------------

Wire up the middleware in your application:

.. code-block:: python

 from repoze.debug.threads import MonitoringMiddleware
 middleware = MonitoringMiddleware(app)

Configuration via Paste
------------------------

Use the 'egg:repoze.debug#threads' entry point in your Paste
configuration, e.g.:

.. code-block:: ini

      [pipeline:main]
      pipeline = egg:Paste#cgitb
                 egg:repoze.debug#threads
                 myapp

The middleware accepts no configuration parameters.
