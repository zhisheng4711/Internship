import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("DASHSCOPE_API_KEY")
URL = "https://qianfan.baidubce.com/v2/chat/completions"
MODEL = "ernie-4.5-turbo-128k"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

messages = []

def send_message(user_input):
    messages.append({"role": "user", "content": user_input})
    payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.3,      # ← 降低随机性，更稳定
    "top_p": 0.9,
    "max_tokens": 150        # ← 限制长度
    }
    response = requests.post(URL, headers=headers, json=payload)
    data = response.json()
    
    if 'choices' in data:
        ai_reply = data['choices'][0]['message']['content']
        messages.append({"role": "assistant", "content": ai_reply})
        return ai_reply
    else:
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