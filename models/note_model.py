# models/note_model.py

class NoteModel:
    def __init__(self, db):
        self.db = db

    def get_by_category(self, category_id):
        sql = """
            SELECT id, title 
            FROM notes 
            WHERE category_id = ? 
            ORDER BY updated_at DESC
        """
        return self.db.query(sql, (category_id,))

    def get_by_id(self, note_id):
        sql = "SELECT id, category_id, title, content, updated_at FROM notes WHERE id = ?"
        result = self.db.query(sql, (note_id,))
        return result[0] if result else None

    def add(self, category_id, title):
        sql = "INSERT INTO notes (category_id, title) VALUES (?, ?)"
        cursor = self.db.execute(sql, (category_id, title), commit=True)
        return cursor.lastrowid

    def delete(self, note_id):
        sql = "DELETE FROM notes WHERE id = ?"
        self.db.execute(sql, (note_id,), commit=True)

    def rename(self, note_id, new_title):
        sql = "UPDATE notes SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        self.db.execute(sql, (new_title, note_id), commit=True)

    def update_content(self, note_id, content):
        sql = "UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        self.db.execute(sql, (content, note_id), commit=True)

    def update_title(self, note_id, title):
        # 可合并进 rename 方法；保留独立函数便于调用清晰
        sql = "UPDATE notes SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        self.db.execute(sql, (title, note_id), commit=True)

    def update(self, note_id, title=None, content=None):
        """可选更新标题与内容"""
        fields = []
        params = []

        if title is not None:
            fields.append("title = ?")
            params.append(title)
        if content is not None:
            fields.append("content = ?")
            params.append(content)

        if not fields:
            return  # 无更新内容

        fields.append("updated_at = CURRENT_TIMESTAMP")
        sql = f"UPDATE notes SET {', '.join(fields)} WHERE id = ?"
        params.append(note_id)
        self.db.execute(sql, tuple(params), commit=True)
