from db import Pool, cursors

class manage_order:
    """管理订单（上下文管理器版本）"""
    def __enter__(self):
        self.conn = Pool.connection()
        self.cursor = self.conn.cursor(cursors.DictCursor)
        return self.conn, self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()