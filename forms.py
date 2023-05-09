from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, FieldList, FormField
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
    """Form for adding workouts."""

    # Select field for all workout types
    description = StringField("Let's give your workout a Name or Description:", validators=[DataRequired()])

    form_name = "Add Workout"
    form_title = "Create A New Workout"
    submit_text = "Create"

class WorkoutEditForm(FlaskForm):
    """Form for editing workouts."""

    # Select field for all workout types
    description = StringField("Edit workout Name or Description:", validators=[DataRequired()])

    form_name = "Edit Workout"
    form_title = "Edit Your Workout"
    submit_text = "Update"

class WorkoutCopyForm(FlaskForm):
    """Copies Workout"""

    submit_text = "Copy Workout"

class GoalAddForm(FlaskForm):
    """Form for adding goals to your workout."""

    exercise = SelectField('Exercise Goal:', coerce=int)
    goal_reps = IntegerField('Reps:', validators=[InputRequired(message='Must have at least 1 "rep."')])
    goal_sets = IntegerField('Sets:', validators=[InputRequired(message='Must have at least 1 "set."')])
    goal_time_sec = IntegerField('Time (Seconds):', validators=[Optional()])
    goal_weight_lbs = IntegerField('Weight (lbs.):', validators=[Optional()])
    goal_distance_miles = IntegerField('Distance (Miles):', validators=[Optional()])

    form_name = "Add Exercise Goal"
    form_title = "Add an Exercise Goal To Your Workout!"
    submit_text = "Add"

class GoalEditForm(FlaskForm):
    """Form for editing a goal."""

    exercise = SelectField('Exercise Goal:', coerce=int)
    goal_reps = IntegerField('Reps:', validators=[InputRequired(message='Must have at least 1 "rep."')])
    goal_sets = IntegerField('Sets:', validators=[InputRequired(message='Must have at least 1 "set."')])
    goal_time_sec = IntegerField('Time (Seconds):', validators=[Optional()])
    goal_weight_lbs = IntegerField('Weight (lbs.):', validators=[Optional()])
    goal_distance_miles = IntegerField('Distance (Miles):', validators=[Optional()])

    form_name = "Edit Exercise Goal"
    form_title = "Edit Your Exercise Goal"
    submit_text = "Save Changes"

class PerformanceAddForm(FlaskForm):
    """Form for adding a performacne record."""

    performance_reps = IntegerField('Actual Reps:')
    performance_sets = IntegerField('Actual Sets:')
    performance_time_sec = IntegerField('Actual Time (seconds):', validators=[Optional()])
    performance_weight_lbs = IntegerField('Actual Weight (lbs):', validators=[Optional()])

    form_name = "Create Performance Record"
    form_title = ""
    submit_text = "Next Exercise"

class PerformanceEditForm(FlaskForm):
    """Form for editing a performance record."""

    performance_reps = IntegerField('Reps:')
    performance_sets = IntegerField('Sets:')
    performance_time_sec = IntegerField('Time (seconds):', validators=[Optional()])
    performance_weight_lbs = IntegerField('Weight (lbs):', validators=[Optional()])

    form_name = "Edit Performance Record"
    form_title = ""
    submit_text = "Save Changes"

##############################################################################

# FOR STEP-THROUGH

class PerformanceStepForm(FlaskForm):
    """Performance Add/Edit form for STEP-THROUGH functionality."""

    performance_reps = IntegerField('Actual Reps:')
    performance_sets = IntegerField('Actual Sets:')
    performance_time_sec = IntegerField('Actual Time (seconds):', validators=[Optional()])
    performance_weight_lbs = IntegerField('Actual Weight (lbs):', validators=[Optional()])

    form_name = "Create Performance Record"
    form_title = None
    previous_text = None
    next_text = "Next Goal"
    next_style = "btn-primary"
    # finish_text = None

##############################################################################

# FOR MULTIPLE PERFORMANCE ENTRIES ON SINGLE PAGE

# class PerformanceAddSingle(Form):
#     """
#     SUBFORM. - Add a performance record for a single goal of a workout.
#     Never used by itself.
#     """

#     performance_reps = IntegerField('Actual Reps:')
#     performance_sets = IntegerField('Actual Sets:')
#     performance_time_sec = IntegerField('Actual Time (seconds):', validators=[Optional()])
#     performance_weight_lbs = IntegerField('Actual Weight (lbs):', validators=[Optional()])

# class PerformanceAddBulk(FlaskForm):
#     """
#     SUPERFORM. - Add instances of PerformanceAddSingle to capture all performance records for all goals of a workout.
#     """

#     performance_records  = FieldList(
#         FormField(PerformanceAddSingle),
#         min_entries=1,
#         max_entries=20
#     )
