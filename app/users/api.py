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
        # print(result)
        if (result['status'] and result['data']):
            user = Users.get(Users, result['data'])
            returnUser = {
                'id': user[0]["id"],
                'insurance_number': user[0]["insurance_number"],
                'phone': user[0]["phone"],
                'login_time': user[0]["login_time"]
            }
            result = common.trueReturn(returnUser, "请求成功")
        return jsonify(result)