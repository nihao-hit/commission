from flask_wtf import FlaskForm
from wtforms import IntegerField,SubmitField
from wtforms.validators import DataRequired,NumberRange
from datetime import date


class SaleForm(FlaskForm):
    locks = IntegerField(label='Locks',validators=[DataRequired(),
                            NumberRange(1,1000,'Number Out of Range.')])
    stocks = IntegerField(label='Stocks',validators=[DataRequired(),
                            NumberRange(1, 1000, 'Number Out of Range.')])
    barrels = IntegerField(label='Barrels',validators=[DataRequired(),
                            NumberRange(1, 1000, 'Number Out of Range.')])
    submit = SubmitField(label='Submit')


class QueryForm(FlaskForm):
    year = IntegerField(label='Year',validators=[DataRequired(),
                            NumberRange(min=2018,max=date.today().year,
                                message='Year not in range.')])
    month = IntegerField(label='Month',validators=[DataRequired(),
                            NumberRange(min=1,max=12,
                                message='Month not in range.')])
    day = IntegerField(label='Day',validators=[DataRequired(),
                            NumberRange(min=1,max=31,
                                message='Day not in range.')])
    submit = SubmitField(label='Query')