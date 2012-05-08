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


Create a class that inherit from GrokRestViewMixin::

    from restfulgrok import GrokRestViewMixin
    class ExampleRestViewMixin(GrokRestViewMixin):
        def handle_get(self):
            # Return something that can be encoded by JSON and YAML
            return {'hello': 'world'}

        def handle_post(self):
            try:
                # Decode request body as a dict (JSON or YAML)
                request_data = self.get_requestdata_dict()
            except ValueError, e:
                # Did not get a dict
                return self.response_400_bad_request({'error': str(e)})
            else:
                # save to database or something....
                # --- not included in example ---

                # Respond with 201 status and the request_data
                # NOTE: If you just return normally, 200 response status is used
                return self.response_201_created(request_data)

And a ``grok.View``::

    from five import grok
    class ExampleRestView(ExampleRestViewMixin, grok.View):
        grok.context(IMyInterface)
        grok.name('rest')


And a testcase::

    class MockExampleRestMixin(ExampleRestViewMixin):
        def __init__(self, parentnode, id, method='GET', body=''):
            self.response = MockResponse()
            self.request = MockRequest(method, body=body)
            self.context = MockContext(parentnode, id)

    class TestRestFramework(TestCase):
        def test_get(self):
            result = MockExampleRestMixin(None, '10', 'GET').handle()
            self.assertEquals(result, {'hello': 'world'})




API docs
========

.. autoclass:: restfulgrok.view.GrokRestViewMixin
   :members:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

