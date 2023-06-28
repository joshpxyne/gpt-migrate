import typer
import os
from yaspin import yaspin

from utils import prompt_constructor
from utils import write_code

PREFERENCES = "PREFERENCES"
GUIDELINES = "p1_guidelines/guidelines"
WRITE_CODE = "p2_actions/write_code"
CREATE_ENDPOINTS = "p3_steps/3_create_endpoints"
MULTIFILE = "p4_output_formats/multi_file"

def create_target_APIs(globals):

    with open('memory/fileslist', 'r') as file:
        relevant_files_list = file.read().split('\n')

    with open(globals.targetdir+'/Dockerfile', 'r') as file:
        dockerfile_content = file.read().strip()

    create_endpoints_prompt_template = prompt_constructor(PREFERENCES, GUIDELINES, WRITE_CODE, CREATE_ENDPOINTS, MULTIFILE)

    
    for file_name in relevant_files_list:
        file_path = os.path.join(globals.sourcedir, file_name)
        with open(file_path, 'r') as file:
            file_content = file.read()

        prompt = create_endpoints_prompt_template.format(targetlang=globals.targetlang,dockerfile_content=dockerfile_content,sourcefile_content=file_content)
        with yaspin(text=f"Generating APIs...", spinner="dots") as spinner:
            code_completions = globals.ai.write_code(prompt)
            
        print(code_completions)

        for code_completion in code_completions:
            output_filename,_,output_file_content = code_completion

            output_path = os.path.join(globals.targetdir, output_filename)
            with open(output_path, 'w') as output_file:
                output_file.write(output_file_content)

        spinner.ok("✅ ")
        success_text = typer.style(f"Created API endpoints for {file_name} at {output_path}", fg=typer.colors.GREEN)
        typer.echo(success_text)