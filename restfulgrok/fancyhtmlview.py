from jinja2 import Environment, PackageLoader

from view import GrokRestViewMixin
from contenttype import ContentType, ContentTypesRegistry
from contenttype import JsonContentType



class HtmlContentType(ContentType):
    """
    XHTML content type. Provides a dumps-method that uses a jinja2-template
    to generate a bootrap-styled HTML-document which is suitable as
    a default view for a REST API.
    """
    mimetype = 'text/html'
    extension = 'html'
    description = 'Formatted HTML view with help for the REST API.'

    #: Variable forwarded to the template as ``title``.
    html_title = 'REST API'

    #: Variable forwarded to the template as ``brandingtitle``.
    html_brandingtitle = html_title

    #: Variable forwarded to the template as ``heading``.
    html_heading = html_title

    #: Max number of items to show in the data-preview, if the pydata is a list
    datalist_maxitems = 5

    #: jinja2 template name
    template_name = 'fancyhtmlview.jinja.html'

    #: The ``jinja2.Environment``
    template_environment = Environment(loader=PackageLoader('restfulgrok', 'templates'))

    @classmethod
    def get_template_data(cls, pydata, view):
        """
        Get the template data.

        :return: Template data.
        :rtype: dict
        """
        def to_json(data):
            return JsonContentType.dumps(data)

        if isinstance(pydata, list) and len(pydata) > cls.datalist_maxitems:
            pydatalen = len(pydata)
            pydata = pydata[:cls.datalist_maxitems]
            jsondata = to_json(pydata)
            jsondata = jsondata.strip().rstrip(']')
            jsondata += ('\n  // ... only showing the first {0}. There are {1} '
                         'in total.\n]').format(cls.datalist_maxitems,
                                                pydatalen)
        else:
            jsondata = to_json(pydata)
        return dict(jsondata=jsondata,
                    content_types=view.content_types,
                    title=cls.html_title,
                    brandingtitle=cls.html_brandingtitle,
                    heading=cls.html_heading)

    @classmethod
    def dumps(cls, pydata, view):
        template = cls.template_environment.get_template(cls.template_name)
        return template.render(**cls.get_template_data(pydata, view)).encode('utf-8')



class GrokRestViewWithFancyHtmlMixin(GrokRestViewMixin):
    """
    Adds :class:`HtmlContentType` to ``content_types``.
    """
    content_types = GrokRestViewMixin.content_types + ContentTypesRegistry(HtmlContentType)
