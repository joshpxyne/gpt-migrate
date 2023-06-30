from utils import prompt_constructor, llm_write_file, construct_relevant_files
from config import HIERARCHY, GUIDELINES, WRITE_CODE, CREATE_DOCKER, SINGLEFILE
import subprocess
import typer
import os
from yaspin import yaspin
from steps.debug import require_human_intervention

def run_dockerfile(globals):
    try:
        with yaspin(text="Spinning up Docker container...", spinner="dots") as spinner:
            result = subprocess.run(["docker", "build", "-t", "gpt-migrate", globals.targetdir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, text=True)
            print(result.stdout)
            subprocess.run(["docker", "rm", "-f", "gpt-migrate"])
            process = subprocess.Popen(["docker", "run", "-d", "-p", "8080:8080", "--name", "gpt-migrate", "gpt-migrate"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            # Print the first few lines of output
            for _ in range(10):
                print(process.stdout.readline())
            spinner.ok("✅ ")
        success_text = typer.style("Your Docker image is now running. GPT-Migrate will now start testing, and you can independently test as well. The application is exposed on port 8080.", fg=typer.colors.GREEN)
        typer.echo(success_text)
        return "success"
    except subprocess.CalledProcessError as e:
        print("ERROR: ",e.output)
        error_message = e.output
        error_text = typer.style("Something isn't right with Docker. Please ensure Docker is running and take a look over the Dockerfile; there may be errors. Once these are resolved, you can resume your progress with the `--step test` flag.", fg=typer.colors.RED)
        typer.echo(error_text)

        # have typer ask if the user would like to use AI to fix it? If so, call function fix(). if not, raise typer.Exit()
        if typer.confirm("Would you like GPT-Migrate to try to fix this?"):
            return error_message
        else:
            dockerfile_content = ""
            with open(os.path.join(globals.targetdir, 'Dockerfile'), 'r') as file:
                dockerfile_content = file.read()
            require_human_intervention(error_message,relevant_files=construct_relevant_files([("Dockerfile", dockerfile_content)]),globals=globals)
            raise typer.Exit()



        