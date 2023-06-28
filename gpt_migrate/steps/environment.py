import typer
import os
from yaspin import yaspin

from utils import prompt_constructor
from utils import write_code

PREFERENCES = "PREFERENCES"
GUIDELINES = "p1_guidelines/guidelines"
WRITE_CODE = "p2_actions/write_code"
CREATE_DOCKER = "p3_steps/1a_create_target_docker"
CREATE_DEPENDENCIES = "p3_steps/1b_create_env_dependencies"
MULTIFILE = "p4_output_formats/multi_file"
SINGLEFILE = "p4_output_formats/single_file"


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