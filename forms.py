from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, EqualTo


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class AddSong(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    artist = StringField('Artist', validators=[InputRequired()])
    year = StringField('Year', validators=[InputRequired()])
    genre = StringField('Genre', validators=[InputRequired()])
    submit = SubmitField('Add Song')

class EditSong(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    artist = StringField('Artist', validators=[InputRequired()])
    year = StringField('Year', validators=[InputRequired()])
    genre = StringField('Genre', validators=[InputRequired()])
    submit = SubmitField('Edit Song')