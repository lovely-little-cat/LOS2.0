import pymysql
from flask import json
from dbutils.pooled_db import PooledDB
from pymysql import cursors

Pool = PooledDB(
    creator=pymysql,
    maxconnections=10,
    mincached=2,
    maxcached=5,
    maxshared=3,
    blocking=True,
    maxusage=None,
    setsession=[],
    ping=1,
    host='127.0.0.1',
    port=3306,
    db='LOS',
    user='root',
    password='@A3115839287a',
    charset='utf8mb4',
)

def fetchone(sql, params):
    """查询单条数据"""
    conn = None
    cursor = None
    try:
        conn = Pool.connection()
        cursor = conn.cursor(cursors.DictCursor)
        cursor.execute(sql, params)
        return cursor.fetchone()
    except Exception as e:
        print(f"数据库查询错误: {str(e)}")
        return None
    finally:
     
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def fetchall(sql, params):
    """查询多条数据"""
    conn = None
    cursor = None
    try:
        conn = Pool.connection()
        cursor = conn.cursor(cursors.DictCursor)
        cursor.execute(sql, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"数据库查询错误: {str(e)}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def manage_order(sql, params):
    """管理订单"""
    conn = None
    cursor = None
    try:
        conn = Pool.connection()
        cursor = conn.cursor(cursors.DictCursor)
        cursor.execute(sql, params)
        conn.commit()
    except Exception as e:
        print(f"数据库查询错误: {str(e)}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()