
import logging
import os
import sys
import click
from zqb.cli_config import config
import zqb.utils as utils
@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, help="Enable debug mode")
def cli(debug) -> None:
    if debug:
        click.echo("Debug mode is on")
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", stream=sys.stdout)

    # print help if no subcommand is provided
    if not click.get_current_context().invoked_subcommand:
        click.echo(cli.get_help(click.get_current_context()))

cli.add_command(config, name="zqb_config")

@cli.command("zqb_shell")
@click.pass_context
def shell(ctx):
    click.echo("Starting shell...")
    ctx.command = cli
    # Here you can implement the shell functionality
    import click_shell
    # Pass the parent context (cli group) instead of the shell command context
    shell = click_shell.make_click_shell(ctx.parent)
    shell.prompt = "zqb> "
    shell.cmdloop()

def _create_sub_folder(folder : str, currentGroup = cli):
    for sub in os.listdir(folder):
        if sub.startswith("."):
            continue
        subpath = os.path.join(folder, sub)
        # filter out none .py, .ps1, .sh, .bash files + folders
        if not (subpath.endswith(".py") or subpath.endswith(".ps1") or subpath.endswith(".sh") or subpath.endswith(".bash") or os.path.isdir(subpath)):
            continue
        
        
        logging.debug(f"Found sub item: {sub}")
        if os.path.isdir(subpath):
            new_group = click.Group(sub)
            _create_sub_folder(subpath, new_group)
            currentGroup.add_command(new_group)
        elif os.path.isfile(subpath):
            if subpath.endswith(".py"):
                command = utils.create_ccommand_python(subpath)
                currentGroup.add_command(command)
            elif subpath.endswith(".ps1"):
                command = utils.create_ccommand_pwsh(subpath)
                currentGroup.add_command(command)
            elif subpath.endswith(".sh") or subpath.endswith(".bash"):
                command = utils.create_ccommand_bash(subpath)
                currentGroup.add_command(command)

def init_cli():
    print("zqb command line interface")
    if "--debug" in sys.argv:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", stream=sys.stdout)

    for entry in utils.list_entry():
        if os.path.exists(entry) and os.path.isdir(entry):
            logging.debug(f"Creating commands from entry: {entry}")
        _create_sub_folder(entry)
    cli()

if __name__ == "__main__":
    init_cli()