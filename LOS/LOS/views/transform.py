from flask import render_template, session, Blueprint, make_response, request
from ..utils import db
from io import BytesIO, StringIO
from openpyxl import Workbook
import xlwt  # 适配xls格式
import csv   # 适配csv格式
from urllib.parse import quote
from ..utils.STATUS_map import STATUS_MAP
import traceback

tra = Blueprint('transform', __name__)

def verify(user, user_id):
    """
    验证用户权限
    :param user: 当前登录用户
    :param user_id: 请求操作的用户ID
    :return: 是否有权限
    """
    user = session.get('user')
    is_admin = (user.get('role') == 'admin')
    is_user = (user.get('role') == 'user') 
    if not user :
        return render_template('error.html', error="请先登录")
def export_table_to_file(headers, data, export_format, filename_prefix):
    """
    通用表格导出函数
    :param headers: 表头列表
    :param data: 导出数据列表（字典格式）
    :param export_format: 导出格式（xlsx/xls/csv）
    :param filename_prefix: 文件名前缀（最终文件名：前缀.格式）
    :return: BytesIO/StringIO, 文件名, Content-Type
    """
    # 格式校验
    if export_format not in ['xlsx', 'xls', 'csv']:
        raise ValueError(f"不支持的导出格式：{export_format}，仅支持xlsx/xls/csv")

    filename = f"{filename_prefix}.{export_format}"
    encoded_filename = quote(filename, encoding='utf-8')

    # 1. xlsx格式（openpyxl）
    if export_format == 'xlsx':
        wb = Workbook()
        ws = wb.active
        ws.title = filename_prefix
        ws.append(headers)
        for row in data:
            ws.append(row)
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"# 微软Excel格式
    
    # 2. xls格式（xlwt）
    elif export_format == 'xls':
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet(filename_prefix)
        # 写入表头
        for col, header in enumerate(headers):
            ws.write(0, col, header)
        # 写入数据
        for row_idx, row in enumerate(data, start=1):
            for col_idx, value in enumerate(row):
                ws.write(row_idx, col_idx, value)
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        content_type = "application/vnd.ms-excel"# 微软Excel格式
    
    # 3. csv格式（csv模块）
    elif export_format == 'csv':
        output = StringIO()
        # 解决csv中文乱码问题（添加BOM）
        output.write('\ufeff')
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(data)
        output.seek(0)
        content_type = "text/csv; charset=utf-8"# CSV格式

    return output, encoded_filename, content_type

def get_order_data():
    user = session.get('user')
    if not user:
        return render_template("login.html", error="请先登录")
    role = user.get('role')
    
    """提取通用订单数据查询逻辑"""
    try:
        if role == 'admin':
            sql = """
                SELECT u.id AS o.user_id,
                o.products_id AS p.products_id,
                u.user_name,
                u.address,
                u.phone,
                o.count,
                o.status
                p.products_price,
                p.cost

                FROM `order` o 
                LEFT JOIN price p ON o.products_id = p.products_id
                LEFT JOIN user u ON o.user_id = u.id
            """
            orders = db.fetchall(sql, [])
        else:
            sql = """
                SELECT u.user_name, u.address, u.phone, o.* 
                FROM `order` o 
                LEFT JOIN user u ON o.user_id = u.id
                WHERE o.user_id=%s
            """
            orders = db.fetchall(sql, [user['id']])
        
        # 格式化数据（适配导出函数的列表格式）
        formatted_data = []
        for order in orders:
            formatted_data.append([
                order['user_name'],
                order['address'],
                order['phone'],
                order['id'],
                order['user_id'],
                order['products_id'],
                order['count'],
                STATUS_MAP.get(order['status'], "未知状态")
            ])
        return formatted_data
    except Exception as e:
        print(f"查询订单数据失败：{str(e)}，详情：{traceback.format_exc()}")
        raise


