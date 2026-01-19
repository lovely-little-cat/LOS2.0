from flask import render_template, session, Blueprint, make_response
from ..utils import db  
from io import BytesIO
from openpyxl import Workbook
from urllib.parse import quote
from ..utils.STATUS_map import STATUS_MAP
import logging

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('error.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

TABLE_CONFIG = {
    "order": {
        "headers": ["用户名", "地址", "电话", "订单ID", "用户ID", "商品ID", "数量", "订单状态"],
        "sql": {
            "admin": """
                SELECT u.user_name, u.address, u.phone, o.* 
                FROM `order` o 
                JOIN user u ON o.user_id = u.id
            """,
            "user": """
                SELECT u.user_name, u.address, u.phone, o.* 
                FROM `order` o 
                JOIN user u ON o.user_id = u.id
                WHERE o.user_id=%s
            """
        },
        "formatter": lambda row: [
            row['user_name'], row['address'], row['phone'], row['id'],
            row['user_id'], row['products_id'], row['count'],
            STATUS_MAP.get(row['status'], "未知状态")
        ]
    },
    "user": {
        "headers": ["用户ID", "用户名", "地址", "电话", "角色", "创建时间"],
        "sql": {
            "admin": "SELECT u.id, u.user_name, u.address, u.phone, u.role, o.buy_time FROM `user` u JOIN `order` o ON o.user_id = u.id",
            "user": "SELECT u.id, u.user_name, u.address, u.phone, u.role, o.buy_time FROM `user` u JOIN `order` o ON o.user_id = u.id WHERE u.id=%s"
        },
        "formatter": lambda row: [
            row['id'], row['user_name'], row['address'], row['phone'],
            row['role'], row['buy_time']
        ]
    },
    "price": {
        "headers": ["价格ID", "商品ID", "价格", "更新时间"],
        "sql": {
            "admin": "SELECT p.id, p.products_id, p.products_price, o.buy_time FROM `price` p JOIN `order` o ON p.products_id=o.products_id",
            "user": "SELECT p.*, o.buy_time FROM `price` p JOIN `order` o ON p.products_id=o.products_id WHERE o.user_id=%s"
        },
        "formatter": lambda row: [
            row['id'], row['products_id'], row['products_price'], row['buy_time']
        ]
        
    }
}

tra = Blueprint('transform', __name__)

def query_table_data(table_name: str, user: dict) -> list:
    """
    通用表数据查询
    :param table_name: 表名（order/user/price）
    :param user: 会话用户信息
    :return: 查询结果列表（字典格式）
    :raises PermissionError: 权限/表名无效异常
    """
   
    if table_name not in TABLE_CONFIG:
        raise PermissionError(f"不支持的表：{table_name}")
    
   
    role = user.get('role')
    user_id = user.get('id')
    if not role or not user_id:
        raise PermissionError("用户信息不完整，请重新登录")
    
  
    config = TABLE_CONFIG[table_name]
    sql = config["sql"].get(role)
    if not sql:
        raise PermissionError(f"角色{role}无{table_name}表访问权限")
    
   
    params = [user_id] if role == 'user' else []
    result = db.fetchall(sql, params)
    
   
    if not result:
        logger.warning(f"用户{user_id}查询{table_name}表无数据")
    return result

def generate_excel_by_table(table_name: str, data: list) -> BytesIO:
    """通用Excel生成（逻辑不变，适配db.py返回的字典格式数据）"""
    try:
        config = TABLE_CONFIG[table_name]
        wb = Workbook()
        ws = wb.active
        ws.title = f"{table_name}表数据"
        

        ws.append(config["headers"])

        for row in data:
            ws.append(config["formatter"](row))
        
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output
    except Exception as e:
        logger.error(f"生成{table_name}表Excel失败: {str(e)}")
        raise Exception(f"{table_name}表Excel生成失败，请联系管理员") from e

def build_download_response(excel_io: BytesIO, filename: str) -> make_response:
    """通用下载响应构建（逻辑不变）"""
    encoded_filename = quote(filename, encoding='utf-8')
    response = make_response(excel_io.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

def check_login(user):
    """通用登录校验"""
    if not user:
        return render_template("login.html", error="请先登录")
    return None

@tra.route('/transform/order', methods=['GET','POST'])
def transform_order():
    """订单表导出"""
    try:
        user = session.get('user')
        login_error = check_login(user)
        if login_error:
            return login_error
        
        data = query_table_data("order", user)
        excel_io = generate_excel_by_table("order", data)
        return build_download_response(excel_io, "订单数据.xlsx")
    except PermissionError as e:
        return render_template("error.html", error=str(e))
    except Exception as e:
        return render_template("error.html", error=str(e))

@tra.route('/transform/user', methods=['GET','POST'])
def transform_user():
    """用户表导出"""
    try:
        user = session.get('user')
        login_error = check_login(user)
        if login_error:
            return login_error
        
        data = query_table_data("user", user)
        excel_io = generate_excel_by_table("user", data)
        return build_download_response(excel_io, "用户数据.xlsx")
    except PermissionError as e:
        return render_template("error.html", error=str(e))
    except Exception as e:
        return render_template("error.html", error=str(e))

@tra.route('/transform/price', methods=['GET','POST'])
def transform_price():
    """价格表导出"""
    try:
        user = session.get('user')
        login_error = check_login(user)
        if login_error:
            return login_error
        
        data = query_table_data("price", user)
        excel_io = generate_excel_by_table("price", data)
        return build_download_response(excel_io, "价格数据.xlsx")
    except PermissionError as e:
        return render_template("error.html", error=str(e))
    except Exception as e:
        return render_template("error.html", error=str(e))
