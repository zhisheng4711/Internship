from flask import Flask, request, session, render_template_string
import os
from dotenv import load_dotenv
import json
# 加载环境与配置（和 chatbot.py 一致）
load_dotenv()
with open("config/model_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
with open("docs/prompt_examples.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

GENERATION_CONFIG = config["generation"]
API_KEY = os.getenv("DASHSCOPE_API_KEY")
URL = config["api"]["url"]
MODEL = config["api"]["model"]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用于 session 加密

def send_message_web(user_input, history):
    """复用 chatbot 逻辑，但传入历史"""
    messages = [{"role": "system", "content": system_prompt}] + history
    messages.append({"role": "user", "content": user_input})
    
    payload = {
        "model": MODEL,
        "messages": messages,
        **GENERATION_CONFIG
    }
    
    import requests
    response = requests.post(URL, headers=headers, json=payload)
    data = response.json()
    
    if 'choices' in data:
        ai_reply = data['choices'][0]['message']['content']
        return ai_reply
    else:
        error_msg = data.get('error', {}).get('message', '未知错误')
        return f"❌ 调用失败: {error_msg}"

@app.route("/", methods=["GET", "POST"])
def index():
    # 使用 session 存储对话历史（每用户独立）
    if "history" not in session:
        session["history"] = []
    
    if request.method == "POST":
        user_input = request.form["question"].strip()
        if user_input:
            # 获取当前历史
            history = session["history"]
            # 调用模型
            ai_reply = send_message_web(user_input, history)
            # 更新历史（只保留最近3轮，防超长）
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": ai_reply})
            session["history"] = history[-6:]  # 保留最后3轮（6条消息）
    
    # 构建对话显示
    chat_display = ""
    for msg in session.get("history", []):
        role = "🧑 你" if msg["role"] == "user" else "🤖 小桂"
        chat_display += f"<div><strong>{role}:</strong> {msg['content']}</div><br>"
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>桂电AI学姐 — 小桂</title>
        <style>
            body { font-family: "Microsoft YaHei", sans-serif; max-width: 700px; margin: 30px auto; padding: 20px; background: #f8f9fa; }
            h1 { color: #c0392b; text-align: center; margin-bottom: 30px; }
            .chat-box { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; min-height: 100px; }
            .input-area { display: flex; gap: 10px; }
            .input-area input { flex: 1; padding: 12px; font-size: 16px; border: 1px solid #ddd; border-radius: 6px; }
            .input-area button { padding: 12px 20px; background: #3498db; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; }
            .input-area button:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <h1>🎓 桂电AI学姐 — 小桂</h1>
        <div class="chat-box">
            ''' + (chat_display if chat_display else "<em>暂无对话，快向小桂提问吧～</em>") + '''
        </div>
        <form method="post" class="input-area">
            <input type="text" name="question" placeholder="问小桂：选课怎么弄？图书馆几点关？..." required>
            <button type="submit">发送</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)