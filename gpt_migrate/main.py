import typer
from utils import detect_language
import os

import steps
from ai import AI

app = typer.Typer()

class Globals:
    def __init__(self, sourcedir, targetdir, sourcelang, targetlang, ai):
        self.sourcedir = sourcedir
        self.targetdir = targetdir
        self.sourcelang = sourcelang
        self.targetlang = targetlang
        self.ai = ai

@app.command()
def main(
    model: str = typer.Option("gpt-4-32k", help="Large Language Model to be used."),
    temperature: float = typer.Option(0, help="Temperature setting for the AI model."),
    sourcedir: str = typer.Option("../source", help="Source directory containing the API to be migrated."),
    sourcelang: str = typer.Option(None, help="Source language or framework of the API to be migrated."),
    targetdir: str = typer.Option("../target", help="directory containing the API to be migrated."),
    targetlang: str = typer.Option(..., help="Target language or framework for migration."),
    spec: str = typer.Option("OpenAPI", help="Specification to be generated.")
):

    ai = AI(
        model=model,
        temperature=temperature,
    )

    sourcedir = os.path.abspath(sourcedir)
    targetdir = os.path.abspath(targetdir)
    os.makedirs(targetdir, exist_ok=True)

    detected_language = detect_language(sourcedir) if not sourcelang else sourcelang

    if not sourcelang:
        if detected_language:
            is_correct = typer.confirm(f"Is your source project a {detected_language} project?")
            if is_correct:
                sourcelang = detected_language
            else:
                sourcelang = typer.prompt("Please enter the correct language for the source project")
        else:
            sourcelang = typer.prompt("Unable to detect the language of the source project. Please enter it manually")
    
    globals = Globals(sourcedir, targetdir, sourcelang, targetlang, ai)
    typer.style(f"Reading {sourcelang} project from directory '{sourcedir}'. Outputting {targetlang} project to directory '{targetdir}'.", fg=typer.colors.BLUE)

    # Let's get to work!

    '''
    Setup
    '''
    steps.create_environment(globals)
    steps.create_io_spec(globals, spec=spec)


    '''
    Migration
    '''
    steps.create_target_APIs(globals)


if __name__ == "__main__":
    app()