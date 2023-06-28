import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

PREFERENCES = "PREFERENCES"
GUIDELINES = "p1_guidelines/guidelines"
WRITE_CODE = "p2_actions/write_code"
CREATE_DOCKER = "p3_steps/1a_create_target_docker"
CREATE_DEPENDENCIES = "p3_steps/1b_create_env_dependencies"
IDENTIFY_ENDPOINT_FILES = "p3_steps/2a_identify_endpoint_files"
CREATE_SPEC = "p3_steps/2b_create_spec"
CREATE_ENDPOINTS = "p3_steps/3_create_endpoints"
FILENAMES = "p4_output_formats/filenames"
MULTIFILE = "p4_output_formats/multi_file"
SINGLEFILE = "p4_output_formats/single_file"