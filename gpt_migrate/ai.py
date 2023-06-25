from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from config import OPENAI_API_KEY
import os
import re
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

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

class AI:
    def __init__(self, model="gpt-4-32k", temperature=0.9):
        self.temperature = temperature
        try:
            self.model = OpenAI(model_name=model, temperature=temperature, openai_api_key=OPENAI_API_KEY)
        except Exception as e:
            print(
                e
            )
            self.model = OpenAI(model_name="gpt-3.5-turbo", temperature=temperature, openai_api_key=OPENAI_API_KEY)

    def write_code(self, prompt):

        prompt_template = PromptTemplate(
                input_variables=[], # level this up later
                template=prompt
            )
        chain = LLMChain(llm=self.model, prompt=prompt_template)
        result = chain.run({})
        code_triples = parse_code_string(result)
        return code_triples
    
    def run(self, prompt):
        prompt_template = PromptTemplate(
                input_variables=[], # level this up later
                template=prompt
            )
        chain = LLMChain(llm=self.model, prompt=prompt_template)
        result = chain.run({})
        return result
    
    def write_code_openai(self, prompt):
        message=[{"role": "user", "content": prompt}] 
        response = openai.ChatCompletion.create(
            messages=message,
            stream=False,
            model="gpt-4-32k",
            max_tokens=10000,
            temperature=0.9
        )
        print(response["choices"][0]["message"]["content"])
        code_triples = parse_code_string(response["choices"][0]["message"]["content"])
        return code_triples

    def run_openai(self, prompt):
        message=[{"role": "user", "content": prompt}] 
        response = openai.ChatCompletion.create(
            messages=message,
            stream=True,
            model="gpt-4-32k",
            max_tokens=10000,
            temperature=0.9
        )
        chat = ""
        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            msg = delta.get("content", "")
            print(msg, end="")
            chat += msg
        return chat
    