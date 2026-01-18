# web_app.py

from flask import Flask, request, jsonify, render_template_string
from chatbot import ChatBot
import threading

app = Flask(__name__)

# 全局机器人实例（注意：生产环境应改用会话隔离）
bot = ChatBot()

# 简单 HTML 模板（内嵌）
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI 聊天机器人</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px; }
        #chat { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 10px; background: #f9f9f9; }
        .user { color: blue; }
        .ai { color: green; }
        input[type="text"] { width: 70%; padding: 8px; }
        button { padding: 8px 16px; }
        .controls { margin-top: 10px; }
    </style>
</head>
<body>
    <h2>🤖 AI 聊天机器人</h2>
    <div id="chat"></div>
    <input type="text" id="userInput" placeholder="输入消息..." onkeypress="if(event.key==='Enter') sendMessage()" />
    <button onclick="sendMessage()">发送</button>
    <div class="controls">
        <button onclick="clearHistory()">清空历史</button>
        <button onclick="location.reload()">重启会话</button>
    </div>

    <script>
        function appendMessage(role, text) {
            const chat = document.getElementById('chat');
            const p = document.createElement('p');
            p.className = role;
            p.innerHTML = '<b>' + (role === 'user' ? '👤 你:' : '🤖 AI:') + '</b> ' + text;
            chat.appendChild(p);
            chat.scrollTop = chat.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const msg = input.value.trim();
            if (!msg) return;
            appendMessage('user', msg);
            input.value = '';

            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const data = await res.json();
            if (data.reply) {
                appendMessage('ai', data.reply);
            } else {
                appendMessage('ai', '❌ 错误: ' + data.error);
            }
        }

        async function clearHistory() {
            await fetch('/clear', {method: 'POST'});
            document.getElementById('chat').innerHTML = '';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '').strip()
    if not user_msg:
        return jsonify({"error": "输入为空"})
    reply = bot.send_message(user_msg)
    return jsonify({"reply": reply})

@app.route('/clear', methods=['POST'])
def clear():
    bot.clear_history()
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    print("🌐 启动 Web 服务... 打开 http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)