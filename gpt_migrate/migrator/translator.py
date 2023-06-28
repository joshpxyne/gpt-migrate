from utils import prompt_constructor
from config import PREFERENCES, GUIDELINES, WRITE_CODE, CREATE_DOCKER, CREATE_DEPENDENCIES, IDENTIFY_ENDPOINT_FILES, CREATE_SPEC, CREATE_ENDPOINTS, MULTIFILE, SINGLEFILE, FILENAMES

class Translator:
    def __init__(self, intermediate_representation, target_language, ai):
        self.intermediate_representation = intermediate_representation
        self.target_language = target_language
        self.ai = ai

    def translate(self):
        translate_prompt_template = prompt_constructor(PREFERENCES,
                                                        GUIDELINES,
                                                        WRITE_CODE,
                                                        IDENTIFY_ENDPOINT_FILES,
                                                        MULTIFILE)

        prompt = translate_prompt_template.format(intermediate_representation=self.intermediate_representation,
                                                  target_language=self.target_language)

        translated_code = self.ai.run_openai(prompt)

        return translated_code