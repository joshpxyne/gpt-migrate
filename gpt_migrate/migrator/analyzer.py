import os
from utils import prompt_constructor
from config import PREFERENCES, GUIDELINES, WRITE_CODE, CREATE_DOCKER, CREATE_DEPENDENCIES, IDENTIFY_ENDPOINT_FILES, CREATE_SPEC, CREATE_ENDPOINTS, MULTIFILE, SINGLEFILE, FILENAMES


class Analyzer:
    def __init__(self, source_directory, source_language, ai):
        self.source_directory = source_directory
        self.source_language = source_language
        self.ai = ai

    def analyze(self):

        analyze_prompt_template = prompt_constructor(PREFERENCES,
                                                     GUIDELINES,
                                                     WRITE_CODE,
                                                     IDENTIFY_ENDPOINT_FILES,
                                                     MULTIFILE)

        prompt = analyze_prompt_template.format(source_directory=self.source_directory,
                                                source_language=self.source_language)

        analyzed_data = self.ai.run_openai(prompt)

        return analyzed_data