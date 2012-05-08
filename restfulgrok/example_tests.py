from unittest import TestCase

from example import ExampleRestViewMixin
from mock import MockResponse
from mock import MockRequest
from mock import MockContext


class MockExampleRestMixin(ExampleRestViewMixin):
    def __init__(self, parentnode, id, method='GET', body=''):
        self.response = MockResponse()
        self.request = MockRequest(method, body=body)
        self.context = MockContext(parentnode, id)

class TestExampleRestMixin(TestCase):
    def test_get(self):
        result = MockExampleRestMixin(None, '10', 'GET').handle()
        self.assertEquals(result, {'hello': 'world'})

    def test_post(self):
        import json
        data = {'a': 'test'}
        result = MockExampleRestMixin(None, '10', 'POST', body=json.dumps(data)).handle()
        self.assertEquals(result, {'a': 'test'})


if __name__ == '__main__':
    import unittest
    unittest.main()
