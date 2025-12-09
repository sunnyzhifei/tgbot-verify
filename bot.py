"""Telegram 机器人主程序"""
import logging
from functools import partial

from telegram import Update, BotCommand, BotCommandScopeChat
from telegram.ext import Application, CommandHandler, ContextTypes

from config import BOT_TOKEN,ADMIN_USER_ID
from database import Database
from handlers.user_commands import (
    start_command,
    about_command,
    help_command,
    balance_command,
    checkin_command,
    invite_command,
    use_command,
)
from handlers.verify_commands import (
    verify_command,
    verify2_command,
    verify4_command,
    getV4Code_command,
)
from handlers.admin_commands import (
    addbalance_command,
    block_command,
    white_command,
    blacklist_command,
    genkey_command,
    listkeys_command,
    broadcast_command,
)

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context) -> None:
    """全局错误处理"""
    logger.exception("处理更新时发生异常: %s", context.error, exc_info=context.error)

# --- 核心配置函数 ---
async def post_init(application: Application):
    """
    Bot 启动后自动配置命令菜单
    """
    bot = application.bot
    
    # 1. 定义【普通用户】命令列表
    # (Telegram 命令必须全小写，不能包含 < > 等特殊符号，只能是字母数字下划线)
    user_commands = [
        BotCommand("start", "开始使用（注册）"),
        BotCommand("about", "了解机器人功能"),
        BotCommand("balance", "查看积分余额"),
        BotCommand("qd", "每日签到（+1积分）"),
        BotCommand("invite", "生成邀请链接（+2积分/人）"),
        BotCommand("use", "使用卡密兑换积分"),
        BotCommand("verify", "Gemini One Pro 认证（-1积分）"),
        BotCommand("verify2", "ChatGPT Teacher K12 认证（-1积分）"),
        BotCommand("verify4", "Bolt.new Teacher 认证（-1积分）"),
        BotCommand("getv4code", "获取 Bolt.new 认证码"), # 命令转为小写
        BotCommand("help", "查看帮助信息 & 失败解决"),
    ]

    # 2. 定义【管理员】专属命令列表
    # (我在描述里加上了参数提示，方便您直接看)
    admin_commands = [
        BotCommand("addbalance", "加分 <ID> <积分>"),
        BotCommand("block", "拉黑 <ID>"),
        BotCommand("white", "解封 <ID>"),
        BotCommand("blacklist", "查看黑名单"),
        BotCommand("genkey", "制卡 <卡密> <积分> [次数] [天数]"),
        BotCommand("listkeys", "查看卡密列表"),
        BotCommand("broadcast", "全员广播 <文本>"),
    ]

    # 3. 设置默认菜单（所有用户可见）
    await bot.set_my_commands(user_commands)
    
    # 4. 设置管理员菜单（仅管理员 ID 可见）
    # 这样管理员输入 / 时，会看到上面两组命令的合集
    if ADMIN_USER_ID:
        try:
            # 将 int 转换，防止报错
            admin_id = int(ADMIN_USER_ID)
            await bot.set_my_commands(
                commands=user_commands + admin_commands,
                scope=BotCommandScopeChat(chat_id=admin_id)
            )
            print(f"✅ 已为管理员 {admin_id} 配置专属菜单")
        except Exception as e:
            print(f"❌ 设置管理员菜单失败: {e}")

def main():
    """主函数"""
    # 初始化数据库
    db = Database()

    # 创建应用 - 启用并发处理
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)  # 🔥 关键：启用并发处理多个命令
        .post_init(post_init)
        .build()
    )

    # 注册用户命令（使用 partial 传递 db 参数）
    application.add_handler(CommandHandler("start", partial(start_command, db=db)))
    application.add_handler(CommandHandler("about", partial(about_command, db=db)))
    application.add_handler(CommandHandler("help", partial(help_command, db=db)))
    application.add_handler(CommandHandler("balance", partial(balance_command, db=db)))
    application.add_handler(CommandHandler("qd", partial(checkin_command, db=db)))
    application.add_handler(CommandHandler("invite", partial(invite_command, db=db)))
    application.add_handler(CommandHandler("use", partial(use_command, db=db)))

    # 注册验证命令
    application.add_handler(CommandHandler("verify", partial(verify_command, db=db)))
    application.add_handler(CommandHandler("verify2", partial(verify2_command, db=db)))
    application.add_handler(CommandHandler("verify4", partial(verify4_command, db=db)))
    application.add_handler(CommandHandler("getV4Code", partial(getV4Code_command, db=db)))

    # 注册管理员命令
    application.add_handler(CommandHandler("addbalance", partial(addbalance_command, db=db)))
    application.add_handler(CommandHandler("block", partial(block_command, db=db)))
    application.add_handler(CommandHandler("white", partial(white_command, db=db)))
    application.add_handler(CommandHandler("blacklist", partial(blacklist_command, db=db)))
    application.add_handler(CommandHandler("genkey", partial(genkey_command, db=db)))
    application.add_handler(CommandHandler("listkeys", partial(listkeys_command, db=db)))
    application.add_handler(CommandHandler("broadcast", partial(broadcast_command, db=db)))

    # 注册错误处理器
    application.add_error_handler(error_handler)

    logger.info("机器人启动中...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
