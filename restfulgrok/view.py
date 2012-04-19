import json
#from AccessControl.unauthorized import Unauthorized


class GrokRestViewMixin(object):
    """
    .. attribute:: supported_methods

        List of supported HTTP request methods in lowercase.
        Defaults to ``['get', 'post', 'put', 'delete', 'options', 'head']``.
        You do not have to override this to disallow any of
        those request methods since their default ``handle_<method>()``
        implementations responds with *405 Method Not Allowed*. However,
        if you implement other methods, such as TRACE, you need to add them to
        the list.
    """
    supported_methods = ['get', 'post', 'put', 'delete', 'options', 'head']

    def render(self):
        responsedata = self.handle()
        return self.encode(responsedata)

    def handle(self):
        """
        Takes care of all the logic for :meth:`render`, except that it does not
        :meth:`encode` the response data. This makes this method very suitable for
        use in tests or custom render() implementations.
        """
        self.response.setHeader('Content-Type',
                                'application/json; charset=UTF-8')
        if self.get_requestmethod() in self.supported_methods:
            return getattr(self, 'handle_' + self.get_requestmethod())()
        else:
            return self.response_405_method_not_allowed()

    def get_requestmethod(self):
        return self.request.method.lower()

    def error_response(self, status, statusmsg, body):
        self.response.setStatus(status, statusmsg)
        return body

    def response_405_method_not_allowed(self):
        errormsg = 'Method Not Allowed: {0}'.format(self.request.method)
        return self.error_response(405, errormsg, body={'error': errormsg})

    def response_400_bad_request(self, body):
        return self.error_response(400, 'Bad Request', body)

    def handle_get(self):
        return self.response_405_method_not_allowed()
    def handle_post(self):
        return self.response_405_method_not_allowed()
    def handle_put(self):
        return self.response_405_method_not_allowed()
    def handle_delete(self):
        return self.response_405_method_not_allowed()
    def handle_options(self):
        return self.response_405_method_not_allowed()
    def handle_head(self):
        return self.response_405_method_not_allowed()

    def get_requestdata(self):
        """
        Decode the body of the request using :meth:`decode`, and return the
        decoded data.
        """
        raw_request_body = self.request.get('BODY')
        decoded = self.decode(raw_request_body)
        return decoded

    def get_requestdata_dict(self):
        """
        Just like :meth:`get_requestdata`, however, the :exc:`ValueError` is raised
        if the decoded data is not a ``dict``.
        """
        decoded = self.get_requestdata()
        if not isinstance(decoded, dict):
            raise ValueError('Request body must be a dict (mapping of fieldnames to values).')
        return decoded

    def encode(self, pydata):
        """
        Encode the given python datastructure.

        :raise ValueError: If ``pydata`` can not be encoded.
        """
        return json.dumps(pydata, indent=2)

    def decode(self, rawdata):
        """
        Decode the given ``rawdata``.

        :raise ValueError: If ``rawdata`` can not be decoded.
        """
        return json.loads(rawdata)
