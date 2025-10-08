
import click

from zqb.utils import add_entry
import os

@click.group()
def config() -> None:
    pass

@config.command("add")
@click.argument("path", type=click.Path(exists=True,file_okay=False, dir_okay=True))
def config_add_path(path: str):
    # normalize path
    path = os.path.abspath(path)
    add_entry(path)
    click.echo(f"Added path: {path}")

@config.command("list")
def config_list_paths():
    from zqb.utils import list_entry
    paths = list_entry()
    if not paths:
        click.echo("No paths configured.")
    else:
        click.echo("Configured paths:")
        for p in paths:
            click.echo(f"- {p}")

@config.command("remove")
@click.argument("path", type=click.Path(exists=True,file_okay=False, dir_okay=True))
def config_remove_path(path: str):
    from zqb.utils import remove_entry
    remove_entry(path)
    click.echo(f"Removed path: {path}")

@config.command("clear")
def config_clear_paths():
    from zqb.utils import clear_entry
    clear_entry()
    click.echo("Cleared all configured paths.")

