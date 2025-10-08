import json
from importlib import resources
from typing import TextIO

from colander_data_converter.base.models import ColanderFeed
from colander_data_converter.exporters.exporter import BaseExporter
from colander_data_converter.exporters.template import TemplateExporter

resource_package = __name__


class GraphvizExporter(BaseExporter):
    """
    Exporter for generating Graphviz_ DOT format files from Colander data feeds.

    This exporter creates Graphviz-compatible DOT format output that can be used to
    visualize entity relationships and hierarchies. It uses Jinja2_ templates for
    rendering and supports customizable themes for styling the generated graphs.

    The exporter automatically loads a default theme if none is provided, ensuring
    consistent visual output. The theme controls various visual aspects like colors,
    shapes, and styling attributes for different entity types.

    .. _Graphviz: https://graphviz.org/
    .. _Jinja2: https://jinja.palletsprojects.com/
    """

    def __init__(self, feed: ColanderFeed, theme: dict = None):
        """
        Initialize the GraphvizExporter with feed data and optional theme configuration.

        Sets up the exporter with the provided data feed and theme. If no theme is
        provided, loads the default theme from the package resources. Initializes
        the internal :py:class:`~colander_data_converter.exporters.template.TemplateExporter` with the Graphviz_ template.

        Args:
            feed: The data feed containing entities to
                be exported. This feed will be processed and converted to Graphviz DOT format.
            theme: Theme configuration dictionary that controls the
                visual styling of the generated graph. If None, the
                default theme will be loaded automatically.
        """
        self.feed = feed
        self.theme = theme
        if not self.theme:
            self.load_default_theme()
        template_name = "graphviz.jinja2"
        template_source_dir = resources.files(resource_package).joinpath("..").joinpath("data").joinpath("templates")
        self.template_exporter = TemplateExporter(feed, str(template_source_dir), template_name)
        self.feed.resolve_references()

    def load_default_theme(self):
        """
        Load the default theme configuration from the package resources.

        Reads the default theme JSON file from the package's data/themes directory
        and loads it into the theme attribute. This method is automatically called
        during initialization if no custom theme is provided.
        """
        theme_file = (
            resources.files(resource_package)
            .joinpath("..")
            .joinpath("data")
            .joinpath("themes")
            .joinpath("default.json")
        )
        with theme_file.open() as f:
            self.theme = json.load(f)

    def export(self, output: TextIO, **kwargs):
        """
        Export the feed data as Graphviz DOT format to the specified output stream.

        Renders the Colander data feed using the configured Jinja2_ template and theme
        to produce Graphviz_ DOT format output. The theme is passed to the template
        as a context variable, allowing the template to apply consistent styling.

        Args:
            output: A text-based output stream where the DOT format content
                will be written. This can be a file object, StringIO, or
                any object implementing the TextIO interface.
            **kwargs: Additional keyword arguments that will be passed to the underlying
                :py:class:`~colander_data_converter.exporters.template.TemplateExporter`. These can be used to
                provide additional context variables to the Jinja2 template.

        Raises:
            ~jinja2.TemplateError: If there are errors in the template syntax or rendering
            ~jinja2.TemplateNotFound: If the Graphviz template file cannot be found
            IOError: If there are issues writing to the output stream

        Note:
            The generated DOT format can be processed by Graphviz_ tools (dot, neato, etc.)
            to create visual representations in various formats (PNG, SVG, PDF, etc.).
            The theme dictionary is automatically passed to the template as the 'theme'
            variable.
        """
        self.template_exporter.export(output, theme=self.theme)
