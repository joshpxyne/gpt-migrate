import os

'''
Environment variables
'''
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

'''
Global variables
'''
MAX_ERROR_MESSAGE_CHARACTERS = 5000
MAX_DOCKER_LOG_CHARACTERS = 2000

'''
Prompt directory
'''
HIERARCHY = "HIERARCHY"
GUIDELINES = "p1_guidelines/guidelines"
WRITE_CODE = "p2_actions/write_code"
CREATE_DOCKER = "p3_setup/create_target_docker"
GET_EXTERNAL_DEPS = "p3_migrate/1_get_external_deps"
GET_INTERNAL_DEPS = "p3_migrate/2_get_internal_deps"
WRITE_MIGRATION = "p3_migrate/3_write_migration"
ADD_DOCKER_REQUIREMENTS = "p3_migrate/4_add_docker_requirements"
REFINE_DOCKERFILE = "p3_migrate/5_refine_target_docker"
CREATE_TESTS = "p3_test/create_tests"
DEBUG_DOCKERFILE = "p3_debug/debug_target_docker"
IDENTIFY_ACTION = "p3_debug/identify_action"
MOVE_FILES = "p3_debug/move_files"
CREATE_FILE = "p3_debug/create_file"
IDENTIFY_FILE = "p3_debug/identify_file"
DEBUG_FILE = "p3_debug/debug_file"
DEBUG_TESTFILE = "p3_debug/debug_testfile"
HUMAN_INTERVENTION = "p3_debug/human_intervention"
MULTIFILE = "p4_output_formats/multi_file"
SINGLEFILE = "p4_output_formats/single_file"
FILENAMES = "p4_output_formats/filenames"

'''
Living list of types of files that should be excluded from being copied over
'''
EXCLUDED_FILES = [
    # Docker
    'Dockerfile',

    # Python
    'requirements.txt', 
    '__pycache__/',

    # JS
    'package.json', 
    'package-lock.json', 
    'yarn.lock', 
    'node_modules/'

    # Rust
    'Cargo.toml'

    # TODO: add more
]

'''
Living list of file extensions that should be copied over
'''
INCLUDED_EXTENSIONS = (
    '.env', 
    '.txt', 
    '.json',
    '.csv',
    '.rdb',
    '.db'

    # TODO: add more
)

EXTENSION_TO_LANGUAGE = {
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