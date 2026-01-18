# chatbot.py

import requests
import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatBot:  # 聊天机器人类
    def __init__(   
        self,   # 实例本身
        model_config_path: str = "config/model_config.json",    # 模型配置文件路径
        prompt_path: str = "docs/prompt_examples.md",   # 系统提示词文件路径
        max_history_rounds: int = 10,   # 最大保留对话轮数（不包括 system）
        timeout: int = 30   # API 请求超时时间（秒）
    ):  
        """ 
        初始化聊天机器人。  
        
        :param model_config_path: 模型配置文件路径
        :param prompt_path: 系统提示词文件路径
        :param max_history_rounds: 最大保留对话轮数（不包括 system）
        :param timeout: API 请求超时时间（秒）
        """
        load_dotenv()   # 加载环境变量
        self.model_config_path = Path(model_config_path)    
        self.prompt_path = Path(prompt_path)    
        self.max_history_rounds = max_history_rounds    
        self.timeout = timeout  

        # 加载配置
        self.config = self._load_model_config()
        self.system_prompt = self._load_system_prompt()
        self.generation_config = self.config["generation"]
        self.api_url = self.config["api"]["url"]
        self.model_name = self.config["api"]["model"]

        # 获取并校验 API Key
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("❌ DASHSCOPE_API_KEY 未设置，请检查 .env 文件。")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 初始化消息历史（包含 system）
        self.messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]

    def _load_model_config(self) -> dict:   #
        with open(self.model_config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_system_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _trim_history(self):
        """保留 system 消息 + 最近 max_history_rounds 轮对话（每轮含 user + assistant）"""
        if len(self.messages) <= 1 + 2 * self.max_history_rounds:
            return
        # 保留第一条（system）+ 最近 2 * N 条
        self.messages = [self.messages[0]] + self.messages[-2 * self.max_history_rounds:]

    def send_message(self, user_input: str) -> str:
        """
        发送用户消息并获取 AI 回复。
        
        :param user_input: 用户输入文本
        :return: AI 的回复或错误信息
        """
        if not user_input.strip():
            return "⚠️ 输入为空，请输入有效内容。"

        # 添加用户消息
        self.messages.append({"role": "user", "content": user_input})
        self._trim_history()  # 控制上下文长度

        payload = {
            "model": self.model_name,
            "messages": self.messages,
            **self.generation_config
        }

        logger.info(f"用户输入: {user_input[:50]}...")
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            if 'choices' in data and data['choices']:
                ai_reply = data['choices'][0]['message']['content']
                self.messages.append({"role": "assistant", "content": ai_reply})
                logger.info("AI 回复成功。")
                return ai_reply
            else:
                error_msg = data.get('error', {}).get('message', '未知错误')
                logger.error(f"API 返回错误: {error_msg}")
                return f"❌ 调用失败: {error_msg}"

        except requests.exceptions.Timeout:
            logger.error("请求超时")
            return "❌ 请求超时，请稍后再试。"
        except requests.exceptions.ConnectionError:
            logger.error("网络连接错误")
            return "❌ 网络连接失败，请检查网络。"
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP 错误: {e}")
            return f"❌ HTTP 错误: {e}"
        except Exception as e:
            logger.exception("未知异常")
            return f"❌ 未知错误: {str(e)}"

    def clear_history(self):
        """清空对话历史（保留 system prompt）"""
        self.messages = [{"role": "system", "content": self.system_prompt}]
        logger.info("对话历史已清空。")


# CLI 入口（保持兼容）
if __name__ == "__main__":
    try:
        bot = ChatBot()
    except Exception as e:
        print(f"初始化失败: {e}")
        exit(1)

    print("🤖 欢迎使用 AI 聊天机器人！输入 '退出' 结束对话，'清空' 清除历史。")
    while True:
        user_input = input("\n你: ").strip()
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