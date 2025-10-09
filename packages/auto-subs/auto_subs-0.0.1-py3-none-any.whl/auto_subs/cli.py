import typer
from . import __version__

app = typer.Typer()


def version_callback(value: bool):
    if value:
        typer.echo(f"auto-subs version: {__version__}")
        raise typer.Exit()


@app.command()
def main(
        version: bool = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True,
                                     help="Show the version and exit."),
):
    """
    A powerful CLI for video transcription and subtitle generation.

    This is a placeholder for the main functionality.
    Run 'auto-subs transcribe --help' for more info in the future.
    """
    typer.echo("Welcome to auto-subs! This CLI is under construction.")
    typer.echo("Future commands: transcribe, style, ...")
