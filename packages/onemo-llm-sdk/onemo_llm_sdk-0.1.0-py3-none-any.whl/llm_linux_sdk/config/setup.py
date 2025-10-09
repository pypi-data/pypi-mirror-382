# config/setup.py
from typing import Dict, Any
from ..config.manager import ModelConfig

def get_user_input(prompt: str, default: str = "") -> str:
    """获取用户输入，支持默认值"""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "

    user_input = input(full_prompt).strip()
    return user_input if user_input else default

def select_platform() -> Dict[str, str]:
    """平台选择"""
    platforms = {
        "1": {"name": "阿里百炼大模型服务平台", "url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
        "2": {"name": "CMIOT_AI能力底座大模型服务平台", "url": "http://ai.ai.iot.chinamobile.com/imaas/v1/"}
    }

    print("\n请选择大模型平台:")
    for key, value in platforms.items():
        print(f"  {key}. {value['name']}")

    while True:
        choice = input("请输入选择 (1-2): ").strip()
        if choice in platforms:
            selected = platforms[choice]
            return selected
        else:
            print("无效选择，请重新输入")

def get_models_by_platform(platform_name: str) -> Dict[str, Dict[str, str]]:
    """根据平台名称返回对应的模型列表"""
    if platform_name == "阿里百炼大模型服务平台":
        return {
            "1": {"name": "qwen-plus", "desc": "能力均衡，推理效果、成本和速度介于通义千问Max和通义千问Flash之间，适合中等复杂任务"},
            "2": {"name": "qwen3-max", "desc": "通义千问系列效果最好的模型，适合复杂、多步骤的任务"},
            "3": {"name": "qwen-flash", "desc": "通义千问系列速度最快、成本极低的模型，适合简单任务"}
        }
    elif platform_name == "CMIOT_AI能力底座大模型服务平台":
        return {
            "1": {"name": "DeepSeek-V3.1", "desc": "DeepSeek最新版本模型，综合能力强大"},
            "2": {"name": "jiutian-lan", "desc": "中国移动九天大模型，具备强大的文本处理、多模态融合能力，以及安全可信、全栈国产化等特点"}
        }

def set_platform_config(config: ModelConfig):
    """设置平台配置"""
    print("\n=== 平台配置 ===")

    # 选择平台
    platform_info = select_platform()
    config.update_config("platform", platform_info["name"])
    config.update_config("api_url", platform_info["url"])

    # 获取API-KEY
    api_key = get_user_input("请输入API-KEY")
    config.update_config("api_key", api_key)

    print("平台配置完成!")

def update_model_config(config: ModelConfig):
    """更新模型配置"""
    print("\n=== 模型参数配置 ===")

    # 检查是否已设置平台
    current_platform = config.config.get("platform", "")
    if not current_platform:
        print("请先设置平台配置!")
        return

    # 根据平台获取对应的模型列表
    models = get_models_by_platform(current_platform)

    print(f"当前平台: {current_platform}")
    print("请选择模型:")
    for key, value in models.items():
        print(f"  {key}. {value['name']} ({value['desc']})")

    # 获取默认选择（根据平台不同设置不同的默认值）
    default_choice = "1"  # 默认选择第一个模型

    model_choice = get_user_input("请输入选择", default_choice)
    if model_choice in models:
        selected_model = models[model_choice]["name"]
        config.update_config("model", selected_model)
        print(f"已选择模型: {selected_model}")
    else:
        print("无效选择，使用默认模型")

    # 是否流式配置
    try:
        stream = get_user_input("是否启用流式输出 (y/n)", "n").lower()
        config.update_config("stream", stream == "y")
    except ValueError:
        print("流式配置无效，使用默认值")

    # 是否启用联网搜索功能 - 仅阿里百炼平台支持
    if current_platform == "阿里百炼大模型服务平台":
        try:
            search = get_user_input("是否启用联网搜索 (y/n)", "n").lower()
            config.update_config("search", search == "y")
        except ValueError:
            print("联网搜索功能无效，使用默认值")
    else:
        # CMIOT平台不支持联网搜索，强制设置为False
        print("当前平台不支持联网搜索功能，已自动禁用")
        config.update_config("search", False)

    # 温度参数
    try:
        temperature = float(get_user_input("设置temperature (0.1-1.0)", str(config.config["temperature"])))
        config.update_config("temperature", max(0.1, min(1.0, temperature)))
    except ValueError:
        print("温度参数无效，使用默认值")

    # 最大token数
    try:
        current_model = config.config.get("model", "")
        if current_platform == "阿里百炼大模型服务平台" and current_model == "qwen3-max":
            max_tokens = int(get_user_input("设置max_tokens (0-262,144)", str(config.config["max_tokens"])))
            config.update_config("max_tokens", max(0, min(262144, max_tokens)))
        elif current_platform == "阿里百炼大模型服务平台" and current_model != "qwen3-max":
            max_tokens = int(get_user_input("设置max_tokens (0-1,000,000)", str(config.config["max_tokens"])))
            config.update_config("max_tokens", max(0, min(1000000, max_tokens)))
        else:
            max_tokens = int(get_user_input("设置max_tokens (0-1,024)", str(config.config["max_tokens"])))
            config.update_config("max_tokens", max(0, min(1024, max_tokens)))
    except ValueError:
        print("最大token数无效，使用默认值")

    print("模型参数配置完成!")