from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class UserAddForm(FlaskForm):
    """Form for adding users."""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

    form_name = "User Signup"
    form_title = "Let's Get Started!"
    submit_text = "Signup"

class UserEditForm(FlaskForm):
    """Form for editing users."""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])

    # Fields in addition to UserAddForm
    image_url = StringField('(Optional) Image URL')
    bio = TextAreaField('(Optional) Bio')

    # Password for validation
    password = PasswordField('Password', validators=[Length(min=6)])

    form_name = "User Edit"
    form_title = "Edit Your Details"
    submit_text = "Save Changes"

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

    form_name = "User Login"
    form_title = "Log in To Get Started"
    submit_text = "Login"

##############################################################################

# class WorkoutAddForm(FlaskForm):
#     """Form for adding workouts."""

#     # Select field for all workout types
