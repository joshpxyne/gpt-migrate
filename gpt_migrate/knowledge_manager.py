import os
from dataclasses import dataclass

@dataclass
class KnowledgeManager:
    filename: str
    
    def read_file(self):
        if not os.path.exists(self.filename):
            return "File does not exist."
        
        with open(self.filename, 'r') as file:
            return file.read()

    def write_file(self, content: str):
        with open(self.filename, 'w') as file:
            file.write(content)

    def update_file(self, content: str):
        with open(self.filename, 'a') as file:
            file.write(content)

