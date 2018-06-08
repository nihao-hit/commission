from random import randint
from faker import Faker
from . import db
from .models import User,Order,Goods


def users(count=100):
    fake = Faker()
    i = 0
    while i<count:
        u = User(email=fake.email(),
                 name=fake.user_name(),
                 password='password',
                 confirmed=True)
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except:
            db.session.rollback()


def orders(count=100):
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0,user_count-1)).first()
        locks = randint(0,60)
        stocks = randint(0,70)
        barrels = randint(0,80)
        order = Order(master=u,
                      locks=locks,
                      stocks=stocks,
                      barrels=barrels
                     )
        order.calculate_total()
        db.session.add(order)
    db.session.commit()


def goods(count=100):
    user_count = User.query.count()
    for i in range(user_count):
        u = User.query.offset(i).first()
        goods = Goods(master=u,
                      locks=randint(0,100),
                      stocks=randint(0,100),
                      barrels=randint(0,100))
        db.session.add(goods)
        try:
            db.session.commit()
        except:
            db.session.rollback()
