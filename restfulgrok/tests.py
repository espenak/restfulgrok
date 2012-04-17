import json
from unittest import TestCase

from mock import MockRequest
from mock import MockRestView


class MockRestViewAllImpl(MockRestView):
    def handle_get(self):
        return 'GET called'
    def handle_post(self):
        return 'POST called'
    def handle_put(self):
        return 'PUT called'
    def handle_delete(self):
        return 'DELETE called'


class TestRestFramework(TestCase):
    def test_handle_unsupported(self):
        for method in ('GET', 'POST', 'PUT', 'DELELTE', 'OPTIONS', 'HEAD'):
            view = MockRestView(request=MockRequest(method))
            responsedata = view.handle()
            errormsg = 'Method Not Allowed: {0}'.format(method)
            self.assertEquals(view.response.status, (405, errormsg))
            self.assertEquals(responsedata, {'error': errormsg})

    def test_handle_override(self):
        self.assertEquals(MockRestViewAllImpl(request=MockRequest('GET')).handle(), 'GET called')
        self.assertEquals(MockRestViewAllImpl(request=MockRequest('POST')).handle(), 'POST called')
        self.assertEquals(MockRestViewAllImpl(request=MockRequest('PUT')).handle(), 'PUT called')
        self.assertEquals(MockRestViewAllImpl(request=MockRequest('DELETE')).handle(), 'DELETE called')

    def test_get_requestdata(self):
        pydata = {'hello': 'world'}
        rawdata = json.dumps({'hello': 'world'})
        self.assertEquals(MockRestView(request=MockRequest(body=rawdata)).get_requestdata(),
                          pydata)

    def test_get_requestdata_dict(self):
        pydata = {'hello': 'world'}
        rawdata = json.dumps({'hello': 'world'})
        self.assertEquals(MockRestView(request=MockRequest(body=rawdata)).get_requestdata_dict(),
                          pydata)
        with self.assertRaises(ValueError):
            MockRestView(request=MockRequest(body=json.dumps(['a', 'b']))).get_requestdata_dict()

    def test_get_requestmethod(self):
        self.assertEquals(MockRestView(request=MockRequest('GET')).get_requestmethod(), 'get')

    def test_response_400_bad_request(self):
        view = MockRestView(request=MockRequest('GET'))
        data = {'hello': 'world'}
        self.assertEquals(view.response_400_bad_request({'hello': 'world'}),
                          data)
        self.assertEquals(view.response.status, (400, 'Bad Request'))

    def test_response_405_method_not_allowed(self):
        view = MockRestView(request=MockRequest('GET'))
        self.assertEquals(view.response_405_method_not_allowed(),
                          {'error': 'Method Not Allowed: GET'})
        self.assertEquals(view.response.status, (405, 'Method Not Allowed: GET'))


if __name__ == '__main__':
    import unittest
    unittest.main()
