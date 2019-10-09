import jwt, datetime, time
from flask import jsonify, session
from app.users.model import Users
from app.msql_api import FlaskAPI
from .. import config
from .. import common
from werkzeug.security import generate_password_hash


class Auth():
    @staticmethod
    def encode_auth_token(user_id, login_time):
        """
        生成认证Token
        :param user_id: int
        :param login_time: int(timestamp)
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=10),
                'iat': datetime.datetime.utcnow(),
                'iss': 'ken',
                'data': {
                    'id': user_id,
                    'login_time': login_time
                }
            }
            return jwt.encode(
                payload,
                config.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        验证Token
        :param auth_token:
        :return: integer|string
        """
        try:
            # payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), leeway=datetime.timedelta(seconds=10))
            # 取消过期时间验证
            payload = jwt.decode(auth_token, config.SECRET_KEY, options={'verify_exp': False})
            if ('data' in payload and 'id' in payload['data']):
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return 'Token过期'
        except jwt.InvalidTokenError:
            return '无效Token'


    def authenticate(self, name, phone, car_plate_number):
        """
        用户登录，登录成功返回token，写将hash_auth写入数据库；登录失败返回失败原因
        :param password:
        :return: json
        """
        # 查找该用户是否存在
        # userInfo = Users.query.filter_by(username=username).first()
        userInfo = FlaskAPI.filter_user(data1=name, data2=phone, data3=car_plate_number)
        # print(userInfo)
        if (userInfo == 'user is not exist'):
            return jsonify(common.falseReturn('', '找不到用户'))
        else:
            hash_auth = generate_password_hash(phone)
            res = FlaskAPI.save_hash(hash_auth, phone)
            if res == 'update success':
                if (Users.check_password(Users, userInfo[0]["hash_auth"], phone)):
                    login_time = str(int(time.time()))
                    save_status = FlaskAPI.save_login_time(login_time, phone)
                    if save_status == 'update success':
                    # userInfo.login_time = login_time
                    # Users.update(Users)
                        token = self.encode_auth_token(userInfo[0]["id"], login_time)
                        # session["auth_token"] = token
                        # print(session["auth_token"])
                        return jsonify(common.trueReturn(token.decode(), '登录成功'))
                    else:
                        return jsonify(common.falseReturn('', '添加token时间失败'))
                else:
                    return jsonify(common.falseReturn('', '密码不正确'))
            else:
                return jsonify(common.falseReturn('', '加盐失败'))

    def identify(self, request):
        """
        用户鉴权
        :return: list
        """
        auth_header = request.headers.get('Authorization')
        if (auth_header):
            auth_tokenArr = auth_header.split(" ")
            if (not auth_tokenArr or auth_tokenArr[0] != 'JWT' or len(auth_tokenArr) != 2):
                result = common.falseReturn('', '请传递正确的验证头信息')
            else:
                auth_token = auth_tokenArr[1]
                payload = self.decode_auth_token(auth_token)
                if not isinstance(payload, str):
                    user = Users.get(Users, payload['data']['id'])
                    if (user == 'user is not exist'):
                        result = common.falseReturn('', '找不到该用户信息')
                    else:
                        # print(type(user[0]["login_time"]))
                        # print(type(payload['data']['login_time']))
                        if (user[0]["login_time"] == payload['data']['login_time']):
                            result = common.trueReturn(user[0]["id"], '请求成功')
                        else:
                            result = common.falseReturn('', 'Token已更改，请重新登录获取')
                else:
                    result = common.falseReturn('', payload)
        else:
            result = common.falseReturn('', '没有提供认证token')
        return result