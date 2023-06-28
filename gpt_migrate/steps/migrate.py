from utils import prompt_constructor, llm_write_file, llm_run, build_directory_structure
from config import HIERARCHY, GUIDELINES, WRITE_CODE, GET_EXTERNAL_DEPS, GET_INTERNAL_DEPS, WRITE_MIGRATION, SINGLEFILE
import os


def get_dependencies(sourcefile,globals):

    '''Get external and internal dependencies of source file'''

    external_deps_prompt_template = prompt_constructor(HIERARCHY, GUIDELINES, GET_EXTERNAL_DEPS)
    internal_deps_prompt_template = prompt_constructor(HIERARCHY, GUIDELINES, GET_INTERNAL_DEPS)

    sourcefile_content = ""
    with open(os.path.join(globals.sourcedir, sourcefile), 'r') as file:
        sourcefile_content = file.read()
    
    prompt = external_deps_prompt_template.format(targetlang=globals.targetlang, 
                                                    sourcelang=globals.sourcelang, 
                                                    sourcefile_content=sourcefile_content)

    external_dependencies = llm_run(prompt,
                            waiting_message=f"Getting external dependencies for {sourcefile}...",
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
                            waiting_message=f"Getting internal dependencies for {sourcefile}...",
                            success_message=None,
                            globals=globals)
    
    internal_deps_list = []
    if internal_dependencies!="NONE":
        internal_deps_list = internal_dependencies.split(',')
    
    return internal_deps_list, external_deps_list
                    
def write_migration(sourcefile, external_deps_list, globals):

    '''Write migration file'''
    
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
                    waiting_message=f"Writing migration file for {sourcefile}...",
                    success_message=None,
                    globals=globals)