from app.models import User,Goods,Order
from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField,SelectField, \
    PasswordField,SubmitField
from wtforms.validators import DataRequired,Length,Email,EqualTo
#Regexp, \
from wtforms import ValidationError


class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),
                                         Email()])
    name = StringField('Name',validators=[DataRequired(),Length(1,64)])
    '''Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                            'Usernames must have only letters,numbers,dots or \
                            underscores')
                            ])'''
    password = StringField('Password',validators=[DataRequired(),
                    EqualTo('password2',message='Password must match.')])
    password2 = PasswordField('Confirm password',validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_name(self,field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('Name already be used.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),
                                            Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New password',validators=[DataRequired(),
                            EqualTo('password2',message='Password must match.')])
    password2 = PasswordField('Confirm password',validators=[DataRequired()])
    submit = SubmitField('Reset password')


class ChangeEmailForm(FlaskForm):
    email = StringField('New email',validators=[DataRequired(),Length(1,64),
                                                Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Update email address.')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password',validators=[DataRequired()])
    password = PasswordField('New password', validators=[DataRequired(),
                            EqualTo('password2', 'Password must match.')])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update Password')