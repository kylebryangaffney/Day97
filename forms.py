from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class AddMoneyForm(FlaskForm):
    amount = FloatField("Amount", validators=[DataRequired()])
    submit = SubmitField("Add Money")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ItemForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    price = FloatField("Price of Item", validators=[DataRequired()])
    barcode = StringField("Barcode", validators=[DataRequired()])
    description = StringField("Description of item", validators=[DataRequired()])
    submit = SubmitField("Submit")
