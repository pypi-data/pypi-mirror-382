import subprocess
import sys

from ..config import load_and_validate_config


def install_requirements(path, typer, verbose):
    config = load_and_validate_config(path, typer, verbose)

    for service in config:
        service_path = config.dir / config.type2folder(service.type) / service.name
        reqs_path = service_path / "requirements.txt"
        if not reqs_path.exists():
            continue
        typer.echo(f"Installing requirements for {service.type} '{service.name}'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(reqs_path)])
    return "done"
