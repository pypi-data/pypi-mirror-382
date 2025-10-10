from pathlib import Path
from typing import Optional

import click  # type: ignore
from rich.console import Console  # type: ignore

from .format import CHAR_LIMIT_DEFAULT, find_yaml_files, format_yaml_file
from .watch import ModifyStatuteHandler, Watcher

console: Console = Console()


@click.group()
def cli():
    """Extensible wrapper of commands."""
    pass


@click.command()
@click.option(
    "--folder",
    default="../corpus-statutes",
    required=True,
    help="Folder to watch files for changes.",
)
def watch_files(folder: str):
    """When files found in the folder being watched are updated (based on
    ModifyDecisionHandler config), handle the update."""
    handler = ModifyStatuteHandler()
    w = Watcher(folder, handler)
    w.run()


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--inplace", is_flag=True, default=False, help="Format files in place.")
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output file (only for single file input).",
)
@click.option(
    "--char-limit",
    type=int,
    default=CHAR_LIMIT_DEFAULT,
    help="Maximum line length for wrapping.",
)
def format_statute(
    path: str, inplace: bool, output: Optional[str], char_limit: int
) -> None:
    """Format a YAML file or all `.yml` files in a folder."""
    path_obj: Path = Path(path)
    if path_obj.is_file():
        out_path: Optional[Path] = Path(output) if output else None
        console.print(f"[cyan]Processing file:[/cyan] {path_obj}")
        format_yaml_file(
            path_obj, inplace=inplace, output_file=out_path, char_limit=char_limit
        )
    elif path_obj.is_dir():
        if output:
            raise click.BadParameter("Cannot specify --output when input is a folder")
        console.print(f"[cyan]Processing folder recursively:[/cyan] {path_obj}")
        for file in find_yaml_files(path_obj):
            format_yaml_file(file, inplace=True, char_limit=char_limit)
    else:
        raise click.BadParameter(f"Path is neither file nor folder: {path}")


if __name__ == "__main__":
    cli()  # type: ignore
