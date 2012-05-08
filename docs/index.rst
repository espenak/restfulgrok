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

- Content negotiation:
    - Assumes same input and out mimetype (simplifies the implementation)
    - Can be specified in a GET parameter (E.g.: ``?mimetype=application/yaml``)
    - Can be specified use HTTP ACCEPT header.
    - Supports:
        - JSON
        - YAML
        - HTML (read only)
        - ... :ref:`customcontenttype`
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


Documentation
=============

.. toctree::
   :maxdepth: 2

   api
   customcontenttype


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

