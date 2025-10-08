import json
from importlib import resources
from typing import TextIO

from colander_data_converter.base.models import ColanderFeed
from colander_data_converter.exporters.exporter import BaseExporter
from colander_data_converter.exporters.template import TemplateExporter

resource_package = __name__


class MermaidExporter(BaseExporter):
    """
    Exporter class for generating Mermaid diagrams from Colander feed data.

    This exporter uses Jinja2 templates to transform Colander feed data into
    Mermaid diagram syntax. It supports custom themes and falls back to a
    default theme if none is provided.
    """

    def __init__(self, feed: ColanderFeed, theme: dict = None):
        """
        Initialize the Mermaid exporter.

        Args:
            feed: The Colander feed data to be exported
            theme: Custom theme configuration. If None, loads the default theme automatically
        """
        self.feed = feed
        self.theme = theme
        if not self.theme:
            self.load_default_theme()
        template_name = "mermaid.jinja2"
        template_source_dir = resources.files(resource_package).joinpath("..").joinpath("data").joinpath("templates")
        self.template_exporter = TemplateExporter(feed, str(template_source_dir), template_name)
        self.feed.resolve_references()

    def load_default_theme(self):
        """
        Load the default theme configuration from the package resources.

        Reads the default theme JSON file from the package's data/themes directory
        and loads it into the theme attribute. This method is automatically called
        during initialization if no custom theme is provided.

        Raises:
            FileNotFoundError: If the default theme file cannot be found
            ~json.JSONDecodeError: If the theme file contains invalid JSON
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
        Export the Colander feed data as a Mermaid diagram.

        Uses the configured template and theme to generate Mermaid diagram syntax
        and writes it to the provided output stream. It does not render the diagram.

        Args:
            output: The output stream to write the Mermaid diagram to
            **kwargs: Additional keyword arguments passed to the template engine
        """
        self.template_exporter.export(output, theme=self.theme)
