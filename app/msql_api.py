# TODO: sqlAPI


from app.decorate import cur_p


class FlaskAPI():
    # TODO: 将字典数据转换为字符串的形式
    @staticmethod
    def deal_data(data):
        # 接收数据并判断数据有效性
        if type(data) == dict and len(data) > 0:
            key = '(' + ','.join([i for i in data.keys()]) + ')'
            value = str([data[i] for i in data]).replace('[', '(').replace(']', ')')
            return key, value
        else:
            return 'data status error'

    @staticmethod
    @cur_p
    def insert_data(data, table, cur='', conn=''):
        res = FlaskAPI.deal_data(data)
        if res != 'data status error':
            try:
                cur.execute("insert into {0} {1} values {2}".format(table, res[0], res[1]))
                return 'success'
            except Exception as e:
                print("写入失败", e)
                return 'error'
        else:
            return 'insert error'

    # TODO: 获取该用户
    # userInfo = Users.query.filter_by(username=username).first()
    @staticmethod
    @cur_p
    def filter_user(data1, data2, data3, cur='', conn=''):
        try:
            sql = "select * from user_detail where name='{0}' and phone='{1}' and car_plate_number='{2}'".format(data1, data2, data3)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'user is not exist'
        except Exception as e:
            print("获取用户对象失败", e)
            return "error"

    # TODO: auth存hash
    @staticmethod
    @cur_p
    def save_hash(data1, data2, cur='', conn=''):
        try:
            sql = "update user_detail set hash_auth = '{0}' where phone='{1}'".format(data1, data2)
            cur.execute(sql)
            # res = cur.fetchall()
            # if res:
            return 'update success'
            # else:
            #     return 'user is not exist'
        except Exception as e:
            print("auth存hash失败", e)
            return "error"

    # TODO: token添加login_time
    @staticmethod
    @cur_p
    def save_login_time(data1, data2, cur='', conn=''):
        try:
            sql = "update user_detail set login_time = '{0}' where phone='{1}'".format(data1, data2)
            cur.execute(sql)
            # res = cur.fetchall()
            # if res:
            return 'update success'
            # else:
            #     return 'user is not exist'
        except Exception as e:
            print("token添加login_time失败", e)
            return "error"

    # TODO: 根据用户id获取用户信息
    @staticmethod
    @cur_p
    def filter_by_id(data, cur='', conn=''):
        try:
            sql = "select * from user_detail where id = {0}".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'user is not exist'
        except Exception as e:
            print("获取用户对象失败", e)

    # # TODO: 添加酒后代驾服务信息
    # @staticmethod
    # @cur_p
    # def create_driver_info(data, cur='', conn=''):
    #     try:
    #         sql = "insert into booking_service {0} {1}"
    #     except Exception as e:
    #         print("添加酒后代驾服务信息失败", e)
    #         return "error"