from flask_wtf import FlaskForm
from wtforms import IntegerField,SubmitField
from wtforms.validators import DataRequired,NumberRange
from wtforms import ValidationError


class SaleForm(FlaskForm):
    locks = IntegerField(label='Locks',validators=[DataRequired(),
                            NumberRange(1,1000,'Number Out of Range.')])
    stocks = IntegerField(label='Stocks',validators=[DataRequired(),
                            NumberRange(1, 1000, 'Number Out of Range.')])
    barrels = IntegerField(label='Barrels',validators=[DataRequired(),
                            NumberRange(1, 1000, 'Number Out of Range.')])
    submit = SubmitField(label='Submit')