from flask import jsonify, request, session
from app.users.model import Users
from app.msql_api import FlaskAPI
from app.auth.auths import Auth
from .. import common


def init_api(app):
    @app.route('/auth/user/login', methods=['POST'])
    def login():
        """
        用户登录
        :return: json
        """
        name = request.json.get('name')
        phone = request.json.get('phone')
        car_plate_number = request.json.get('car_plate_number')
        # print(insurance_number)
        if (not name or not phone or not car_plate_number):
            return jsonify(common.falseReturn('', '车牌号和手机号不能为空'))
        else:
            return Auth.authenticate(Auth, name, phone, car_plate_number)

    @app.route('/user', methods=['GET'])
    def get():
        """
        获取用户信息
        :return: json
        """
        result = Auth.identify(Auth, request)
        print(result)
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            print(user)
            returnUser = {
                'id': user[0]["id"],
                'insurance_id': user[0]["insurance_id"],
                'phone': user[0]["phone"],
                'login_time': user[0]["login_time"]
            }
            result = common.trueReturn(returnUser, "请求成功")
        return jsonify(result)


    @app.route('/booking/drunk_driver')
    def driver():
        """
        酒后代驾信息填写
        :return: json
        """
        result = Auth.identify(Auth, request)
        # service_id = request.json.get('service_id')
        data_json = request.json.get('data_json')
        # phone = request.json.get('phone')
        print(result)
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            print(user)
            # 根据token用户保单号查询该用户增值服务次数/用户id查询
            # user[0][""]
            data = {
                # service_list表中服务id（代驾-4）
                "service_id": 4,
                "user_id": user[0]["id"],
                "insurance_coy_id": user[0]["insurance_coy_id"],
                "order_detail": data_json
            }
            FlaskAPI.insert_data(data=data, table="booking_service")
            returnUser = {
                'id': user[0]["id"],
                'insurance_id': user[0]["insurance_id"],
                'phone': user[0]["phone"],
                'login_time': user[0]["login_time"]
            }
            res = FlaskAPI.insert_data(data)
            if res == "success":
                result = common.trueReturn(returnUser, "代驾信息提交完成")
            else:
                result = common.trueReturn(returnUser, "代驾信息提交失败")
        return jsonify(result)


    # @app.route('/service_list', methods=['GET'])
    # def get():
    #     """
    #     获取列表服务（非预约服务/预约类服务）
    #     :return: json
    #     """
    #     result = Auth.identify(Auth, request)
    #     # print(result)
    #     if (result['status'] and result['data']):
    #         user = Users.get(Users, result['data'])
    #         returnUser = {
    #             'id': user[0]["id"],
    #             'insurance_number': user[0]["insurance_number"],
    #             'phone': user[0]["phone"],
    #             'login_time': user[0]["login_time"]
    #         }
    #         result = common.trueReturn(returnUser, "请求成功")
    #     return jsonify(result)