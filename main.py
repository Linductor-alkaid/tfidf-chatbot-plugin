from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent, PrivateMessageEvent, MessageSegment
from .handlers.message_handler import process_message
from .handlers.response_handler import get_response
from .utils.storage import initialize_files
from .utils.tfidf import calculate_tfidf


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
    global allow_speak

    # 检查是否为管理员私聊命令
    if isinstance(event, PrivateMessageEvent) and str(event.user_id) == ADMIN_QQ:
        command = event.message.extract_plain_text().strip()
        if command == "允许发言":
            allow_speak = True
            print("发言已允许")  # 调试输出
            await message_event.finish("收到")
        elif command == "禁止发言":
            allow_speak = False
            print("发言已禁止")  # 调试输出
            await message_event.finish("收到")

    # 输出当前的 allow_speak 状态
    print(f"当前发言状态: {allow_speak}")

    # 检查发言权限
    if allow_speak:
        response, response_type = get_response(event)
        # 如果有回复内容，且允许发言，则发送回复
        if response:
            print(f"回复内容: {response}")  # 输出回复内容
            if response_type == "text":
                await message_event.finish(response)
            elif response_type == "image":
                await message_event.send(MessageSegment.image(f"file://{response}"))
        else:
            print("没有生成回复")
            calculate_tfidf()
            
