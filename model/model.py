import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


class Llm_model:
    def __init__(self , model_name:str , temperature:float = 0.3):
        self.model_name = model_name
        self.temperature = temperature
        load_dotenv()
    
    def chose_model(self):
        if self.model_name.lower() == 'openrouter':
            return  ChatOpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="openrouter/free",
    temperature=self.temperature,
    timeout= 30)
             
        return ChatOpenAI(
    model=self.model_name,
    temperature=self.temperature,
    base_url=os.environ.get('OPENAI_BASE_URL'),
    api_key=os.environ.get('AGENTROUTER_API_KEY'),
    default_headers={
        "User-Agent": "claude-cli/1.0.108 (external, cli)",
        "x-app": "cli",
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "claude-code-20250219,oauth-2025-04-20",
        "X-Stainless-Runtime": "node",
        "X-Stainless-Arch": "x64",
        "X-Stainless-OS": "Windows",
        "X-Stainless-Lang": "js",
    }
)
    
