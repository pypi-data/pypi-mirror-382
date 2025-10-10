from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from engin import Supply
from engin._cli._common import COMMON_HELP, get_engin_instance, print_error

cli = typer.Typer()
_CLI_HELP = {
    "type": "Filter providers by the provided type, e.g. `AsyncClient` or `float[]`",
    "module": "Filter providers by the provided type's module, e.g. `engin` or `httpx`",
    "verbose": "Enables verbose output",
}


@cli.command(name="inspect")
def serve_graph(
    app: Annotated[
        str | None,
        typer.Argument(help=COMMON_HELP["app"]),
    ] = None,
    type_: Annotated[
        str | None,
        typer.Option("--type", help=_CLI_HELP["type"]),
    ] = None,
    module: Annotated[
        str | None,
        typer.Option(help=_CLI_HELP["module"]),
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help=_CLI_HELP["verbose"])
    ] = False,
) -> None:
    """
    Shows metadata for all matching providers.

    Examples:

        1. `engin inspect --module httpx`
        2. `engin inspect --type AsyncClient`
    """
    module_name, _, instance = get_engin_instance(app)

    console = Console()

    providers = []
    for provider in instance.assembler.providers:
        type_id = provider.return_type_id
        if type_ is not None:
            type_name = str(type_id).rsplit(".", maxsplit=1)[-1]
            if type_ != type_name:
                if verbose:
                    console.print(
                        f"Ignoring '{provider.return_type_id}' as `{type_} != {type_name}",
                        style="dim",
                    )
                continue
        if module is not None:
            module_name = str(type_id).split(".", maxsplit=1)[0]
            if module != module_name:
                if verbose:
                    console.print(
                        f"Ignoring '{provider.return_type_id}' as `{module} != {module_name}",
                        style="dim",
                    )
                continue
        providers.append(provider)

    matching_provider_count = len(providers)
    if matching_provider_count == 0:
        available = sorted(map(str, instance.assembler.providers))
        print_error(f"No matching providers, available: {available}")

    console.print(
        f"Found {matching_provider_count} matching provider"
        + ("s" if matching_provider_count > 1 else ""),
        style="dim",
    )

    table = Table(show_header=False, show_lines=False, box=box.ASCII)

    for provider in sorted(providers, key=lambda p: p.source_module):
        is_supply = isinstance(provider, Supply)

        table.add_row("name", str(provider), style="bold", end_section=True)
        table.add_row("scope", provider.scope or "N/A")
        table.add_row("func", provider.func_name if not is_supply else "N/A")
        table.add_row("block", provider.block_name or "N/A")
        table.add_row("source module", provider.source_module or "N/A")
        table.add_row("source package", provider.source_package or "N/A")
        table.add_section()

    console.print(table)
