import typer
import os
from yaspin import yaspin

from utils import format_directory_structure

PREFERENCES = "PREFERENCES"
GUIDELINES = "p1_guidelines/guidelines"
WRITE_CODE = "p2_actions/write_code"
CREATE_DOCKER = "p3_steps/1_create_target_docker"
IDENTIFY_ENDPOINT_FILES = "p3_steps/2a_identify_endpoint_files"
CREATE_SPEC = "p3_steps/2b_create_spec"
CREATE_ENDPOINTS = "p3_steps/3_create_endpoints"
FILENAMES = "p4_output_formats/filenames"
MULTIFILE = "p4_output_formats/multi_file"
SINGLEFILE = "p4_output_formats/single_file"

def prompt_constructor(*args):
    prompt = ""
    for arg in args:
        with open(os.path.abspath(f'prompts/{arg}'), 'r') as file:
            prompt += file.read().strip()
    return prompt

def create_environment(globals):

    docker_prompt_template = prompt_constructor(PREFERENCES, 
                                                GUIDELINES, 
                                                WRITE_CODE, 
                                                CREATE_DOCKER, 
                                                SINGLEFILE)
    prompt = docker_prompt_template.format(targetlang=globals.targetlang)

    with yaspin(text="Creating your environment...", spinner="dots") as spinner:
        _, _, dockerfile_content = globals.ai.write_code(prompt)[0]
        with open(os.path.join(globals.targetdir, "Dockerfile"), "w") as file:
            file.write(dockerfile_content)
        spinner.ok("✅ ")

    success_text = typer.style(f"Created Docker environment for {globals.targetlang} project in directory '{globals.targetdir}'.", fg=typer.colors.GREEN, bold=True)
    typer.echo(success_text)

def create_io_spec(globals, spec="OpenAPI"):
    dir_structure = format_directory_structure(globals.sourcedir)

    identify_endpoints_prompt_template = prompt_constructor(PREFERENCES,
                                                            GUIDELINES,
                                                            IDENTIFY_ENDPOINT_FILES,
                                                            FILENAMES)

    prompt = identify_endpoints_prompt_template.format(dir_structure=dir_structure, sourcelang=globals.sourcelang)

    with yaspin(text="Analyzing directory structure...", spinner="dots") as spinner:
        relevant_files = globals.ai.run(prompt)
        spinner.ok("✅ ")

    info_text = typer.style(f"Relevant files for API endpoints: {relevant_files}", fg=typer.colors.BLUE)
    typer.echo(info_text)

    if relevant_files == "NONE FOUND" or not typer.confirm("Are these files correct?"):
        user_files = typer.prompt("Please input a comma-separated list of relevant filenames")
        relevant_files_list = [file.strip() for file in user_files.split(',')]
    else:
        relevant_files_list = [file.strip() for file in relevant_files.split(',')]

    with open('memory/fileslist', 'w') as file:
        file.write('\n'.join(relevant_files_list))

    spec_prompt_template = prompt_constructor(PREFERENCES,
                                                GUIDELINES,
                                                WRITE_CODE,
                                                CREATE_SPEC,
                                                SINGLEFILE)

    for file_name in relevant_files_list:
        file_path = os.path.join(globals.sourcedir, file_name)
        with open(file_path, 'r') as file:
            file_content = file.read()

        prompt = spec_prompt_template.format(file_content=file_content,spec=spec)
        print(prompt)

        with yaspin(text=f"Generating {spec} spec for {file_name}...", spinner="dots") as spinner:
            _,_,openapi_spec = globals.ai.write_code_openai(prompt)[0]
            spinner.ok("✅ ")

        output_filename = f"{spec}_{file_name}.yaml"
        output_path = os.path.join(globals.targetdir, output_filename)
        with open(output_path, 'w') as output_file:
            output_file.write(openapi_spec)

        success_text = typer.style(f"Created {spec} spec for {file_name} at {output_path}", fg=typer.colors.GREEN)
        typer.echo(success_text)

def create_target_APIs(globals):

    with open('memory/fileslist', 'r') as file:
        relevant_files_list = file.read().split('\n')

    with open(globals.targetdir+'/Dockerfile', 'r') as file:
        dockerfile_content = file.read().strip()

    create_endpoints_prompt_template = prompt_constructor(PREFERENCES,
                                                            GUIDELINES,
                                                            WRITE_CODE,
                                                            CREATE_ENDPOINTS,
                                                            MULTIFILE)

    
    for file_name in relevant_files_list:
        # Read the content of the file
        file_path = os.path.join(globals.sourcedir, file_name)
        with open(file_path, 'r') as file:
            file_content = file.read()

        prompt = create_endpoints_prompt_template.format(targetlang=globals.targetlang,dockerfile_content=dockerfile_content,sourcefile_content=file_content)
        with yaspin(text=f"Generating APIs...", spinner="dots") as spinner:
            code_completions = globals.ai.write_code_openai(prompt)
            
        print(code_completions)

        for code_completion in code_completions:
            output_filename,_,output_file_content = code_completion

            output_path = os.path.join(globals.targetdir, output_filename)
            with open(output_path, 'w') as output_file:
                output_file.write(output_file_content)

        # Output text in color
        spinner.ok("✅ ")
        success_text = typer.style(f"Created API endpoints for {file_name} at {output_path}", fg=typer.colors.GREEN)
        typer.echo(success_text)
