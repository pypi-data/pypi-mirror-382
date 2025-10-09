import os
import subprocess
from typing import List
import schedule
import time
from multiprocessing import Process
from pathlib import Path
import json

import typer

from ..config import load_and_validate_config
from ..storage import create_or_retrieve_s3_bucket


def safe_run(cmd, check=True, env=None):
    try:
        subprocess.run(cmd, check=check, env=env)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed with exit code {e.returncode}: {e.cmd}") from e


def run_service(service, command: List):
    if service.command:
        safe_run(service.command, check=True)
    else:
        safe_run(command, check=True)


def run_script(args: tuple[List, str, typer.Typer]):
    script, dir, typer = args
    typer.echo(f"Running script '{script.name}'...")
    os.chdir(dir / f"scripts/{script.name}")
    run_service(script, ["python", "main.py"])


def run_notebook(notebook, dir, typer):
    typer.echo(f"Running notebook '{notebook.name}'...")
    os.chdir(dir / "notebooks" / notebook.name)
    safe_run(["jupyter", "notebook"])


def run_api(api, dir, port, host, reload):
    os.chdir(dir / f"apis/{api.name}")
    safe_run(["python", "main.py", "--port", str(port), "--host", host])


def run_ui(ui, dir, api_urls):
    ui_path = dir / f"uis/{ui.name}"
    os.chdir(ui_path)

    env = os.environ.copy()
    for name, value in ui.env.items():
        if value in api_urls:
            env[name] = api_urls[value]

    if ui.runtime == "node":
        if not os.path.exists(ui_path / "node_modules"):
            try:
                safe_run(["npm", "install"], env=env)
            except Exception as e:
                raise ValueError(
                    f"There was an error installing the npm dependencies for the ui '{ui.name}'.\n{e}"
                )
    if not isinstance(ui.command, list):
        raise ValueError(
            f"The command for the ui '{ui.name}' must be a list of strings."
        )
    safe_run(ui.command, env=env)

def run_schdule():
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_local(dir, variables, typer):
    config = load_and_validate_config(dir, typer)
    dir = Path(dir).resolve()  # required because of the chdir
    typer.echo("Deploying locally...")
    # save variables
    if variables:
        try:
            # load current variables
            with open(dir / "spai.vars.json", "r") as f:
                current_variables = json.load(f)
        except FileNotFoundError:
            current_variables = {}
        # merge variables
        variables = {**current_variables, **variables}
        with open(dir / "spai.vars.json", "w") as f:
            json.dump(variables, f)
    keep_alive = False
    processes = []
    if config.storage:
        typer.echo("Setting up storage...")
        for storage in config.storage:
            if storage.type == "s3" and not storage.credentials:
                # raise ValueError("S3 storage requires credentials")
                typer.echo(
                    "S3 storage credentials not provided, an S3 bucket will be created if it does not already exist."
                )
                # if not typer.confirm("Do you want to continue?"):
                #     raise typer.Abort()
                storage.credentials = create_or_retrieve_s3_bucket(
                    config.project, storage.name
                )
        # set env variables
        prefix = "SPAI_STORAGE"
        names = []
        for storage in config.storage:
            names.append(storage.type + "_" + storage.name)
            name = storage.name.upper()
            if storage.type == "local":
                os.environ[f"{prefix}_LOCAL_{name}_PATH"] = (
                    str(dir) + "/" + str(storage.path)
                )
            elif storage.type == "s3":
                os.environ[f"{prefix}_S3_{name}_URL"] = storage.credentials.url
                os.environ[f"{prefix}_S3_{name}_ACCESS"] = (
                    storage.credentials.access_key
                )
                os.environ[f"{prefix}_S3_{name}_SECRET"] = (
                    storage.credentials.secret_key
                )
                os.environ[f"{prefix}_S3_{name}_REGION"] = storage.credentials.region
                os.environ[f"{prefix}_S3_{name}_BUCKET"] = storage.credentials.bucket
        os.environ[f"{prefix}_NAMES"] = ",".join(names)
    if config.scripts:
        typer.echo("Deploying scripts...")
        for script in config.scripts:
            # the order affects in the execution of the scheduled tasks
            if script.run_on_start:
                run_script((script, dir, typer))
            if script.run_every:
                keep_alive = True
                schedule.every(script.run_every).minutes.do(
                    run_script, (script, dir, typer)
                )  # if a task goes after another than takes more time than the scheduled time, it will have to wait
    if config.notebooks:
        typer.echo("Deploying notebooks...")
        for notebook in config.notebooks:
            p = Process(target=run_notebook, args=(notebook, dir, typer))
            p.start()
            processes.append(p)
    api_urls = {}
    if config.apis:
        typer.echo("Deploying apis...")
        for api in config.apis:
            typer.echo(f"Running api '{api.name}'...")
            p = Process(target=run_api, args=(api, dir, api.port, api.host, api.reload))
            p.start()
            processes.append(p)
            # save api_urls in case UIs need them
            api_urls[f"api.{api.name}"] = f"{api.host}:{api.port}"
    if config.uis:
        typer.echo("Deploying uis...")
        for ui in config.uis:
            typer.echo(f"Running ui '{ui.name}'...")
            p = Process(target=run_ui, args=(ui, dir, api_urls))
            p.start()
            processes.append(p)
    typer.echo(f"Project '{config.project}' deployed.")
    if keep_alive:
        p = Process(target=run_schdule)
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    return
