# models/category_model.py

class CategoryModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.query("SELECT id, name FROM categories ORDER BY name")

    def add(self, name):
        self.db.execute("INSERT INTO categories (name) VALUES (?)", (name,), commit=True)

    def rename(self, category_id, new_name):
        self.db.execute(
            "UPDATE categories SET name = ? WHERE id = ?",
            (new_name, category_id),
            commit=True
        )

    def delete(self, category_id):
        # 连带删除 notes，不需额外 SQL，因为已开启外键级联
        self.db.execute("DELETE FROM categories WHERE id = ?", (category_id,), commit=True)
