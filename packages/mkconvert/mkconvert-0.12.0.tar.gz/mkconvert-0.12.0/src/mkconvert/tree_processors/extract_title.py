"""Tree processor for extracting document title using ElementTree."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from mkconvert.tree_processors.base import ETTreeProcessor


if TYPE_CHECKING:
    from xml.etree import ElementTree as ET


class ExtractTitleETProcessor(ETTreeProcessor):
    """Extract title from the first h1 element using ElementTree."""

    def __init__(self, priority: int = -10) -> None:
        """Initialize with a low priority to run near the end.

        Args:
            priority: Execution priority (lower runs later)
        """
        super().__init__(priority)
        self.title: str | None = None

    def process_tree(self, tree: ET.Element) -> ET.Element:
        """Extract title from the first h1 element.

        Args:
            tree: The HTML DOM tree

        Returns:
            The unchanged tree
        """
        try:
            # Find the first h1 element
            h1_elements = self.find_elements(tree, ".//h1")
            if not h1_elements:
                return tree

            h1 = h1_elements[0]

            # Handle trailing anchor if present (common in some markdown renderers)
            if len(h1) > 0 and h1[-1].tag == "a" and not (h1[-1].tail or "").strip():
                h1 = copy.copy(h1)
                h1.remove(h1[-1])

            # Extract all text content
            title = self.get_text_content(h1)
            self.title = title.strip()

        except Exception as e:  # noqa: BLE001
            # Log but don't fail if title extraction has an issue
            import logging

            logging.getLogger(__name__).warning("Error extracting title: %s", e)

        return tree
