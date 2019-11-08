from flask import jsonify, request, session
from app.users.model import Users
from app.msql_api import FlaskAPI
from app.auth.auths import Auth
from .. import common
import time,json, datetime
from .add import choose_sp


def init_api(app):
    @app.route('/auth/user/login', methods=['POST'])
    def login():
        """
        用户登录
        用户姓名 name/车架号后六位 vin/保单号 insurance_id
        :return: json
        """
        name = request.json.get('name')
        # phone = request.json.get('phone')
        inc_vin = request.json.get('inc_vin')
        # car_plate_number = request.json.get('car_plate_number')
        insurance_id = request.json.get('insurance_id')
        company_id = request.json.get('company_id')
        # print(insurance_number)
        if (not name or not inc_vin or not insurance_id or not company_id):
            return jsonify(common.falseReturn('', '车牌号和手机号不能为空'))
        else:
            # print(name, phone, car_plate_number)
            return Auth.authenticate(Auth, name, inc_vin, insurance_id, company_id)

    @app.route('/info/complete', methods=['POST'])
    def complete():
        """
        完善信息
        用户姓名 name/车架号后六位 vin/保单号 insurance_id
        :return: json
        """
        result = Auth.identify(Auth, request)
        inc_name = request.json.get('inc_name')
        phone = request.json.get('phone')
        dob = request.json.get('dob')
        car_plate_number = request.json.get('car_plate_number')
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            # 查询该用户信息是否完善
            # 出生日期 str 转 date
            birth_date = datetime.datetime.strptime(dob, "%Y-%m-%d")
            res = FlaskAPI.complete_info(inc_name, phone, car_plate_number, birth_date, user[0]["id"])
            if res == 'success':
                result = common.trueReturn(True, "请求成功")
            else:
                result = common.falseReturn(False, "请求失败")
        return jsonify(result)

    @app.route('/user', methods=['GET'])
    def get():
        """
        获取用户信息
        :return: json
        """
        result = Auth.identify(Auth, request)
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            returnUser = {
                'id': user[0]["id"],
                'insurance_id': user[0]["insurance_id"],
                'phone': user[0]["phone"],
                'login_time': user[0]["login_time"],
                "inc_state": user[0]["inc_state"]
            }
            result = common.trueReturn(returnUser, "请求成功")
        return jsonify(result)


    @app.route('/booking/drunk_driver', methods=['POST'])
    def driver():
        """
        预约-酒后代驾信息填写
        :return: json
        """
        result = Auth.identify(Auth, request)
        data_json = request.json.get('data_json')
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            # 查询该用户增值服务次数
            pack_number = FlaskAPI.filter_pack(data=user[0]["id"])
            if len(pack_number) > 0:
                # 次数清洗
                json_data = json.loads(pack_number[0]["service_quota"])
                number = json_data["service4"]
                if number > 0:
                    booking_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    # 自定义订单编号
                    order_id = int(time.time())
                    data = {
                        # 服务名称 4-代驾
                        "service_id": 4,
                        # 用户主键
                        "user_id": user[0]["id"],
                        # 服务公司
                        "insurance_company_id": user[0]["insurance_company_id"],
                        # 服务发布时间
                        "booking_date": booking_time,
                        # 默认发布状态为待完成
                        "status": 1,
                        # json表单内容
                        "order_detail": data_json,
                        # 预约类型
                        "order_number": 'DJ19' + '{0}'.format(order_id),
                        # sp_id 服务提供商
                        "sp_id": choose_sp(4)
                    }
                    # 插入预约服务信息并减少服务使用次数
                    up1 = number - 1
                    res2 = FlaskAPI.insert_up_data(data=data, up1=up1, up2=user[0]["id"], up3=4, table="booking_service")
                    if res2 == "success":
                        result = common.trueReturn(True, "预约服务代驾信息提交完成")
                    else:
                        result = common.trueReturn(False, "预约服务代驾信息提交失败")
                else:
                    result = common.trueReturn(False, "该服务次数不足")
            else:
                result = common.trueReturn(False, "暂无该用户服务信息")
        return jsonify(result)

    @app.route('/booking/airport', methods=['POST'])
    def airport():
        """
        预约-境内机场接送信息填写
        :return: json
        """
        result = Auth.identify(Auth, request)
        data_json = request.json.get('data_json')
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            # 查询该用户增值服务次数
            pack_number = FlaskAPI.filter_pack(data=user[0]["id"])
            if len(pack_number) > 0:
                # 次数清洗
                json_data = json.loads(pack_number[0]["service_quota"])
                number = json_data["service5"]
                if number > 0:
                    booking_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    # 自定义订单编号
                    order_id = int(time.time())
                    data = {
                        # 服务名称 5-境外机场接送
                        "service_id": 5,
                        # 用户主键
                        "user_id": user[0]["id"],
                        # 服务公司
                        "insurance_company_id": user[0]["insurance_company_id"],
                        # 服务发布时间
                        "booking_date": booking_time,
                        # 默认发布状态为待完成/完成/取消 1/2/3
                        "status": 1,
                        # json表单内容
                        "order_detail": data_json,
                        # 预约类型
                        "order_number": 'JNJ19' + '{0}'.format(order_id),
                        # sp_id 服务提供商
                        "sp_id": choose_sp(5)
                    }
                    # 插入预约服务信息并减少服务使用次数
                    up1 = number - 1
                    res2 = FlaskAPI.insert_up_data(data=data, up1=up1, up2=user[0]["id"], up3=5,
                                                   table="booking_service")
                    if res2 == "success":
                        result = common.trueReturn(True, "预约服务境外机场接送信息提交完成")
                    else:
                        result = common.trueReturn(False, "预约服务境外机场接送信息提交失败")
                else:
                    result = common.trueReturn(False, "该服务次数不足")
            else:
                result = common.trueReturn(False, "暂无该用户服务信息")
        return jsonify(result)

    @app.route('/booking/hsr', methods=['POST'])
    def hsr():
        """
        境内高铁站接送信息填写
        :return: json
        """
        result = Auth.identify(Auth, request)
        data_json = request.json.get('data_json')
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            # 查询该用户增值服务次数
            pack_number = FlaskAPI.filter_pack(data=user[0]["id"])
            if len(pack_number) > 0:
                # 次数清洗
                json_data = json.loads(pack_number[0]["service_quota"])
                number = json_data["service6"]
                if number > 0:
                    booking_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    # 自定义订单编号
                    order_id = int(time.time())
                    data = {
                        # 服务名称 6-境内高铁站接送
                        "service_id": 6,
                        # 用户主键
                        "user_id": user[0]["id"],
                        # 服务公司
                        "insurance_company_id": user[0]["insurance_company_id"],
                        # 服务发布时间
                        "booking_date": booking_time,
                        # 默认发布状态为待完成/完成/取消 1/2/3
                        "status": 1,
                        # json表单内容
                        "order_detail": data_json,
                        # 预约类型
                        "order_number": 'JNG19' + '{0}'.format(order_id),
                        # sp_id 服务提供商
                        "sp_id": choose_sp(6)
                    }
                    # 插入预约服务信息并减少服务使用次数
                    up1 = number - 1
                    res2 = FlaskAPI.insert_up_data(data=data, up1=up1, up2=user[0]["id"], up3=6,
                                                   table="booking_service")
                    if res2 == "success":
                        result = common.trueReturn(True, "预约服务境内高铁站接送信息提交完成")
                    else:
                        result = common.trueReturn(False, "预约服务境内高铁站接送信息提交失败")
                else:
                    result = common.trueReturn(False, "该服务次数不足")
            else:
                result = common.trueReturn(False, "暂无该用户服务信息")
        return jsonify(result)

    @app.route('/booking/airportvip', methods=['POST'])
    def airportvip():
        """
        机场/高铁贵宾厅信息填写
        :return: json
        """
        result = Auth.identify(Auth, request)
        data_json = request.json.get('data_json')
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            # 查询该用户增值服务次数
            pack_number = FlaskAPI.filter_pack(data=user[0]["id"])
            if len(pack_number) > 0:
                # 次数清洗
                json_data = json.loads(pack_number[0]["service_quota"])
                number = json_data["service7"]
                if number > 0:
                    booking_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    # 自定义订单编号
                    order_id = int(time.time())
                    data = {
                        # 服务名称 7-机场/高铁贵宾厅
                        "service_id": 7,
                        # 用户主键
                        "user_id": user[0]["id"],
                        # 服务公司
                        "insurance_company_id": user[0]["insurance_company_id"],
                        # 服务发布时间
                        "booking_date": booking_time,
                        # 默认发布状态为待完成/完成/取消 1/2/3
                        "status": 1,
                        # json表单内容
                        "order_detail": data_json,
                        # 预约类型
                        "order_number": 'GBT19' + '{0}'.format(order_id),
                        # sp_id 服务提供商
                        "sp_id": choose_sp(7)
                    }
                    # 插入预约服务信息并减少服务使用次数
                    up1 = number - 1
                    res2 = FlaskAPI.insert_up_data(data=data, up1=up1, up2=user[0]["id"], up3=7,
                                                   table="booking_service")
                    if res2 == "success":
                        result = common.trueReturn(True, "预约服务机场/高铁贵宾厅信息提交完成")
                    else:
                        result = common.trueReturn(False, "预约服务机场/高铁贵宾厅信息提交失败")
                else:
                    result = common.trueReturn(False, "该服务次数不足")
            else:
                result = common.trueReturn(False, "暂无该用户服务信息")
        return jsonify(result)

    # @app.route('/booking/parking', methods=['POST'])
    # def parking():
    #     """
    #     机场附近停车信息填写
    #     :return: json
    #     """
    #     result = Auth.identify(Auth, request)
    #     data_json = request.json.get('data_json')
    #     if (result['status'] and result['data']):
    #         user = Users.get(Users, result['data'])
    #         res1 = FlaskAPI.filter_by_insurance_id(data=7)
    #         if res1 != 'third_party_coupo is not exist' and res1 != 'error':
    #             # insurance_company_id  user[0]["insurance_coy_id]
    #             booking_time = time.strftime('%Y-%m-%d %H:%M:%S')
    #             data = {
    #                 # 代券
    #                 "ticket_id": res1[0]["id"],
    #                 # service_list表中服务id（代驾-4）
    #                 "service_id": 8,
    #                 # 未知商店id
    #                 "store_id": 1,
    #                 "user_id": user[0]["id"],
    #                 "insurance_company_id": user[0]["insurance_company_id"],
    #                 # 未知来源
    #                 # "booking_type": "Y",
    #                 # 未知来源/服务使用时间
    #                 "booking_date": booking_time,
    #                 # 默认发布状态为待完成
    #                 "status": 1,
    #                 # "sp_id": res1["sp_id"],
    #                 # user_detail_info主键
    #                 "order_detail": data_json
    #             }
    #             # 插入服务信息
    #             res2 = FlaskAPI.insert_data(data=data, table="booking_service")
    #
    #             if res2 == "success":
    #                 # 自定义订单编号
    #                 order_id = int(time.time())
    #                 # 修改三方使用券中的订单编号
    #                 res3 = FlaskAPI.update_order_id(data1=order_id, data2=res1[0]["id"])
    #                 if res3 == 'error':
    #                     result = common.trueReturn({}, "订单提交失败")
    #                     return jsonify(result)
    #                 result = common.trueReturn(True, "机场附近停车信息提交完成")
    #             else:
    #                 result = common.trueReturn(True, "机场附近停车信息提交失败")
    #         else:
    #             result = common.trueReturn(False, "三方券信息查询失败")
    #     return jsonify(result)

    @app.route('/booking/annualInspect', methods=['POST'])
    def annualInspect():
        """
        待办年检信息填写
        :return: json
        """
        result = Auth.identify(Auth, request)
        data_json = request.json.get('data_json')
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            # 查询该用户增值服务次数
            pack_number = FlaskAPI.filter_pack(data=user[0]["id"])
            if len(pack_number) > 0:
                # 次数清洗
                json_data = json.loads(pack_number[0]["service_quota"])
                number = json_data["service9"]
                if number > 0:
                    booking_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    # 自定义订单编号
                    order_id = int(time.time())
                    data = {
                        # 服务名称 9-待办年检
                        "service_id": 9,
                        # 用户主键
                        "user_id": user[0]["id"],
                        # 服务公司
                        "insurance_company_id": user[0]["insurance_company_id"],
                        # 服务发布时间
                        "booking_date": booking_time,
                        # 默认发布状态为待完成/完成/取消 1/2/3
                        "status": 1,
                        # json表单内容
                        "order_detail": data_json,
                        # 预约类型
                        "order_number": 'NJ19' + '{0}'.format(order_id),
                        # sp_id 服务提供商
                        "sp_id": choose_sp(9)
                    }
                    # 插入预约服务信息并减少服务使用次数
                    up1 = number - 1
                    res2 = FlaskAPI.insert_up_data(data=data, up1=up1, up2=user[0]["id"], up3=9,
                                                   table="booking_service")
                    if res2 == "success":
                        result = common.trueReturn(True, "预约服务待办年检信息提交完成")
                    else:
                        result = common.trueReturn(False, "预约服务待办年检信息提交失败")
                else:
                    result = common.trueReturn(False, "该服务次数不足")
            else:
                result = common.trueReturn(False, "暂无该用户服务信息")
        return jsonify(result)

    @app.route('/api/order', methods=['GET'])
    def orders():
        """
        订单查询
        :return: json
        """
        result = Auth.identify(Auth, request)
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            # 订单-预约服务
            res1 = FlaskAPI.filter_booking_service(user[0]["id"])
            # 订单-非预约服务
            res2 = FlaskAPI.filter_non_booking_service(user[0]["id"])
            if res2 != 'error':
                for i in res2:
                    stores_info = FlaskAPI.filter_stores_cxj(i["store_id"])
                    cpmpany = FlaskAPI.filter_company(stores_info[0]["store_provider"])
                    i["store_id"] = stores_info[0]
                    i["store_id"]["company"] = cpmpany[0]['sp_name']
            # 订单完成
            res3 = FlaskAPI.filter_invoice(user[0]["id"])
            if res3 != 'error':
                for j in res3:
                    if j["store_id"] is not None:
                        stores_info_j = FlaskAPI.filter_stores_cxj(j["store_id"])
                        cpmpany = FlaskAPI.filter_company(stores_info_j[0]["store_provider"])
                        j["store_id"] = stores_info_j[0]
                        j["store_id"]["company"] = cpmpany[0]['sp_name']
            # 订单取消
            res4 = FlaskAPI.filter_invoice_cancel(user[0]["id"])
            if res4 != 'error':
                for z in res4:
                    if z["store_id"] is not None:
                        stores_info_z = FlaskAPI.filter_stores_cxj(z["store_id"])
                        cpmpany = FlaskAPI.filter_company(stores_info_z[0]["store_provider"])
                        z["store_id"] = stores_info_z[0]
                        z["store_id"]["company"] = cpmpany[0]['sp_name']
            if res1 != 'error' and res2 != 'error' and res3 != 'error' and res4 != 'error':
                res = res1 + res2 + res3 + res4
                result = common.trueReturn(res, "请求成功")
            else:
                result = common.trueReturn(False, "服务查询失败")
            return jsonify(result)
        else:
            return jsonify("token error")

    @app.route('/api/cancel', methods=['POST'])
    def cancel():
        """
        订单取消
        :return: json
        """
        result = Auth.identify(Auth, request)
        data = request.json.get('data')
        if (result['status'] and result['data']):
            booking_time = time.strftime('%Y-%m-%d %H:%M:%S')
            user = Users.get(Users, result['data'])
            # 服务类型(预约/非预约)
            type = data["service_type"]
            # 主键
            pid = data["primary_id"]
            if type == '1':
                # 预约
                rs = FlaskAPI.booking_service(pid)
                if rs != 'booking_service is not exist':
                    # 查询该用户增值服务次数
                    pack_number = FlaskAPI.filter_pack(data=user[0]["id"])
                    json_data = json.loads(pack_number[0]["service_quota"])
                    number = json_data["service{0}".format(rs[0]["service_id"])]
                    up_number = number + 1
                    results = FlaskAPI.insert_cancel_data(pid, rs[0]["service_id"], up_number, user[0]["id"], rs, booking_time)
                else:
                    results = 'false'
            else:
                # 非预约
                rs = FlaskAPI.non_booking_service(pid)
                # 查询该用户增值服务次数
                pack_number = FlaskAPI.filter_pack(data=user[0]["id"])
                json_data = json.loads(pack_number[0]["service_quota"])
                number = json_data["service{0}".format(rs[0]["service_id"])]
                up_number = number + 1
                results = FlaskAPI.insert_cancels_data(pid, rs[0]["service_id"], up_number, user[0]["id"], rs, booking_time)
            if results == 'success':
                result = common.trueReturn(True, "取消订单成功")
            else:
                result = common.falseReturn(False, "取消订单失败")
            return jsonify(result)
        else:
            return jsonify("token error")

    @app.route('/api/company', methods=['GET'])
    def company():
        """
        返回公司列表
        :return: json
        """
        res1 = FlaskAPI.get_company()
        if len(res1) > 0:
            result = res1
        else:
            result = common.trueReturn(False, "返回公司列表失败")
        return jsonify(result)

    @app.route('/api/filter_airport', methods=['post'])
    def filter_airport():
        """
        模糊查询机场地址
        :return: json
        """
        result = Auth.identify(Auth, request)
        data_json = request.json.get('data_json')
        if (result['status'] and result['data']):
            res = FlaskAPI.filter_like_airport(data_json)
            if len(res) > 0:
                result = common.trueReturn(res, "返回机场列表失败")
            else:
                result = common.trueReturn(False, "返回机场列表失败")
            result = common.trueReturn(result, "请求成功")
            return jsonify(result)
        else:
            return jsonify("token error")

    @app.route('/api/filter_station', methods=['post'])
    def filter_station():
        """
        模糊查询高铁站地址
        :return: json
        """
        result = Auth.identify(Auth, request)
        data_json = request.json.get('data_json')
        if (result['status'] and result['data']):
            res = FlaskAPI.filter_like_station(data_json)
            if len(res) > 0:
                result = common.trueReturn(res, "返回高铁站列表成功")
            else:
                result = common.trueReturn(False, "返回高铁站列表失败")
            result = common.trueReturn(result, "请求成功")
            return jsonify(result)
        else:
            return jsonify("token error")

    @app.route('/booking/cxj', methods=['POST'])
    def wash_car():
        """
        车享家--预约洗车/喷漆/保养信息填写
        :return: json
        """
        result = Auth.identify(Auth, request)
        data_json = request.json.get('data_json')
        data = request.json.get('data')
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            # 查询该用户增值服务次数
            pack_number = FlaskAPI.filter_pack(data=user[0]["id"])
            if len(pack_number) > 0:
                # 次数清洗
                json_data = json.loads(pack_number[0]["service_quota"])
                number = json_data["service1"]
                if number > 0:
                    ticket_info = FlaskAPI.filter_by_insurance_id(data=data["service_type"])
                    # print(ticket_info)
                    if ticket_info != 'third_party_coupo is not exist' and ticket_info != 'error':
                        # print(ticket_info)
                        # if ticket_info
                        booking_time = time.strftime('%Y-%m-%d %H:%M:%S')
                        # 自定义订单编号
                        order_id = int(time.time())
                        datas = {
                            # 公司id
                            "store_id": data["store_id"],
                            # 票券id
                            "ticket_id": ticket_info[0]["id"],
                            # 服务名称 4-代驾
                            "service_id": data["service_type"],
                            # 用户主键
                            "user_id": user[0]["id"],
                            # 服务公司
                            "insurance_company_id": user[0]["insurance_company_id"],
                            # 服务发布时间
                            "booking_date": booking_time,
                            # 默认发布状态为待完成
                            "status": 1,
                            # 订单编号
                            "order_number": 'CXJ19' + '{0}'.format(order_id),
                            # json表单内容
                            "order_detail": data_json,
                        }
                        # 插入预约服务信息并减少服务使用次数
                        up1 = number - 1
                        res2 = FlaskAPI.insert_ups_data(data=datas, up1=up1, up2=user[0]["id"], up3=data["service_type"],
                                                        third_id=ticket_info[0]["id"], table="non_booking_service")
                        if res2 == "success":
                            result = common.trueReturn(ticket_info[0]["ticket_code"], "非预约服务信息提交完成")
                        else:
                            result = common.trueReturn(False, "非预约服务信息提交失败")
                    else:
                        result = common.trueReturn(False, "三方券信息查询失败")
                else:
                    result = common.trueReturn(False, "该服务次数不足")
            else:
                result = common.trueReturn(False, "暂无该用户服务信息")
        return jsonify(result)

    @app.route('/stores/location', methods=['POST'])
    def location():
        """
        店铺定位
        :return: json
        """
        result = Auth.identify(Auth, request)
        # data包含服务类型及详细地址
        data = request.json.get('data')
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            # 省份
            province = data["province"]
            # 城市
            city = data["city"]
            # 地区
            area = data["area"]
            # 页数
            page = data["page"]
            # 页记录条数
            count = data["count"]
            # 服务类型
            service_type = data["service_type"]
            if service_type == '1':
                # wash_service
                pg = "wash_service"
            elif service_type == '2':
                # maintenance_service
                pg = "maintenance_service"
            elif service_type == '3':
                # maintenance_service
                pg = "lacquer_service"
            else:
                # lacquer_service
                pg = "stopcar_service"
            # 区分车享家用户和非车享家用户
            rep = FlaskAPI.filter_user_cxj(user[0]["id"])
            if len(rep) > 0:
                # 查询到此用户
                dic = {}
                if rep[0]["is_luxuryBrand"] == 1:
                    # 是车享家用户
                    res = FlaskAPI.filter_stores(province, city, area, pg, (page - 1) * count, count)
                    for i in res:
                        store_name = FlaskAPI.filter_company(i["store_provider"])
                        i["store_provider"] = store_name[0]["sp_name"]
                        # res1 = FlaskAPI.filter_by_insurance_id(data=3)

                    if res != 'stores_cxj is not exist' or res != 'error':
                        res1 = FlaskAPI.filter_stores_numbers(province, city, area, pg)
                        if res1 != 'number is not exist' or res1 != 'error':
                            total_count = res1[0]["count(*)"]
                            dic["total_count"] = total_count
                            dic["data_info"] = res
                            result = common.trueReturn(dic, "店铺信息查询完成")
                    else:
                        result = common.falseReturn(False, "店铺信息查询失败")
                else:
                    # 非车享家用户
                    res = FlaskAPI.filter_stores_common(province, city, area, pg, (page - 1) * count, count)
                    for i in res:
                        store_name = FlaskAPI.filter_company(i["store_provider"])
                        i["store_provider"] = store_name[0]["sp_name"]
                    if res != 'stores_cxj is not exist' or res != 'error':
                        res1 = FlaskAPI.filter_stores_numbers_common(province, city, area, pg)
                        if res1 != 'number is not exist' or res1 != 'error':
                            total_count = res1[0]["count(*)"]
                            dic["total_count"] = total_count
                            dic["data_info"] = res
                            result = common.trueReturn(dic, "店铺信息查询完成")
                    else:
                        result = common.falseReturn(False, "店铺信息查询失败")
            else:
                # 无此用户信息
                result = common.falseReturn(rep, "无此用户信息")
        return jsonify(result)
            # user = Users.get(Users, result['data'])
            # print(user)
            # 根据token用户保单号查询该用户增值服务次数/用户id查询user_list
            # 保单号（third_party_coupo 根据ticket_code(保单号)查 id  id即为ticket_id）
            # user[0]["insurance_id"]
            # if service_type == '1':
            #     # wash_service
            #     pg = "wash_service"
            # elif service_type == '2':
            #     # maintenance_service
            #     pg = "maintenance_service"
            # elif service_type == '3':
            #     # maintenance_service
            #     pg = "lacquer_service"
            # else:
            #     # lacquer_service
            #     pg = "stopcar_service"
            # res = FlaskAPI.filter_stores(province, city, area, pg, (page - 1) * count, count)
            # for i in res:
            #     store_name = FlaskAPI.filter_company(i["store_provider"])
            #     i["store_provider"] = store_name[0]["sp_name"]
            # # res1 = FlaskAPI.filter_by_insurance_id(data=3)
            # dic = {}
            # if res != 'stores_cxj is not exist' or res != 'error':
            #     res1 = FlaskAPI.filter_stores_numbers(province, city, area, pg)
            #     if res1 != 'number is not exist' or res1 != 'error':
            #         total_count = res1[0]["count(*)"]
            #         dic["total_count"] = total_count
            #         dic["data_info"] = res
            #     result = common.trueReturn(dic, "店铺信息查询完成")
            # else:
            #     result = common.falseReturn(False, "店铺信息查询失败")
        # return jsonify(result)

    @app.route('/stores/details', methods=['POST'])
    def details():
        """
        出示二维码
        :return: json
        """
        result = Auth.identify(Auth, request)
        data = request.json.get('data')
        if (result['status'] and result['data']):
            # 服务类型
            service_type = data["service_type"]
            user = Users.get(Users, result['data'])
            # 查询该用户增值服务次数
            pack_number = FlaskAPI.filter_pack(data=user[0]["id"])
            if len(pack_number) > 0:
                # 次数清洗
                json_data = json.loads(pack_number[0]["service_quota"])
                number = json_data["service{0}".format(service_type)]
                if number > 0:
                    ticket_info = FlaskAPI.filter_by_insurance_id(data=service_type)
                    # print(ticket_info)
                    if ticket_info != 'third_party_coupo is not exist' and ticket_info != 'error':
                        # print(ticket_info)
                        # if ticket_info
                        booking_time = time.strftime('%Y-%m-%d %H:%M:%S')
                        # 自定义订单编号
                        order_id = int(time.time())
                        data = {
                            # 公司id
                            "store_id": data["store_id"],
                            # 票券id
                            "ticket_id": ticket_info[0]["id"],
                            # 服务名称 4-代驾
                            "service_id": int(service_type),
                            # 用户主键
                            "user_id": user[0]["id"],
                            # 服务公司
                            "insurance_company_id": user[0]["insurance_company_id"],
                            # 服务发布时间
                            "booking_date": booking_time,
                            # 默认发布状态为待完成
                            "status": 1,
                            # 订单编号
                            "order_number": 'FYY19' + '{0}'.format(order_id)
                        }
                        # 插入预约服务信息并减少服务使用次数
                        up1 = number - 1
                        res2 = FlaskAPI.insert_ups_data(data=data, up1=up1, up2=user[0]["id"], up3=service_type,
                                                        third_id=ticket_info[0]["id"], table="non_booking_service")
                        if res2 == "success":
                            result = common.trueReturn(ticket_info[0]["ticket_code"], "非预约服务信息提交完成")
                        else:
                            result = common.trueReturn(False, "非预约服务信息提交失败")
                    else:
                        result = common.trueReturn(False, "三方券信息查询失败")
                else:
                    result = common.trueReturn(False, "该服务次数不足")
            else:
                result = common.trueReturn(False, "暂无该用户服务信息")
        return jsonify(result)

    @app.route('/api/right', methods=['post'])
    def right():
        """
        查看自己的权益
        :return: json
        """
        result = Auth.identify(Auth, request)
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            res = FlaskAPI.filter_right(user[0]["id"])
            if len(res) > 0:
                result = common.trueReturn(res[0]["service_quota"], "返回权益列表成功")
            else:
                result = common.trueReturn(False, "返回权益列表失败")
            result = common.trueReturn(result, "请求成功")
            return jsonify(result)
        else:
            return jsonify("token error")

    @app.route('/api/cxj/judge', methods=['post'])
    def judge():
        """
        查看车享家订单状态
        :return: json
        """
        result = Auth.identify(Auth, request)
        data = request.json.get('data')
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            # res = FlaskAPI.filter_right(user[0]["id"])
            service_id = data["service_id"]
            # 查询非预约服务中是否存在车享家的服务
            res = FlaskAPI.cxj_exits(service_id, user[0]["id"])
            if res != 'error' and len(res) > 0:
                result = common.trueReturn(res, "有未处理订单")
            else:
                result = common.trueReturn(res, "暂无未处理订单")
            return jsonify(result)
        else:
            return jsonify("token error")

    @app.route('/api/cxj/count', methods=['post'])
    def count():
        """
        查看车享家订单数量
        :return: json
        """
        result = Auth.identify(Auth, request)
        data = request.json.get('data')
        if (result['status'] and result['data']):
            # user = Users.get(Users, result['data'])
            # res = FlaskAPI.filter_right(user[0]["id"])
            detail_info = data["detail_info"]
            service_id = data["service_id"]
            store_id = data["store_id"]
            # 查询非预约服务中是否存在车享家的服务
            res = FlaskAPI.cxj_count(json.loads(detail_info), service_id, store_id)
            if res != 'error':
                result = common.trueReturn(res, "获取订单数量")
            else:
                result = common.trueReturn(res, "暂无未处理订单")
            return jsonify(result)
        else:
            return jsonify("token error")


    '''

        @app.route('/booking/airport', methods=['POST'])
        def airport():
            """
            境外机场接送信息填写
            :return: json
            """
            result = Auth.identify(Auth, request)
            # service_id = request.json.get('service_id')
            data_json = request.json.get('data_json')
            print(data_json)
            print(type(data_json))
            # data_json = json.loads(data_json)
            # phone = request.json.get('phone')
            print(result)
            if (result['status'] and result['data']):
                user = Users.get(Users, result['data'])
                print(user)
                # 根据token用户保单号查询该用户增值服务次数/用户id查询user_list
                # 保单号（third_party_coupo 根据ticket_code(保单号)查 id  id即为ticket_id）
                # user[0]["insurance_id"]
                res1 = FlaskAPI.filter_by_insurance_id(data=6)
                print(res1)
                if res1 != 'third_party_coupo is not exist' and res1 != 'error':
                    # insurance_company_id  user[0]["insurance_coy_id]
                    data = {
                        # 代券
                        "ticket_id": res1[0]["id"],
                        # service_list表中服务id（代驾-4）
                        "service_id": 6,
                        # 未知商店id
                        "store_id": 1,
                        "user_id": user[0]["id"],
                        "insurance_company_id": user[0]["insurance_company_id"],
                        # 未知来源
                        # "booking_type": "Y",
                        # 未知来源/服务使用时间
                        "booking_date": "",
                        # 默认发布状态为待完成
                        "status": 1,
                        # "sp_id": res1["sp_id"],
                        # user_detail_info主键
                        "order_detail": data_json
                    }
                    # 插入服务信息
                    res2 = FlaskAPI.insert_data(data=data, table="booking_service")

                    if res2 == "success":
                        # 自定义订单编号
                        order_id = int(time.time())
                        # 修改三方使用券中的订单编号
                        res3 = FlaskAPI.update_order_id(data1=order_id, data2=res1[0]["id"])
                        if res3 == 'error':
                            result = common.trueReturn({}, "订单提交失败")
                            return jsonify(result)
                        result = common.trueReturn(True, "代驾信息提交完成")
                    else:
                        result = common.trueReturn(True, "代驾信息提交失败")
                else:
                    result = common.trueReturn(False, "三方券信息查询失败")
            return jsonify(result)'''
