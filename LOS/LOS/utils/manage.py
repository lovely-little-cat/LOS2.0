from ..utils.db import Pool, cursors

class ManageOrder:  # 类名改为大写开头（PEP8规范），避免和函数名冲突
    """管理订单（上下文管理器版本）"""
    def __enter__(self):
        # 初始化属性，避免__exit__中访问不存在的属性
        self.conn = None
        self.cursor = None
        try:
            self.conn = Pool.connection()
            self.cursor = self.conn.cursor(cursors.DictCursor)
            return self.conn, self.cursor  # 返回(conn, cursor)
        except Exception as e:
            # 连接失败时清理资源
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            raise e  # 抛出异常供上层处理

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.conn:
                if exc_type:  # 有异常则回滚
                    self.conn.rollback()
                else:  # 无异常则提交
                    self.conn.commit()
        finally:
            # 确保游标和连接最终关闭
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        
        # 返回True抑制异常（可选，根据需求调整：返回False则异常继续抛出）
        # return True  
        return False