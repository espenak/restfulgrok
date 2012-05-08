.. restfulgrok documentation master file, created by
   sphinx-quickstart on Tue May  8 12:48:01 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to restfulgrok's documentation!
=======================================

``restfulgrok`` provides a very simple RESTful view mixin for
``five.grok.View``. It is not meant to be a full-featured REST library, only a
quick solution for simple REST APIs using ``five.grok.View``.

Features:

- Content negotiation.
- Data conversion (JSON and YAML by default)
- HTTP response helpers for common response types.


Getting started
===============


Create a class that inherit from GrokRestViewMixin:

.. literalinclude:: ../restfulgrok/example.py

And a testcase:

.. literalinclude:: ../restfulgrok/example_tests.py


And finally use the mixin to create a ``grok.View``::

    from five import grok
    class ExampleRestView(ExampleRestViewMixin, grok.View):
        grok.context(IMyInterface)
        grok.name('rest')



API docs
========

views
-----------------
.. autoclass:: restfulgrok.view.GrokRestViewMixin
   :members:


mock
-----------------
Mock classes to simplify testing. See the sourcecode (or the *source* links below).

.. automodule:: restfulgrok.mock
   :members:
   :undoc-members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

