from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class UserAddForm(FlaskForm):
    """Form for adding users."""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for editing users."""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])

    password = PasswordField('Password', validators=[Length(min=6)])

    # Fields in addition to UserAddForm
    header_image_url = StringField('(Optional) Image URL')
    bio = TextAreaField('text')

##############################################################################

# class WorkoutAddForm(FlaskForm):
#     """Form for adding workouts."""

#     # Select field for all workout types
