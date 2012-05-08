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
    """

    .. attribute:: template_debug

        If ``True``, reload template on each request. If ``False``, cache the
        template data in the class after first read.

    .. attribute:: template_path

        The ``pkg_resources.resource_string`` args for the template.
        Defaults to::

            ('restfulgrok', 'fancyhtmltemplate.jinja.html')

    .. attribute:: html_pagetitle

        Variable forwarded to the template as ``pagetitle``.
        Defaults to: ``"REST API``.
    """
    default_content_type = 'text/html'

    html_listed_contenttypes = {'application/json': json_description,
                                'application/yaml': yaml_description,
                                'text/html': 'The current view.'}

    encoders = GrokRestViewMixin.encoders.copy()
    encoders['text/html'] = 'encode_html'
    decoders = GrokRestViewMixin.decoders.copy()
    decoders['text/html'] = 'decode_null'

    template_debug = True
    template_path = (__name__, 'fancyhtmltemplate.jinja.html')
    css = resource_string(__name__, 'bootstrap.min.css')
    html_pagetitle = 'REST API'

    @classmethod
    def get_templatedata(cls):
        """
        Load the template from :attr:`template_path`. If :attr:`template_debug`
        is ``False``, cache the results.
        """
        if not cls.template_debug and hasattr(cls, 'template_data'):
            return cls.template_data
        else:
            template_data = resource_string(*cls.template_path)
            if not cls.template_debug:
                cls.template_data = template_data
            return template_data

    def encode_html(self, pydata):
        jsondata = self.encode_json(pydata)
        template = Template(self.__class__.get_templatedata())
        return template.render(jsondata=jsondata,
                               css=self.css,
                               listed_contenttypes=self.html_listed_contenttypes,
                               pagetitle = self.html_pagetitle
                              ).encode('utf-8')
