# interface/chat.py
from openai import OpenAI
from ..config.manager import ModelConfig
from ..client.model_client import ModelClient

def interactive_chat(config: ModelConfig):
    """交互式聊天模式（使用OpenAI方式）"""
    client = ModelClient(config)

    print("\n=== 进入交互模式 ===")
    print("输入 'quit' 退出，输入 'reset' 重置对话")

    # 维护对话历史
    conversation_history = []

    while True:
        try:
            prompt = input("\n您: ").strip()

            if prompt.lower() == 'quit':
                break
            elif prompt.lower() == 'reset':
                conversation_history = []
                print("对话已重置")
                continue

            if not prompt:
                continue

            # 添加当前用户消息到历史
            conversation_history.append({"role": "user", "content": prompt})

            client_model = OpenAI(
                api_key=config.config["api_key"],
                base_url=config.config["api_url"]
            )

            if config.config["search"]:
                print("🔍AI大模型(联网)：", end="", flush=True)
            else:
                print("AI大模型：", end="", flush=True)

            # 构建请求参数
            request_params = {
                "model": config.config["model"],
                "messages": conversation_history,
                "temperature": config.config["temperature"],
                "max_tokens": config.config["max_tokens"],
                "stream": config.config["stream"],
            }

            # 只在支持搜索的平台添加搜索参数
            if config.config["platform"] == "阿里百炼大模型服务平台":
                request_params["extra_body"] = {
                    "enable_search": config.config["search"]
                }

            # 使用OpenAI客户端调用
            try:
                response = client_model.chat.completions.create(**request_params)

                if config.config["stream"]:
                    # 流式输出：逐步输出响应内容
                    full_response = ""
                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                            ai_response_chunk = chunk.choices[0].delta.content
                            full_response += ai_response_chunk
                            print(ai_response_chunk, end="", flush=True)
                    print()  # 换行

                    # 将完整回复添加到历史
                    if full_response:
                        conversation_history.append({"role": "assistant", "content": full_response})
                else:
                    # 非流式输出
                    if response.choices and response.choices[0].message:
                        ai_response = response.choices[0].message.content
                        print(ai_response)
                        # 添加AI回复到历史
                        conversation_history.append({"role": "assistant", "content": ai_response})
                    else:
                        print("未收到有效回复")

            except Exception as e:
                print(f"调用失败: {e}")
                # 从历史中移除当前用户消息，因为调用失败了
                if conversation_history and conversation_history[-1]["role"] == "user":
                    conversation_history.pop()

        except KeyboardInterrupt:
            print("\n\n退出交互模式")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")