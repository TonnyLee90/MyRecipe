from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

class SignupForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(),Length(min=3, max=32)])
    password = PasswordField("Password", validators=[DataRequired(),Length(min=8)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(),EqualTo("password", message="Passwords must match")])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class PostRecipeForm(FlaskForm):
    name = StringField("Recipe Name", validators=[DataRequired(), Length(max=120)])
    ingredients = TextAreaField("Ingredients", validators=[DataRequired(), Length(max=5000)])
    instructions = TextAreaField("Instructions", validators=[DataRequired(), Length(max=5000)])
    body = TextAreaField("Description", validators=[DataRequired(), Length(max=5000)])
    submit = SubmitField("Submit")

class DeleteForm(FlaskForm):
    pass

class SaveRecipeForm(FlaskForm):
    recipe_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField("❤️ Save")

class UnsaveRecipeForm(FlaskForm):
    recipe_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField("💔 Unsave")