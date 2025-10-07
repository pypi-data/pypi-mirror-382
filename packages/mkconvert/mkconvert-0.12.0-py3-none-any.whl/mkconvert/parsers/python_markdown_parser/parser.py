"""Python-Markdown parser implementation."""

from __future__ import annotations

from typing import Any, Literal

from mkconvert.parsers.base_parser import BaseParser


class PythonMarkdownParser(BaseParser):
    """Parser implementation using Python-Markdown."""

    def __init__(
        self,
        extensions: list[str] | None = None,
        extension_configs: dict[str, dict[str, Any]] | None = None,
        output_format: Literal["html", "xhtml"] | None = "html",
        **kwargs: Any,
    ) -> None:
        """Initialize the Python-Markdown parser.

        Args:
            extensions: List of extensions to use
            extension_configs: Configuration for extensions
            output_format: Output format (html, html5, xhtml, etc.)
            kwargs: Additional keyword arguments passed to Python-Markdown
        """
        import markdown

        self._extensions = extensions or []
        self._extension_configs = extension_configs or {}
        self._output_format = output_format
        self._kwargs = kwargs

        # Create the parser instance once
        self._parser = markdown.Markdown(
            extensions=self._extensions,
            extension_configs=self._extension_configs,
            output_format=self._output_format,
            **self._kwargs,
        )

    def convert(self, markdown_text: str) -> str:
        """Convert markdown to HTML.

        Args:
            markdown_text: Input markdown text
            **options: Override default options

        Returns:
            HTML output as string
        """
        self._parser.reset()  # Reset parser state for new conversion
        return self._parser.convert(markdown_text)

    @property
    def name(self) -> str:
        """Get the name of the parser."""
        return "python-markdown"

    @property
    def features(self) -> set[str]:
        """Get the set of supported features."""
        base_features = {"basic_markdown", "fenced_code"}

        # Add features based on loaded extensions
        extension_feature_map = {
            "tables": "tables",
            "pymdownx.tilde": "strikethrough",
            "pymdownx.magiclink": "autolink",
            "pymdownx.tasklist": "tasklists",
            "pymdownx.arithmatex": "math",
            "admonition": "admonition",
            "pymdownx.details": "details",
            "pymdownx.superfences": "superfences",
            # Add more mappings as needed
        }

        for extension in self._extensions:
            if extension in extension_feature_map:
                base_features.add(extension_feature_map[extension])

        return base_features


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)

    parser = PythonMarkdownParser()
    print(parser.convert("# Test"))
