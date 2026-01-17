# chatbot.py（修改后）

import requests
import json
from dotenv import load_dotenv
import os

# 加载模型配置
def load_model_config(path="config/model_config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
# 加载提示词
def load_system_prompt(path="docs/prompt_examples.md"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
load_dotenv()       # 加载环境变量
config = load_model_config()    # 读取模型配置
system_prompt = load_system_prompt()    # 读取系统提示词
GENERATION_CONFIG = config["generation"]    # 读取生成参数
API_KEY = os.getenv("DASHSCOPE_API_KEY")    # 获取API密钥
URL = config["api"]["url"]  # 获取API URL
MODEL = config["api"]["model"]  # 获取模型名称

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}   # 设置请求头

# 初始化对话消息
messages = [{"role": "system", "content": system_prompt}]

def send_message(user_input):
    messages.append({"role": "user", "content": user_input})
    payload = {
    "model": MODEL,
    "messages": messages,   
    **GENERATION_CONFIG
    }
    response = requests.post(URL, headers=headers, json=payload)    
    data = response.json()
    
    if 'choices' in data:   # 成功响应
        ai_reply = data['choices'][0]['message']['content']
        messages.append({"role": "assistant", "content": ai_reply}) 
        return ai_reply
    else:   # 错误响应
        error_msg = data.get('error', {}).get('message', '未知错误')
        return f"❌ 调用失败: {error_msg}"

if __name__ == "__main__":
    print("🤖 欢迎使用 AI 聊天机器人！输入 '退出' 结束对话。")
    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in ['退出', 'quit', 'exit']:
            print("👋 再见！")
            break
        if not user_input:
            continue
        reply = send_message(user_input)
        print(f"\nAI: {reply}")