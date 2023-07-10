
import pandas as pd
import openai
openai.api_key = "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"

def get_completion_from_messages(messages, 
                                 model="gpt-3.5-turbo", 
                                 temperature=0, 
                                 max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]

delimiter = "####"

system_message = f"""
你是一个经验丰富的新闻撰写记者。\
你将会被提供贵州日报的新闻。\
新闻将会用 {delimiter} 分割。\
将新闻进行分类。\
每条新闻允许拥有多条分类。\
你的输出将是该条新闻的类别，用","分割。\

新闻类别：天气, 教育, 交通, 科技, 旅游, 经济
"""

data = pd.read_excel("5167503212_贵州日报官微.xlsx", nrows=1)

user_message = f"""\
I want you to delete my profile and all of my user data"""
messages =  [  
{'role':'system', 
 'content': system_message},    
{'role':'user', 
 'content': f"{delimiter}{user_message}{delimiter}"},  
] 
response = get_completion_from_messages(messages)
print(response)



pass