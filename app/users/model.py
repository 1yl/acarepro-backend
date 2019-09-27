# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from app.msql_api import FlaskAPI
# from app import db

class Users():
    # id = db.Column(db.Integer, primary_key=True)
    # email = db.Column(db.String(250),  unique=True, nullable=False)
    # username = db.Column(db.String(250),  unique=True, nullable=False)
    # password = db.Column(db.String(250))
    # login_time = db.Column(db.Integer)

    def __init__(self, insurance_number, phone):
        self.insurance_number = insurance_number
        self.phone = phone

    def __str__(self):
        return "Users(id='%s')" % self.id

    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, hash, password):
        # generate_password_hash(password)
        return check_password_hash(hash, password)

    def get(self, id):
        # 根据id获取该用户
        u_obj = FlaskAPI.filter_by_id(id)
        return u_obj
        # return self.query.filter_by(id=id).first()

    # def add(self, user):
    #     db.session.add(user)
    #     return session_commit()

    # def update(self):
    #     return session_commit()
    #
    # def delete(self, id):
    #     self.query.filter_by(id=id).delete()
    #     return session_commit()


# def session_commit():
#     try:
#         db.session.commit()
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         reason = str(e)
#         return reason