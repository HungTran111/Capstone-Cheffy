from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

class UserForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class RecipesForm(FlaskForm):
    recipe_name = StringField('Name Of The Recipe', validators=[InputRequired()])
    text = StringField('Ingredients', validators=[InputRequired()])
    