@tra.route('/transform/user', methods=['GET'])
def transform_user():
    """用户仅导出自己的订单（仅user角色）"""
    try:
        user = session.get('user')
        if not user:
            return render_template("login.html", error="请先登录")
        if user.get('role') != 'user':
            return render_template("login.html", error="您没有权限访问")
        
        # 获取导出格式（默认xlsx）
        export_format = request.args.get('format', 'xlsx').lower()
        # 查询数据
        order_data = get_order_data(user, user_id=user['id'])
        # 定义表头和文件名
        headers = ["用户名", "地址", "电话", "订单ID", "用户ID", "商品ID", "数量", "订单状态"]
        filename_prefix = "用户订单数据"
        
        # 生成文件流
        output, encoded_filename, content_type = export_table_to_file(
            headers, order_data, export_format, filename_prefix
        )
        
        # 构建响应
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
        response.headers["Content-Type"] = content_type
        return response
    
    except ValueError as e:
        return render_template("error.html", error=f"导出失败：{str(e)}"), 400
    except Exception as e:
        return render_template("error.html", error=f"系统异常：{str(e)}"), 500

@tra.route('/transform/order', methods=['GET'])
def transform_order():
    """管理员导出所有订单，普通用户导出自己的订单"""
    try:
        user = session.get('user')
        if not user:
            return render_template("login.html", error="请先登录")
        
        export_format = request.args.get('format', 'xlsx').lower()
        is_admin = (user.get('role') == 'admin')
        order_data = get_order_data(user, is_admin=is_admin)
        
        headers = ["用户名", "地址", "电话", "订单ID", "用户ID", "商品ID", "数量", "订单状态"]
        filename_prefix = "订单数据"
        
        output, encoded_filename, content_type = export_table_to_file(
            headers, order_data, export_format, filename_prefix
        )
        
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
        response.headers["Content-Type"] = content_type
        return response
    
    except ValueError as e:
        return render_template("error.html", error=f"导出失败：{str(e)}"), 400
    except Exception as e:
        return render_template("error.html", error=f"系统异常：{str(e)}"), 500

@tra.route('/transform/order/price', methods=['GET'])
def transform_order_price():
    """导出含价格的订单数据（补充price相关逻辑，需根据实际表结构调整）"""
    try:
        user = session.get('user')
        if not user:
            return render_template("login.html", error="请先登录")
        
        export_format = request.args.get('format', 'xlsx').lower()
        is_admin = (user.get('role') == 'admin')
        

        try:
            if is_admin:
                sql = """
                    SELECT p.products_price, p.id,p.products_id,p.stock,p.sell,p.cost, o.* 
                    FROM `order` o 
                    JOIN user u ON o.user_id = u.id
                """
                orders = db.fetchall(sql, [])
            else:
                sql = """
                    SELECT u.user_name, u.address, u.phone, o.* 
                    FROM `order` o 
                    JOIN user u ON o.user_id = u.id
                    WHERE o.user_id=%s
                """
                orders = db.fetchall(sql, [user['id']])
            
            # 格式化数据（新增价格列）
            formatted_data = []
            for order in orders:
                formatted_data.append([
                    order['user_name'],
                    order['address'],
                    order['phone'],
                    order['id'],
                    order['user_id'],
                    order['products_id'],
                    order['count'],
                    STATUS_MAP.get(order['status'], "未知状态"),
                    order.get('price', 0)  # 补充价格字段（需确认表结构）
                ])
        except Exception as e:
            print(f"查询含价格的订单数据失败：{str(e)}")
            raise
        
        # 表头新增「订单金额」
        headers = ["用户名", "地址", "电话", "订单ID", "用户ID", "商品ID", "数量", "订单状态", "订单金额"]
        filename_prefix = "订单数据（含价格）"
        
        output, encoded_filename, content_type = export_table_to_file(
            headers, formatted_data, export_format, filename_prefix
        )
        
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
        response.headers["Content-Type"] = content_type
        return response
    
    except ValueError as e:
        return render_template("error.html", error=f"导出失败：{str(e)}"), 400
    except Exception as e:
        return render_template("error.html", error=f"系统异常：{str(e)}"), 500