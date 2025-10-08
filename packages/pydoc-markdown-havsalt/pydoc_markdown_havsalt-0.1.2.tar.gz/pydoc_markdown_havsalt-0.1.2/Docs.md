# Table of Contents

* [pydoc\_markdown\_havsalt](#pydoc_markdown_havsalt)
* [pydoc\_markdown\_havsalt.renderers](#pydoc_markdown_havsalt.renderers)
  * [RuffMarkdownRenderer](#pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer)
    * [format\_code](#pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.format_code)
    * [include\_self\_arg](#pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.include_self_arg)
    * [include\_cls\_arg](#pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.include_cls_arg)
    * [tab\_size](#pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.tab_size)
    * [page\_title](#pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.page_title)

<a id="pydoc_markdown_havsalt"></a>

# Module `pydoc_markdown_havsalt`

Plugin for `pydoc-markdown`
===========================

This plugin offers additional features for documenting with the
well-written `pydoc-markdown` tool.

Often used in `Havsalt`'s projects.

<a id="pydoc_markdown_havsalt.renderers"></a>

# Module `pydoc_markdown_havsalt.renderers`

<a id="pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer"></a>

## Class `RuffMarkdownRenderer`

```python
@dataclass
class RuffMarkdownRenderer(MarkdownRenderer)
```

Use custom formatting of function/method arguments.

This formatting is like the one used by `ruff`.

See the docs for a list default values.

**Example**:

  
  Using [`RuffMarkdownRenderer`](#pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer) in `pyproject.toml`:
  
```toml
[tool.pydoc-markdown.renderer]
type = "pydoc_markdown_havsalt.RuffMarkdownRenderer"
include_self_arg = true
include_cls_arg = true
tab_size = 2
```

<a id="pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.format_code"></a>

### `format_code`

Whether to override the *new* default formatting.
The parent class `MarkdownRenderer` has this turned on by default,
but this class provides a custom implementation.
Disabled by default.

<a id="pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.include_self_arg"></a>

### `include_self_arg`

Whether to include `self` argument in a method.
Disabled by default.

<a id="pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.include_cls_arg"></a>

### `include_cls_arg`

Whether to include `cls` argument in a `@classmethod`.
Disabled by default.

<a id="pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.tab_size"></a>

### `tab_size`

Tabsize when formatting a long list of arguments.
Default is `4` spaces.

<a id="pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.page_title"></a>

### `page_title`

Optional page title string,
to be used in conjunction with option `render_page_title`.
If left as `None` and `render_single_page` is called with [`page_title`](#pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.page_title),
it will use the value of [`page_title`](#pydoc_markdown_havsalt.renderers.RuffMarkdownRenderer.page_title), even if `None`.
Defaults to `None`.

