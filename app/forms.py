from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField


class AdminPassForm(FlaskForm):
    password = PasswordField('Password')
    submit = SubmitField('Submit')

