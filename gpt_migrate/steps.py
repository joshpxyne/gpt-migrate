import typer
import os
from yaspin import yaspin

from utils import format_directory_structure, prompt_constructor, write_code
from config import PREFERENCES, GUIDELINES, WRITE_CODE, CREATE_DOCKER, CREATE_DEPENDENCIES, IDENTIFY_ENDPOINT_FILES, CREATE_SPEC, CREATE_ENDPOINTS, MULTIFILE, SINGLEFILE, FILENAMES

CONTEXT_WINDOWS = {
    "gpt-4-32k": 32000,
    "gpt-3.5-turbo-16k": 16000,
    "gpt-4": 4000,
    "gpt-3.5-turbo": 4000,
}

def create_environment(globals):

    '''Create Dockerfile'''
    docker_prompt_template = prompt_constructor(PREFERENCES, 
                                                GUIDELINES, 
                                                WRITE_CODE, 
                                                CREATE_DOCKER, 
                                                SINGLEFILE)
    
    prompt = docker_prompt_template.format(targetlang=globals.targetlang)

    dockerfile_content = write_code(prompt,
                                    target_path="Dockerfile",
                                    waiting_message="Creating your environment...",
                                    success_message=f"Created Docker environment for {globals.targetlang} project in directory '{globals.targetdir}'.",
                                    globals=globals)

    '''Create related files'''
    dependencies_prompt_template = prompt_constructor(PREFERENCES,
                                                        GUIDELINES,
                                                        WRITE_CODE,
                                                        CREATE_DEPENDENCIES,
                                                        MULTIFILE)
    prompt = dependencies_prompt_template.format(dockerfile=dockerfile_content)


def create_io_spec(globals, spec="OpenAPI"):
    dir_structure = format_directory_structure(globals.sourcedir)

    identify_endpoints_prompt_template = prompt_constructor(PREFERENCES,
                                                            GUIDELINES,
                                                            IDENTIFY_ENDPOINT_FILES,
                                                            FILENAMES)

    prompt = identify_endpoints_prompt_template.format(dir_structure=dir_structure, sourcelang=globals.sourcelang)

    with yaspin(text="Analyzing directory structure...", spinner="dots") as spinner:
        relevant_files = globals.ai.run_openai(prompt)
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

        spinner.ok("✅ ")
        success_text = typer.style(f"Created API endpoints for {file_name} at {output_path}", fg=typer.colors.GREEN)
        typer.echo(success_text)
