from chatbot import ChatBot

def main():
    try:
        bot = ChatBot()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    print("🤖 欢迎使用 AI 聊天机器人！输入 '退出' 结束对话，'清空' 清除历史。")
    while True:
        try:
            user_input = input("\n你: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 再见！")
            break

        if user_input.lower() in ['退出', 'quit', 'exit']:
            print("👋 再见！")
            break
        elif user_input.lower() == '清空':
            bot.clear_history()
            print("✅ 对话历史已清空。")
            continue
        if not user_input:
            continue

        reply = bot.send_message(user_input)
        print(f"\nAI: {reply}")

if __name__ == "__main__":
    main()