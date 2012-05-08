from jinja2 import Template
from pkg_resources import resource_string

from view import GrokRestViewMixin
from contenttype import ContentType, ContentTypesRegistry
from contenttype import JsonContentType



class HtmlContentType(ContentType):
    """
    XHTML content type.
    """
    mimetype = 'text/html'
    extension = 'html'
    description = 'Formatted HTML view with help for the REST API.'

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

    @classmethod
    def get_template_data(cls, pydata, view):
        """
        Get the template data.

        :return: Template data.
        :rtype: dict
        """
        jsondata = JsonContentType.dumps(pydata)
        return dict(jsondata=jsondata,
                    css=cls.get_css_source(),
                    content_types=view.content_types,
                    pagetitle = cls.html_pagetitle)

    @classmethod
    def dumps(cls, pydata, view):
        template = Template(cls.get_template_source())
        return template.render(**cls.get_template_data(pydata, view)).encode('utf-8')



class GrokRestViewWithFancyHtmlMixin(GrokRestViewMixin):
    default_mimetype = 'text/html'
    content_types = GrokRestViewMixin.content_types + ContentTypesRegistry(HtmlContentType)
