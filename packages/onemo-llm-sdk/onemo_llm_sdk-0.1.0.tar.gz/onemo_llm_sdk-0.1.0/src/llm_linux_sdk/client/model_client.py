# client/model_client.py
from openai import OpenAI
from ..config.manager import ModelConfig

class ModelClient:
    """大模型客户端类"""

    def __init__(self, config: ModelConfig):
        self.config = config

    def test_connection(self) -> bool:
        """测试API连接（使用OpenAI兼容方式）"""
        # 确保有API Key
        api_key = self.config.config["api_key"]
        if not api_key:
            print("❌ 请先设置API Key")
            return False

        try:
            # 重新初始化客户端（确保使用最新的API Key）
            self.client = OpenAI(
                api_key=api_key,
                base_url=self.config.config["api_url"]
            )

            # 使用OpenAI兼容方式测试连接
            response = self.client.chat.completions.create(
                model=self.config.config["model"],
                messages=[{"role": "user", "content": "请回复'连接成功'"}],
                temperature=0.1,
                max_tokens=10
            )

            # 检查响应是否包含有效内容
            if response.choices and response.choices[0].message.content:
                return True
            else:
                print("❌ 连接测试返回了空响应")
                return False

        except Exception as e:
            print(f"连接测试失败: {e}")
            return False