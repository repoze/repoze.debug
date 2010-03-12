:mod:`repoze.debug` canary middleware
=====================================

The ``canary`` middleware is middleware helps figure out if your application
is leaking WSGI environment dictionary objects.

Configuration via Python
------------------------

Wire up the middleware in your application:

.. code-block:: python

 from repoze.debug.canary import CanaryMiddleware
 middleware = CanaryMiddleware(app)

Configuration via Paste
-----------------------

Wire the canary middleware up into your pipeline:

.. code-block:: ini

 [pipeline:main]
 pipeline = egg:Paste#cgitb
            egg:repoze.debug#canary
            myapp

Usage
-----

If refcounts to ``repoze.debug.canary.Canary`` grow without bound, you
know you are leaking WSGI environment dictionaries.  Use e.g. :mod:`Dozer`
to find the reference leaks.
