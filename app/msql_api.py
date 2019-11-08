# TODO: sqlAPI


from app.decorate import cur_p
import json, datetime

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
                print(res[0], res[1])
                cur.execute("insert into {0} {1} values {2}".format(table, res[0], res[1]))
                return 'success'
            except Exception as e:
                print("写入失败", e)
                return 'error'
        else:
            return 'insert error'

    @staticmethod
    @cur_p
    def insert_up_data(data, up1, up2, up3, table, cur='', conn=''):
        res = FlaskAPI.deal_data(data)
        if res != 'data status error':
            try:
                cur.execute("insert into {0} {1} values {2}".format(table, res[0], res[1]))
                sql = "update service_pack set service_quota = JSON_SET(service_quota, '$.service{0}', {1}) where user_id = {2};".format(up3, up1, up2)
                cur.execute(sql)
                return 'success'
            except Exception as e:
                conn.rollback()
                print("写入失败", e)
                return 'error'
        else:
            return 'insert error'

    @staticmethod
    @cur_p
    def insert_cancel_data(d1, d2, d3, d4, d5, d6, cur='', conn=''):
        # id, status, service_id, order_detail, order_number
        try:
            # 增
            cur.execute("insert into invoice_cancel (status, service_id, user_id, "
                        "ic_id, order_detail, order_number, completion_date, booking_type) values (3, "
                        "{0}, {1}, {2}, {3}, '{4}', '{5}', 1);".format(d5[0]['service_id'],
                                                           d5[0]['user_id'], d5[0]['insurance_company_id'],
                                                           json.dumps(d5[0]['order_detail'], ensure_ascii=False), d5[0]['order_number'], d6))
            # 删
            cur.execute("delete from booking_service where id = {0};".format(d1))
            # 改
            sql = "update service_pack set service_quota = JSON_SET(service_quota, '$.service{0}', {1}) where user_id = {2};".format(
                d2, d3, d4)
            cur.execute(sql)
            return 'success'
        except Exception as e:
            conn.rollback()
            print("写入失败", e)
            return 'error'

    @staticmethod
    @cur_p
    def insert_ups_data(data, up1, up2, up3, table, third_id, cur='', conn=''):
        res = FlaskAPI.deal_data(data)
        if res != 'data status error':
            try:
                cur.execute("insert into {0} {1} values {2}".format(table, res[0], res[1]))
                cur.execute("update third_party_coupon set is_used = 1 where id = {0};".format(third_id))
                sql = "update service_pack set service_quota = JSON_SET(service_quota, '$.service{0}', {1}) where user_id = {2};".format(
                    up3, up1, up2)
                cur.execute(sql)
                return 'success'
            except Exception as e:
                conn.rollback()
                print("写入失败", e)
                return 'error'
        else:
            return 'insert error'

    @staticmethod
    @cur_p
    def insert_cancels_data(d1, d2, d3, d4, d5, d6, cur='', conn=''):
        try:
            # 增
            cur.execute("insert into invoice_cancel (status, service_id, user_id, "
                        "ic_id, order_detail, order_number, completion_date, booking_type, ticket_code, store_id) values (3, "
                        "{0}, {1}, {2}, {3}, '{4}', '{5}', 1, {6}, {7});".format(d5[0]['service_id'],
                                                                       d5[0]['user_id'], d5[0]['insurance_company_id'],
                                                                       json.dumps(d5[0]['order_detail'],
                                                                                  ensure_ascii=False),
                                                                       d5[0]['order_number'], d6, d5[0]['ticket_id'], d5[0]['store_id']))
            # 删
            cur.execute("delete from non_booking_service where id = {0};".format(d1))
            # 改
            cur.execute("update third_party_coupon set is_used = 0 where id = {0};".format(d5[0]['ticket_id']))
            sql = "update service_pack set service_quota = JSON_SET(service_quota, '$.service{0}', {1}) where user_id = {2};".format(
                d2, d3, d4)
            cur.execute(sql)
            return 'success'
        except Exception as e:
            conn.rollback()
            print("写入失败", e)
            return 'error'


    # TODO: 获取该用户
    # userInfo = Users.query.filter_by(username=username).first()
    @staticmethod
    @cur_p
    def filter_user(data1, data2, data3, data4, cur='', conn=''):
        try:
            sql = "select * from user_detail_info where name='{0}' and inc_vin='{1}' and insurance_id='{2}' and insurance_company_id='{3}';".format(data1, data2, data3, data4)
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
            sql = "update user_detail_info set hash_auth = '{0}' where inc_vin='{1}';".format(data1, data2)
            cur.execute(sql)
            return 'update success'
        except Exception as e:
            print("auth存hash失败", e)
            return "error"

    # TODO: token添加login_time
    @staticmethod
    @cur_p
    def save_login_time(data1, data2, cur='', conn=''):
        try:
            sql = "update user_detail_info set login_time = '{0}' where inc_vin='{1}';".format(data1, data2)
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
            sql = "select * from user_detail_info where id = {0};".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'user is not exist'
        except Exception as e:
            print("获取用户对象失败", e)
            return "error"

    # TODO: 保单号（third_party_coupo 根据ticket_code(保单号)查 id  id即为ticket_id）
    @staticmethod
    @cur_p
    def filter_by_insurance_id(data, cur='', conn=''):
        try:
            sql = "select id, sp_id, ticket_code from third_party_coupon where service_id = {0} and is_used = 0 limit 1;".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'third_party_coupo is not exist'
        except Exception as e:
            print("ticket_id获取失败", e)
            return "error"

    # TODO: 三方表添加服务订单号order_id
    @staticmethod
    @cur_p
    def update_order_id(data1, data2, cur='', conn=''):
        try:
            sql = "update third_party_coupon set order_id = {0} where id = {1};".format(data1, data2)
            cur.execute(sql)
            return 'update success'
        except Exception as e:
            print("order_id修改失败", e)
            return "error"

    # TODO: 查询用户的预约服务booking_service
    @staticmethod
    @cur_p
    def filter_booking_service(data, cur='', conn=''):
        try:
            sql = "select id, status, service_id, order_detail, order_number from booking_service where user_id = {0};".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return []
        except Exception as e:
            print("预约服务查询失败", e)
            return "error"

    # TODO: 查询用户的预约服务booking_service
    @staticmethod
    @cur_p
    def booking_service(data, cur='', conn=''):
        try:
            sql = "select * from booking_service where id = {0};".format(
                data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'booking_service is not exist'
        except Exception as e:
            print("预约服务查询失败", e)
            return "error"

    # TODO: 查询用户的非预约服务booking_service
    @staticmethod
    @cur_p
    def filter_non_booking_service(data, cur='', conn=''):
        try:
            sql = "select id, status, service_id, order_detail, ticket_id, order_number, store_id, booking_date from non_booking_service where user_id = {0};".format(
                data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return []
        except Exception as e:
            print("非预约服务查询失败", e)
            return "error"

    # TODO: 查询用户的非预约服务booking_service
    @staticmethod
    @cur_p
    def non_booking_service(data, cur='', conn=''):
        try:
            sql = "select * from non_booking_service where id = {0};".format(
                data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'non_booking_service is not exist'
        except Exception as e:
            print("非预约服务查询失败", e)
            return "error"

    # TODO: 查询用户的操作订单服务invoice
    @staticmethod
    @cur_p
    def filter_invoice(data, cur='', conn=''):
        try:
            sql = "select id, status, service_id, order_detail, completion_date, ticket_code, order_number, store_id from invoice where user_id = {0};".format(
                data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return []
        except Exception as e:
            print("操作订单失败", e)
            return "error"

    # TODO: 查询用户的操作订单服务invoice
    @staticmethod
    @cur_p
    def filter_invoice_cancel(data, cur='', conn=''):
        try:
            sql = "select id, status, service_id, order_detail, completion_date, ticket_code, order_number, store_id from invoice_cancel where user_id = {0};".format(
                data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return []
        except Exception as e:
            print("操作订单失败", e)
            return "error"

    # TODO: 根据ticket_id查订单编号
    @staticmethod
    @cur_p
    def filter_ticket(data, cur='', conn=''):
        try:
            sql = "select order_id from third_party_coupon where id = {0};".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'third_party_coupon is not exist'
        except Exception as e:
            print("order_id修改失败", e)
            return "error"

    # TODO: 返回公司列表
    @staticmethod
    @cur_p
    def get_company(cur='', conn=''):
        try:
            sql = "select id,name from insurance_company"
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'insurance_company is not exist'
        except Exception as e:
            print("公司info获取失败", e)
            return "error"

    # TODO: 模糊query机场
    @staticmethod
    @cur_p
    def filter_like_airport(data, cur='', conn=''):
        try:
            sql = "select * from airports where name like '%{0}%' or province like '%{1}%'".format(data, data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'airports is not exist'
        except Exception as e:
            print("模糊查询机场信息失败", e)
            return "error"

    # TODO: 模糊query高铁站
    @staticmethod
    @cur_p
    def filter_like_station(data, cur='', conn=''):
        try:
            sql = "select * from stations where name like '%{0}%' or province like '%{1}%'".format(data,
                                                                                                          data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'airports is not exist'
        except Exception as e:
            print("模糊高铁站信息失败", e)
            return "error"

    # TODO: 查次数
    @staticmethod
    @cur_p
    def filter_pack(data, cur='', conn=''):
        try:
            sql = "select service_quota from service_pack where user_id = {0}".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'service_pack is not exist'
        except Exception as e:
            print("次数查询失败", e)
            return "error"

    # TODO: 查询某地区附近门店(车享家可查看全部)
    @staticmethod
    @cur_p
    def filter_stores(province, city, area, d1, d2, d3, cur='', conn=''):
        try:
            sql = "select id,store_phone,store_address,name, store_provider, longitude, latitude from stores_cxj where " \
                  "province = '{0}' and city = '{1}' and area = '{2}' and {3} = 1 and id >= (select id from stores_cxj " \
                  "where province = '{0}' and city = '{1}' and area = '{2}' and {3} = 1 limit {4}, 1) " \
                  "limit {5};".format(province, city, area, d1, d2, d3)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'stores_cxj is not exist'
        except Exception as e:
            print("该地区附近门店查询失败", e)
            return "error"

    # TODO: 查询某地区附近门店(普通)
    @staticmethod
    @cur_p
    def filter_stores_common(province, city, area, d1, d2, d3, cur='', conn=''):
        try:
            sql = "select id,store_phone,store_address,name, store_provider, longitude, latitude from stores_cxj where " \
                  "province = '{0}' and city = '{1}' and area = '{2}' and {3} = 1 and store_provider != (select id from " \
                  "service_provider_list where sp_name = '车享家') and id >= (select id from stores_cxj " \
                  "where province = '{0}' and city = '{1}' and area = '{2}' and {3} = 1 and store_provider != (select id " \
                  "from service_provider_list where sp_name = '车享家')limit {4}, 1) " \
                  "limit {5};".format(province, city, area, d1, d2, d3)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return []
        except Exception as e:
            print("该地区附近门店查询失败", e)
            return "error"

    # TODO: 查询某地区附近门店数量
    @staticmethod
    @cur_p
    def filter_stores_numbers(province, city, area, d1, cur='', conn=''):
        try:
            sql = "select count(*) from stores_cxj where province = '{0}' and city = '{1}' and area = '{2}' and {3} = 1;".format(province, city, area, d1)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'number is not exist'
        except Exception as e:
            print("该地区附近门店数量查询失败", e)
            return "error"

    # TODO: 查询某地区附近门店数量
    @staticmethod
    @cur_p
    def filter_stores_numbers_common(province, city, area, d1, cur='', conn=''):
        try:
            sql = "select count(*) from stores_cxj where province = '{0}' and city = '{1}' and area = '{2}' and " \
                  "store_provider != (select id from service_provider_list where sp_name = '车享家') and {3} = 1;".format(
                province, city, area, d1)
            print(sql)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'number is not exist'
        except Exception as e:
            print("该地区附近门店数量查询失败", e)
            return "error"

    # TODO: 查询用户信息是否完善
    @staticmethod
    @cur_p
    def filter_info_complete(data, cur='', conn=''):
        try:
            sql = "select inc_state from user_detail_info where id = {0};".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'user_detail_info is not exist'
        except Exception as e:
            print("该用户信息是否完善查询失败", e)
            return "error"

    # TODO: 完善用户信息
    @staticmethod
    @cur_p
    def complete_info(d1, d2, d3, d4, d5, cur='', conn=''):
        try:
            sql = "update user_detail_info set inc_state = 1, inc_name = '{0}', phone = {1}, car_plate_number = '{2}', dob = '{3}' where id = {4};".format(d1, d2, d3, d4, d5)
            cur.execute(sql)
            return 'success'
        except Exception as e:
            print("更新失败", e)
            return 'error'

    # TODO: 查询公司名称
    @staticmethod
    @cur_p
    def filter_company(data, cur='', conn=''):
        try:
            sql = "select * from service_provider_list where id = {0};".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'service_provider_list is not exist'
        except Exception as e:
            print("查找失败", e)
            return 'error'

    # TODO: 查询网点名称
    @staticmethod
    @cur_p
    def filter_stores_cxj(data, cur='', conn=''):
        try:
            sql = "select * from stores_cxj where id = {0};".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'stores_cxj is not exist'
        except Exception as e:
            print("查找失败", e)
            return 'error'

    # TODO: 查询权益
    @staticmethod
    @cur_p
    def filter_right(data, cur='', conn=''):
        try:
            sql = "select service_quota from service_pack where user_id = {0};".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return 'service_quota is not exist'
        except Exception as e:
            print("查找失败", e)
            return 'error'

    # TODO: 查询非预约服务中是否存在车享家的服务
    @staticmethod
    @cur_p
    def cxj_exits(d1, d2, cur='', conn=''):
        try:
            sql = "select store_id from non_booking_service where service_id = {0} and user_id = {1} and store_id in " \
                   "(select id from stores_cxj where store_provider = (select id from service_provider_list where " \
                   "sp_name = '车享家'));".format(d1, d2)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return []
        except Exception as e:
            print("查找失败", e)
            return 'error'

    # TODO: 查询非预约服务中是否存在车享家的服务
    @staticmethod
    @cur_p
    def cxj_count(d1, d2, d3, cur='', conn=''):
        try:
            sql1 = "select order_detail from non_booking_service where service_id = {0} and store_id = {1};".format(d2, d3)
            cur.execute(sql1)
            cf = cur.fetchall()
            res = 0
            for i in cf:
                a = json.loads(i["order_detail"])
                if a["UserTime"] == d1["UserTime"]:
                    res += 1
            return res
        except Exception as e:
            print("查找失败", e)
            return 'error'

    # TODO: 判断车享家和非车享家用户附近店铺的筛选
    @staticmethod
    @cur_p
    def filter_user_cxj(data, cur='', conn=''):
        try:
            sql = "select is_luxuryBrand from car_brand as a join user_detail_info as b on b.user_car_brand = a.id " \
                  "where b.id = {0};".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return res
            else:
                return []
        except Exception as e:
            print("筛选用户失败", e)
            return "error"