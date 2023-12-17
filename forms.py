from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class TodoListForm(FlaskForm):
    todo_list = StringField("Type an item: ", validators=[DataRequired()])
    add = SubmitField("Add Item")



class SignupForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired()])
    email = StringField("Email: ", validators=[DataRequired()])
    password = PasswordField("Password: ", validators=[DataRequired()])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired()])
    password = PasswordField("Password: ", validators=[DataRequired()])
    submit = SubmitField("Log In")


class ContactForm(FlaskForm):
    message = TextAreaField('Your message:', render_kw={"rows": 6})
    submit = SubmitField("Submit")
