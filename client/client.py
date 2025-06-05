from dotenv import load_dotenv
import os
from openai import OpenAI
from pathlib import Path
import time
from typing import List, Optional, Dict, Any

class LlmClient:
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化客户端
        :param model: 模型名称（可选）
        :param api_key: API 密钥（可选，若未提供将尝试读取环境变量或使用默认值）
        """
        self.model = model or os.getenv("OPENAI_MODEL", "gemini-2.0-flash-exp")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        # print(self.model,self.api_key,self.base_url)
        try:
                # 使用关键字参数传递配置
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                # print(f"初始化成功{self.model}")
        except Exception as e:
            print(f"[api初始化失败] {e}")
            self.client = None
            
    def list_models(self) -> Optional[Dict[str, Any]]:
        """
        获取可用的模型列表
        :return: 返回模型列表字典，失败则返回None
        """
        if not self.client:
            print("[错误] api客户端未初始化成功")
            return None
            
        try:
            response = self.client.models.list()
            return response.data
        except Exception as e:
            print(f"[获取模型列表失败] {e}")
            return None
        
    def print_available_models(self):
        """
        打印可用的模型列表
        """
        models = self.list_models()
        if models:
            print("\n可用模型列表:")
            for model in models:
                print(f"- {model.id}")
            print()
        else:
            print("无法获取模型列表")
        
    def call_chat_text(self, messages, model, temperature: Optional[float] = 0.1):
        """
        调用聊天补全 API
        :param messages: 消息列表（字典格式）
        :param temperature: 控制生成随机性
        :return: 返回回复内容字符串，失败则返回 None
        """
        if not self.client:
            print("[错误] api 客户端未初始化成功")
            return None

        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=model if model else self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=8192
            )
            # print(response)
            end_time = time.time()
            token_count = response.usage.completion_tokens
            elapsed_time = end_time - start_time
            token_speed = token_count / elapsed_time if elapsed_time > 0 else 0
            print(f"输出 {token_count} 个token，用时 {elapsed_time:.2f} 秒，速度为 {token_speed:.2f} token/秒")

            return response.choices[0].message.content
        except Exception as e:
            print(f"[api 对话 API错误] {e}")
            return None
        
    def call_chat_images(self, prompt, image, model):
        try_times = 0
        while try_times < 5:
            try:
                image_data = {"type": "image_url", "image_url": {"url": f"data:image/jpg;base64,{image}", "detail": "high"}}
                text_data = {"type": "text","text": prompt}
                # qwen-vl-max-latest
                response = self.client.chat.completions.create(messages=[{"role": "system", "content": "You are an expert with certain knowledge of bioinformatics and chemistry. Please help finish these domain-related paper-reading tasks."}, 
                                                                    {"role": "user", "content": [ text_data, image_data]}],
                                                            model=model if model else self.model, temperature=0.15)
                # print(response)
                output = response.choices[0].message.content
                return output
            except Exception as e:
                print(f'{self.model} {try_times} try failed:', e)
                try_times += 1
        print(f"响应超时，处理错误")
        return  '[]'
    
if __name__ == "__main__":
        load_dotenv()  # 加载当前目录的 .env 文件
        model = os.getenv("OPENAI_MODEL", "gemini-2.0-flash-exp")
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        client = LlmClient(model, api_key, base_url)
