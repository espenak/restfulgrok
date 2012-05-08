from jinja2 import Template
from pkg_resources import resource_string

from view import GrokRestViewMixin



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


class GrokRestViewWithFancyHtmlMixin(GrokRestViewMixin):
    default_content_type = 'text/html'

    #: Content types listed in...
    html_listed_contenttypes = {'application/json': json_description,
                                'application/yaml': yaml_description,
                                'text/html': 'The current view.'}

    encoders = GrokRestViewMixin.encoders.copy()
    encoders['text/html'] = 'encode_html'

    decoders = GrokRestViewMixin.decoders.copy()
    decoders['text/html'] = 'decode_null'

    #: If ``True``, reload template on each request. If ``False``, cache the
    #: template data in the class after first read.
    template_debug = True

    #: The :func:`pkg_resources.resource_string` args for the template file.
    template_path = (__name__, 'fancyhtmltemplate.jinja.html')

    #: The :func:`pkg_resources.resource_string` args for the css file.
    css_path = (__name__, 'bootstrap.min.css')

    #: Variable forwarded to the template as ``pagetitle``.
    html_pagetitle = 'REST API'

    @classmethod
    def get_cached_file(cls, cacheattr, resource_string_path):
        """
        Get file contents using :func:`pkg_resources.resource_string`. If
        :obj:`.template_debug` is ``False``, cache the data in the
        class attribute ``cacheattr`` and use the cache on subsequent calls.

        :param cacheattr: Attribute to use a cache of the file contents.
        :param resource_string: :func:`pkg_resources.resource_string` path to the file.
        """
        if cls.template_debug:
            return resource_string(*resource_string_path)
        else:
            if not hasattr(cls, cacheattr):
                source = resource_string(*resource_string_path)
                setattr(cls, cacheattr, source)
            return getattr(cls, cacheattr)


    @classmethod
    def get_template_source(cls):
        """
        Use :meth:`.get_cached_file` to get :obj:`.template_path`.
        """
        return cls.get_cached_file('cache_template_source', cls.template_path)

    @classmethod
    def get_css_source(cls):
        """
        Use :meth:`.get_cached_file` to get :obj:`.css_path`.
        """
        return cls.get_cached_file('cache_template_source', cls.css_path)

    def get_template_data(self, pydata):
        """
        Get the template data.

        :return: Template data.
        :rtype: dict
        """
        jsondata = self.encode_json(pydata)
        return dict(jsondata=jsondata,
                    css=self.get_css_source(),
                    listed_contenttypes=self.html_listed_contenttypes,
                    pagetitle = self.html_pagetitle)

    def encode_html(self, pydata):
        """
        Encode as text/html.
        """
        template = Template(self.__class__.get_template_source())
        return template.render(**self.get_template_data(pydata)).encode('utf-8')
