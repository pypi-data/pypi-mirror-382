# Documentation for `pydoc-markdown-havsalt`

## Table of Contents

* [pydoc\_markdown\_havsalt](#pydoc_markdown_havsalt)
  * [ComposePublicExportsProcessor](#pydoc_markdown_havsalt.ComposePublicExportsProcessor)
  * [RuffMarkdownRenderer](#pydoc_markdown_havsalt.RuffMarkdownRenderer)
    * [format\_code](#pydoc_markdown_havsalt.RuffMarkdownRenderer.format_code)
    * [include\_self\_arg](#pydoc_markdown_havsalt.RuffMarkdownRenderer.include_self_arg)
    * [include\_cls\_arg](#pydoc_markdown_havsalt.RuffMarkdownRenderer.include_cls_arg)
    * [tab\_size](#pydoc_markdown_havsalt.RuffMarkdownRenderer.tab_size)
    * [page\_title](#pydoc_markdown_havsalt.RuffMarkdownRenderer.page_title)

<a id="pydoc_markdown_havsalt"></a>

# Module `pydoc_markdown_havsalt`

Plugin for `pydoc-markdown`
===========================

This plugin offers additional features for documenting with the
well-written `pydoc-markdown` tool.

Often used in `Havsalt`'s projects.

<a id="pydoc_markdown_havsalt.ComposePublicExportsProcessor"></a>

## Class `ComposePublicExportsProcessor`

```python
@dataclass
class ComposePublicExportsProcessor(Processor)
```

`ComposePublicExportsProcessor` that only exposes members of `__all__`.

Currently, composes public exports into a single top level module,
keeping the original module name (often the project name in _snake\_case_).

`NOTE` Processor `filter` (`FilterProcessor`) **cannot appear _before_** [`ComposePublicExportsProcessor`](#pydoc_markdown_havsalt.ComposePublicExportsProcessor).

**Example**:

  
  Using [`ComposePublicExportsProcessor`](#pydoc_markdown_havsalt.ComposePublicExportsProcessor) in `pyproject.toml`:
  
```toml
[[tool.pydoc-markdown.processors]]
type = "pydoc_markdown_havsalt.ComposePublicExportsProcessor"
```

<a id="pydoc_markdown_havsalt.RuffMarkdownRenderer"></a>

## Class `RuffMarkdownRenderer`

```python
@dataclass
class RuffMarkdownRenderer(MarkdownRenderer)
```

`RuffMarkdownRenderer` for better formatting of function/method arguments.

This formatting is like the one used by `ruff`.
See the docs for a list default values.

**Example**:

  
  Using [`RuffMarkdownRenderer`](#pydoc_markdown_havsalt.RuffMarkdownRenderer) in `pyproject.toml`:
  
```toml
[tool.pydoc-markdown.renderer]
type = "pydoc_markdown_havsalt.RuffMarkdownRenderer"
include_self_arg = true
include_cls_arg = true
tab_size = 2
```

<a id="pydoc_markdown_havsalt.RuffMarkdownRenderer.format_code"></a>

### `format_code`

Whether to override the *new* default formatting.
The parent class `MarkdownRenderer` has this turned on by default,
but this class provides a custom implementation.
Disabled by default.

<a id="pydoc_markdown_havsalt.RuffMarkdownRenderer.include_self_arg"></a>

### `include_self_arg`

Whether to include `self` argument in a method.
Disabled by default.

<a id="pydoc_markdown_havsalt.RuffMarkdownRenderer.include_cls_arg"></a>

### `include_cls_arg`

Whether to include `cls` argument in a `@classmethod`.
Disabled by default.

<a id="pydoc_markdown_havsalt.RuffMarkdownRenderer.tab_size"></a>

### `tab_size`

Tabsize when formatting a long list of arguments.
Default is `4` spaces.

<a id="pydoc_markdown_havsalt.RuffMarkdownRenderer.page_title"></a>

### `page_title`

Optional page title string,
to be used in conjunction with option `render_page_title`.
If left as `None` and `render_single_page` is called with [`page_title`](#pydoc_markdown_havsalt.RuffMarkdownRenderer.page_title),
it will use the value of [`page_title`](#pydoc_markdown_havsalt.RuffMarkdownRenderer.page_title), even if `None`.
Defaults to `None`.

