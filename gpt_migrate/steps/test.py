from utils import prompt_constructor, llm_write_file, construct_relevant_files, find_and_replace_file
from config import HIERARCHY, GUIDELINES, WRITE_CODE, CREATE_TESTS, SINGLEFILE
import subprocess
import typer
import os
import time as time
from yaspin import yaspin
from steps.debug import require_human_intervention

def run_dockerfile(globals):
    try:
        with yaspin(text="Spinning up Docker container...", spinner="dots") as spinner:
            result = subprocess.run(["docker", "build", "-t", "gpt-migrate", globals.targetdir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, text=True)
            subprocess.run(["docker", "rm", "-f", "gpt-migrate"])
            process = subprocess.Popen(["docker", "run", "-d", "-p", "8080:8080", "--name", "gpt-migrate", "gpt-migrate"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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
        
def create_tests(testfile,globals):

    # Makedir gpt_migrate in targetdir if it doesn't exist
    if not os.path.exists(os.path.join(globals.targetdir, 'gpt_migrate')):
        os.makedirs(os.path.join(globals.targetdir, 'gpt_migrate'))

    old_file_content = ""
    with open(os.path.join(globals.sourcedir, testfile), 'r') as file:
        old_file_content = file.read()

    create_tests_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, CREATE_TESTS, SINGLEFILE)

    prompt = create_tests_template.format(targetport=globals.targetport,
                                          old_file_content=old_file_content,
                                          guidelines=globals.guidelines)

    _, _, file_content = llm_write_file(prompt,
                                        target_path=f"gpt_migrate/{testfile}.tests.py",
                                        waiting_message="Creating tests file...",
                                        success_message=f"Created {testfile}.tests.py file in directory gpt_migrate.",
                                        globals=globals)
    return f"{testfile}.tests.py"

def validate_tests(testfile,globals):
    try:
        with yaspin(text="Validating tests...", spinner="dots") as spinner:
            # find all instances of globals.targetport in the testfile and replace with the port number globals.sourceport
            find_and_replace_file(os.path.join(globals.targetdir, f"gpt_migrate/{testfile}"), str(globals.targetport), str(globals.sourceport))
            time.sleep(0.3)
            result = subprocess.run(["python3", os.path.join(globals.targetdir,f"gpt_migrate/{testfile}")], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, text=True, timeout=15)
            spinner.ok("✅ ")
        print(result.stdout)
        find_and_replace_file(os.path.join(globals.targetdir, f"gpt_migrate/{testfile}"), str(globals.sourceport), str(globals.targetport))
        typer.echo(typer.style(f"Tests validated successfully on your source app.", fg=typer.colors.GREEN))
        return "success"
    except subprocess.CalledProcessError as e:
        find_and_replace_file(os.path.join(globals.targetdir, f"gpt_migrate/{testfile}"), str(globals.sourceport), str(globals.targetport))
        print("ERROR: ",e.output)
        error_message = e.output
        error_text = typer.style(f"Validating {testfile} against your existing service failed. Please take a look at the error message and try to resolve the issue. Once these are resolved, you can resume your progress with the `--step test` flag.", fg=typer.colors.RED)
        typer.echo(error_text)

        if typer.confirm("Would you like GPT-Migrate to try to fix this?"):
            return error_message
        else:
            tests_content = ""
            with open(os.path.join(globals.targetdir, f"gpt_migrate/{testfile}"), 'r') as file:
                tests_content = file.read()
            require_human_intervention(error_message,relevant_files=construct_relevant_files([(f"gpt_migrate/{testfile}", tests_content)]),globals=globals)
            raise typer.Exit()
    except subprocess.TimeoutExpired as e:
        print(f"gpt_migrate/{testfile} timed out due to an unknown error and requires debugging.")
        return f"gpt_migrate/{testfile} timed out due to an unknown error and requires debugging."

def run_test(testfile,globals):
    try:
        with yaspin(text="Running tests...", spinner="dots") as spinner:
            time.sleep(0.3)
            result = subprocess.run(["python3", os.path.join(globals.targetdir,f"gpt_migrate/{testfile}")], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, text=True, timeout=15)
            spinner.ok("✅ ")

        print(result.stdout)
        success_text = typer.style(f"Tests passed for {testfile}!", fg=typer.colors.GREEN)
        typer.echo(success_text)
        return "success"
    except subprocess.CalledProcessError as e:
        print("ERROR: ",e.output)
        error_message = e.output
        error_text = typer.style(f"One or more tests in {testfile} failed. Please take a look at the error message and try to resolve the issue. Once these are resolved, you can resume your progress with the `--step test` flag.", fg=typer.colors.RED)
        typer.echo(error_text)

        if typer.confirm("Would you like GPT-Migrate to try to fix this?"):
            return error_message
        else:
            tests_content = ""
            with open(os.path.join(globals.targetdir, f"gpt_migrate/{testfile}"), 'r') as file:
                tests_content = file.read()
            require_human_intervention(error_message,relevant_files=construct_relevant_files([(f"gpt_migrate/{testfile}", tests_content)]),globals=globals)
            raise typer.Exit()

    except subprocess.TimeoutExpired as e:
        print(f"gpt_migrate/{testfile} timed out due to an unknown error and requires debugging.")
        return f"gpt_migrate/{testfile} timed out due to an unknown error and requires debugging."


        