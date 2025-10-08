import typing as t
from dataclasses import dataclass

import docspec
import typing_extensions as te
from pydoc_markdown.util.docspec import is_function
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer, dotted_name


def get_arglist(
    args: t.Sequence[docspec.Argument],
    render_type_hints: bool = True,
) -> list[str]:
    params: list[str] = []

    for arg in args:
        parts: list[str] = []
        if arg.type == docspec.Argument.Type.KEYWORD_ONLY and not any(
            x.startswith("*") for x in params
        ):
            params.append("*")
        parts = [arg.name]
        if arg.datatype and render_type_hints:
            parts.append(": " + arg.datatype)
        if arg.default_value:
            if arg.datatype:
                parts.append(" ")
            parts.append("=")
        if arg.default_value:
            if arg.datatype:
                parts.append(" ")
            parts.append(arg.default_value)
        if arg.type == docspec.Argument.Type.POSITIONAL_REMAINDER:
            parts.insert(0, "*")
        elif arg.type == docspec.Argument.Type.KEYWORD_REMAINDER:
            parts.insert(0, "**")
        params.append("".join(parts))

    return params


def is_classmethod(func: docspec.ApiObject) -> te.TypeGuard[docspec.Function]:
    return is_function(func) and any(
        "classmethod" in d.name for d in func.decorations or []
    )


def format_function_signature(
    func: docspec.Function,
    exclude_self: bool = False,
    exclude_cls: bool = False,
    tab_size: int = 4,
) -> str:
    assert isinstance(func, docspec.Function), type(func)
    args = func.args[:]
    if exclude_self and args and args[0].name == "self":
        args.pop(0)
    if exclude_cls and args and args[0].name == "cls":
        args.pop(0)
    arg_list = get_arglist(args)
    if len(arg_list) <= 1:
        sig = "(" + ",".join(get_arglist(args)) + ")"
    else:
        # fmt: off
        sig = (
            "(\n" + " " * tab_size
            + (",\n" + " " * tab_size).join(arg_list)
            + ",\n)"
        )
        # fmt: on
    if func.return_type:
        sig += f" -> {func.return_type}"
    return sig


@dataclass
class RuffMarkdownRenderer(MarkdownRenderer):
    """Use custom formatting of function/method arguments.

    This formatting is like the one used by `ruff`.

    See the docs for a list default values.

    Example:

    Using #RuffMarkdownRenderer in `pyproject.toml`:

    ```toml
    [tool.pydoc-markdown.renderer]
    type = "pydoc_markdown_havsalt.RuffMarkdownRenderer"
    include_self_arg = true
    include_cls_arg = true
    tab_size = 2
    ```
    """

    #: Whether to override the *new* default formatting.
    #: The parent class #MarkdownRenderer has this turned on by default,
    #: but this class provides a custom implementation.
    #: Disabled by default.
    format_code: bool = False

    #: Whether to include `self` argument in a method.
    #: Disabled by default.
    include_self_arg: bool = False

    #: Whether to include `cls` argument in a `@classmethod`.
    #: Disabled by default.
    include_cls_arg: bool = False

    #: Tabsize when formatting a long list of arguments.
    #: Default is `4` spaces.
    tab_size: int = 4

    #: Optional page title string,
    #: to be used in conjunction with option #render_page_title.
    #: If left as `None` and #render_single_page is called with #page_title,
    #: it will use the value of #page_title, even if `None`.
    #: Defaults to `None`.
    page_title: str | None = None

    def render_single_page(
        self,
        fp: t.TextIO,
        modules: list[docspec.Module],
        page_title: str | None = None,
    ) -> None:
        return super().render_single_page(
            fp,
            modules,
            self.page_title or page_title,
        )

    def _is_classmethod(self, func: docspec.ApiObject) -> bool:
        # This method is indeed redundant,
        # but it was left here to fit the style of #MarkdownRenderer.
        return is_classmethod(func)

    def _format_function_signature(
        self,
        func: docspec.Function,
        override_name: str | None = None,
        add_method_bar: bool = True,
    ) -> str:
        parts: list[str] = []
        if self.signature_with_decorators:
            parts += self._format_decorations(func.decorations or [])
        if self.signature_python_help_style and not self._is_method(func):
            parts.append("{} = ".format(dotted_name(func)))
        parts += [x + " " for x in func.modifiers or []]
        if self.signature_with_def:
            parts.append("def ")
        if self.signature_class_prefix and self._is_method(func):
            parent = func.parent
            assert parent, func
            parts.append(parent.name + ".")
        parts.append((override_name or func.name))
        parts.append(
            format_function_signature(
                func,
                not self.include_self_arg and self._is_method(func),
                not self.include_cls_arg and self._is_classmethod(func),
                tab_size=self.tab_size,
            )
        )
        result = "".join(parts)
        result = self._yapf_code(result + ": pass").rpartition(":")[0].strip()

        if add_method_bar and self._is_method(func):
            result = "\n".join(" | " + l for l in result.split("\n"))
        return result
