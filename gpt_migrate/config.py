import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

HIERARCHY = "HIERARCHY"
GUIDELINES = "p1_guidelines/guidelines"
WRITE_CODE = "p2_actions/write_code"
CREATE_DOCKER = "p3_steps/1_create_target_docker"
GET_EXTERNAL_DEPS = "p3_steps/2_get_external_deps"
GET_INTERNAL_DEPS = "p3_steps/3_get_internal_deps"
WRITE_MIGRATION = "p3_steps/4_write_migration"
ADD_DOCKER_REQUIREMENTS = "p3_steps/5_add_docker_requirements"
MULTIFILE = "p4_output_formats/multi_file"
SINGLEFILE = "p4_output_formats/single_file"