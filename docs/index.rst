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


Extending and styling the HtmlContentType view
==============================================
The html provided with :class:`restfulgrok.fancyhtmlview.HtmlContentType` does
not have a stylesheet, however it is designed to work with `Bootstrap
<http://twitter.github.com/bootstrap/>`_. Just override the template,
and override the ``head_extra`` block. For example:

1. Create your own html content type (example assumes your app is ``my.package``)::

    from jinja2 import Environment, PrefixLoader, PackageLoader
    class MyHtmlContentType(HtmlContentType):
        template_name = 'fancyhtmlview.jinja.html'
        template_environment = Environment(loader = PrefixLoader({
            'restfulgrok': PackageLoader('restfulgrok'),
            'mypackage': PackageLoader('my.package')
        }))

2. Create ``my/package/templates`` and ``my/package/staticfiles``.
3. Add static directory to ``configure.zcml``::

    <browser:resourceDirectory
        name="my.package"
        directory="staticfiles"
        />

4. Create your own template, ``my/package/templates/view.jinja.html``,
   extending the one from ``restfulgrok``::

    {% extends "restfulgrok/fancyhtmlview.jinja.html" %}
    {% block head_extra %}
        <link rel="stylesheet/less" href="++resource++my.package/bootstrap/less/bootstrap.less">
        <script src="++resource++my.package/less-1.3.0.min.js"></script>
    {% endblock %}



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

