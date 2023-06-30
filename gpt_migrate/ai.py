from langchain.chat_models import ChatOpenAI
from config import OPENAI_API_KEY
import os
import openai
from utils import parse_code_string

openai.api_key = os.getenv("OPENAI_API_KEY")

class AI:
    def __init__(self, model="gpt-4-32k", temperature=0.1, max_tokens=10000):
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model_name = model
        try:
            _ = ChatOpenAI(model_name=model) # check to see if model is available to user
        except Exception as e:
            print(e)
            self.model_name = "gpt-3.5-turbo"
    
    def write_code(self, prompt):
        message=[{"role": "user", "content": str(prompt)}] 
        response = openai.ChatCompletion.create(
            messages=message,
            stream=False,
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        if response["choices"][0]["message"]["content"].startswith("INSTRUCTIONS:"):
            return ("INSTRUCTIONS:","",response["choices"][0]["message"]["content"][14:])
        else:
            code_triples = parse_code_string(response["choices"][0]["message"]["content"])
            return code_triples

    def run(self, prompt):
        message=[{"role": "user", "content": str(prompt)}] 
        response = openai.ChatCompletion.create(
            messages=message,
            stream=True,
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        chat = ""
        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            msg = delta.get("content", "")
            chat += msg
        return chat
    