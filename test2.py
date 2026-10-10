from model.model import Llm_model

llm = Llm_model('deepseek-v4-flash').chose_model()
llm_n = llm.invoke('tell me short about a plan')
print(llm_n)