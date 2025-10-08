from dataclasses import dataclass

import docspec
from pydoc_markdown.interfaces import Processor, Resolver


@dataclass
class ComposePublicExportsProcessor(Processor):
    r"""`ComposePublicExportsProcessor` that only exposes members of `__all__`.

    Currently, composes public exports into a single top level module,
    keeping the original module name (often the project name in _snake\_case_).

    `NOTE` Processor `filter` (`FilterProcessor`) **cannot appear _before_** #ComposePublicExportsProcessor.

    Example:

    Using #ComposePublicExportsProcessor in `pyproject.toml`:

    ```toml
    [[tool.pydoc-markdown.processors]]
    type = "pydoc_markdown_havsalt.ComposePublicExportsProcessor"
    ```
    """

    def __post_init__(self) -> None:
        self._all_public_names: set[str] = set()
        #: Pair structure: <ApiObject>.name: <ApiObject>
        self._all_public_objs: dict[str, docspec.ApiObject] = {}

    def process(self, modules: list[docspec.Module], resolver: Resolver | None) -> None:
        # Fetch `__all__` fields in top module
        if not modules:
            raise ValueError(
                "Parameter 'modules' is empty, when expected to have at least 1 element"
            )
        top_mod = modules[0]  # Assume first module is top level module
        for member in top_mod.members:
            if not isinstance(member, docspec.Variable):
                continue
            if member.name != "__all__":
                continue
            if member.value is None:
                raise ValueError(f"Field '__all__' in {top_mod.path} is 'None'")
            self._all_public_names = self._parse_export_string(member.value)
            break
        else:
            raise ValueError(f"Member '__all__' not found in {top_mod.path}")
        # After getting the list,
        # visit each module and collect all namespaces.
        # Then select which to keep bases on content of `__all__`
        docspec.visit(modules, self._process)
        # Replace top level module with all public exports
        top_mod.members.clear()
        top_mod.members.extend(self._all_public_objs.values())  # type: ignore
        top_mod.sync_hierarchy()
        # Mutate to keep only top level module (the __init__.py)
        modules.clear()
        modules.append(top_mod)

    def _process(self, obj: docspec.ApiObject) -> None:
        if isinstance(obj, docspec.Indirection):
            return
        if obj.name not in self._all_public_names:
            return
        if obj.name in self._all_public_objs:
            return
        self._all_public_objs[obj.name] = obj

    def _parse_export_string(self, export_string: str) -> set[str]:
        # fmt: off
        return set(
            # filter: Filter out empty export names
            filter(
                lambda export_name: export_name != "",
            # map: Remove leading and trailing string quotes
            map(
                lambda export_name: export_name.strip("\"\'"),
                export_string
                    .replace("\n", "")  # Remove newlines if vertical layout
                    .replace(" ", "")   # Remove spaces, to better split
                    .strip("[]")        # Remove outer brackets
                    .strip("()")        # - or parentheses, if used instead of brackets
                    .split(",")         # Split each element
                )
            )
        )
        # fmt: on
