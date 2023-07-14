from utils import prompt_constructor, llm_write_file, llm_run, build_directory_structure, copy_files, write_to_memory, read_from_memory, file_exists_in_memory, convert_sigs_to_string
from config import HIERARCHY, GUIDELINES, WRITE_CODE, GET_EXTERNAL_DEPS, GET_INTERNAL_DEPS, ADD_DOCKER_REQUIREMENTS, REFINE_DOCKERFILE, WRITE_MIGRATION, SINGLEFILE, EXCLUDED_FILES, GET_FUNCTION_SIGNATURES
from typing import List
import os
import json
import typer

def get_function_signatures(targetfiles: List[str], globals): 
    '''  Get the function signatures and a one-sentence summary for each function '''    
    all_sigs = []

    for targetfile in targetfiles:
        sigs_file_name = targetfile + "_sigs.json"

        if file_exists_in_memory(sigs_file_name):
            with open(os.path.join("memory", sigs_file_name), 'r') as f:
                sigs = json.load(f)
            all_sigs.extend(sigs)
        
        else:
            function_signatures_template = prompt_constructor(HIERARCHY, GUIDELINES, GET_FUNCTION_SIGNATURES)

            targetfile_content = ""
            with open(os.path.join(globals.targetdir, targetfile), 'r') as file:
                targetfile_content = file.read()
            
            prompt = function_signatures_template.format(targetlang=globals.targetlang,
                                                sourcelang=globals.sourcelang, 
                                                targetfile_content=targetfile_content)

            sigs = json.loads(llm_run(prompt,
                                    waiting_message=f"Parsing function signatures for {targetfile}...",
                                    success_message=None,
                                    globals=globals))
            
            all_sigs.extend(sigs)

            with open(os.path.join('memory', sigs_file_name), 'w') as f:
                json.dump(sigs, f)

    return all_sigs

def get_dependencies(sourcefile, globals):

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
    
    external_deps_list = external_dependencies.split(',') if external_dependencies != "NONE" else []
    write_to_memory("external_dependencies",external_deps_list)

    prompt = internal_deps_prompt_template.format(targetlang=globals.targetlang,
                                                    sourcelang=globals.sourcelang,
                                                    sourcefile=sourcefile,
                                                    sourcefile_content=sourcefile_content,
                                                    source_directory_structure=globals.source_directory_structure)
    
    internal_dependencies = llm_run(prompt,
                            waiting_message=f"Identifying internal dependencies for {sourcefile}...",
                            success_message=None,
                            globals=globals)
    
    # Sanity checking internal dependencies to avoid infinite loops 
    if sourcefile in internal_dependencies:
        typer.echo(typer.style(f"Warning: {sourcefile} seems to depend on itself. Automatically removing {sourcefile} from the list of internal dependencies.", fg=typer.colors.YELLOW))
        internal_dependencies = internal_dependencies.replace(sourcefile, "")
    
    internal_deps_list = [dep for dep in internal_dependencies.split(',') if dep] if internal_dependencies != "NONE" else []
    
    return internal_deps_list, external_deps_list
                    
def write_migration(sourcefile, external_deps_list, deps_per_file, globals) -> str:

    ''' Write migration file '''

    sigs = get_function_signatures(deps_per_file, globals) if deps_per_file else []
    
    write_migration_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, WRITE_MIGRATION, SINGLEFILE)

    sourcefile_content = ""
    with open(os.path.join(globals.sourcedir, sourcefile), 'r') as file:
        sourcefile_content = file.read()
    
    prompt = write_migration_template.format(targetlang=globals.targetlang,
                                                targetlang_function_signatures=convert_sigs_to_string(sigs),
                                                sourcelang=globals.sourcelang,
                                                sourcefile=sourcefile,
                                                sourcefile_content=sourcefile_content,
                                                external_deps=','.join(external_deps_list),
                                                source_directory_structure=globals.source_directory_structure,
                                                target_directory_structure=build_directory_structure(globals.targetdir),
                                                guidelines=globals.guidelines)
    
    return llm_write_file(prompt,
                    target_path=None,
                    waiting_message=f"Creating migration file for {sourcefile}...",
                    success_message=None,
                    globals=globals)[0]
    
def add_env_files(globals):

    ''' Copy all files recursively with included extensions from the source directory to the target directory in the same relative structure '''

    copy_files(globals.sourcedir, globals.targetdir, excluded_files=EXCLUDED_FILES)

    ''' Add files required from the Dockerfile '''

    add_docker_requirements_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, ADD_DOCKER_REQUIREMENTS, SINGLEFILE)

    dockerfile_content = ""
    with open(os.path.join(globals.targetdir, 'Dockerfile'), 'r') as file:
        dockerfile_content = file.read()
    
    external_deps = read_from_memory("external_dependencies")

    prompt = add_docker_requirements_template.format(dockerfile_content=dockerfile_content,
                                                        external_deps=external_deps,
                                                        target_directory_structure=build_directory_structure(globals.targetdir),
                                                        targetlang=globals.targetlang,
                                                        guidelines=globals.guidelines)

    external_deps_name, _, external_deps_content = llm_write_file(prompt,
                    target_path=None,
                    waiting_message=f"Creating dependencies file required for the Docker environment...",
                    success_message=None,
                    globals=globals)
    
    ''' Refine Dockerfile '''
    
    refine_dockerfile_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, REFINE_DOCKERFILE, SINGLEFILE)
    prompt = refine_dockerfile_template.format(dockerfile_content=dockerfile_content,
                                                target_directory_structure=build_directory_structure(globals.targetdir),
                                                external_deps_name=external_deps_name,
                                                external_deps_content=external_deps_content,
                                                guidelines=globals.guidelines)

    llm_write_file(prompt,
                    target_path="Dockerfile",
                    waiting_message=f"Refining Dockerfile based on dependencies required for the Docker environment...",
                    success_message="Refined Dockerfile with dependencies required for the Docker environment.",
                    globals=globals)