# test_model.py
from chatbot import ChatBot  # 导入类，不是函数
import os

# 确保 data 目录和测试文件存在
test_file = "data/test_prompts.txt"
if not os.path.exists(test_file):
    print(f"❌ 找不到测试文件: {test_file}")
    exit(1)

with open(test_file, "r", encoding="utf-8") as f:
    prompts = [line.strip() for line in f if line.strip()]

if not prompts:
    print("❌ 测试文件为空！")
    exit(1)

print("🧪 开始批量测试...\n")

# 创建 ChatBot 实例（会自动加载 .env 和配置）
bot = ChatBot()

for i, prompt in enumerate(prompts, 1):
    print(f"[{i}] 问题: {prompt}")
    try:
        answer = bot.send_message(prompt)  # 调用实例方法
        print(f"回答: {answer}\n{'-'*50}")
    except Exception as e:
        print(f"错误: {e}\n{'-'*50}")