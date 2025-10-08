# mkconvert

[![PyPI License](https://img.shields.io/pypi/l/mkconvert.svg)](https://pypi.org/project/mkconvert/)
[![Package status](https://img.shields.io/pypi/status/mkconvert.svg)](https://pypi.org/project/mkconvert/)
[![Monthly downloads](https://img.shields.io/pypi/dm/mkconvert.svg)](https://pypi.org/project/mkconvert/)
[![Distribution format](https://img.shields.io/pypi/format/mkconvert.svg)](https://pypi.org/project/mkconvert/)
[![Wheel availability](https://img.shields.io/pypi/wheel/mkconvert.svg)](https://pypi.org/project/mkconvert/)
[![Python version](https://img.shields.io/pypi/pyversions/mkconvert.svg)](https://pypi.org/project/mkconvert/)
[![Implementation](https://img.shields.io/pypi/implementation/mkconvert.svg)](https://pypi.org/project/mkconvert/)
[![Releases](https://img.shields.io/github/downloads/phil65/mkconvert/total.svg)](https://github.com/phil65/mkconvert/releases)
[![Github Contributors](https://img.shields.io/github/contributors/phil65/mkconvert)](https://github.com/phil65/mkconvert/graphs/contributors)
[![Github Discussions](https://img.shields.io/github/discussions/phil65/mkconvert)](https://github.com/phil65/mkconvert/discussions)
[![Github Forks](https://img.shields.io/github/forks/phil65/mkconvert)](https://github.com/phil65/mkconvert/forks)
[![Github Issues](https://img.shields.io/github/issues/phil65/mkconvert)](https://github.com/phil65/mkconvert/issues)
[![Github Issues](https://img.shields.io/github/issues-pr/phil65/mkconvert)](https://github.com/phil65/mkconvert/pulls)
[![Github Watchers](https://img.shields.io/github/watchers/phil65/mkconvert)](https://github.com/phil65/mkconvert/watchers)
[![Github Stars](https://img.shields.io/github/stars/phil65/mkconvert)](https://github.com/phil65/mkconvert/stars)
[![Github Repository size](https://img.shields.io/github/repo-size/phil65/mkconvert)](https://github.com/phil65/mkconvert)
[![Github last commit](https://img.shields.io/github/last-commit/phil65/mkconvert)](https://github.com/phil65/mkconvert/commits)
[![Github release date](https://img.shields.io/github/release-date/phil65/mkconvert)](https://github.com/phil65/mkconvert/releases)
[![Github language count](https://img.shields.io/github/languages/count/phil65/mkconvert)](https://github.com/phil65/mkconvert)
[![Github commits this month](https://img.shields.io/github/commit-activity/m/phil65/mkconvert)](https://github.com/phil65/mkconvert)
[![Package status](https://codecov.io/gh/phil65/mkconvert/branch/main/graph/badge.svg)](https://codecov.io/gh/phil65/mkconvert/)
[![PyUp](https://pyup.io/repos/github/phil65/mkconvert/shield.svg)](https://pyup.io/repos/github/phil65/mkconvert/)

[Read the documentation!](https://phil65.github.io/mkconvert/)


| Feature | Python-Markdown | Markdown2 | Mistune | Comrak (Rust) | PyroMark (Rust) | Markdown-It-PyRS (Rust) |
|---------|----------------|-----------|---------|---------------|-----------------|-------------------------|
| **Core CommonMark** | ✅ | ✅ | ✅ | ✅ (100% compliant) | ✅ | ✅ (100% compliant) |
| Fenced code blocks | ✅ | ✅ (with ext) | ✅ | ✅ | ✅ | ✅ |
| **GitHub Flavored Markdown** |||||||
| Tables | ✅ (with ext) | ✅ (with ext) | ✅ (with plugin) | ✅ (with `.table`) | ✅ (optional) | ✅ (with GFM or `.table`) |
| Task lists | ✅ (with pymdownx.tasklist) | ✅ (with ext) | ✅ (with plugin) | ✅ (with `.tasklist`) | ✅ (optional) | ✅ (with `.tasklist`) |
| Strikethrough | ✅ (with pymdownx.tilde) | ✅ (with ext) | ✅ (with plugin) | ✅ (with `.strikethrough`) | ✅ (optional) | ✅ (with GFM or `.strikethrough`) |
| Autolinks | ✅ (with pymdownx.magiclink) | ❌ | ✅ (with plugin) | ✅ (with `.autolink`) | ✅ (with GFM) | ✅ (with `.autolink_ext`) |
| GFM Alerts | ❌ | ❌ | ❌ | ✅ (with `.alerts`) | ✅ (with GFM) | ❌ |
| **Extended Features** |||||||
| Footnotes | ✅ (with ext) | ✅ (with ext) | ✅ (with plugin) | ✅ (with `.footnotes`) | ✅ (optional) | ✅ (with `.footnote`) |
| Definition lists | ✅ (with ext) | ✅ (with ext) | ❌ | ✅ (with `.description_lists`) | ✅ (optional) | ✅ (with `.deflist`) |
| Admonitions | ✅ (with ext) | ❌ | ❌ | ❌ | ❌ | ❌ |
| Math notation | ✅ (with pymdownx.arithmatex) | ❌ | ✅ (with plugin) | ✅ (with `.math_dollars`/`.math_code`) | ✅ (optional) | ❌ |
| Superscript | ✅ (with ext) | ❌ | ❌ | ✅ (with `.superscript`) | ✅ (optional) | ❌ |
| Subscript | ✅ (with ext) | ❌ | ❌ | ✅ (with `.subscript`) | ✅ (optional) | ❌ |
| Table of Contents | ✅ (with ext) | ✅ (with ext) | ❌ | ❌ | ❌ | ❌ |
| Front matter | ✅ (with ext) | ✅ (with ext) | ❌ | ✅ (with `.front_matter_delimiter`) | ✅ (optional) | ✅ (with `.front_matter`) |
| Wikilinks | ✅ (with ext) | ❌ | ❌ | ✅ (with `.wikilinks_*`) | ✅ (optional) | ❌ |
| Header IDs | ✅ (with ext) | ✅ (with ext) | ❌ | ✅ (with `.header_ids`) | ✅ (optional) | ✅ (with `.heading_anchors`) |
| Multiline blockquotes | ❌ | ❌ | ❌ | ✅ (with `.multiline_block_quotes`) | ❌ | ❌ |
| Syntax highlighting | ✅ (with ext) | ✅ (with ext) | ✅ (with plugin) | ✅ (with plugins) | ❌ | ❌ |
| Special features | Admonitions | Smart quotes | Custom renderers | Spoiler, Greentext | Definition lists | Tree structure, very fast (20x faster than Python-Markdown) |
