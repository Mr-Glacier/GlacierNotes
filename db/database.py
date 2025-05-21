import sqlite3
import os


class Database:
    def __init__(self, db_path='glacier_notes.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 返回字典式结果
        self._init_schema()

    def _init_schema(self):
        """初始化数据库表结构"""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            """)

    def execute(self, sql, params=(), commit=False):
        """通用执行方法，适用于 INSERT、UPDATE、DELETE"""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        if commit:
            self.conn.commit()
        return cursor

    def query(self, sql, params=()):
        """通用查询方法"""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

    def execute_transaction(self, operations):
        """
        执行一个事务操作列表
        operations: List[Tuple[sql:str, params:tuple]]
        """
        try:
            with self.conn:
                for sql, params in operations:
                    self.conn.execute(sql, params)
        except sqlite3.Error as e:
            print("事务失败:", e)
            raise

    def get_connection(self):
        """返回底层连接（不推荐外部使用）"""
        return self.conn

    def close(self):
        """关闭连接"""
        self.conn.close()
