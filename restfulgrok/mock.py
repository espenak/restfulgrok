from view import GrokRestViewMixin


class MockResponse(object):
    def __init__(self):
        self.headers = []
        self.status = None

    def setHeader(self, header, value):
        self.headers.append((header, value))

    def setStatus(self, code, msg):
        self.status = (code, msg)


class MockRequest(object):
    def __init__(self, method='GET', body=''):
        self.method = method
        self.body = body

    def get(self, key, default=None):
        if key == 'BODY':
            return self.body
        else:
            raise KeyError()


class MockContext(object):
    def __init__(self, parentnode=None, id=None):
        self.bibfolder = parentnode
        self.id = id

    def getParentNode(self):
        return self.parentnode


class MockRestView(GrokRestViewMixin):
    def __init__(self, request=None, response=MockResponse(), context=None):
        self.request = request
        self.response = response
        self.context = context
