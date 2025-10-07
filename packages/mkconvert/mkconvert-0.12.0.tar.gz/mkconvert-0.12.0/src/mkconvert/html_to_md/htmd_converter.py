"""HTML to Markdown converter implementation using htmd."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from typing import TYPE_CHECKING, Any, ClassVar

from mkconvert.html_to_md.base import (
    BaseHtmlToMarkdown,
)


if TYPE_CHECKING:
    import htmd

    from mkconvert.html_to_md.base import (
        CodeBlockStyle,
        CodeFenceStyle,
        EmphasisStyle,
        HeadingStyle,
        HorizontalRuleStyle,
        LineBreakStyle,
        LinkStyle,
        ListMarkerStyle,
    )


# Check if htmd is available
HTMD_AVAILABLE = importlib.util.find_spec("htmd") is not None


def _map_heading_style(style: HeadingStyle) -> str:
    if style == "atx":
        return "atx"
    return "setex"


def _map_hr_style(style: HorizontalRuleStyle) -> str:
    if style == "dashes":
        return "dashes"
    if style == "underscores":
        return "underscores"
    return "asterisks"


def _map_br_style(style: LineBreakStyle) -> str:
    if style == "backslash":
        return "backslash"
    return "two_spaces"


def _map_link_style(style: LinkStyle) -> str:
    if style == "reference":
        return "referenced"
    return "inlined"


def _map_code_block_style(style: CodeBlockStyle) -> str:
    if style == "indented":
        return "indented"
    return "fenced"


def _map_code_fence_style(style: CodeFenceStyle) -> str:
    if style == "tildes":
        return "tildes"
    return "backticks"


def _map_list_marker_style(style: ListMarkerStyle) -> str:
    if style == "dash":
        return "dash"
    return "asterisk"


@dataclass
class HtmdOptions:
    """Options for the htmd converter."""

    heading_style: HeadingStyle = "atx"
    hr_style: HorizontalRuleStyle = "asterisks"
    br_style: LineBreakStyle = "spaces"
    link_style: LinkStyle = "inline"
    code_block_style: CodeBlockStyle = "fenced"
    code_block_fence: CodeFenceStyle = "backticks"
    bullet_list_marker: ListMarkerStyle = "asterisk"
    preformatted_code: bool = False
    skip_tags: list[str] | None = None

    def to_htmd_options(self) -> htmd.Options:  # pyright: ignore
        import htmd

        htmd_opts = htmd.Options()  # pyright: ignore
        htmd_opts.heading_style = _map_heading_style(self.heading_style)
        htmd_opts.hr_style = _map_hr_style(self.hr_style)
        htmd_opts.br_style = _map_br_style(self.br_style)
        htmd_opts.link_style = _map_link_style(self.link_style)
        htmd_opts.code_block_style = _map_code_block_style(self.code_block_style)
        htmd_opts.code_block_fence = _map_code_fence_style(self.code_block_fence)
        htmd_opts.bullet_list_marker = _map_list_marker_style(self.bullet_list_marker)
        htmd_opts.preformatted_code = self.preformatted_code
        if self.skip_tags:
            htmd_opts.skip_tags = self.skip_tags
        return htmd_opts


class HtmdConverter(BaseHtmlToMarkdown):
    """HTML to Markdown converter using htmd."""

    REQUIRED_PACKAGES: ClassVar = {"htmd-py"}

    def __init__(
        self,
        # Common options from BaseHtmlToMarkdown
        heading_style: HeadingStyle | None = None,
        link_style: LinkStyle | None = None,
        code_block_style: CodeBlockStyle | None = None,
        code_fence_style: CodeFenceStyle | None = None,
        list_marker_style: ListMarkerStyle | None = None,
        line_break_style: LineBreakStyle | None = None,
        hr_style: HorizontalRuleStyle | None = None,
        emphasis_style: EmphasisStyle | None = None,
        skip_tags: list[str] | None = None,
        # htmd-specific options
        preformatted_code: bool = False,
        **options: Any,
    ) -> None:
        """Initialize htmd converter with options.

        Args:
            heading_style: Style for headings
            link_style: Style for links
            code_block_style: Style for code blocks
            code_fence_style: Style for code fences
            list_marker_style: Style for bullet list markers
            line_break_style: Style for line breaks
            hr_style: Style for horizontal rules
            emphasis_style: Style for emphasis (not used by htmd)
            skip_tags: HTML tags to skip during conversion
            preformatted_code: Whether to preserve whitespace in code
            **options: Additional options

        Raises:
            ImportError: If htmd is not installed
        """
        if not HTMD_AVAILABLE:
            msg = "htmd is not installed. Install it with 'pip install htmd-py'."
            raise ImportError(msg)
        self._preformatted_code = preformatted_code
        super().__init__(
            heading_style=heading_style,
            link_style=link_style,
            code_block_style=code_block_style,
            code_fence_style=code_fence_style,
            list_marker_style=list_marker_style,
            line_break_style=line_break_style,
            hr_style=hr_style,
            emphasis_style=emphasis_style,
            skip_tags=skip_tags,
            **options,
        )

    def _initialize_options(self) -> None:
        """Initialize htmd-specific options."""
        self._options = HtmdOptions(
            heading_style=self._heading_style,  # pyright: ignore
            hr_style=self._hr_style,  # pyright: ignore
            br_style=self._line_break_style,  # pyright: ignore
            link_style=self._link_style,  # pyright: ignore
            code_block_style=self._code_block_style,  # pyright: ignore
            code_block_fence=self._code_fence_style,  # pyright: ignore
            bullet_list_marker=self._list_marker_style,  # pyright: ignore
            preformatted_code=self._preformatted_code,
            skip_tags=self._skip_tags,
        )

    def convert(self, html: str) -> str:
        """Convert HTML to Markdown using htmd.

        Args:
            html: HTML content to convert

        Returns:
            Markdown representation of the HTML
        """
        import htmd

        htmd_opts = self._options.to_htmd_options()
        return htmd.convert_html(html, htmd_opts)  # pyright: ignore


if __name__ == "__main__":
    converter = HtmdConverter()
    result = converter.convert("<h1>test</h1>")
    print(result)
