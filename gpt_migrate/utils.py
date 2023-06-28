import os
import typer
from yaspin import yaspin
from collections import Counter
import re

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

def format_directory_structure(directory, indent=0):
    structure = ""
    if os.path.isdir(directory):
        structure += "    " * indent + f"[Directory] {os.path.basename(directory)}\n"
        for item in os.listdir(directory):
            structure += format_directory_structure(os.path.join(directory, item), indent + 1)
    else:
        structure += "    " * indent + f"[File] {os.path.basename(directory)}\n"
    return structure

def prompt_constructor(*args):
    prompt = ""
    for arg in args:
        with open(os.path.abspath(f'prompts/{arg}'), 'r') as file:
            prompt += file.read().strip()
    return prompt

def write_code(prompt,target_path,waiting_message,success_message,globals):
    
    file_content = ""
    with yaspin(text=waiting_message, spinner="dots") as spinner:
        _,_,file_content = globals.ai.write_code_openai(prompt)[0]
        spinner.ok("✅ ")

    with open(os.path.join(globals.targetdir, target_path), 'w') as file:
        file.write(file_content)

    success_text = typer.style(success_message, fg=typer.colors.GREEN)
    typer.echo(success_text)
    
    return file_content

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