import os
from collections import Counter

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