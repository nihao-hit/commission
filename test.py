import unittest
from app import create_app,db
from app.models import User
from flask import url_for


class FlaskClientTestCase(unittest.TestCase):
    '''
    界面测试：sold note,sold report,sold draw,
            admin,gunsmith,salesperson
    '''
    def setUp(self):
        self.app = create_app(name='test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        self.app_context.pop()

    def test_soldNote_get_post(self):
        res = self.client.get(url_for('main.index'))
        self.assertTrue(res.status_code == 200)

        res = self.client.post(url_for('main.index'),data={
            'year':2018,
            'month':6,
            'salesperson':'莫燕'
        })
        self.assertTrue(res.status_code == 200)

    def test_soldReport_get_post(self):
        res = self.client.get(url_for('main.soldreport'))
        self.assertTrue(res.status_code == 200)

        res = self.client.post(url_for('main.soldreport'),data={
            'month':4
        })
        self.assertTrue(res.status_code == 200)

    def test_soldDraw_get_post(self):
        res = self.client.get(url_for('main.draw'))
        self.assertTrue(res.status_code == 200)

    def test_login_logout(self):
        res = self.client.post(url_for('auth.login'),data={
            'email':'726582630@qq.com',
            'password':'p'
        },follow_redirects=True)
        self.assertTrue('Welcome' in res.get_data(as_text=True))

        res = self.client.get(url_for('auth.logout'),
                              follow_redirects=True)
        self.assertTrue('Stranger' in res.get_data(as_text=True))

    def test_app_exist(self):
        self.assertTrue(self.app is not None)


if __name__ == '__main__':
    unittest.main()