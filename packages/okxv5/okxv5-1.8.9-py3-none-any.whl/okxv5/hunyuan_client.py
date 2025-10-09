# hunyuan_client.py
import requests
import json
import yaml
from pathlib import Path

class HunYuanClient:
    def __init__(self, config_path='config.yaml'):
        """
        初始化 HunYuanClient 实例，从 config.yaml 读取配置。

        :param config_path: 配置文件路径
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        self.url = 'https://open.hunyuan.tencent.com/openapi/v1/agent/chat/completions'
        self.headers = {
            'X-Source': 'openapi',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {config.get("token")}'
        }
        self.assistant_id = config.get('assistant_id')
        self.user_id = config.get('user_id')

        if not all([self.assistant_id, self.user_id, self.headers['Authorization'].startswith('Bearer ')]):
            raise ValueError("配置文件缺少必要的参数或 Token 格式不正确。")

    def send_message(self, message):
        """
        发送消息到腾讯混元大模型并获取响应。

        :param message: 要发送的消息字符串
        :return: API 响应的 JSON 数据
        """
        data = {
            "assistant_id": self.assistant_id,
            "user_id": self.user_id,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                }
            ]
        }
        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response.raise_for_status()  # 检查请求是否成功
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求出错: {e}")
            return None

    def send_message_text(self, message):
        """
        发送纯文本消息并返回格式化后的响应。

        :param message: 要发送的消息字符串
        :return: 格式化后的响应字符串
        """
        result = self.send_message(message)
        if result:
            return json.dumps(result, ensure_ascii=False, indent=2)
        return None