from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent, PrivateMessageEvent
from .handlers.message_handler import process_message
from .handlers.response_handler import get_response
from .utils.storage import initialize_files

# 初始化文件
initialize_files()

# 管理员 QQ 号
ADMIN_QQ = "2052046346"

# 发言控制开关
allow_speak = False

# 注册消息事件，优先级为5
message_event = on_message(priority=5)

@message_event.handle()
async def handle_message(event: MessageEvent):
    """
    当接收到消息时，处理并响应消息。
    """
    global allow_speak

    # 检查是否为管理员私聊命令
    if isinstance(event, PrivateMessageEvent) and str(event.user_id) == ADMIN_QQ:
        # 获取管理员发送的文本消息
        command = event.message.extract_plain_text().strip()

        # 处理发言控制命令
        if command == "允许发言":
            allow_speak = True
            await message_event.finish("收到")
        elif command == "禁止发言":
            allow_speak = False
            await message_event.finish("收到")
    
    # 存储消息（由 message_handler 处理消息存储逻辑）
    await process_message(event)

    # 检查发言权限
    if allow_speak:
        # 获取机器人响应（由 response_handler 获取回复逻辑）
        response = get_response(event)
        
        # 如果有回复内容，且允许发言，则发送回复
        if response:
            await message_event.finish(response)
