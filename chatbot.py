# chatbot.py

import requests
import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from config import MODEL_CONFIG_PATH, PROMPT_PATH, MAX_HISTORY_ROUNDS, TIMEOUT

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()
class ChatBot:  # 聊天机器人类
    def __init__(self):
        self.model_config_path = Path(MODEL_CONFIG_PATH)
        self.prompt_path = Path(PROMPT_PATH)
        self.max_history_rounds = MAX_HISTORY_ROUNDS
        self.timeout = TIMEOUT

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
        #   发送请求
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
        #   处理常见请求异常
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