import os
import typer
from yaspin import yaspin
from collections import Counter
import fnmatch
import re
import shutil

def detect_language(source_directory):

    file_extensions = []

    for filenames in os.walk(source_directory):
        for filename in filenames[2]:
            ext = filename.split('.')[-1]
            file_extensions.append(ext)
    
    extension_counts = Counter(file_extensions)
    most_common_extension, _ = extension_counts.most_common(1)[0]
    
    extension_to_language = {
        'py': 'Python',
        'js': 'JavaScript',
        'java': 'Java',
        'rb': 'Ruby',
        'php': 'PHP',
        'cs': 'C#',
        'go': 'Go',
        'rs': 'Rust',
        'cpp': 'C++',
        'cc': 'C++',
        'cxx': 'C++',
        'c': 'C',
        'swift': 'Swift',
        'm': 'Objective-C',
        'kt': 'Kotlin',
        'scala': 'Scala',
        'pl': 'Perl',
        'pm': 'Perl',
        'r': 'R',
        'lua': 'Lua',
        'groovy': 'Groovy',
        'ts': 'TypeScript',
        'tsx': 'TypeScript',
        'jsx': 'JavaScript',
        'dart': 'Dart',
        'elm': 'Elm',
        'erl': 'Erlang',
        'ex': 'Elixir',
        'fs': 'F#',
        'hs': 'Haskell',
        'jl': 'Julia',
        'nim': 'Nim',
        'php': 'PHP',
}
    
    # Determine the language based on the most common file extension
    language = extension_to_language.get(most_common_extension)
    
    return language

def prompt_constructor(*args):
    prompt = ""
    for arg in args:
        with open(os.path.abspath(f'prompts/{arg}'), 'r') as file:
            prompt += file.read().strip()
    return prompt

def llm_run(prompt,waiting_message,success_message,globals):
    
    output = ""
    with yaspin(text=waiting_message, spinner="dots") as spinner:
        output = globals.ai.run(prompt)
        spinner.ok("✅ ")

    if success_message:
        success_text = typer.style(success_message, fg=typer.colors.GREEN)
        typer.echo(success_text)
    
    return output

def llm_write_file(prompt,target_path,waiting_message,success_message,globals):
    
    file_content = ""
    with yaspin(text=waiting_message, spinner="dots") as spinner:
        file_name,language,file_content = globals.ai.write_code(prompt)[0]
        spinner.ok("✅ ")

    if target_path:
        with open(os.path.join(globals.targetdir, target_path), 'w') as file:
            file.write(file_content)
    else:
        with open(os.path.join(globals.targetdir, file_name), 'w') as file:
            file.write(file_content)

    if success_message:
        success_text = typer.style(success_message, fg=typer.colors.GREEN)
        typer.echo(success_text)
    else:
        success_text = typer.style(f"Created {file_name} at {globals.targetdir}", fg=typer.colors.GREEN)
        typer.echo(success_text)
    
    return file_name, language, file_content

def llm_write_files(prompt,target_path,waiting_message,success_message,globals):
    
    file_content = ""
    with yaspin(text=waiting_message, spinner="dots") as spinner:
        results = globals.ai.write_code(prompt)
        spinner.ok("✅ ")

    for result in results:
        file_name,language,file_content = result

        if target_path:
            with open(os.path.join(globals.targetdir, target_path), 'w') as file:
                file.write(file_content)
        else:
            with open(os.path.join(globals.targetdir, file_name), 'w') as file:
                file.write(file_content)

        if not success_message:
            success_text = typer.style(f"Created {file_name} at {globals.targetdir}", fg=typer.colors.GREEN)
            typer.echo(success_text)
    if success_message:
        success_text = typer.style(success_message, fg=typer.colors.GREEN)
        typer.echo(success_text)
    
    return results

def load_templates_from_directory(directory_path):
    templates = {}
    for filename in os.listdir(directory_path):
        with open(os.path.join(directory_path, filename), 'r') as file:
            key = os.path.splitext(filename)[0]
            templates[key] = file.read()
    return templates

def parse_code_string(code_string):
    sections = code_string.split('---')
    
    pattern = re.compile(r'^(.+)\n```(.+?)\n(.*?)\n```', re.DOTALL)
    
    code_triples = []

    for section in sections:
        match = pattern.match(section)
        if match:
            filename, language, code = match.groups()
            code_triples.append((section.split("\n```")[0], language.strip(), code.strip()))
    
    return code_triples

def read_gitignore(path):
    gitignore_path = os.path.join(path, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def is_ignored(entry, gitignore_patterns):
    for pattern in gitignore_patterns:
        if fnmatch.fnmatch(entry, pattern):
            return True
    return False

def build_directory_structure(path='.', indent='', is_last=True, parent_prefix='', is_root=True):
    gitignore_patterns = read_gitignore(path) + [".gitignore"] if indent == '' else []

    base_name = os.path.basename(path)

    if not base_name:
        base_name = '.'

    if indent == '':
        prefix = '|-- ' if not is_root else ''
    elif is_last:
        prefix = parent_prefix + '└── '
    else:
        prefix = parent_prefix + '├── '

    if os.path.isdir(path):
        result = indent + prefix + base_name + '/\n' if not is_root else ''
    else:
        result = indent + prefix + base_name + '\n'

    if os.path.isdir(path):
        entries = os.listdir(path)
        for index, entry in enumerate(entries):
            entry_path = os.path.join(path, entry)
            new_parent_prefix = '    ' if is_last else '│   '
            if not is_ignored(entry, gitignore_patterns):
                result += build_directory_structure(entry_path, indent + '    ', index == len(entries) - 1, parent_prefix + new_parent_prefix, is_root=False)

    return result

def copy_files(sourcedir, targetdir, excluded_files=[]):
    gitignore_patterns = read_gitignore(sourcedir) + [".gitignore"]
    for item in os.listdir(sourcedir):
        if os.path.isfile(os.path.join(sourcedir, item)):
            if item.endswith(('.env', '.txt', '.json', '.yml', '.yaml')) and item not in excluded_files:
                if not is_ignored(item, gitignore_patterns):
                    os.makedirs(targetdir, exist_ok=True)
                    shutil.copy(os.path.join(sourcedir, item), targetdir)
                    typer.echo(typer.style(f"Copied {item} from {sourcedir} to {targetdir}", fg=typer.colors.GREEN))
        else:
            copy_files(os.path.join(sourcedir, item), os.path.join(targetdir, item))