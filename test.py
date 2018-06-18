'''
白盒测试,采用路径覆盖法编写测试用例
'''
import unittest
from app import create_app
from flask import url_for


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(name='test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        self.app_context.pop()

    #测试用例
    def test_1_get_register(self):
        res = self.client.get(url_for('auth.register'))
        self.assertTrue(res.status_code == 200)

    def test_2_post_register(self):
        res = self.client.post(url_for('auth.register'),data={
            'email':'newbieorveteran@gmail.com',
            'name':'陈鑫',
            'password':'p',
            'password2':'p'
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_3_post_register(self):
        res = self.client.post(url_for('auth.register'), data={
            'email': '726582630@qq.com',
            'name': '不重复的名字',
            'password': 'p',
            'password2': 'p'
        })
        self.assertTrue('Email already registered.' in res.get_data(as_text=True))

    def test_4_post_register(self):
        res = self.client.post(url_for('auth.register'), data={
            'email': 'example@example.com',
            'name': '陈鑫',
            'password': 'p',
            'password2': 'p'
        })
        self.assertTrue('Name already be used.' in res.get_data(as_text=True))

    def test_5_post_register(self):
        res = self.client.post(url_for('auth.register'), data={
            'email': 'example@example.com',
            'name': '不重复的名字',
            'password': 'p',
            'password2': 'pp'
        })
        self.assertTrue('Password must match.'
                        in res.get_data(as_text=True))

    def test_6_get_login(self):
        res = self.client.get(url_for('auth.login'))
        self.assertTrue(res.status_code == 200)

    def test_7_post_login_gunsmith(self):
        res = self.client.post(url_for('auth.login'),data={
            'email':'726582630@qq.com',
            'password':'p'
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_8_post_login_salesperson(self):
        res = self.client.post(url_for('auth.login'),data={
            'email':'mayong@kang.com',
            'password':'p'
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_9_post_login(self):
        res = self.client.post(url_for('auth.login'),data={
            'email':'example@example.com',
            'password':'p'
        })
        self.assertTrue('Invalid email or password.'
                        in res.get_data(as_text=True))

    def test_10_post_login(self):
        res = self.client.post(url_for('auth.login'),data={
            'email':'726582630@qq.com',
            'password':'pp'
        })
        self.assertTrue('Invalid email or password.'
                        in res.get_data(as_text=True))

    def test_11_get_logout(self):
        res = self.client.get(url_for('auth.logout'),
                              follow_redirects=True)
        self.assertTrue(res.status_code == 200)


class GunsmithTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(name='test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

        self.client.post(url_for('auth.login'),data={
            'email':'726582630@qq.com',
            'password':'p'
        })

    def tearDown(self):
        self.client.get(url_for('auth.logout'))

        self.app_context.pop()

    def test_12_get_soldnote(self):
        res = self.client.get(url_for('main.index'))
        self.assertTrue(res.status_code == 200)

    def test_13_post_soldnote_query(self):
        res = self.client.post(url_for('main.index'),
                               follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_14_post_soldnote_query(self):
        res = self.client.post(url_for('main.index'),data={
            'salesperson':'莫燕'
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_15_post_soldnote_query(self):
        res = self.client.post(url_for('main.index'), data={
            'year':2018
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_16_post_soldnote_query(self):
        res = self.client.post(url_for('main.index'), data={
            'month':12
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_17_post_soldnote_query(self):
        res = self.client.post(url_for('main.index'), data={
            'day':22
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_18_post_soldnote_query(self):
        res = self.client.post(url_for('main.index'), data={
            'town':'山东'
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_19_post_soldnote_query(self):
        res = self.client.post(url_for('main.index'), data={
            'year':30
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_20_get_soldreport(self):
        res = self.client.get(url_for('main.soldreport'))
        self.assertTrue(res.status_code == 200)

    def test_21_post_soldreport_query(self):
        res = self.client.post(url_for('main.soldreport'),
                               follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_22_post_soldreport_query(self):
        res = self.client.post(url_for('main.soldreport'),data={
            'salesperson':'莫燕'
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_23_post_soldreport_query(self):
        res = self.client.post(url_for('main.soldreport'), data={
            'year':2018
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_24_post_soldreport_query(self):
        res = self.client.post(url_for('main.soldreport'), data={
            'month':4
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_25_post_soldreport_query(self):
        res = self.client.post(url_for('main.soldreport'), data={
            'day':33
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_26_get_draw(self):
        res = self.client.get(url_for('main.draw'))
        self.assertTrue(res.status_code == 200)

    def test_27_get_gunsmith(self):
        res = self.client.get(url_for('main.gunsmith',name='陈鑫'))
        self.assertTrue(res.status_code == 200)

    '''
    def test_28_calculate_commission(self):
        res = self.client.get(url_for('main.commission',
                                      s='苍秀梅',name='陈鑫'),
                              follow_redirects=True)
        self.assertTrue(res.status_code == 200)
    '''

    def test_29_supply(self):
        res = self.client.get(url_for('main.supply',
                                      s='苍秀梅', name='陈鑫'),
                              follow_redirects=True)
        self.assertTrue(res.status_code == 200)


class SalespersonTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(name='test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

        self.client.post(url_for('auth.login'),data={
            'email':'mayong@kang.com',
            'password':'p'
        })

    def tearDown(self):
        self.client.get(url_for('auth.logout'))

        self.app_context.pop()

    def test_30_get_salesperson(self):
        res = self.client.get(url_for('main.salesperson',
                                      name='荀丽华'))
        self.assertTrue(res.status_code == 200)

    def test_31_get_salesperson(self):
        res = self.client.get(url_for('main.salesperson',
                                      name='荀丽华',r=1))
        self.assertTrue(res.status_code == 200)

    def test_32_get_salesperson_orders(self):
        res = self.client.get(url_for('main.orders',name='荀丽华'),
                              follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_33_get_salesperson_reports(self):
        res = self.client.get(url_for('main.reports',name='荀丽华'),
                              follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    def test_34_get_sale(self):
        res = self.client.get(url_for('main.sale',name='荀丽华'))
        self.assertTrue(res.status_code == 200)

    def test_35_post_sale(self):
        res = self.client.post(url_for('main.sale',name='荀丽华'))
        #self.assertTrue('Number Out of Range.'in res.get_data(as_text=True))
        self.assertTrue(res.status_code == 200)

    def test_36_post_sale(self):
        res = self.client.post(url_for('main.sale',name='荀丽华'),data={
            'locks':-1,
            'stocks':1,
            'barrels':1,
            'town':'北京',
        })
        self.assertTrue('Number Out of Range.'
                        in res.get_data(as_text=True))

    def test_37_post_sale(self):
        res = self.client.post(url_for('main.sale',name='荀丽华'),data={
            'locks':1000,
            'stocks':1,
            'barrels':1,
            'town': '北京',
        },follow_redirects=True)
        self.assertTrue('Invalid Numbers.' in res.get_data(as_text=True))

    def test_38_post_sale(self):
        res = self.client.post(url_for('main.sale',name='荀丽华'),data={
            'locks':1,
            'stocks':0,
            'barrels':1,
            'town': "北京",
        },follow_redirects=True)
        self.assertTrue(res.status_code == 200)

    '''
    def test_39_get_report(self):
        res = self.client.get(url_for('main.report',name='荀丽华'))
    '''


if __name__ == '__main__':
    unittest.main()