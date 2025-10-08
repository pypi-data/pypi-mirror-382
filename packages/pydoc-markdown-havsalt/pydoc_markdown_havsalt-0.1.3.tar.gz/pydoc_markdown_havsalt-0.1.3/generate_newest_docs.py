"""
Documentation Build Tool
========================

Tool to help build the latest styled docs for `pydoc-markdown-havsalt`.
To generate the newest docs, run:

```bash
uv run generate_newest_docs.py
```
"""

from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor

from pydoc_markdown_havsalt import RuffMarkdownRenderer, ComposePublicExportsProcessor


engine = PydocMarkdown(
    loaders=[
        PythonLoader(
            packages=["pydoc_markdown_havsalt"],
        )
    ],
    processors=[
        ComposePublicExportsProcessor(),
        FilterProcessor(do_not_filter_modules=False, skip_empty_modules=True),
        SmartProcessor(),
        CrossrefProcessor(),
    ],
    renderer=RuffMarkdownRenderer(
        filename="Docs.md",
        page_title="Documentation for `pydoc-markdown-havsalt`",
        render_page_title=True,
        render_toc=True,
        insert_header_anchors=True,
        code_headers=True,
        descriptive_class_title="Class ",
        descriptive_module_title=True,
        add_module_prefix=True,
        add_method_class_prefix=True,
        header_level_by_type={
            "Module": 1,
            "Function": 2,
            "Class": 2,
            "Method": 3,
            "Variable": 3,
        },
    ),
)

modules = engine.load_modules()
engine.process(modules)
engine.render(modules)
