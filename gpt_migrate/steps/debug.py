from utils import prompt_constructor, llm_write_file, llm_run, build_directory_structure, construct_relevant_files
from config import HIERARCHY, GUIDELINES, WRITE_CODE, IDENTIFY_ACTION, MOVE_FILES, CREATE_FILE, IDENTIFY_FILE, DEBUG_FILE, DEBUG_TESTFILE, HUMAN_INTERVENTION, SINGLEFILE, FILENAMES, MAX_ERROR_MESSAGE_CHARACTERS, MAX_DOCKER_LOG_CHARACTERS
import os
import typer
import subprocess
    
def debug_error(error_message,relevant_files,globals):

    identify_action_template = prompt_constructor(HIERARCHY, GUIDELINES, IDENTIFY_ACTION)

    prompt = identify_action_template.format(error_message=error_message[-min(MAX_ERROR_MESSAGE_CHARACTERS, len(error_message)):],
                                                target_directory_structure=build_directory_structure(globals.targetdir))
    
    actions = llm_run(prompt,
                        waiting_message=f"Planning actions for debugging...",
                        success_message="",
                        globals=globals)
    
    action_list = actions.split(',')
    
    if "MOVE_FILES" in action_list:

        if not os.path.exists(os.path.join(globals.targetdir, 'gpt_migrate')):
            os.makedirs(os.path.join(globals.targetdir, 'gpt_migrate')) 

        move_files_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, MOVE_FILES, SINGLEFILE)

        prompt = move_files_template.format(error_message=error_message[-min(MAX_ERROR_MESSAGE_CHARACTERS, len(error_message)):],
                                              target_directory_structure=build_directory_structure(globals.targetdir),
                                              current_full_path=globals.targetdir,
                                              operating_system=globals.operating_system,
                                              guidelines=globals.guidelines)
        
        file_name, language, shell_script_content = llm_write_file(prompt,
                                                            target_path="gpt_migrate/debug.sh",
                                                            waiting_message=f"Writing shell script...",
                                                            success_message="Wrote debug.sh based on error message.",
                                                            globals=globals)
        
        # execute shell script from file_content using subprocess. Check with user using shell commands before executing.
        if typer.confirm("GPT-Migrate wants to run this shell script to debug your application, which is also stored in gpt_migrate/debug.sh: \n\n"+shell_script_content+"\n\nWould you like to run it?"):
            try:
                result = subprocess.run(["bash", "gpt_migrate/debug.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, text=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print("ERROR: ",e.output)
                error_message = e.output
                error_text = typer.style("Something isn't right with your shell script. Please ensure it is valid and try again.", fg=typer.colors.RED)
                typer.echo(error_text)
                raise typer.Exit()

    if "EDIT_FILES" in action_list:
        
        if relevant_files != "":
            fileslist = globals.testfiles.split(',')
            files_to_construct = []
            for file_name in fileslist:
                with open(os.path.join(globals.sourcedir, file_name), 'r') as file:
                    file_content = file.read()
                files_to_construct.append(("migration_source/"+file_name, file_content))
        
            relevant_files = construct_relevant_files(files_to_construct)

        identify_file_template = prompt_constructor(HIERARCHY, GUIDELINES, IDENTIFY_FILE, FILENAMES)

        docker_logs = subprocess.run(["docker", "logs", "gpt-migrate"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, text=True).stdout

        prompt = identify_file_template.format(error_message=error_message[-min(MAX_ERROR_MESSAGE_CHARACTERS, len(error_message)):],
                                                target_directory_structure=build_directory_structure(globals.targetdir),
                                                docker_logs=docker_logs[-min(MAX_DOCKER_LOG_CHARACTERS, len(docker_logs)):]),

        file_names = llm_run(prompt,
                                waiting_message=f"Identifying files to debug...",
                                success_message="",
                                globals=globals)
        
        file_name_list = file_names.split(',')
        for file_name in file_name_list:
            old_file_content = ""
            try:
                with open(os.path.join(globals.targetdir, file_name), 'r') as file:
                    old_file_content = file.read()
            except:
                print("File not found: "+file_name+". Please ensure the file exists and try again. You can resume the debugging process with the `--step test` flag.")
                raise typer.Exit()
        
            debug_file_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, DEBUG_FILE, SINGLEFILE)
            
            prompt = debug_file_template.format(error_message=error_message[-min(MAX_ERROR_MESSAGE_CHARACTERS, len(error_message)):],
                                                file_name=file_name,
                                                old_file_content=old_file_content,
                                                targetlang=globals.targetlang,
                                                sourcelang=globals.sourcelang,
                                                docker_logs=docker_logs[-min(MAX_DOCKER_LOG_CHARACTERS, len(docker_logs)):],
                                                relevant_files=relevant_files,
                                                guidelines=globals.guidelines),

            _, language, file_content = llm_write_file(prompt,
                                                        target_path=file_name,
                                                        waiting_message=f"Debugging {file_name}...",
                                                        success_message=f"Re-wrote {file_name} based on error message.",
                                                        globals=globals)
        
            new_file_content = ""
            with open(os.path.join(globals.targetdir, file_name), 'r') as file:
                new_file_content = file.read()
            
            if new_file_content==old_file_content:
                require_human_intervention(error_message,construct_relevant_files([(file_name, new_file_content)]),globals)

    if "CREATE_FILE" in action_list:

        create_file_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, CREATE_FILE, SINGLEFILE)

        prompt = create_file_template.format(error_message=error_message[-min(MAX_ERROR_MESSAGE_CHARACTERS, len(error_message)):],
                                                target_directory_structure=build_directory_structure(globals.targetdir),
                                                guidelines=globals.guidelines)

        new_file_name, language, file_content = llm_write_file(prompt,
                                                                waiting_message=f"Creating a new file...",
                                                                success_message="",
                                                                globals=globals)
        
        success_text = typer.style(f"Created new file {new_file_name}.", fg=typer.colors.GREEN)
        typer.echo(success_text)

def debug_testfile(error_message,testfile,globals):

    source_file_content = ""
    with open(os.path.join(globals.sourcedir, testfile), 'r') as file:
        source_file_content = file.read()
    
    relevant_files = construct_relevant_files([("migration_source/"+testfile, source_file_content)])

    file_name = f"gpt_migrate/{testfile}.tests.py"
    try:
        with open(os.path.join(globals.targetdir, file_name), 'r') as file:
            old_file_content = file.read()
    except:
        print("File not found: "+file_name+". Please ensure the file exists and try again. You can resume the debugging process with the `--step test` flag.")
        raise typer.Exit()

    debug_file_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, DEBUG_TESTFILE, SINGLEFILE)
    
    prompt = debug_file_template.format(error_message=error_message[-min(MAX_ERROR_MESSAGE_CHARACTERS, len(error_message)):],
                                        file_name=file_name,
                                        old_file_content=old_file_content,
                                        relevant_files=relevant_files,
                                        guidelines=globals.guidelines),

    _, language, file_content = llm_write_file(prompt,
                                                target_path=file_name,
                                                waiting_message=f"Debugging {file_name}...",
                                                success_message=f"Re-wrote {file_name} based on error message.",
                                                globals=globals)

    with open(os.path.join(globals.targetdir, file_name), 'r') as file:
        new_file_content = file.read()
    
    if new_file_content==old_file_content:
        require_human_intervention(error_message,construct_relevant_files([(file_name, new_file_content)]),globals)
    
def require_human_intervention(error_message,relevant_files,globals):

    human_intervention_template = prompt_constructor(HIERARCHY, GUIDELINES, WRITE_CODE, HUMAN_INTERVENTION, SINGLEFILE)
    
    prompt = human_intervention_template.format(error_message=error_message[-min(MAX_ERROR_MESSAGE_CHARACTERS, len(error_message)):],
                                                relevant_files=relevant_files,
                                                target_directory_structure=build_directory_structure(globals.targetdir),
                                                guidelines=globals.guidelines)
    
    instructions = llm_run(prompt,
                            waiting_message=f"Writing instructions for how to proceed...",
                            success_message="",
                            globals=globals)
    
    typer.echo(typer.style(f"GPT-Migrate is having some trouble debugging your app and requires human intervention. Below are instructions for how to fix your application.", fg=typer.colors.BLUE))
    print(instructions)
    typer.echo(typer.style(f"Once the fix is implemented, you can pick up from the testing phase using the `--step test` flag.", fg=typer.colors.BLUE))

    raise typer.Exit()