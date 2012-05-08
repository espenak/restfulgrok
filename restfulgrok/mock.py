from view import GrokRestViewMixin
from fancyhtmlview import GrokRestViewWithFancyHtmlMixin


class MockResponse(object):
    def __init__(self):
        self.headers = []
        self.status = None

    def setHeader(self, header, value):
        self.headers.append((header, value))

    def setStatus(self, code, msg):
        self.status = (code, msg)


class MockRequest(object):
    def __init__(self, method='GET', body='', getdata={}):
        self.method = method
        self.body = body
        self.getdata = {'BODY': self.body,
                        'mimetype': 'application/json'}
        self.getdata.update(getdata)

    def get(self, key, default=None):
        return self.getdata.get(key, default)


class MockContext(object):
    def __init__(self, parentnode=None, id=None):
        self.parentnode = parentnode
        self.id = id

    def getParentNode(self):
        return self.parentnode


class MockRestView(GrokRestViewMixin):
    def __init__(self, request=None, response=MockResponse(), context=None):
        self.request = request
        self.response = response
        self.context = context

class MockRestViewWithFancyHtml(GrokRestViewWithFancyHtmlMixin):
    def __init__(self, request=None, response=MockResponse(), context=None):
        self.request = request
        self.response = response
        self.context = context
