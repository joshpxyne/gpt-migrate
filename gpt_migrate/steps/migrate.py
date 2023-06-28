from utils import prompt_constructor, llm_write_file, llm_write_files, llm_run, build_directory_structure, copy_files
from config import HIERARCHY, GUIDELINES, WRITE_CODE, GET_EXTERNAL_DEPS, GET_INTERNAL_DEPS, ADD_DOCKER_REQUIREMENTS, WRITE_MIGRATION, SINGLEFILE, MULTIFILE
import os


def get_dependencies(sourcefile,globals):

    ''' Get external and internal dependencies of source file '''

    external_deps_prompt_template = prompt_constructor(HIERARCHY, GUIDELINES, GET_EXTERNAL_DEPS)
    internal_deps_prompt_template = prompt_constructor(HIERARCHY, GUIDELINES, GET_INTERNAL_DEPS)

    sourcefile_content = ""
    with open(os.path.join(globals.sourcedir, sourcefile), 'r') as file:
        sourcefile_content = file.read()
    
    prompt = external_deps_prompt_template.format(targetlang=globals.targetlang, 
                                                    sourcelang=globals.sourcelang, 
                                                    sourcefile_content=sourcefile_content)

    external_dependencies = llm_run(prompt,
                            waiting_message=f"Identifying external dependencies for {sourcefile}...",
                            success_message=None,
                            globals=globals)
    
    external_deps_list = []
    if external_dependencies!="NONE":
        external_deps_list = external_dependencies.split(',')
    with open('memory/external_dependencies', 'a+') as file:
        for dependency in external_deps_list:
            if dependency not in file.read():
                file.write(dependency+'\n')

    prompt = internal_deps_prompt_template.format(targetlang=globals.targetlang,
                                                    sourcelang=globals.sourcelang,
                                                    sourcefile=sourcefile,
                                                    sourcefile_content=sourcefile_content,
                                                    source_directory_structure=globals.source_directory_structure)
    
    internal_dependencies = llm_run(prompt,
                            waiting_message=f"Identifying internal dependencies for {sourcefile}...",
                            success_message=None,
                            globals=globals)
    
    internal_deps_list = []
    if internal_dependencies!="NONE":
        internal_deps_list = internal_dependencies.split(',')
    
    return internal_deps_list, external_deps_list
                    
def write_migration(sourcefile, external_deps_list, globals):

    ''' Write migration file '''
    
    write_migration_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, WRITE_MIGRATION, SINGLEFILE)

    sourcefile_content = ""
    with open(os.path.join(globals.sourcedir, sourcefile), 'r') as file:
        sourcefile_content = file.read()
    
    prompt = write_migration_template.format(targetlang=globals.targetlang,
                                                sourcelang=globals.sourcelang,
                                                sourcefile=sourcefile,
                                                sourcefile_content=sourcefile_content,
                                                external_deps=','.join(external_deps_list),
                                                source_directory_structure=globals.source_directory_structure,
                                                target_directory_structure=build_directory_structure(globals.targetdir))

    llm_write_file(prompt,
                    target_path=None,
                    waiting_message=f"Creating migration file for {sourcefile}...",
                    success_message=None,
                    globals=globals)
    
def add_env_files(globals):

    ''' Copy all files recursively with the extensions .env, .txt, .json, .yml, .yaml, or no extension from the source directory to the target directory in the same relative structure '''

    copy_files(globals.sourcedir, globals.targetdir, excluded_files=['requirements.txt', 'Dockerfile', 'package.json', 'package-lock.json', 'yarn.lock', 'node_modules/'])

    ''' Add files required from the Dockerfile '''

    add_docker_requirements_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, ADD_DOCKER_REQUIREMENTS, SINGLEFILE)

    dockerfile_content = ""
    with open(os.path.join(globals.targetdir, 'Dockerfile'), 'r') as file:
        dockerfile_content = file.read()
    
    external_deps = ""
    with open('memory/external_dependencies', 'r') as file:
        external_deps = file.read()

    prompt = add_docker_requirements_template.format(dockerfile_content=dockerfile_content,
                                                        external_deps=external_deps)

    llm_write_file(prompt,
                    target_path=None,
                    waiting_message=f"Creating dependencies file required for the Docker environment...",
                    success_message=None,
                    globals=globals)
    
    