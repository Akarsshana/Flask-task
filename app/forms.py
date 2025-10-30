from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, SelectField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Optional, Length


class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    qty = IntegerField('Quantity', validators=[NumberRange(min=0)], default=0)
    submit = SubmitField('Save')


class LocationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save')


class MovementForm(FlaskForm):
    product_id = SelectField('Product', coerce=str, validators=[DataRequired()])
    from_location = SelectField('From Location (leave blank for inbound)', coerce=str, validators=[Optional()])
    to_location = SelectField('To Location (leave blank for outbound)', coerce=str, validators=[Optional()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Save')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Register')
