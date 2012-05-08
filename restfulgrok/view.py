import json
import yaml


class ContentType(object):
    """
    Superclass for all content-types for the :class:`.ContentTypesRegistry`.
    """
    #: The mimetype of this content type. Must be set in subclasses.
    mimetype = None

    #: Extension for files of this type. Must be set in subclasses.
    extension = None

    #: A short description for users of the content-type.
    description = ''

    def __init__(self):
        raise Exception('You can not create instances of ContentType subclasses.')

    @classmethod
    def dumps(self, pydata, view):
        """
        Dump ``pydata`` to a string and return the string.

        :param pydata: The python data to encode.
        :param view: A :class:`GrokRestViewMixin` instance.
        """
        return pydata

    @classmethod
    def loads(self, rawdata, view):
        """
        Load the ``rawdata`` bytestring and return it as a decoded pyton object.

        :param rawdata: The bytestring to decode.
        :param view: A :class:`GrokRestViewMixin` instance.
        """
        return rawdata


json_description = """
Javascript Object Notation, a lightweight data-interchange format with parsers
available for most programming languages. The Python programming language has
<a href="http://docs.python.org/library/json.html">native support</a> for JSON.
Read more on the <a href="http://json.org/">JSON website</a>.
"""

yaml_description = """
YAML Ain't Markup Language, a lightweight and easily human-readable
data-interchange format with parsers available for most programming languages.
Read more on the <a href="http://yaml.org/">YAML website</a>.
"""

class JsonContentType(ContentType):
    """
    JSON content type. Implements both loads and dumps.
    """
    mimetype = 'application/json'
    extension = 'json'
    description = json_description

    @classmethod
    def dumps(self, pydata, view=None):
        return json.dumps(pydata, indent=2)

    @classmethod
    def loads(self, rawdata, view=None):
        return json.loads(rawdata)

class YamlContentType(ContentType):
    """
    YAML content type. Implements both loads and dumps.
    """
    mimetype = 'application/yaml'
    extension = 'yaml'
    description = yaml_description

    @classmethod
    def dumps(self, pydata, view=None):
        try:
            return yaml.safe_dump(pydata, default_flow_style=False)
        except yaml.YAMLError, e:
            raise ValueError(str(e))

    @classmethod
    def loads(self, rawdata, view=None):
        try:
            return yaml.safe_load(rawdata)
        except yaml.YAMLError, e:
            raise ValueError(str(e))


class ContentTypesRegistry(object):
    """
    Registry of :class:`ContentType` objects.
    """
    def __init__(self, *content_types):
        """
        :param content_types:
            List of content types. Added to the registry using :meth:`.add`.
        """
        self._registry = {}
        self.addmany(*content_types)

    def add(self, content_type):
        """
        Add the given ``content_type`` to the registry. They are added indexed
        by their ``mimetype``, so adding multiple content-types with the same
        mimetype will only add the last one.
        """
        self._registry[content_type.mimetype] = content_type

    def addmany(self, *content_types):
        """
        Run :meth:`add` for each item in ``content_types``.
        """
        for content_type in content_types:
            self.add(content_type)

    def __getitem__(self, mimetype):
        """
        Get a :class:`ContentType` by its mimetype.
        """
        return self._registry[mimetype]

    def __contains__(self, mimetype):
        """
        Return ``True`` if a :class:`ContentType` with the given ``mimetype``
        is in the registry.
        """
        return mimetype in self._registry

    def aslist(self):
        """
        Return list of :class:`ContentType`s in the registry.
        """
        return self._registry.values()

    def __add__(self, other):
        """
        Merge ``self`` and ``other`` into a new ContentTypesRegistry, and
        return the new registry.
        """
        registry = ContentTypesRegistry()
        registry.addmany(*self.aslist())
        registry.addmany(*other.aslist())
        return registry

    def __iter__(self):
        """
        Iterate over all the :class:`ContentType`s in the registry.
        """
        return self._registry.itervalues()


class CouldNotDetermineContentType(Exception):
    """
    Raised when :meth:`GrokRestViewMixin.get_content_type` fails to detect a
    supported content-type.
    """

class GrokRestViewMixin(object):
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
        getmimetype = self.request.get('mimetype')
        if getmimetype and getmimetype in self.content_types:
            mimetype = getmimetype
        else:
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
