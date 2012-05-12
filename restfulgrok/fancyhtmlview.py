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

    #: jinja2 template name
    template_name = 'fancyhtmlview.jinja.html'

    #: The ``jinja2.Environment``
    template_environment = Environment(loader=PackageLoader('restfulgrok', 'templates'))

    @classmethod
    def get_previewdata(cls, pydata):
        """
        Get the data that should be added to the data preview box.

        :return: A string containing the data.
        """
        return JsonContentType.dumps(pydata)

    @classmethod
    def get_template_data(cls, pydata, view):
        """
        Get the template data.

        :return: Template data.
        :rtype: dict
        """
        return dict(previewdata=cls.get_previewdata(pydata),
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
