"""数据库模块 - 兼容性封装

这是一个兼容性包装层，提供对 database_mysql 模块的别名。
这样可以保持导入接口的一致性。
"""

from database_mysql import MySQLDatabase

# 创建别名，使 'from database import Database' 可用
Database = MySQLDatabase

__all__ = ['Database']
