# TODO: mysql连接并创建游标
# 对每一个接口进程请求生成一个数据库游标，并在操作结束后释放游标
from app.config import DB_DB, DB_HOST, DB_PASSWORD, DB_USER, DB_PORT
import pymysql



def cur_p(fun):
    def connect(*args, **kwargs):
        conn = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_DB, DB_PORT)
        cur = conn.cursor(pymysql.cursors.DictCursor)
        res = fun(*args, **kwargs, conn=conn, cur=cur)
        conn.commit()
        cur.close()
        conn.close()
        return res
    return connect