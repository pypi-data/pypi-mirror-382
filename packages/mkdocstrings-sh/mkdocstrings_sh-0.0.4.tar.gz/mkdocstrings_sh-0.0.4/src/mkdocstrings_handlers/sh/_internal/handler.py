# This module implements a handler for Sh.

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from mkdocs.exceptions import PluginError
from mkdocstrings import BaseHandler, CollectionError, CollectorItem, get_logger

from mkdocstrings_handlers.sh._internal.config import ShConfig, ShOptions
from mkdocstrings_handlers.sh._internal import shdocgen

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping

    from mkdocs.config.defaults import MkDocsConfig
    from mkdocstrings import HandlerOptions


_logger = get_logger(__name__)


class ShHandler(BaseHandler):
    """The Sh handler class."""

    name: ClassVar[str] = "sh"
    """The handler's name."""

    domain: ClassVar[str] = "sh"
    """The cross-documentation domain/language for this handler."""
    # Typically: the file extension, like `py`, `go` or `rs`.
    # For non-language handlers, use the technology/tool name, like `openapi` or `click`.

    enable_inventory: ClassVar[bool] = False
    """Whether this handler is interested in enabling the creation of the `objects.inv` Sphinx inventory file."""

    fallback_theme: ClassVar[str] = "material"
    """The theme to fallback to."""

    def __init__(self, config: ShConfig, base_dir: Path, **kwargs: Any) -> None:
        """Initialize the handler.

        Parameters:
            config: The handler configuration.
            base_dir: The base directory of the project.
            **kwargs: Arguments passed to the parent constructor.
        """
        super().__init__(**kwargs)

        self.config = config
        """The handler configuration."""
        self.base_dir = base_dir
        """The base directory of the project."""
        self.global_options = config.options
        """The global configuration options."""

        self._collected: dict[str, CollectorItem] = {}

    def get_options(self, local_options: Mapping[str, Any]) -> HandlerOptions:
        """Get combined default, global and local options.

        Arguments:
            local_options: The local options.

        Returns:
            The combined options.
        """
        extra = {
            **self.global_options.get("extra", {}),
            **local_options.get("extra", {}),
        }
        options = {**self.global_options, **local_options, "extra": extra}
        try:
            return ShOptions.from_data(**options)
        except Exception as error:
            raise PluginError(f"Invalid options: {error}") from error

    def collect(
        self, identifier: str, options: ShOptions
    ) -> CollectorItem:  # noqa: ARG002
        """Collect data given an identifier and selection configuration."""
        # In the implementation, you either run a specialized tool in a subprocess
        # to capture its JSON output, that you load again in Python data structures,
        # or you parse the source code directly, for example with tree-sitter.
        #
        # The `identifier` argument is the fully qualified name of the object to collect.
        # For example, in Python, it would be 'package.module.function' to collect documentation
        # for this function. Other languages have different conventions.
        #
        # The `options` argument is the configuration options for loading/rendering the data.
        # It contains both the global and local options, combined together.
        #
        # You might want to store collected data in `self._collected`, for easier retrieval later,
        # typically when mkdocstrings will try to get aliases for an identifier through your `get_aliases` method.
        file = identifier.split(" ", 1)[0]
        script_path = self.base_dir / file
        try:
            root = shdocgen.parse_script(
                script_path,
                filename=file,
                includeregex=options.includeregex,
                excluderegex=options.excluderegex,
            )
        except FileNotFoundError as error:
            raise CollectionError(f"Could not find script {script_path}") from error
        name = " ".join(identifier.split(" ", 1)[1:]) if " " in identifier else None
        if name:
            ret = shdocgen.find_name(root, name)
            if not ret:
                raise CollectionError(
                    f"Could not find symbol {repr(name)} in script {script_path}"
                )
            ret["file"] = root["file"]
        else:
            ret = root
        return ret

    def render(self, data: CollectorItem, options: ShOptions) -> str:
        """Render a template using provided data and configuration options."""
        # The `data` argument is the data to render, that was collected above in `collect()`.
        # The `options` argument is the configuration options for loading/rendering the data.
        # It contains both the global and local options, combined together.

        # You might want to get the template based on the data type.
        template = self.env.get_template(f"{data['type']}.html.jinja")
        # All the following variables will be available in the Jinja templates.
        return template.render(
            config=options,
            data=data,
            filename=Path(data["file"]).name,
            heading_level=options.heading_level,
            source_url=options.source_url,
        )

    def get_aliases(self, identifier: str) -> tuple[str, ...]:
        """Get aliases for a given identifier."""
        try:
            data = self._collected[identifier]
        except KeyError:
            return ()
        # Update the following code to return the canonical identifier and any aliases.
        return (data.path,)

    def update_env(self, config: dict) -> None:  # noqa: ARG002
        """Update the Jinja environment with any custom settings/filters/options for this handler.

        Parameters:
            config: MkDocs configuration, read from `mkdocs.yml`.
        """
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True
        self.env.keep_trailing_newline = False

    # You can also implement the `get_inventory_urls` and `load_inventory` methods
    # if you want to support loading object inventories.
    # You can also implement the `render_backlinks` method if you want to support backlinks.


def get_handler(
    handler_config: MutableMapping[str, Any],
    tool_config: MkDocsConfig,
    **kwargs: Any,
) -> ShHandler:
    """Simply return an instance of `ShHandler`.

    Arguments:
        handler_config: The handler configuration.
        tool_config: The tool (SSG) configuration.

    Returns:
        An instance of `ShHandler`.
    """
    base_dir = Path(tool_config.config_file_path or "./mkdocs.yml").parent
    return ShHandler(
        config=ShConfig.from_data(**handler_config),
        base_dir=base_dir,
        **kwargs,
    )
