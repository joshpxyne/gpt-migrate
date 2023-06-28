import typer
from utils import detect_language, build_directory_structure
import os

from steps.environment import create_environment
from steps.migrate import get_dependencies, write_migration

import time as time

from ai import AI

app = typer.Typer()

class Globals:
    def __init__(self, sourcedir, targetdir, sourcelang, targetlang, sourceentry, source_directory_structure, ai):
        self.sourcedir = sourcedir
        self.targetdir = targetdir
        self.sourcelang = sourcelang
        self.targetlang = targetlang
        self.sourceentry = sourceentry
        self.source_directory_structure = source_directory_structure
        self.ai = ai
        

@app.command()
def main(
        model: str = typer.Option("gpt-4-32k", help="Large Language Model to be used."),
        temperature: float = typer.Option(0, help="Temperature setting for the AI model."),
        sourcedir: str = typer.Option("../benchmarks/multi_endpoint/flask-nodejs/source", help="Source directory containing the code to be migrated."),
        sourcelang: str = typer.Option(None, help="Source language or framework of the code to be migrated."),
        sourceentry: str = typer.Option("app.py", help="Entrypoint filename relative to the source directory. For instance, this could be an app.py or main.py file for Python."),
        targetdir: str = typer.Option("../benchmarks/multi_endpoint/flask-nodejs/target", help="Directory where the migrated code will live."),
        targetlang: str = typer.Option("nodejs", help="Target language or framework for migration.")
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

    if not os.path.exists(os.path.join(sourcedir, sourceentry)):
        sourceentry = typer.prompt("Unable to find the entrypoint file. Please enter it manually. This must be a file relative to the source directory.")

    source_directory_structure = build_directory_structure(sourcedir)
    globals = Globals(sourcedir, targetdir, sourcelang, targetlang, sourceentry, source_directory_structure, ai)

    typer.echo(typer.style(f"\n • Reading {sourcelang} project from directory '{sourcedir}', with entrypoint '{sourceentry}'.", fg=typer.colors.BLUE))
    time.sleep(0.3)
    typer.echo(typer.style(f"\n • Outputting {targetlang} project to directory '{targetdir}'.", fg=typer.colors.BLUE))
    time.sleep(0.3)
    typer.echo(typer.style("\n • Source directory structure: \n\n" + source_directory_structure, fg=typer.colors.BLUE))


    '''
    Setup
    '''
    create_environment(globals)

    '''
    Migration
    '''

    # recursively work through each of the files in the source directory, starting with the entrypoint.
    def migrate(sourcefile, globals):
        internal_deps_list, external_deps_list = get_dependencies(sourcefile=sourcefile,globals=globals)
        for dependency in internal_deps_list:
            migrate(dependency, globals)
        write_migration(sourcefile, external_deps_list, globals)

    migrate(sourceentry, globals)


if __name__ == "__main__":
    app()