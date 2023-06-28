from utils import prompt_constructor
from config import PREFERENCES, GUIDELINES, WRITE_CODE, CREATE_DOCKER, CREATE_DEPENDENCIES, IDENTIFY_ENDPOINT_FILES, CREATE_SPEC, CREATE_ENDPOINTS, MULTIFILE, SINGLEFILE, FILENAMES

class IntermediateRepresenter:
    def __init__(self, analyzed_data, ai):
        self.analyzed_data = analyzed_data
        self.ai = ai

    def create_ir(self):

        create_ir_prompt_template = prompt_constructor(PREFERENCES,
                                                        GUIDELINES,
                                                        WRITE_CODE,
                                                        IDENTIFY_ENDPOINT_FILES,
                                                        MULTIFILE)

        prompt = create_ir_prompt_template.format(analyzed_data=self.analyzed_data)

        ir = self.ai.run_openai(prompt)

        return ir