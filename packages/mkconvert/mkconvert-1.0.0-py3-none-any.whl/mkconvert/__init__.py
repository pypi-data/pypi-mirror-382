"""mkconvert: main package.

Markdown-HTML converters.
"""

from __future__ import annotations

from importlib.metadata import version

__version__ = version("mkconvert")
__title__ = "mkconvert"

__author__ = "Philipp Temminghoff"
__author_email__ = "philipptemminghoff@googlemail.com"
__copyright__ = "Copyright (c) 2024 Philipp Temminghoff"
__license__ = "MIT"
__url__ = "https://github.com/phil65/mkconvert"

from mkconvert.parsers.base_parser import BaseParser
from mkconvert.parsers.parser import MarkdownParser
from mkconvert.parsers.comrak_parser import ComrakParser
from mkconvert.parsers.github_api_parser import GithubApiParser
from mkconvert.parsers.markdown2_parser import Markdown2Parser
from mkconvert.parsers.markdown_it_pyrs_parser import MarkdownItPyRSParser
from mkconvert.parsers.marko_parser import MarkoParser
from mkconvert.parsers.mistune_parser import MistuneParser
from mkconvert.parsers.pyromark_parser import PyroMarkParser
from mkconvert.parsers.python_markdown_parser import PythonMarkdownParser

from mkconvert.pre_processors.base import PreProcessor
from mkconvert.pre_processors.admonition_converter import MkDocsToGFMAdmonitionProcessor

from mkconvert.tree_processors.base import (
    ETTreeProcessor,
    LXMLTreeProcessor,
    TreeProcessor,
)
from mkconvert.tree_processors.extract_title import ExtractTitleETProcessor
from mkconvert.tree_processors.extract_title_lxml import ExtractTitleLXMLProcessor

from mkconvert.post_processors.base import PostProcessor
from mkconvert.post_processors.sanitizer import SanitizeHTMLProcessor

__all__ = [
    "BaseParser",
    "ComrakParser",
    "ETTreeProcessor",
    "ExtractTitleETProcessor",
    "ExtractTitleLXMLProcessor",
    "GithubApiParser",
    "LXMLTreeProcessor",
    "Markdown2Parser",
    "MarkdownItPyRSParser",
    "MarkdownParser",
    "MarkoParser",
    "MistuneParser",
    "MkDocsToGFMAdmonitionProcessor",
    "PostProcessor",
    "PreProcessor",
    "PyroMarkParser",
    "PythonMarkdownParser",
    "SanitizeHTMLProcessor",
    "TreeProcessor",
    "__version__",
]
