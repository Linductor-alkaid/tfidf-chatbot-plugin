from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent
from .handlers.message_handler import process_message
from .handlers.response_handler import get_response

# 注册消息事件，优先级为5
message_event = on_message(priority=5)

@message_event.handle()
async def handle_message(event: MessageEvent):
    """
    当接收到消息时，处理并响应消息。
    """
    # 处理消息并存储（由 message_handler 处理消息存储逻辑）
    await process_message(event)

    # 获取机器人响应（由 response_handler 获取回复逻辑）
    response = get_response(event)
    
    # 如果有回复内容，则发送回复
    if response:
        await message_event.finish(response)
