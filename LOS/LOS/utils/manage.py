from ..utils.db import Pool, cursors

class ManageOrder:  
    """管理订单（上下文管理器版本）"""
    def __enter__(self):
        self.conn = None
        self.cursor = None
        try:
            self.conn = Pool.connection()
            self.cursor = self.conn.cursor(cursors.DictCursor)
            return self.conn, self.cursor 
        except Exception as e:

            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            raise e  

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.conn:
                if exc_type: 
                    self.conn.rollback()
                else:  
                    self.conn.commit()
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        
        return False