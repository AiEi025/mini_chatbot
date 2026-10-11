from model.model import Llm_model

llm = Llm_model('deepseek-v4-flash').chose_model()
llm_n = llm.invoke('give me short information about your self')
print(llm_n)