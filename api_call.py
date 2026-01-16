import requests
import json
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("DASHSCOPE_API_KEY")
url = "https://qianfan.baidubce.com/v2/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

user_input = input("请输入你的问题: ")

def call_qianfan(prompt):
    data = {
        "model": "ernie-4.5-turbo-128k",
        "messages": [{"role": "user", "content": prompt}]
    }
    res = requests.post(url, headers=headers, data=json.dumps(data))
    return res.json()["choices"][0]["message"]["content"]

print(call_qianfan(user_input))