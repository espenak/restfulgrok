import json
import yaml
import negotiator


class ContentTypeError(Exception):
    """
    Superclass for :class:`.ContentType` errors.
    """

class ContentTypeLoadError(ContentTypeError):
    """
    Raised when :meth:`ContentType.loads` fails.
    """

class ContentTypeDumpError(ContentTypeError):
    """
    Raised when :meth:`ContentType.dumps` fails.
    """



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
    def dumps(cls, pydata, view):
        """
        Dump ``pydata`` to a string and return the string.

        :param pydata: The python data to encode.
        :param view: A :class:`GrokRestViewMixin` instance.
        """
        return pydata

    @classmethod
    def loads(cls, rawdata, view):
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
    def dumps(cls, pydata, view=None):
        try:
            return json.dumps(pydata, indent=2)
        except TypeError, e:
            raise ContentTypeDumpError(str(e))
        except ValueError, e:
            raise ContentTypeDumpError(str(e))

    @classmethod
    def loads(cls, rawdata, view=None):
        try:
            return json.loads(rawdata)
        except TypeError, e:
            raise ContentTypeLoadError(str(e))
        except ValueError, e:
            raise ContentTypeDumpError(str(e))

class YamlContentType(ContentType):
    """
    YAML content type. Implements both loads and dumps.
    """
    mimetype = 'application/x-yaml'
    extension = 'yaml'
    description = yaml_description

    @classmethod
    def dumps(cls, pydata, view=None):
        try:
            return yaml.safe_dump(pydata, default_flow_style=False)
        except yaml.YAMLError, e:
            raise ContentTypeDumpError(str(e))

    @classmethod
    def loads(cls, rawdata, view=None):
        try:
            return yaml.safe_load(rawdata)
        except yaml.YAMLError, e:
            raise ContentTypeLoadError(str(e))


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

    def get_mimetypelist(self):
        return self._registry.keys()

    def negotiate_accept_header(self, acceptheader):
        """
        Parse the HTTP accept header and find any acceptable mimetypes from the
        registry.

        :return: An acceptable mimetype, or ``None`` if no acceptable mimetype is found.
        :rtype: str
        """
        acceptable = []
        for content_type in self._registry.itervalues():
            acceptable.append(negotiator.AcceptParameters(negotiator.ContentType(content_type.mimetype)))
        cn = negotiator.ContentNegotiator(acceptable=acceptable)
        result = cn.negotiate(acceptheader)
        if result:
            return result.content_type.mimetype()
        else:
            return None
