# test_model.py
from chatbot import send_message  # 复用上面的函数
import os
# 确保 data 目录存在
if not os.path.exists("data/test_prompts.txt"):
    print("❌ 找不到测试文件: data/test_prompts.txt")
    exit(1)
with open("data/test_prompts.txt", "r", encoding="utf-8") as f:
    prompts = [line.strip() for line in f if line.strip()]
if not prompts:
    print("❌ 测试文件为空！")
    exit(1)

print("🧪 开始批量测试...\n")
for i, prompt in enumerate(prompts, 1):
    print(f"[{i}] 问题: {prompt}")
    answer = send_message(prompt)
    print(f"回答: {answer}\n{'-'*50}")