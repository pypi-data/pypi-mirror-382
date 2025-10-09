import os
import subprocess
import platform
from pathlib import Path
from typing import Optional

from nonebot import on_message, logger
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot, PrivateMessageEvent, MessageEvent
from nonebot.rule import Rule

from .config import Config, plugin_config

__plugin_meta__ = PluginMetadata(
    name="远程文件打开",
    description="通过检测特定私聊关键词来打开对应文件",
    usage="在私聊中发送配置的关键词即可打开对应文件",
    type="application",
    homepage="https://github.com/Xenith-Ethereon/nonebot-plugin-file-opener.git",
    supported_adapters={"~onebot.v11"},
    config=Config,  
    extra={
        'author': '星淆_xenith',
        'version': 'beta-1',
    },
)

def is_admin_private_message() -> Rule:
    """检查是否为管理员的私聊消息"""
    async def _is_admin_private_message(event: MessageEvent) -> bool:
        # 检查是否为私聊消息
        if not isinstance(event, PrivateMessageEvent):
            return False
        
        # 检查是否为管理员
        user_id = str(event.user_id)
        return user_id in plugin_config.file_opener_admins
    
    return Rule(_is_admin_private_message)


# 处理管理员的私聊消息
file_opener = on_message(
    rule=is_admin_private_message(),
    priority=10,
    block=False
)


def open_file_with_system(file_path: str) -> bool:

    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            return False
        
        # 根据操作系统选择打开方式
        system = platform.system()
        
        if system == "Windows":
            # Windows 使用 start 命令
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            # macOS 使用 open 命令
            subprocess.run(["open", file_path], check=True)
        elif system == "Linux":
            # Linux 使用 xdg-open 命令
            subprocess.run(["xdg-open", file_path], check=True)
        else:
            logger.error(f"不支持的操作系统: {system}")
            return False
        
        logger.info(f"成功打开文件: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"打开文件失败 {file_path}: {e}")
        return False


def resolve_file_path(file_path: str) -> str:

    # 如果是绝对路径，直接返回
    if os.path.isabs(file_path):
        return file_path
    
    # 如果是相对路径，相对于项目根目录
    # 获取当前插件文件的目录
    current_dir = Path(__file__).parent
    # 向上找到项目根目录
    project_root = current_dir
    while project_root.parent != project_root:
        if (project_root / "pyproject.toml").exists():
            break
        project_root = project_root.parent
    
    # 拼接相对路径
    resolved_path = project_root / file_path
    return str(resolved_path.resolve())


@file_opener.handle()
async def handle_file_opener(bot: Bot, event: PrivateMessageEvent):
    """处理文件打开请求"""
    
    # 检查插件是否启用
    if not plugin_config.file_opener_enable:
        return
    
    # 获取消息内容
    message_text = event.get_plaintext().strip()
    
    # 检查是否匹配关键词
    matched_file: Optional[str] = None
    matched_keyword: Optional[str] = None
    
    for keyword, file_path in plugin_config.file_opener_keywords.items():
        if keyword in message_text:
            matched_file = file_path
            matched_keyword = keyword
            break
    
    # 如果没有匹配的关键词，不处理
    if not matched_file or not matched_keyword:
        return
    
    # 记录操作日志
    if plugin_config.file_opener_log_enabled:
        logger.info(f"用户 {event.user_id} 触发关键词 '{matched_keyword}'，尝试打开文件: {matched_file}")
    
    # 解析文件路径
    resolved_path = resolve_file_path(matched_file)
    
    # 尝试打开文件
    success = open_file_with_system(resolved_path)
    
    # 发送反馈消息
    if success:
        await bot.send_private_msg(
            user_id=event.user_id,
            message=f"已成功打开文件: {os.path.basename(resolved_path)}"
        )
    else:
        await bot.send_private_msg(
            user_id=event.user_id,
            message=f"打开文件失败: {os.path.basename(resolved_path)}\n请检查文件路径是否正确"
        )
