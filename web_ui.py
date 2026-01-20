from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import hashlib
from chatbot import ChatBot

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # ⚠️ 替换为随机字符串（生产环境必须保密）

# 模拟数据库（实际应使用数据库）
users_db = {}  # {username: {password_hash, is_admin}}

# 初始化聊天机器人
try:
    bot = ChatBot()
except Exception as e:
    print(f"❌ ChatBot 初始化失败: {e}")
    bot = None

@app.route('/chat', methods=['POST'])
def chat():
    if not bot:
        return jsonify({"reply": "❌ AI 服务未初始化，请检查配置。", "error": "Bot not initialized"})
    
    data = request.get_json()
    message = data.get('message', '')
    
    if not message.strip():
        return jsonify({"reply": "⚠️ 输入为空，请输入有效内容。", "error": None})
    
    # 调用 AI
    ai_reply = bot.send_message(message)
    
    return jsonify({
        "reply": ai_reply,
        "error": None
    })

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "用户名和密码不能为空"})

    # 加密密码（简单哈希）
    password_hash = hashlib.md5(password.encode()).hexdigest()

    # 检查是否已存在该用户
    if username not in users_db:
        # 新用户 → 注册并设为管理员（第一个注册）
        users_db[username] = {
            'password_hash': password_hash,
            'is_admin': len(users_db) == 0  # 第一个用户是管理员
        }
        session['username'] = username
        return jsonify({"success": True, "message": "注册成功，欢迎！"})
    else:
        # 已有用户 → 验证密码
        if users_db[username]['password_hash'] == password_hash:
            session['username'] = username
            return jsonify({"success": True, "message": "登录成功！"})
        else:
            return jsonify({"success": False, "message": "用户名或密码错误"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("🌐 启动 Web 服务... 打开 http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)