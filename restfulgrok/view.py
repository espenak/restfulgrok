from contenttype import YamlContentType
from contenttype import JsonContentType
from contenttype import ContentTypesRegistry
from contenttype import ContentTypeError


class CouldNotDetermineContentType(Exception):
    """
    Raised when :meth:`GrokRestViewMixin.get_content_type` fails to detect a
    supported content-type.
    """
    def __init__(self, querystring_error, acceptheader_error, acceptable_mimetypes):
        self.querystring_error = querystring_error
        self.acceptheader_error = acceptheader_error
        self.acceptable_mimetypes = acceptable_mimetypes

    def __str__(self):
        error = ('{querystring_error}. {acceptheader_error}. '
                 'Acceptable acceptable_mimetypes: '
                 '{acceptable_mimetypes}').format(**self.__dict__)
        return error

    def asdict(self):
        return dict(error=str(self),
                    querystring_error=self.querystring_error,
                    acceptheader_error=self.acceptheader_error,
                    acceptable_mimetypes=self.acceptable_mimetypes)

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


    #: Map of request method to permission.
    #: You should have one (lowercase) key for each request method in
    #: :obj:`.supported_methods`, or a "default" key defining a default
    #: permission.
    permissions = {'get': 'View',
                   'post': 'Add portal content',
                   'put': 'Modify portal content',
                   'default': 'Modify portal content'}

    def authorize(self):
        """
        Called by :meth:`.render` to authorize the user before calling :meth:`.handle`.

        The permissions required for each method is defined in :obj:`permissions`.

        :raise AccessControl.Unauthorized:
            If the current user do not have
            permission to perform the requested method.
        """
        from AccessControl import Unauthorized, getSecurityManager
        method = self.get_requestmethod()
        permission = self.permissions.get(method)
        if not permission:
            permission = self.permissions['default']
        if not getSecurityManager().checkPermission(permission, self):
            raise Unauthorized('Not authorized for: {0} requests. '
                               'Required permission: {1}'.format(method.upper(),
                                                                 permission))

    def render(self):
        """
        Called to render the view. Uses :meth:`handle` to handle all the logic
        and :meth:`encode_output_data` to encode the response from
        :meth:`handle`.
        """
        from AccessControl.unauthorized import Unauthorized
        try:
            try:
                self.authorize()
                responsedata = self.handle()
            except Unauthorized, e:
                self.set_contenttype_header()
                responsedata = self.response_401_unauthorized(str(e))
            except ContentTypeError, e:
                self.set_contenttype_header()
                responsedata = self.response_400_bad_request({'error': str(e)})
            try:
                return self.encode_output_data(responsedata)
            except ContentTypeError, e:
                self.set_contenttype_header('text/plain')
                contenttype = self.get_content_type()
                errormsg = 'COULD NOT ENCODE ERROR MESSAGE AS: {contenttype}.\n\nError\n==================\n\n{e}'.format(**vars())
                return self.response_400_bad_request(errormsg)
        except CouldNotDetermineContentType, e:
            # Note that we need to wrap both because set_contenttype_header
            # uses get_content_type, which can raise CouldNotDetermineContentType.
            return self.create_response(406, 'Not Acceptable', e.asdict())

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
        else:
            querystring_error = 'No acceptable mimetype in QUERY_STRING: {0}'.format(querystring_mimetype)
            if acceptheader:
                mimetype = self.content_types.negotiate_accept_header(acceptheader)
            if not mimetype:
                acceptheader_error = 'No acceptable mimetype in ACCEPT header: {0}'.format(acceptheader)
                raise CouldNotDetermineContentType(querystring_error=querystring_error,
                                                   acceptheader_error=acceptheader_error,
                                                   acceptable_mimetypes=self.content_types.get_mimetypelist())
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

    def set_contenttype_header(self, mimetype=None):
        """
        Set the content type header. Called by :meth:`handle`, and may be overridden.
        """
        mimetype = mimetype or self.get_content_type().mimetype
        self.response.setHeader('Content-Type',
                                '{0}; charset=UTF-8'.format(mimetype))

    def handle(self):
        """
        Takes care of all the logic for :meth:`render`, except that it does not
        :meth:`encode_output_data` the response data, and it does not do
        authorization. This makes this method very suitable for use in tests or
        custom render() implementations.
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

    def response_401_unauthorized(self, error='Unauthorized'):
        """
        Respond with 401 Unauthorized, and ``{'error': 'Unauthorized'}`` as body.
        """
        return self.create_response(401, 'Unauthorized', {'error': error})

    def response_201_created(self, body):
        """
        Run ``self.response.setStatus(201, 'Created')`` and return body.
        """
        return self.create_response(201, 'Created', body)

    def get_requestdata(self):
        """
        Decode the body of the request using :meth:`decode_input_data`, and return the
        decoded data.
        """
        self.request.stdin.seek(0)
        raw_request_body = self.request.stdin.read()
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

        :raise restfulgrok.contenttype.ContentTypeDumpError: If ``pydata`` can not be encoded.
        """
        return self.get_content_type().dumps(pydata, self)

    def decode_input_data(self, rawdata):
        """
        Decode the given ``rawdata``.

        :raise restfulgrok.contenttype.ContentTypeLoadError: If ``rawdata`` can not be decoded.
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
