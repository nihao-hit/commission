import datetime
import calendar
import hashlib
from sqlalchemy import extract,and_
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin,AnonymousUserMixin
from . import db,login_manager


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    users = db.relationship('User',backref='role',lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = ['Admin','Gunsmith','Salesperson']
        for role in roles:
            r = Role.query.filter_by(name=role).first()
            if not r:
                r = Role(name=role)
                db.session.add(r)
        db.session.commit()

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),index=True)

    email = db.Column(db.String(64),unique=True,index=True)
    confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute.')
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    password_hash = db.Column(db.String(128))

    avatar_hash = db.Column(db.String(32))
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    goods = db.relationship('Goods',backref='master',lazy='dynamic')
    orders = db.relationship('Order',backref='master',lazy='dynamic')
    reports = db.relationship('Report',backref='master',lazy='dynamic')

    def __init__(self,**kwargs):
        '''
        初始化时完成对角色的定义，和头像hash值的存储
        :param kwargs:
        '''
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['MAIL_USERNAME']:
                self.role = Role.query.filter_by(name='Admin').first()
            else:
                self.role = Role.query.filter_by(name='Salesperson').first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def generate_reset_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'reset':self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token,new_password):
        '''
        设计这类函数有一个很重要的问题：
        我在函数中执行了某个操作，改变了某个数据，我应该返回什么？
        答案是返回能反映操作结果的一个值，如此例中的True or False
        :param token:
        :param new_password:
        :return:
        '''
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if not user:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id}).decode('utf-8')

    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            global data
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_email_change_token(self,new_email,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'change_email':self.id,'new_email':new_email}) \
                .decode('utf-8')

    def change_email(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.load(current_app.config['SECRET_KEY'])
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if not new_email:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def gravatar_hash(self):
        return hashlib.md5(self.email.encode('utf-8')).hexdigest()

    def gravatar(self,size=100,default='identicon',rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'. \
            format(url=url,hash=hash,size=size,default=default,rating=rating)

    def can(self,role_name):
        return self.role.name == role_name

    def canReport(self):
        today = datetime.date.today()
        report = self.reports.filter_by(year=today.year). \
            filter_by(month=today.month).first()
        if report:
            return False
        return True

    def report(self,today):
        orders = self.orders.filter_by(year=today.year). \
            filter_by(month=today.month).all()
        locks = 0
        stocks = 0
        barrels = 0
        total = 0
        for order in orders:
            locks += order.locks
            stocks += order.stocks
            barrels += order.barrels
            total += order.total
        db.session.add(Report(user_id=self.id,
                             locks=locks,
                             stocks=stocks,
                             barrels=barrels,
                             total=total,
                             year=today.year,
                             month=today.month))

    def canCommission(self,name):
        salesperson = User.query.filter_by(name=name).first()
        if salesperson and \
            salesperson.reports.filter(Report.commission==0.0).first():
            return True
        return False

    @staticmethod
    def commission(salesperson):
        report = salesperson.reports.filter_by(commission=0.0).first()
        commission = (report.total - 1800) * 0.2 + \
            ((report.total - 1800) - (report.total - 1000)) * 0.15 + \
            ((report.total + 1) % 1000 - 1) * 0.1
        report.commission = commission
        db.session.add(report)
        db.session.commit()

    def __repr__(self):
        return '<User {}>'.format(self.name)


login_manager.anonymous_user = AnonymousUserMixin
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Goods(db.Model):
    __tablename__ = 'goods'
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                        primary_key=True)
    locks = db.Column(db.Integer)
    stocks = db.Column(db.Integer)
    barrels = db.Column(db.Integer)
    supplyDate = db.Column(db.Date)

    def canSupply(self):
        today = datetime.date.today()
        if today.day == 1 and self.supplyDate != today:
            return True
        return False

    def supply(self):
        self.locks += 70
        self.stocks += 80
        self.barrels += 90
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Goods (master:{})>'. \
            format(self.master.name)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer,primary_key=True)
    locks = db.Column(db.Integer)
    stocks = db.Column(db.Integer)
    barrels = db.Column(db.Integer)
    total = db.Column(db.Integer)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        index=True)
    town_id = db.Column(db.Integer,db.ForeignKey('towns.id'))

    def __init__(self,*args,**kwargs):
        super(Order,self).__init__(*args,**kwargs)
        today = datetime.date.today()
        self.year = today.year
        self.month = today.month
        self.day = today.day

    def calculate_total(self):
        self.total = self.locks*45+self.stocks*30+self.barrels*25

    def __repr__(self):
        return '<Order (master:{})>'.format(self.master.name)


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer,primary_key=True)
    locks = db.Column(db.Integer)
    stocks = db.Column(db.Integer)
    barrels = db.Column(db.Integer)
    total = db.Column(db.Integer)
    commission = db.Column(db.Float,default=0.0)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                        index=True)

    def __repr__(self):
        return '<Report {}年{}月>'.format(self.year,self.month)


class Town(db.Model):
    __tablename__ = 'towns'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    orders = db.relationship('Order',backref='town',lazy='dynamic')

    @staticmethod
    def insert_towns():
        shenfen = ['北京','天津','上海','重庆','河北','山西','辽宁','吉林',
                   '黑龙江','江苏','浙江','安徽','福建','江西','山东','河南',
                   '湖北','湖南','广东','海南','四川','贵州','云南','陕西',
                   '甘肃','青海','台湾','内蒙古','广西','西藏','宁夏',
                   '新疆','香港','澳门']
        for x in shenfen:
            town = Town.query.filter_by(name=x).first()
            if not town:
                town = Town(name=x)
                db.session.add(town)
            db.session.commit()

    def __repr__(self):
        return '<Town {}>'.format(self.name)

