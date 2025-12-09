#!/usr/bin/env python3
"""
诊断脚本 - 帮助排查为什么管理员命令没有响应
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_env():
    """检查环境变量配置"""
    logger.info("=" * 60)
    logger.info("🔍 检查环境变量配置")
    logger.info("=" * 60)
    
    required_vars = {
        'BOT_TOKEN': '必需 - Telegram Bot Token',
        'ADMIN_USER_ID': '必需 - 管理员 User ID',
        'MYSQL_HOST': '必需 - MySQL 主机',
        'MYSQL_USER': '必需 - MySQL 用户名',
        'MYSQL_PASSWORD': '必需 - MySQL 密码',
        'MYSQL_DATABASE': '必需 - MySQL 数据库名',
    }
    
    missing = []
    warnings = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append(f"  ❌ {var:20} - {description}")
        elif var == 'ADMIN_USER_ID':
            try:
                admin_id = int(value)
                if admin_id == 123456789:
                    warnings.append(f"  ⚠️  {var:20} - 默认值 123456789，可能不是你的 User ID")
                else:
                    logger.info(f"  ✅ {var:20} = {admin_id}")
            except ValueError:
                missing.append(f"  ❌ {var:20} - 必须是数字，当前值: {value}")
        elif var == 'BOT_TOKEN':
            if value == 'YOUR_BOT_TOKEN_HERE':
                missing.append(f"  ❌ {var:20} - 仍为默认值，请设置真实的 Token")
            else:
                logger.info(f"  ✅ {var:20} = {value[:20]}...")
        else:
            logger.info(f"  ✅ {var:20} = 已设置")
    
    if missing:
        logger.error("\n缺少必需的环境变量:")
        for msg in missing:
            logger.error(msg)
    
    if warnings:
        logger.warning("\n警告:")
        for msg in warnings:
            logger.warning(msg)
    
    return len(missing) == 0

def check_database():
    """检查数据库连接"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 检查数据库连接")
    logger.info("=" * 60)
    
    try:
        import pymysql
        logger.info("  ✅ pymysql 已安装")
    except ImportError:
        logger.error("  ❌ pymysql 未安装，运行: pip install pymysql")
        return False
    
    try:
        from database_mysql import MySQLDatabase
        logger.info("  ✅ database_mysql 模块可导入")
        
        try:
            db = MySQLDatabase()
            logger.info("  ✅ 数据库连接成功")
            return True
        except ValueError as e:
            logger.error(f"  ❌ 数据库配置错误: {e}")
            return False
        except Exception as e:
            logger.error(f"  ❌ 数据库连接失败: {e}")
            return False
    except Exception as e:
        logger.error(f"  ❌ 导入 database_mysql 失败: {e}")
        return False

def check_admin_id():
    """检查管理员 ID 配置"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 检查管理员 ID")
    logger.info("=" * 60)
    
    admin_id_str = os.getenv('ADMIN_USER_ID')
    
    if not admin_id_str:
        logger.error("  ❌ ADMIN_USER_ID 未设置")
        logger.error("\n如何获取你的 User ID:")
        logger.error("  1. 在 Telegram 中搜索 @userinfobot")
        logger.error("  2. 给它发送 /start 命令")
        logger.error("  3. 它会返回你的数字 ID，例如: 123456789")
        logger.error("  4. 将这个 ID 设置到 .env 文件: ADMIN_USER_ID=123456789")
        return False
    
    try:
        admin_id = int(admin_id_str)
        logger.info(f"  ✅ ADMIN_USER_ID = {admin_id}")
        
        if admin_id == 123456789:
            logger.warning(f"  ⚠️  警告: 这是示例 ID，可能不是你的真实 ID")
            logger.warning("  请确认这是你从 @userinfobot 获取的真实 ID")
        
        return True
    except ValueError:
        logger.error(f"  ❌ ADMIN_USER_ID 必须是数字，当前值: {admin_id_str}")
        return False

def show_next_steps():
    """显示后续步骤"""
    logger.info("\n" + "=" * 60)
    logger.info("📋 后续步骤")
    logger.info("=" * 60)
    
    logger.info("""
1. 确保你在 .env 文件中正确设置了 ADMIN_USER_ID
   - 这个 ID 必须是你的 Telegram User ID
   - 从 @userinfobot 获取你的 ID

2. 确保数据库正确配置并且已连接

3. 启动机器人后，在 Telegram 中给机器人发送 /addbalance 命令
   - 如果你不是管理员，会收到: "您没有权限使用此命令。"
   - 如果配置正确，会显示使用帮助

4. 查看日志输出，查找错误信息

5. 常见问题:
   ✗ "您没有权限使用此命令" 
     → ADMIN_USER_ID 配置不对（不是你的真实 ID）
   
   ✗ 没有任何响应
     → 数据库连接失败，检查 MySQL 配置
     → 或者机器人崩溃，查看日志
   
   ✗ "参数格式错误"
     → 命令格式错误，应该是: /addbalance <用户ID> <积分数量>
     → 例如: /addbalance 987654321 10
""")

def main():
    """主诊断函数"""
    logger.info("\n🤖 Telegram 机器人管理员命令诊断工具\n")
    
    # 检查环境变量
    env_ok = check_env()
    
    # 检查管理员 ID
    admin_ok = check_admin_id()
    
    # 检查数据库
    db_ok = check_database()
    
    # 显示总结
    logger.info("\n" + "=" * 60)
    logger.info("📊 诊断总结")
    logger.info("=" * 60)
    
    status = [
        ("环境变量", env_ok),
        ("管理员 ID", admin_ok),
        ("数据库", db_ok),
    ]
    
    for name, ok in status:
        symbol = "✅" if ok else "❌"
        logger.info(f"  {symbol} {name:15} {'正常' if ok else '异常'}")
    
    if all(ok for _, ok in status):
        logger.info("\n✅ 所有检查都通过了！")
        logger.info("机器人应该可以正常运行管理员命令。\n")
        return 0
    else:
        logger.error("\n❌ 检查到问题，请按照提示修复。\n")
        show_next_steps()
        return 1

if __name__ == '__main__':
    sys.exit(main())
