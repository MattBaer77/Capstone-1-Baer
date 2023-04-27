from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, InputRequired, Optional

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

    form_name = "Add Workout"
    form_title = "Create A New Workout"
    submit_text = "Create"

class WorkoutEditForm(FlaskForm):
    """Form for adding/edit workouts."""

    # Select field for all workout types
    description = StringField("Edit workout Name or Description:", validators=[DataRequired()])

    form_name = "Edit Workout"
    form_title = "Edit Your Workout"
    submit_text = "Update"

class GoalAddForm(FlaskForm):
    """Form for adding exercises to your workout."""

    exercise = SelectField('Exercise Goal:', coerce=int)
    goal_reps = IntegerField('Reps:', validators=[InputRequired(message='Must have at least 1 "rep."')])
    goal_sets = IntegerField('Sets:', validators=[InputRequired(message='Must have at least 1 "set."')])
    goal_time_sec = IntegerField('Time (seconds):', validators=[Optional()])
    goal_weight_lbs = IntegerField('Weight (lbs):', validators=[Optional()])

    form_name = "Add Exercise Goal"
    form_title = "Add an Exercise Goal To Your Workout!"
    submit_text = "Add"

class GoalEditForm(FlaskForm):
    """Form for adding exercises to your workout."""

    exercise = SelectField('Exercise Goal:', coerce=int)
    goal_reps = IntegerField('Reps:', validators=[InputRequired(message='Must have at least 1 "rep."')])
    goal_sets = IntegerField('Sets:', validators=[InputRequired(message='Must have at least 1 "set."')])
    goal_time_sec = IntegerField('Time (seconds):', validators=[Optional()])
    goal_weight_lbs = IntegerField('Weight (lbs):', validators=[Optional()])

    form_name = "Edit Exercise Goal"
    form_title = "Edit Your Exercise Goal"
    submit_text = "Save Changes"

# class WorkoutEditExerciseForm
