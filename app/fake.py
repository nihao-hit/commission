from random import randint
from faker import Faker
from . import db
from .models import User,Order,Goods,Report,Role


def users(count=12):
    fake = Faker(locale='zh-CN')
    i = 0
    while i<count:
        u = User(email=fake.email(),
                 name=fake.name(),
                 password='p',
                 confirmed=True)
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except:
            db.session.rollback()
    u = User(email='nihao_cx@163.com',
             name='陈鑫',
             password='p',
             confirmed=True)
    db.session.add(u)
    u = User(email='726582630@qq.com',
             name='陈鑫',
             password='p',
             confirmed=True)
    u.role = Role.query.get(2)
    db.session.add(u)
    db.session.commit()


def orders():
    user_count = User.query.count()
    for i in range(1,user_count+1):
        u = User.query.get(i)
        if u.role.name == 'Salesperson':
            for j in range(1,7):
                for k in range(5):
                    locks = randint(0,60)
                    stocks = randint(0,70)
                    barrels = randint(0,80)
                    order = Order(master=u,
                                  locks=locks,
                                  stocks=stocks,
                                  barrels=barrels,
                                  town_id=randint(1,34)
                                 )
                    order.calculate_total()
                    order.month = j
                    order.day = randint(0,28)
                    db.session.add(order)
    db.session.commit()


def goods():
    user_count = User.query.count()
    for i in range(1,user_count+1):
        u = User.query.get(i)
        if u.role.name == 'Salesperson':
            goods = Goods(master=u,
                          locks=randint(0,60),
                          stocks=randint(0,70),
                          barrels=randint(0,80))
            db.session.add(goods)
    db.session.commit()


def reports():
    user_count = User.query.count()
    for i in range(1,user_count+1):
        user = User.query.get(i)
        if user.role.name == 'Salesperson':
            for j in range(1,6):
                report = Report(master=user,
                                locks=randint(0,60),
                                stocks=randint(0,70),
                                barrels=randint(0,80),
                                total=randint(1000,5000),
                                commission=float(randint(500,1000)),
                                year=2018,
                                month=j)
                db.session.add(report)
    db.session.commit()