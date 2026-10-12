import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# مقدار درخواستی	رفتار واقعی مدل
# "none"	حالت thinking را کاملاً خاموش می‌کند
# "minimal"	به low نگاشت می‌شود
# "low"	low (سبک‌ترین حالت thinking)
# "medium"	به high نگاشت می‌شود
# "high"	high (پیش‌فرض)
# "xhigh"	به high نگاشت می‌شود
# "max"	max (سنگین‌ترین حالت thinking)
# "ultra"	به max نگاشت می‌شود
class Llm_model:
    def __init__(self , model_name:str,reasoning_effort:str ="high", temperature:float = 0.3 ):
        self.model_name = model_name
        self.temperature = temperature
        self.reasoning_effort = reasoning_effort
        load_dotenv()
    
    def chose_model(self):
        if self.model_name.lower() == 'openrouter':
            return  ChatOpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="openrouter/free",
    temperature=self.temperature,
    timeout= 30)
        
        elif self.model_name.lower() == 'toptool':
            return ChatOpenAI(
                api_key=os.environ.get("TOPTOOLS_API_KEY"),
                base_url="https://top-tools-ai.com/api/v1",
                temperature=self.temperature,
                model='Top-Tools-Ai',
                timeout= 120,
                max_retries=3
                
            )
             
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
    },
    reasoning_effort=self.reasoning_effort
)
    
