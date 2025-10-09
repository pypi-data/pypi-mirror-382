"""
大模型SDK包
"""
from .config.manager import ModelConfig
from .config.setup import set_platform_config, update_model_config
from .client.model_client import ModelClient
from .interface.chat import interactive_chat

__version__ = "1.0.0"
__all__ = [
    "ModelConfig",
    "ModelClient", 
    "set_platform_config",
    "update_model_config",
    "interactive_chat"
]