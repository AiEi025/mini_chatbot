from model.model import Llm_model

llm = Llm_model(model_name='deepseek-v4-flash').chose_model()
print(llm.invoke('hello introduce your self'))