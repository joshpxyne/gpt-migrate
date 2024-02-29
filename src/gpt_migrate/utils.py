import os
from pathlib import Path
from collections import Counter

import typer
from yaspin import yaspin
import fnmatch
import re
import shutil

from gpt_migrate.config import INCLUDED_EXTENSIONS, EXTENSION_TO_LANGUAGE


def detect_language(source_directory):
    file_extensions = []

    for filenames in os.walk(source_directory):
        for filename in filenames[2]:
            ext = filename.split(".")[-1]
            file_extensions.append(ext)

    extension_counts = Counter(file_extensions)
    most_common_extension, _ = extension_counts.most_common(1)[0]

    # Determine the language based on the most common file extension
    language = EXTENSION_TO_LANGUAGE.get(most_common_extension, None)

    return language


def prompt_constructor(*args):
    prompt = ""
    current_file_dir = os.path.dirname(__file__)
    for arg in args:
        file_path = os.path.join(current_file_dir, "prompts", arg)
        with open(file_path, "r") as file:
            prompt += file.read().strip()
    return prompt


def llm_run(prompt, waiting_message, success_message, globals):
    output = ""
    with yaspin(text=waiting_message, spinner="dots") as spinner:
        output = globals.ai.run(prompt)
        spinner.ok("✅ ")

    if success_message:
        success_text = typer.style(success_message, fg=typer.colors.GREEN)
        typer.echo(success_text)

    return output


def llm_write_file(prompt, target_path, waiting_message, success_message, globals):
    file_content = ""
    with yaspin(text=waiting_message, spinner="dots") as spinner:
        file_name, language, file_content = globals.ai.write_code(prompt)[0]
        spinner.ok("✅ ")

    if file_name == "INSTRUCTIONS:":
        return "INSTRUCTIONS:", "", file_content

    full_path = os.path.join(globals.targetdir, target_path or file_name)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w") as file:
        file.write(file_content)

    if success_message:
        success_text = typer.style(success_message, fg=typer.colors.GREEN)
        typer.echo(success_text)
    else:
        success_text = typer.style(
            f"Created {file_name} at {globals.targetdir}", fg=typer.colors.GREEN
        )
        typer.echo(success_text)

    return file_name, language, file_content


def llm_write_files(prompt, target_path, waiting_message, success_message, globals):
    file_content = ""
    with yaspin(text=waiting_message, spinner="dots") as spinner:
        results = globals.ai.write_code(prompt)
        spinner.ok("✅ ")

    for result in results:
        file_name, language, file_content = result

        full_path = os.path.join(globals.targetdir, target_path or file_name)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w") as file:
            file.write(file_content)

        if not success_message:
            success_text = typer.style(
                f"Created {file_name} at {globals.targetdir}", fg=typer.colors.GREEN
            )
            typer.echo(success_text)
    if success_message:
        success_text = typer.style(success_message, fg=typer.colors.GREEN)
        typer.echo(success_text)

    return results


def load_templates_from_directory(directory_path):
    templates = {}
    for filename in os.listdir(directory_path):
        with open(os.path.join(directory_path, filename), "r") as file:
            key = os.path.splitext(filename)[0]
            templates[key] = file.read()
    return templates


def parse_code_string(code_string):
    sections = code_string.split("---")

    pattern = re.compile(r"^(.+)\n```(.+?)\n(.*?)\n```", re.DOTALL)

    code_triples = []

    for section in sections:
        match = pattern.match(section)
        if match:
            filename, language, code = match.groups()
            code_triples.append(
                (section.split("\n```")[0], language.strip(), code.strip())
            )

    return code_triples


def read_gitignore(path):
    gitignore_path = os.path.join(path, ".gitignore")
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns


def is_ignored(entry_path, gitignore_patterns):
    for pattern in gitignore_patterns:
        if fnmatch.fnmatch(entry_path, pattern):
            return True
    return False


def build_directory_structure(
    path=".", indent="", is_last=True, parent_prefix="", is_root=True
):
    gitignore_patterns = (
        read_gitignore(path) + [".gitignore", "*gpt_migrate/*"]
        if indent == ""
        else ["*gpt_migrate/*"]
    )

    base_name = os.path.basename(path)

    if not base_name:
        base_name = "."

    if indent == "":
        prefix = "|-- " if not is_root else ""
    elif is_last:
        prefix = parent_prefix + "└── "
    else:
        prefix = parent_prefix + "├── "

    if os.path.isdir(path):
        result = indent + prefix + base_name + "/\n" if not is_root else ""
    else:
        result = indent + prefix + base_name + "\n"

    if os.path.isdir(path):
        entries = os.listdir(path)
        for index, entry in enumerate(entries):
            entry_path = os.path.join(path, entry)
            new_parent_prefix = "    " if is_last else "│   "
            if not is_ignored(entry_path, gitignore_patterns):
                result += build_directory_structure(
                    entry_path,
                    indent + "    ",
                    index == len(entries) - 1,
                    parent_prefix + new_parent_prefix,
                    is_root=False,
                )

    return result


def copy_files(sourcedir, targetdir, excluded_files=[]):
    gitignore_patterns = read_gitignore(sourcedir) + [".gitignore"]
    for item in os.listdir(sourcedir):
        if os.path.isfile(os.path.join(sourcedir, item)):
            if item.endswith(INCLUDED_EXTENSIONS) and item not in excluded_files:
                if not is_ignored(item, gitignore_patterns):
                    os.makedirs(targetdir, exist_ok=True)
                    shutil.copy(os.path.join(sourcedir, item), targetdir)
                    typer.echo(
                        typer.style(
                            f"Copied {item} from {sourcedir} to {targetdir}",
                            fg=typer.colors.GREEN,
                        )
                    )
        else:
            copy_files(os.path.join(sourcedir, item), os.path.join(targetdir, item))


def construct_relevant_files(files):
    ret = ""
    for file in files:
        name = file[0]
        content = file[1]
        ret += name + ":\n\n" + "```\n" + content + "\n```\n\n"
    return ret


def file_exists_in_memory(filename):
    current_file_dir = Path(__file__).parent
    file_path = current_file_dir / "memory" / filename
    return file_path.exists()


def convert_sigs_to_string(sigs):
    sig_string = ""
    for sig in sigs:
        sig_string += sig["signature"] + "\n" + sig["description"] + "\n\n"
    return sig_string


def write_to_memory(filename, content):
    directory = os.path.join(os.path.dirname(__file__), "memory")
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    with open(file_path, "a+") as file:
        file.seek(0)
        existing_content = set(file.read().split("\n"))
        for item in content:
            if item not in existing_content:
                file.write(item + "\n")


def read_from_memory(filename):
    file_path = os.path.join(os.path.dirname(__file__), "memory", filename)
    with open(file_path, "r") as file:
        content = file.read()
    return content


def find_and_replace_file(filepath, find, replace):
    with open(filepath, "r") as file:
        testfile_content = file.read()
    testfile_content = testfile_content.replace(find, replace)
    with open(filepath, "w") as file:
        file.write(testfile_content)
