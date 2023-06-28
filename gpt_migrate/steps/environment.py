from utils import prompt_constructor, llm_write_file
import os

HIERARCHY = "HIERARCHY"
GUIDELINES = "p1_guidelines/guidelines"
WRITE_CODE = "p2_actions/write_code"
CREATE_DOCKER = "p3_steps/1_create_target_docker"
SINGLEFILE = "p4_output_formats/single_file"

def create_environment(globals):

    '''Create Dockerfile'''
    docker_prompt_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, CREATE_DOCKER, SINGLEFILE)
    
    prompt = docker_prompt_template.format(targetlang=globals.targetlang, 
                                           sourcelang=globals.sourcelang, 
                                           sourceentry=globals.sourceentry)

    llm_write_file(prompt,
                    target_path="Dockerfile",
                    waiting_message="Creating your environment...",
                    success_message=f"Created Docker environment for {globals.targetlang} project in directory '{globals.targetdir}'.",
                    globals=globals)
    
    with open('memory/dependencies', 'w') as file:
        file.write('')