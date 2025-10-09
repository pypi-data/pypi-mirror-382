# config/manager.py
import os
import json
from typing import Dict, Any

class ModelConfig:
    """模型配置管理类"""

    def __init__(self, config_file="model_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载现有配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}, 将使用默认配置")

        # 默认配置
        return {
            "platform": "",
            "api_key": "",
            "api_url": "",
            "model": "qwen-plus",
            "deep_thought": False,
            "temperature": 0.8,
            "max_tokens": 2000,
            "stream": False,
            "search": False
        }

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"配置已保存到: {os.path.abspath(self.config_file)}")
        except Exception as e:
            print(f"保存配置失败: {e}")

    def update_config(self, key: str, value: Any):
        """更新配置项"""
        self.config[key] = value
        print(f"配置已更新: {key} = {value}")