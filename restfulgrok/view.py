from contenttype import YamlContentType
from contenttype import JsonContentType
from contenttype import ContentTypesRegistry


class CouldNotDetermineContentType(Exception):
    """
    Raised when :meth:`GrokRestViewMixin.get_content_type` fails to detect a
    supported content-type.
    """

class GrokRestViewMixin(object):
    """
    Mix-in class for ``five.grok.View``.
    """
    #: List of supported HTTP request methods in lowercase.
    #: Defaults to ``['get', 'post', 'put', 'delete', 'options', 'head']``.
    #: You do not have to override this to disallow any of
    #: those request methods since their default ``handle_<method>()``
    #: implementations responds with *405 Method Not Allowed*. However,
    #: if you implement other methods, such as TRACE, you need to add them to
    #: the list.
    supported_methods = ['get', 'post', 'put', 'delete', 'options', 'head']

    #: A :class:`ContentTypesRegistry` object containing all content-types supported by the API.
    content_types = ContentTypesRegistry(JsonContentType, YamlContentType)

    def render(self):
        """
        Called to render the view. Uses :meth:`handle` to handle all the logic
        and :meth:`encode_output_data` to encode the response from
        :meth:`handle`.
        """
        from AccessControl.unauthorized import Unauthorized
        try:
            responsedata = self.handle()
        except Unauthorized:
            return self.response_401_unauthorized()
        return self.encode_output_data(responsedata)

    def get_content_type(self):
        """
        Detect input/output content type.
        """
        if hasattr(self, '_content_type'):
            return self._content_type
        mimetype = None
        querystring_mimetype = self.request.get('mimetype')
        acceptheader = self.request.getHeader('Accept')
        if querystring_mimetype and querystring_mimetype in self.content_types:
            mimetype = querystring_mimetype
        elif acceptheader:
            mimetype = self.content_types.negotiate_accept_header(acceptheader)
        if not mimetype:
            raise CouldNotDetermineContentType()
        content_type = self.content_types[mimetype]
        self._content_type = content_type
        return content_type

    def add_attachment_header(self):
        """
        Adds Content-Disposition header for filedownload if "downloadfile=yes"
        is in the querystring (request.get).
        """
        if self.request.get('downloadfile') == 'true':
            filename = '{0}.{1}'.format(self.context.id, self.get_content_type().extension)
            self.response.setHeader('Content-Disposition', 'attachment; filename={0}'.format(filename))

    def set_contenttype_header(self):
        """
        Set the content type header. Called by :meth:`handle`, and may be overridden.
        """
        self.response.setHeader('Content-Type',
                                '{0}; charset=UTF-8'.format(self.get_content_type().mimetype))

    def handle(self):
        """
        Takes care of all the logic for :meth:`render`, except that it does not
        :meth:`encode_output_data` the response data. This makes this method very suitable for
        use in tests or custom render() implementations.
        """
        self.set_contenttype_header()
        self.add_attachment_header()
        self.response.setStatus(200, 'OK')
        if self.get_requestmethod() in self.supported_methods:
            return getattr(self, 'handle_' + self.get_requestmethod())()
        else:
            return self.response_405_method_not_allowed()

    def get_requestmethod(self):
        """
        Get the request method as lowercase string.
        """
        return self.request.method.lower()

    def create_response(self, status, statusmsg, body):
        """
        Respond with the given ``status`` and ``statusmessage``, with ``body``
        as response body.
        """
        self.response.setStatus(status, statusmsg)
        return body

    def response_405_method_not_allowed(self):
        """
        Respond with 405 Method Not Allowed.
        """
        errormsg = 'Method Not Allowed: {0}'.format(self.request.method)
        return self.create_response(405, errormsg, body={'error': errormsg})

    def response_400_bad_request(self, body):
        """
        Respond with 400 Bad Request, and the ``body`` parameter as response body.
        """
        return self.create_response(400, 'Bad Request', body)

    def response_401_unauthorized(self):
        """
        Respond with 401 Unauthorized, and ``{'error': 'Unauthorized'}`` as body.
        """
        return self.create_response(401, 'Unauthorized', {'error': 'Unauthorized'})

    def response_201_created(self, body):
        """
        Run ``self.response.setStatus(201, 'Created')`` and return body.
        """
        return self.create_response('201', 'Created', body)

    def get_requestdata(self):
        """
        Decode the body of the request using :meth:`decode_input_data`, and return the
        decoded data.
        """
        raw_request_body = self.request.get('BODY', '')
        decoded = self.decode_input_data(raw_request_body)
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

    def encode_output_data(self, pydata):
        """
        Encode the given python datastructure.

        :raise ValueError: If ``pydata`` can not be encoded.
        """
        return self.get_content_type().dumps(pydata, self)

    def decode_input_data(self, rawdata):
        """
        Decode the given ``rawdata``.

        :raise ValueError: If ``rawdata`` can not be decoded.
        """
        return self.get_content_type().loads(rawdata, self)

    def handle_get(self):
        """
        Override in subclasses. Defaults to :meth:`response_405_method_not_allowed`.
        """
        return self.response_405_method_not_allowed()

    def handle_post(self):
        """
        Override in subclasses. Defaults to :meth:`response_405_method_not_allowed`.
        """
        return self.response_405_method_not_allowed()

    def handle_put(self):
        """
        Override in subclasses. Defaults to :meth:`response_405_method_not_allowed`.
        """
        return self.response_405_method_not_allowed()

    def handle_delete(self):
        """
        Override in subclasses. Defaults to :meth:`response_405_method_not_allowed`.
        """
        return self.response_405_method_not_allowed()

    def handle_options(self):
        """
        Override in subclasses. Defaults to :meth:`response_405_method_not_allowed`.
        """
        return self.response_405_method_not_allowed()

    def handle_head(self):
        """
        Override in subclasses. Defaults to :meth:`response_405_method_not_allowed`.
        """
        return self.response_405_method_not_allowed()
