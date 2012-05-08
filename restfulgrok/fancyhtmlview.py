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

    """
    default_content_type = 'text/html'

    html_listed_contenttypes = {'application/json': json_description,
                                'application/yaml': yaml_description,
                                'text/html': 'The current view.'}

    encoders = GrokRestViewMixin.encoders.copy()
    encoders['text/html'] = 'encode_html'
    decoders = GrokRestViewMixin.decoders.copy()
    decoders['text/html'] = 'decode_null'

    template_file = resource_string(__name__, 'fancyhtmltemplate.jinja.html')
    css = resource_string(__name__, 'bootstrap.min.css')
    html_pagetitle = 'REST API'

    def encode_html(self, pydata):
        self.template_file = resource_string(__name__, 'fancyhtmltemplate.jinja.html') # Comment this in when editing the template to see results on page refresh
        jsondata = self.encode_json(pydata)
        template = Template(self.template_file)
        return template.render(jsondata=jsondata,
                               css=self.css,
                               listed_contenttypes=self.html_listed_contenttypes,
                               pagetitle = self.html_pagetitle
                              ).encode('utf-8')
