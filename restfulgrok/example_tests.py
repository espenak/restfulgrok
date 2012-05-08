from unittest import TestCase
from restfulgrok.mock import MockResponse
from restfulgrok.mock import MockRequest
from restfulgrok.mock import MockContext

from example import ExampleRestViewMixin


class MockExampleRestMixin(ExampleRestViewMixin):
    def __init__(self, method='GET', body=''):
        self.response = MockResponse()
        self.request = MockRequest(method, body=body)
        self.context = MockContext()

class TestExampleRestMixin(TestCase):
    def test_get(self):
        result = MockExampleRestMixin('GET').handle()
        self.assertEquals(result, {'hello': 'world'})

    def test_post(self):
        import json
        data = {'a': 'test'}
        result = MockExampleRestMixin('POST', body=json.dumps(data)).handle()
        self.assertEquals(result, {'a': 'test'})

    def test_put(self):
        import json
        data = {'a': 'test'}
        result = MockExampleRestMixin('PUT', body=json.dumps(data)).handle()
        self.assertEquals(result,
                          {'Updated': 'yes',
                           'result': {'a': 'test',
                                      'last-modified': 'now'}})


if __name__ == '__main__':
    import unittest
    unittest.main()
