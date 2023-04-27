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

class WorkoutAddForm(FlaskForm):
    """Form for adding/edit workouts."""

    # Select field for all workout types
    description = StringField("Let's give your workout a Name or Description:", validators=[DataRequired()])

class GoalAddForm(FlaskForm):
    """Form for adding exercises to your workout."""

    exercise = SelectField('Exercise', choices=[('c1', 'Choice 1'), ('c2', 'Choice2')])
    goal_reps = IntegerField("Reps:" validators=[InputRequired(message='Must have at least 1 "rep."')])
    goal_sets = IntegerField("Sets:" validators=[InputRequired(message='Must have at least 1 "set."')])
    goal_time = IntegerField("Time (seconds):" validators=[Optional()])
    goal_time = IntegerField("Weight (lbs):" validators=[Optional()])

# class WorkoutEditExerciseForm
