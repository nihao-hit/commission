from flask_wtf import FlaskForm
from wtforms import IntegerField,SubmitField, \
    StringField,SelectField
from wtforms.validators import DataRequired,NumberRange
from wtforms import ValidationError
from datetime import date
from app.models import User

shenfen = ['无','北京','天津','上海','重庆','河北','山西','辽宁','吉林',
                   '黑龙江','江苏','浙江','安徽','福建','江西','山东','河南',
                   '湖北','湖南','广东','海南','四川','贵州','云南','陕西',
                   '甘肃','青海','台湾','内蒙古','广西','西藏','宁夏',
                   '新疆','香港','澳门']


class SaleForm(FlaskForm):
    locks = IntegerField(label='Locks',validators=[DataRequired(),
                            NumberRange(1,1000,'Number Out of Range.')])
    stocks = IntegerField(label='Stocks',validators=[DataRequired(),
                            NumberRange(1, 1000, 'Number Out of Range.')])
    barrels = IntegerField(label='Barrels',validators=[DataRequired(),
                            NumberRange(1, 1000, 'Number Out of Range.')])
    town = SelectField(label='Town',choices=list(zip(shenfen,shenfen)))
    submit = SubmitField(label='Submit')


class QueryForm(FlaskForm):
    salesperson = StringField(label='Salesperson')
    year = IntegerField(label='Year',default=0)
    month = IntegerField(label='Month',default=0)
    day = IntegerField(label='Day',default=0)
    town = SelectField(label='Town',choices=list(zip(shenfen,shenfen)))
    submit = SubmitField(label='Query')
'''
    def validate_salesperson(self,field):
        if (not User.query.filter_by(name=field.data).first()):
            raise ValidationError('你查找的售货员不存在。')
'''
class QueryReportForm(FlaskForm):
    salesperson = StringField(label='Salesperson')
    year = IntegerField(label='Year',default=0)
    month = IntegerField(label='Month', default=0)
    submit = SubmitField(label='Query')