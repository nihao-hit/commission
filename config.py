import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY','hard to guess string')

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME','nihao_cx@163.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD','nihao123456789')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI','mysql+pymysql://root:@localhost/commission')

    DEBUG = True

    @staticmethod
    def init_app(app):
        pass