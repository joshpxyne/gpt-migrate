import typer
from ai import AI
from utils import detect_language, format_directory_structure
import os
from yaspin import yaspin

app = typer.Typer()

@app.command()
def main(
    model: str = typer.Option("gpt-4-32k", help="Large Language Model to be used."),
    temperature: float = typer.Option(0.9, help="Temperature setting for the AI model."),
    sourcedir: str = typer.Option("../source", help="Source directory containing the API to be migrated."),
    sourcelang: str = typer.Option(None, help="Source language or framework of the API to be migrated."),
    targetdir: str = typer.Option("../target", help="directory containing the API to be migrated."),
    targetlang: str = typer.Option(..., help="Target language or framework for migration.")
):

    # Initialize AI instance
    ai = AI(
        model=model,
        temperature=temperature,
    )

    # Detect language and framework of the source project
    abs_sourcedir = os.path.abspath(sourcedir)
    abs_targetdir = os.path.abspath(targetdir)
    os.makedirs(abs_targetdir, exist_ok=True)

    typer.echo(f"Reading from directory '{abs_sourcedir}'")

    # Detect language of the source project
    detected_language = detect_language(abs_sourcedir) if not sourcelang else sourcelang

    # Ask the user to confirm detected language
    if not sourcelang:
        if detected_language:
            is_correct = typer.confirm(f"Is your source project a {detected_language} project?")
            if is_correct:
                sourcelang = detected_language
            else:
                sourcelang = typer.prompt("Please enter the correct language for the source project")
        else:
            sourcelang = typer.prompt("Unable to detect the language of the source project. Please enter it manually")

    typer.echo(f"Reading {sourcelang} project from directory '{sourcedir}'.")
    typer.echo(f"Outputting {targetlang} project to directory '{targetdir}'.")

    with open('steps/1_create_target_docker', 'r') as file:
        prompt_template = file.read().strip()

    # Format the prompt with the target language
    prompt = prompt_template.format(targetlang)


    '''
    STEP 1: Create a Dockerfile for the target project.
    '''

    with yaspin(text="Creating your environment...", spinner="dots") as spinner:
        # Run the AI model
        _, _, dockerfile_content = ai.write_code(prompt)[0]

        # Create the Dockerfile in the target directory
        with open(os.path.join(abs_targetdir, "Dockerfile"), "w") as file:
            file.write(dockerfile_content)
        
        # On success
        spinner.ok("✅ ")

    # Output text in color
    success_text = typer.style(f"Created Docker environment for {targetlang} project in directory '{abs_targetdir}'.", fg=typer.colors.GREEN, bold=True)
    typer.echo(success_text)



    '''
    STEP 2: Create an OpenAPI spec for the source project.
    '''
    
    dir_structure = format_directory_structure(abs_sourcedir)

    with open('steps/2a_identify_endpoint_files', 'r') as file:
        prompt_template = file.read().strip()

    # Change this line to use named placeholders
    prompt = prompt_template.format(dir_structure=dir_structure, sourcelang=sourcelang)

    # Feed the prompt to the AI model
    with yaspin(text="Analyzing directory structure...", spinner="dots") as spinner:
        relevant_files = ai.run(prompt)  # assuming ai.run() returns the model's response as a string
        spinner.ok("✅ ")

    # Output text in color
    info_text = typer.style(f"Relevant files for API endpoints: {relevant_files}", fg=typer.colors.BLUE)
    typer.echo(info_text)

    # If the AI could not find relevant files or user wants to provide custom files
    if relevant_files == "NONE FOUND" or not typer.confirm("Are these files correct?"):
        user_files = typer.prompt("Please input a comma-separated list of relevant filenames")
        relevant_files_list = [file.strip() for file in user_files.split(',')]
    else:
        relevant_files_list = [file.strip() for file in relevant_files.split(',')]

    with open('steps/2b_create_openapi_spec', 'r') as file:
        openapi_prompt_template = file.read().strip()

    # Loop through each file and generate the OpenAPI spec
    for file_name in relevant_files_list:
        # Read the content of the file
        file_path = os.path.join(abs_sourcedir, file_name)
        with open(file_path, 'r') as file:
            file_content = file.read()

        # Format the prompt with the file content
        prompt = openapi_prompt_template.format(file_content=file_content)

        # Feed the prompt to the AI model
        with yaspin(text=f"Generating OpenAPI spec for {file_name}...", spinner="dots") as spinner:
            _,_,openapi_spec = ai.write_code_openai(prompt)[0]
            spinner.ok("✅ ")

        # Save the OpenAPI spec to a file (you can choose the filename and directory)
        output_filename = f"{file_name}_openapi.yaml"
        output_path = os.path.join(abs_targetdir, output_filename)
        with open(output_path, 'w') as output_file:
            output_file.write(openapi_spec)

        # Output text in color
        success_text = typer.style(f"Created OpenAPI spec for {file_name} at {output_path}", fg=typer.colors.GREEN)
        typer.echo(success_text)

    '''
    STEP 3: Port over new API endpoints to the target project using the Dockerfile as a guide.
    '''

    with open(abs_targetdir+'/Dockerfile', 'r') as file:
        dockerfile_content = file.read().strip()

    with open('steps/3_create_endpoints', 'r') as file:
        prompt_template = file.read().strip()

    
    for file_name in relevant_files_list:
        # Read the content of the file
        file_path = os.path.join(abs_sourcedir, file_name)
        with open(file_path, 'r') as file:
            file_content = file.read()

        prompt = prompt_template.format(targetlang=targetlang,dockerfile_content=dockerfile_content,sourcefile_content=file_content)
        with yaspin(text=f"Generating APIs...", spinner="dots") as spinner:
            code_completions = ai.write_code_openai(prompt)
            
        print(code_completions)

        for code_completion in code_completions:
            output_filename,_,output_file_content = code_completion

            output_path = os.path.join(abs_targetdir, output_filename)
            with open(output_path, 'w') as output_file:
                output_file.write(output_file_content)

        # Output text in color
        spinner.ok("✅ ")
        success_text = typer.style(f"Created API endpoints for {file_name} at {output_path}", fg=typer.colors.GREEN)
        typer.echo(success_text)

    '''
    STEP 4: Add any necessary requirements to the target project.
    '''
    

if __name__ == "__main__":
    app()