import os
from typing import TextIO, Sequence

from jinja2 import FileSystemLoader, Template
from jinja2.sandbox import SandboxedEnvironment

from colander_data_converter.base.models import ColanderFeed
from colander_data_converter.exporters.exporter import BaseExporter


class TemplateExporter(BaseExporter):
    """
    Template-based exporter using Jinja2_ templating engine.

    This exporter allows for flexible data export by using Jinja2_ templates to format
    the output. It supports both file-based templates loaded from the filesystem and
    pre-compiled :py:obj:`~jinja2.Template` object. The implementation uses a sandboxed environment
    for security when processing templates.

    The exporter streams the template output, making it memory-efficient for large
    datasets by processing data in chunks rather than loading everything into memory.

    .. _Jinja2: https://jinja.palletsprojects.com/

    """

    def __init__(
        self,
        feed: ColanderFeed,
        template_search_path: str | os.PathLike[str] | Sequence[str | os.PathLike[str]],
        template_name: str,
        template_source: str = None,
        **loader_options,
    ):
        """
        Initialize the TemplateExporter with feed data and template configuration.

        This constructor sets up the Jinja2 templating environment and loads the specified
        template. If a pre-compiled :py:obj:`~jinja2.Template` object is provided, it will be used directly.
        Otherwise, the template will be loaded from the filesystem using the provided
        search path and template name.

        Args:
            feed: The data feed containing entities to
                be exported. This feed will be passed to the template as the :py:obj:`feed` variable.
            template_search_path: Path or sequence of paths where template files are located. Can be a single
                path string, PathLike object, or sequence of paths for multiple search locations.
            template_name: The name of the template file to load from the search path.
                Should include the file extension (e.g., "template.j2", "export.html").
            template_source: The source code of the Jinja2 template. If provided,
                :py:obj:`template_search_path` and :py:obj:`template_name` are ignored. Defaults to None.
            **loader_options: Additional keyword arguments passed to the :py:obj:`~jinja2.FileSystemLoader`.

        Note:
            The exporter uses a :py:obj:`~jinja2.sandbox.SandboxedEnvironment` for security, which restricts
            access to potentially dangerous operations in templates. Auto-reload is
            enabled by default for development convenience.
        """
        self.feed = feed
        self.template_search_path = template_search_path
        self.template_name = template_name
        if template_source:
            self.environment = SandboxedEnvironment()
            self.template = self.environment.from_string(template_source)
        else:
            self.loader = FileSystemLoader(self.template_search_path, **loader_options)
            self.environment = SandboxedEnvironment(loader=self.loader, auto_reload=True)
            self.template: Template = self.environment.get_template(self.template_name)

    def export(self, output: TextIO, **kwargs):
        """
        Export data by rendering the template and writing output to the provided stream.

        This method uses Jinja2's streaming to render the template in chunks,
        making it memory-efficient for large datasets. The feed data is passed to the
        template as the 'feed' variable, and any additional keyword arguments are also
        made available as template variables.

        Args:
            output: A text-based output stream where the rendered template
                will be written. This can be a file object, StringIO,
                or any object implementing the TextIO interface.
            **kwargs: Additional keyword arguments that will be passed as variables
                to the template context. These can be used within the template
                to customize the output or provide additional data.

        Raises:
            ~jinja2.TemplateError: If there are errors in template syntax or rendering
            ~jinja2.TemplateNotFound: If the specified template file cannot be found
            IOError: If there are issues writing to the output stream
        """
        for chunk in self.template.stream(feed=self.feed, **kwargs):
            output.write(chunk)
