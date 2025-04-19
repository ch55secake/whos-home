import subprocess

import rich
from rich.progress import Progress, TextColumn, SpinnerColumn

from src.output.typer_output_builder import TyperOutputBuilder


def build():
    with Progress(
        TextColumn(" "),
        SpinnerColumn(style="green", spinner_name="aesthetic"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(
            description=TyperOutputBuilder()
            .apply_bold_green(message=" 📦 Running poetry lock and installing dependencies... ")
            .build(),
            total=None,
        )
        subprocess.run(["poetry", "lock", "--quiet"], check=True)
        subprocess.run(["poetry", "install", "--quiet"], check=True)

    with Progress(
        TextColumn(" "),
        SpinnerColumn(style="green", spinner_name="aesthetic"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(
            description=TyperOutputBuilder().apply_bold_green(message=" ⚙️ Building binary with Nuitka... ").build(),
            total=None,
        )
        subprocess.run(
            [
                "poetry",
                "run",
                "nuitka",
                "--onefile",
                "--quiet",
                "--enable-plugin=upx",
                "--clang",
                "--lto=yes",
                "--remove-output",
                "--output-filename=whos_home",
                "--output-dir=dist",
                "src/whos_home.py",
            ],
            check=True,
        )
    rich.print("[bold green] Binary built successfully! You can find it in dist/whos_home")
