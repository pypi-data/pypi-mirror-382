
import json
import os
import zqb

_cached_entry : list = None

def load_entry() -> list[str]:
    global _cached_entry
    if _cached_entry is None:
        entry = zqb.target_keyring.get_password("ZQB_PY_CONFIG", zqb.current_user)
        json_data = entry if entry is not None else "[]"
        _cached_entry = json.loads(json_data)
    return _cached_entry

def save_entry(entry: list[str]) -> None:
    global _cached_entry
    _cached_entry = entry
    zqb.target_keyring.set_password("ZQB_PY_CONFIG", zqb.current_user, json.dumps(entry))

def add_entry(path: str) -> None:
    entry = load_entry()
    if path not in entry:
        entry.append(path)
        save_entry(entry)

def remove_entry(path: str) -> None:
    entry = load_entry()
    if path in entry:
        entry.remove(path)
        save_entry(entry)

def list_entry() -> list[str]:
    return load_entry()

def clear_entry() -> None:
    zqb.target_keyring.delete_password("ZQB_PY_CONFIG", zqb.current_user)
# normalize name
def normalize_name(name: str) -> str:
    return name.replace("-", "_").replace(" ", "_").lower()


# executor 

def create_ccommand_python(script : str):
    import click

    basename_no_ext = os.path.splitext(os.path.basename(script))[0]
    basename_no_ext = normalize_name(basename_no_ext)
    @click.command(basename_no_ext)
    @click.option("--arg", "-a", multiple=True, help="Arguments to pass to the script, in the format of k=v")
    def command(arg):
        arg_dict = {}
        for a in arg:
            if '=' in a:
                k, v = a.split('=', 1)
                arg_dict[k] = v
        import runpy
        runpy.run_path(script, init_globals=arg_dict)

    return command

def create_ccommand_pwsh(script : str):
    import click
    import subprocess

    basename_no_ext = os.path.splitext(os.path.basename(script))[0]
    basename_no_ext = normalize_name(basename_no_ext)
    @click.command(basename_no_ext)
    @click.option("--arg", "-a", multiple=True, help="Arguments to pass to the script, in the format of k=v")
    def command(arg):
        arg_list = []
        for a in arg:
            if '=' in a:
                k, v = a.split('=', 1)
                arg_list.append(f"-{k} {v}")
        cmd = ["pwsh", "-File", script] + arg_list
        subprocess.run(cmd)

    return command

def create_ccommand_bash(script : str):
    import click
    import subprocess

    basename_no_ext = os.path.splitext(os.path.basename(script))[0]
    basename_no_ext = normalize_name(basename_no_ext)
    @click.command(basename_no_ext)
    @click.option("--arg", "-a", multiple=True, help="Arguments to pass to the script, in the format of k=v")
    def command(arg):
        arg_list = []
        for a in arg:
            if '=' in a:
                k, v = a.split('=', 1)
                arg_list.append(f"--{k}={v}")
        cmd = ["bash", script] + arg_list
        subprocess.run(cmd)

    return command

def create_ccommand_exe(script : str):
    import click
    import subprocess

    basename_no_ext = os.path.splitext(os.path.basename(script))[0]
    basename_no_ext = normalize_name(basename_no_ext)
    @click.command(basename_no_ext)
    @click.option("--arg", "-a", multiple=True, help="Arguments to pass to the executable, in the format of k=v")
    def command(arg):
        arg_list = []
        for a in arg:
            if '=' in a:
                k, v = a.split('=', 1)
                arg_list.append(f"--{k}={v}")
        cmd = [script] + arg_list
        subprocess.run(cmd)

    return command


def create_ccommand_cmd(script : str):
    import click
    import subprocess

    basename_no_ext = os.path.splitext(os.path.basename(script))[0]
    basename_no_ext = normalize_name(basename_no_ext)
    @click.command(basename_no_ext)
    @click.option("--arg", "-a", multiple=True, help="Arguments to pass to the script, in the format of k=v")
    def command(arg):
        arg_list = []
        for a in arg:
            if '=' in a:
                k, v = a.split('=', 1)
                arg_list.append(f"/{k}:{v}")
        cmd = ["cmd", "/C", script] + arg_list
        subprocess.run(cmd)

    return command
