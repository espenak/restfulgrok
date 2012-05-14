import json
from unittest import TestCase

from mock import MockRequest
from mock import MockRestView
from mock import MockRestViewWithFancyHtml
from contenttype import JsonContentType
from contenttype import YamlContentType
from contenttype import ContentTypesRegistry
from contenttype import ContentTypeLoadError
from contenttype import ContentTypeDumpError


class MockRestViewAllImpl(MockRestView):
    def handle_get(self):
        return {'msg': 'GET called'}
    def handle_post(self):
        return {'msg': 'POST called'}
    def handle_put(self):
        return {'msg': 'PUT called'}
    def handle_delete(self):
        return {'msg': 'DELETE called'}
    def handle_options(self):
        return {'msg': 'OPTIONS called'}
    def handle_head(self):
        return {'msg': 'HEAD called'}


class TestContentType(TestCase):
    def test_json_loads(self):
        jsondata = """{
            "portal_type": "ArticleReference",
            "attributes": {"title": "Updated title"
        }"""
        with self.assertRaises(ContentTypeLoadError):
            JsonContentType.loads(jsondata)

    def test_json_dumps(self):
        from datetime import date
        with self.assertRaises(ContentTypeDumpError):
            JsonContentType.dumps(date(2010, 1, 1))

    def test_yaml_loads(self):
        yamldata = """
{portal_type: ArticleReference
attributes:
    title: Updated title
        """
        with self.assertRaises(ContentTypeLoadError):
            YamlContentType.loads(yamldata)

    def test_yaml_dumps(self):
        class Tst(object):
            pass
        with self.assertRaises(ContentTypeDumpError):
            YamlContentType.dumps(Tst())

class TestGrokRestViewMixin(TestCase):
    def test_handle_unsupported(self):
        for method in ('GET', 'POST', 'PUT', 'DELELTE', 'OPTIONS', 'HEAD'):
            view = MockRestView(request=MockRequest(method))
            responsedata = view.handle()
            errormsg = 'Method Not Allowed: {0}'.format(method)
            self.assertEquals(view.response.status, (405, errormsg))
            self.assertEquals(responsedata, {'error': errormsg})

    def test_handle_override(self):
        self.assertEquals(MockRestViewAllImpl(request=MockRequest('GET')).handle(), {'msg': 'GET called'})
        self.assertEquals(MockRestViewAllImpl(request=MockRequest('POST')).handle(), {'msg': 'POST called'})
        self.assertEquals(MockRestViewAllImpl(request=MockRequest('PUT')).handle(), {'msg': 'PUT called'})
        self.assertEquals(MockRestViewAllImpl(request=MockRequest('DELETE')).handle(), {'msg': 'DELETE called'})
        self.assertEquals(MockRestViewAllImpl(request=MockRequest('OPTIONS')).handle(), {'msg': 'OPTIONS called'})
        self.assertEquals(MockRestViewAllImpl(request=MockRequest('HEAD')).handle(), {'msg': 'HEAD called'})

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

    def test_get_content_type(self):
        self.assertEquals(MockRestView(request=MockRequest('GET', getdata={'mimetype': 'application/json'})).get_content_type(),
                          JsonContentType)
        self.assertEquals(MockRestView(request=MockRequest('GET', getdata={'mimetype': 'application/x-yaml'})).get_content_type(),
                          YamlContentType)

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

    def test_get_yaml(self):
        import yaml
        class View(MockRestView):
            def authorize(self):
                pass # Skip authorization
            def handle_get(self):
                data = self.get_requestdata()
                return data
        yamldata = """---
- a
- - b.1
  - b.2
- c
"""
        result = View(request=MockRequest('GET', yamldata, getdata={'mimetype': 'application/x-yaml'})).render()
        outdata = yaml.safe_load(result)
        self.assertEquals(outdata, ['a', ['b.1', 'b.2'], 'c'])



class TestGrokRestViewWithFancyHtmlMixin(TestCase):
    def test_handle_html(self):
        class View(MockRestViewWithFancyHtml):
            def authorize(self):
                pass # Skip authorization
            def handle_get(self):
                return {'hello': 'world'}
        output = View(request=MockRequest('GET', getdata={'mimetype': 'text/html'})).render()
        self.assertTrue('?mimetype=text/html' in output)


class TestContentTypesRegistry(TestCase):
    def test_negotiate_accept_header(self):
        registry = ContentTypesRegistry(JsonContentType, YamlContentType)
        self.assertEquals(registry.negotiate_accept_header('application/x-yaml,application/json'),
                          'application/x-yaml')
        self.assertEquals(registry.negotiate_accept_header('application/json,application/x-yaml'),
                          'application/json')
        self.assertEquals(registry.negotiate_accept_header('application/x-yaml;q=0.8,application/json'),
                          'application/json')
        self.assertEquals(registry.negotiate_accept_header('application/x-yaml;q=1.0,application/json;q=0.8'),
                          'application/x-yaml')

        # Should match yaml or json (they both match "*/*)
        self.assertTrue(registry.negotiate_accept_header('text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
                        in ('application/json', 'application/x-yaml'))

        self.assertEquals(registry.negotiate_accept_header('application/html'),
                          None)


from example_tests import TestExampleRestMixin

if __name__ == '__main__':
    import unittest
    unittest.main()
