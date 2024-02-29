from pathlib import Path

from gpt_migrate.utils import prompt_constructor, llm_write_file
from gpt_migrate.config import (
    HIERARCHY,
    GUIDELINES,
    WRITE_CODE,
    CREATE_DOCKER,
    SINGLEFILE,
)


def create_environment(globals):
    """Create Dockerfile"""

    docker_prompt_template = prompt_constructor(
        HIERARCHY, GUIDELINES, WRITE_CODE, CREATE_DOCKER, SINGLEFILE
    )

    prompt = docker_prompt_template.format(
        targetlang=globals.targetlang,
        sourcelang=globals.sourcelang,
        sourceentry=globals.sourceentry,
        guidelines=globals.guidelines,
    )

    llm_write_file(
        prompt,
        target_path="Dockerfile",
        waiting_message="Creating your environment...",
        success_message=f"Created Docker environment for {globals.targetlang} project in directory '{globals.targetdir}'.",
        globals=globals,
    )

    memory_path = Path(__file__).parent / ".." / "memory"
    memory_path.mkdir(parents=True, exist_ok=True)
    external_dependencies_path = memory_path / "external_dependencies"
    with external_dependencies_path.open("w") as file:
        file.write("")
