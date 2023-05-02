"""View Functions for Routine."""

import os
import pdb
import copy

from secrets import sneakybeaky

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import *
from models import db, connect_db, Exercise, User, Workout, Goal, Performance
from helpers import scrub_default_image_url, replace_default_image_url


CURR_USER_KEY = "curr_user"
WORKOUT_TO_STEP = "workout_to_step"
GOAL_ID_PREVIOUS_STEP = "previous_step"
GOAL_ID_CURRENT_STEP = "current_step"
GOAL_ID_NEXT_STEP = "next_step"

# PERFORMANCE_ID_TO_EDIT = "performance_step_to_edit_id"

PERFORMANCE_RECORDS_CAPTURED_IDS = "performance_records_captured"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///routine'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = sneakybeaky
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def check_for_user():
    """
    Check for a logged in user.
    If User logged in, return True
    """

    if g.user:
        return True


def check_for_user_with_message(message, category):
    """
    Check for a logged in user.
    If User logged in, return True
    """

    if g.user:
        flash(message, category)
        return True


def check_for_not_user_with_message(message, category):
    """
    Check for a logged in user.
    If User logged in, return True
    """

    if not g.user:
        flash(message, category)
        return True


def check_correct_user_with_message(message, category, variable_to_check):
    if g.user.id != variable_to_check:
        flash(message, category)
        return True


# 

##############################################################################

# USER ROUTES

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """
    Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username or email: flash message
    and re-present form.
    """

    if check_for_user_with_message("You are already logged in!", "success"):
        return redirect('/')

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username or email already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('generic-form-page.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    if check_for_user_with_message("You are already logged in!", "success"):
        return redirect('/')

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('generic-form-page.html', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Goodbye!", "info")
    return redirect('/')


@app.route('/users')
def view_users():
    """
    Page with listing of users.
    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/user/<int:user_id>')
def view_user(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging workouts in order from the database;
    # user.workouts won't be in order by default
    workouts = (Workout
                .query
                .filter(Workout.owner_user_id == user_id)
                .order_by(Workout.id.desc())
                .limit(100)
                .all())

    return render_template('users/user.html', user=user, workouts=workouts)


@app.route('/user/edit', methods=["GET", "POST"])
def edit_user():
    """Update profile for current user."""

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    form = UserEditForm(obj=g.user)

    scrub_default_image_url(form)

    if form.validate_on_submit():
        user = User.authenticate(g.user.username,
                                form.password.data)

        if user:
            user.email = form.email.data
            user.username = form.username.data
            user.image_url = form.image_url.data
            replace_default_image_url(form, user)
            user.bio = form.bio.data

            db.session.commit()
            return redirect("/")

        else:
            flash("Access something.", "danger")
            return render_template('users/edit.html', form=form)

    return render_template('users/edit.html', form=form, user=g.user)


# DELETE USER
@app.route('/user/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################

# ROUTES EXERCISES

# VIEW EXERCISES
@app.route('/exercises')
def view_all_exercises():
    """"""

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    search = request.args.get('q')

    if not search:
        exercises = Exercise.query.order_by(Exercise.id.asc()).all()

    else:
        exercises = Exercise.query.filter(Exercise.name.like(f"%{search}%")).order_by(Exercise.id.desc()).all()

    return render_template('exercises.html', exercises=exercises)


##############################################################################

# ROUTES WORKOUTS + GOALS

# VIEW WORKOUTS
@app.route('/workouts')
def view_workouts():
    """
    Page with listing of workouts.
    Can take a 'q' param in querystring to search by that description.
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    search = request.args.get('q')

    if not search:
        workouts = Workout.query.order_by(Workout.id.desc()).all()
    else:
        workouts = Workout.query.filter(Workout.description.like(f"%{search}%")).order_by(Workout.id.desc()).all()

    return render_template('workouts/index.html', user=g.user, workouts=workouts)


# CREATE NEW WORKOUT
@app.route('/workout/add', methods=["GET", "POST"])
def add_workout():
    """"""

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    form = WorkoutAddForm()

    if form.validate_on_submit():
        try:
            workout = Workout.create(
                description=form.description.data,
                owner_user_id=g.user.id
            )
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error - /workout/add - POST", 'danger')
            return redirect('/workout/add')

        return redirect(f'/workout/{workout.id}/goal-add')


    return render_template('generic-form-page.html', form=form)


# ADD GOALS
@app.route('/workout/<int:workout_id>/goal-add', methods=["GET", "POST"])
def add_workout_goal(workout_id):
    """"""

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    workout = Workout.query.get_or_404(workout_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner.id):
        return redirect("/")

    form = GoalAddForm()

    exercises = [(e.id, e.name) for e in Exercise.query.order_by(Exercise.id.asc()).all()]

    form.exercise.choices=exercises

    if form.validate_on_submit():
        try:
            goal = Goal(
                workout_id=workout.id,
                exercise_id= form.exercise.data,
                goal_reps=form.goal_reps.data,
                goal_sets=form.goal_sets.data,
                goal_time_sec=form.goal_time_sec.data,
                goal_weight_lbs=form.goal_weight_lbs.data
            )
            db.session.add(goal)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error - /workout/<int:workout_id>/goal-add - POST", 'danger')
            return redirect('/workout/add')

    return render_template('goals/goals-add-form.html', workout=workout, form=form)


# EDIT WORKOUT
@app.route('/workout/<int:workout_id>/edit', methods=["GET", "POST"])
def edit_workout(workout_id):
    """"""

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    workout = Workout.query.get_or_404(workout_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner.id):
        return redirect("/")

    form = WorkoutEditForm(obj=workout)

    if form.validate_on_submit():
        try:
            workout.description=form.description.data,

            db.session.add(workout)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error - /workout/add - POST", 'danger')
            return redirect('/workout/add')

        return redirect('/')

    return render_template('generic-form-page.html', form=form)


# EDIT GOAL
@app.route('/goal/<int:goal_id>/edit', methods=["GET", "POST"])
def edit_goal(goal_id):
    """"""

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    goal = Goal.query.get_or_404(goal_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", goal.on_workouts.owner_user_id):
        return redirect("/")

    workout = Workout.query.get_or_404(goal.workout_id)

    form = GoalEditForm(obj=goal)

    exercises = [(e.id, e.name) for e in Exercise.query.order_by(Exercise.id.asc()).all()]

    form.exercise.choices=exercises

    if form.validate_on_submit():
        try:
            goal.workout_id=workout.id,
            goal.exercise_id= form.exercise.data,
            goal.goal_reps=form.goal_reps.data,
            goal.goal_sets=form.goal_sets.data,
            goal.goal_time_sec=form.goal_time_sec.data,
            goal.goal_weight_lbs=form.goal_weight_lbs.data
            db.session.add(goal)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error - /workout/<int:workout_id>/goal-add - POST", 'danger')
            return redirect(f'/workout/{workout.id}/goal-add')

        return redirect(f'/workout/{workout.id}/goal-add')

    return render_template('goals/goal-edit-form.html', workout=workout, form=form)


# DELETE GOAL
@app.route('/goal/<int:goal_id>/delete', methods=["POST"])
def delete_goal(goal_id):
    """"""

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    goal = Goal.query.get_or_404(goal_id)

    workout = Workout.query.get_or_404(goal.workout_id)

    db.session.delete(goal)
    db.session.commit()

    return redirect(f'/workout/{workout.id}/goal-add')


# DELETE WORKOUT
@app.route('/workout/<int:workout_id>/delete', methods=["POST"])
def delete_workout(workout_id):
    """"""

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    workout = Workout.query.get_or_404(workout_id)

    db.session.delete(workout)
    db.session.commit()

    return redirect('/')


##############################################################################

# ROUTES PERFORMANCE

# VIEW LIST OF PERFORMANCE RECORDS - ALL GOALS in WORKOUT - CONVERT TO CALENDAR IN FUTURE?
@app.route('/workout/<int:workout_id>/performance')
def view_workout_goals_performance(workout_id):
    """
    View all of the performance toward all the goals in a workout over time.
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    workout = Workout.query.get_or_404(workout_id)

    workout.goals.sort(key=lambda x: x.id, reverse=False)

    for goal in workout.goals:
        goal.performance.sort(key=lambda x: x.id, reverse=False)

    if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner.id):
        return redirect("/")

    return render_template('/performance/view-all.html', workout=workout)

# VIEW LIST OF PERFORMANCE RECORDS - INDIVIDUAL GOAL - CONVERT TO CALENDAR IN FUTURE?
@app.route('/goal/<int:goal_id>/performance')
def view_goal_performance(goal_id):
    """
    View all of the performance toward a single goal over time.
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    goal = Goal.query.get_or_404(goal_id)

    goal.performance.sort(key=lambda x: x.id, reverse=False)

    if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
        return redirect("/")

    return render_template('/performance/view.html', goal=goal)

# EDIT INDIVIDUAL PERFORMANCE RECORDS
@app.route('/performance/<int:performance_id>/edit', methods=["GET", "POST"])
def edit_performance_record(performance_id):
    """
    Edit an individual performance record.
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    performance = Performance.query.get_or_404(performance_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", performance.goal.workout.owner.id):
        return redirect("/")

    form = PerformanceEditForm(obj=performance)

    form.form_title = f"Edit record for Workout: {performance.goal.workout.description} - Goal: {performance.goal.exercise.name}"

    if form.validate_on_submit():
        try:
            performance.performance_reps=form.performance_reps.data,
            performance.performance_sets=form.performance_sets.data,
            performance.performance_time_sec=form.performance_time_sec.data,
            performance.performance_weight_lbs=form.performance_weight_lbs.data

            db.session.add(performance)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error - /workout/add - POST", 'danger')
            return redirect(f'/workout/{performance.goal.workout.id}/performance')

        return redirect(f'/goal/{performance.goal.id}/performance')


    return render_template('generic-form-page.html', form=form)


##############################################################################

# ROUTES USED WHEN PERFORMING A WORKOUT

# PERFORMING A WORKOUT - SINGLE GOAL ROUTE
@app.route('/goal/<int:goal_id>/performance-add', methods=["GET", "POST"])
def create__performance_record(goal_id):
    """
    Displays & handles a form to create a performance record for a single goal in a workout.
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    # performance = Performance.query.get(performance_id)
    goal = Goal.query.get_or_404(goal_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
        return redirect("/")

    temp = Performance(
        goal_id = goal.id,
        performance_reps = goal.goal_reps,
        performance_sets = goal.goal_sets,
        performance_time_sec = goal.goal_time_sec,
        performance_weight_lbs = goal.goal_weight_lbs
    )

    form = PerformanceAddForm(obj=temp)

    form.form_title = f"Create Record For: {goal.workout.description} - Goal: {goal.exercise.name}"

    if form.validate_on_submit():
        try:
            performance = Performance(

                goal_id=goal.id,

                performance_reps=form.performance_reps.data,
                performance_sets=form.performance_sets.data,
                performance_time_sec=form.performance_time_sec.data,
                performance_weight_lbs=form.performance_weight_lbs.data

            )

            db.session.add(performance)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error - /workout/add - POST", 'danger')
            return redirect(f'/workout/{performance.goal.workout.id}/performance')

        return redirect(f'/')

    return render_template('performance/performance-add-single.html', form=form, goal=goal)


##############################################################################

# UTILITY - CLEAR STEP DATA IN SESSION
@app.route('/clear')
def clear():

    if PERFORMANCE_RECORDS_CAPTURED_IDS in session:
        del session[PERFORMANCE_RECORDS_CAPTURED_IDS]
    
    if GOAL_ID_PREVIOUS_STEP in session:
        del session[GOAL_ID_PREVIOUS_STEP]

    if GOAL_ID_CURRENT_STEP in session:
        del session[GOAL_ID_CURRENT_STEP]

    return redirect('/')


# STEP-THROUGH PERFORMANCE ROUTES

# INITIATING A STEP-THROUGH
@app.route('/workout/<int:workout_id>/begin')
def begin_step(workout_id):
    """
    Redirects to start a step-through.
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    workout = Workout.query.get_or_404(workout_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner.id):
        return redirect("/")

    goals = Goal.query.filter(Goal.workout_id == workout_id).order_by(Goal.id.asc()).all()

    session[WORKOUT_TO_STEP] = workout.id

    if GOAL_ID_CURRENT_STEP in session:
        return redirect('/step/next')

    session[GOAL_ID_CURRENT_STEP] = goals[0].id

    session[PERFORMANCE_RECORDS_CAPTURED_IDS] = []

    return redirect(f"/goal/performance-step")

# FINISHING A STEP-THROUGH
@app.route('/finish')
def finish_step():
    """
    Shows stats / graphs of the workout that has been completed.
    Present user with navigation to get to their home page.
    """

    return render_template('/step-through/finish.html')

# STEPPING TO PREVIOUS IN STEP-THROUGH
@app.route('/previous')
def previous_step():
    """
    Increments GOAL_ID_CURRENT_STEP backwards.
    Increments GOAL_ID_PREVIOUS_STEP backwards.
    """

    # CHECK IF A WORKOUT STEP-THROUGH HAS BEEN STARTED AT ALL
    if GOAL_ID_CURRENT_STEP not in session:
        flash("You have not started a workout", "danger")
        return redirect("/")

    # CHECK IF WE ARE ON THE FIRST STEP
    # IF WE ARE DO NOTHING ELSE AND REDIRECT TO THE STEPPER
    if GOAL_ID_PREVIOUS_STEP not in session:
        return redirect('/goal/performance-step')

    goal = Goal.query.get_or_404(session[GOAL_ID_CURRENT_STEP])
    goals = Goal.query.filter(Goal.workout_id == goal.workout.id).order_by(Goal.id.asc()).all()

    current_step_goal_id = goals[(goals.index(goal))].id
    previous_step_goal_id = goals[(goals.index(goal) - 1)].id
    next_previous_step_goal_id = goals[(goals.index(goal) - 2)].id

    session[GOAL_ID_CURRENT_STEP] = previous_step_goal_id
    session[GOAL_ID_PREVIOUS_STEP] = next_previous_step_goal_id

    return redirect('/goal/performance-step')




    # # FROM THE CURRENT STEP - LOOK FOR A PREVIOUS STEP
    # # IF A PREVIOUS STEP EXISTS - MAKE THAT THE CURRENT STEP
    # # IF A PREVIOUS STEP DOES NOT EXIST...
    # try:
    #     previous_step_goal_id = goals[(goals.index(goal) - 1)].id
    #     session[GOAL_ID_CURRENT_STEP] = previous_step_goal_id

    # except IndexError:
    #     previous_step_goal_id = None
    #     del session[GOAL_ID_PREVIOUS_STEP]



    # # IF THE PREVIOUS STEP EXISTED - LOOK FOR THE NEXT PREVIOUS STEP FROM THE ORIGINAL CURRENT STEP
    # # IF THAT EXISTS - MAKE IT THE PREVIOUS STEP
    # # IF NOT, DELETE FROM SESSION

    # if previous_step_goal_id:
    #     try:
    #         next_previous_step_goal_id = goals[(goal.index(goal) - 2)].id
    #         session[GOAL_ID_PREVIOUS_STEP] = next_previous_step_goal_id


    #     except IndexError:
    #         next_previous_step_goal_id = None
    #         del session[GOAL_ID_PREVIOUS_STEP]

    


# # INCREMENTING TO NEXT STEP
# # ELIMINATING THIS BECAUSE IT IS SLOW / REQUIRES ADDITIONAL QUERIES
# @app.route('/next-step')
# def next_step():
#     """
#     Increments to next step of workout
#     """

#     if check_for_not_user_with_message("Access unauthorized.", "danger"):
#         return redirect('/')

#     goal = Goal.query.get_or_404(session[GOAL_ID_CURRENT_STEP])

#     if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
#         return redirect("/")

#     goals = Goal.query.filter(Goal.workout_id == goal.workout.id).order_by(Goal.id.asc()).all()

#     next_step_index = goals.index(goal) + 1

#     session[GOAL_ID_CURRENT_STEP] = goals[(goals.index(goal) + 1)].id

#     return redirect('/goal/performance-step')

#     # ADD LOGIC FOR NO NEXT - REDIRECT TO SAME AND HAVE THEM FINISH
#     # MAYBE CHECK FOR FINISH ELSWHERE AND MODIFY THE NEXT BUTTON TO FINISH
#     # WILL NEED LOGIC IN PREVIOUS AND A LIST OF PREVIOUSLY SUBMITTED IN SESSION TO CHECK FOR TO POPULATE / WRITE OVER SUBMISSION



# PERFORMING A WORKOUT - SINGLE GOAL ROUTE
@app.route('/goal/performance-step', methods=["GET", "POST"])
def create__performance_record_step():
    """
    Displays & handles a form to create a performance record for a single goal in a workout.

    GET-
    Check if there is not a user.
    Check for WOROUT_CURRENT_STEP in session.
    If yes, query the goal of the current step.
    Check that the correct user is accessing this route - owner of the workout.
    Get a list of all goals for this workout in order.
    -
    Determine previous goal.
    Determine next goal.
    (THIS WILL EVENTUALLY REQUIRE LOGIC TO SAVE AND RELOAD PERFORMANCE RECORDS IF YOU NAVIGATE TO PREVIOUS)
    -
    Load default values - (from goals) into form.
    Render Template for form.

    POST-
    Validate form.
    Try to create new performance record from form data.
    If successful - increment stored goal ids to next
    Redirect to next goal.


    """

    # IS A USER NOT LOGGED IN?
    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    # AM I ON A GOAL? WHAT GOAL AM I ON?
    if GOAL_ID_CURRENT_STEP in session:
        goal = Goal.query.get_or_404(session[GOAL_ID_CURRENT_STEP])
    else:
        flash("You have not started a workout", "danger")
        return redirect("/")

    # DOES THIS GOAL BELONG TO THIS USER?
    if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
        return redirect("/")

    goals = Goal.query.filter(Goal.workout_id == goal.workout.id).order_by(Goal.id.asc()).all()

    # I NEED TO -
    # CHECK IF I AM EDITING A STEP FOR WHICH WE HAVE CAPTURED A PERFORNACE RECORD
    # DO THIS BY CHECKING FOR IT IN PERFORMANCE_RECORDS_CAPTURED_IDS
    # IF SO, GET THAT RECORD BY ITS ID
    # PASS THE RELATED INFO INTO THE FORM
    # IF I AM NOT EDITING A PREVIOUS STEP - I SHOULD FILL SOME OF THE FORM WITH GOAL VALUES TO FACILITATE EASY USE

    editing_existing=None

    for record_id in session[PERFORMANCE_RECORDS_CAPTURED_IDS]:
        record = Performance.query.get(record_id)
        if record.goal_id == goal.id:
            editing_existing = record

    if editing_existing:
        obj = editing_existing

    else:
        obj = Performance(
                goal_id = goal.id,
                performance_reps = goal.goal_reps,
                performance_sets = goal.goal_sets
            )

    # CREATE THE FORM AND FILL WITH THE APPROPRIATE DATA
    form = PerformanceStepForm(obj=obj)

    # CHECK FOR PREVIOUS STEP (IF THERE IS ONE) - MODIFY FORM ACCORDINGLY
    if GOAL_ID_PREVIOUS_STEP in session:
        form.previous_text = "Previous Exercise Goal"

    # FIGURE OUT THE ID OF THE NEXT STEP BASED ON YOUR CURRENT STEP
    try:
        next_step_goal_id = goals[(goals.index(goal) + 1)].id

    except IndexError:
        next_step_goal_id = None

    # IF THERE IS NO NEXT STEP - FILL THE FORM WITH DATA APPROPRIATE TO FINISH
    if next_step_goal_id:
        form.next_text = "Next Exercise Goal"
    else:
        form.next_text = "Finish Workout"

    # GIVE THE FORM AN APPROPRIATE TITLE
    form.form_title = f"Create Record For: {goal.workout.description} - Goal: {goal.exercise.name}"

    if editing_existing:
        if form.validate_on_submit():
            try:
                editing_existing.goal_id=goal.id,

                editing_existing.performance_reps=form.performance_reps.data,
                editing_existing.performance_sets=form.performance_sets.data,
                editing_existing.performance_time_sec=form.performance_time_sec.data,
                editing_existing.performance_weight_lbs=form.performance_weight_lbs.data

                db.session.add(editing_existing)
                db.session.commit()

            except IntegrityError:
                flash("Unknown Integrity Error - /workout/add - POST", 'danger')
                return redirect(f'/workout/{performance.goal.workout.id}/performance')

            # IF THERE IS A NEXT STEP - INCREMENT APPROPRIATE VALUES UP - MOVE TO NEXT STEP
            if next_step_goal_id:
                session[GOAL_ID_PREVIOUS_STEP] = goal.id
                session[GOAL_ID_CURRENT_STEP] = next_step_goal_id
                session[PERFORMANCE_RECORDS_CAPTURED_IDS].append(editing_existing.id)
                return redirect('/goal/performance-step')

            # IF THERE IS NOT A NEXT STEP - FINISH THIS WORKOUT STEP-THROUGH
            else:
                return redirect('/finish')


    if form.validate_on_submit():
        try:
            performance = Performance(

                goal_id=goal.id,

                performance_reps=form.performance_reps.data,
                performance_sets=form.performance_sets.data,
                performance_time_sec=form.performance_time_sec.data,
                performance_weight_lbs=form.performance_weight_lbs.data

            )

            db.session.add(performance)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error - /workout/add - POST", 'danger')
            return redirect(f'/workout/{performance.goal.workout.id}/performance')

        # IF THERE IS A NEXT STEP - INCREMENT APPROPRIATE VALUES UP - MOVE TO NEXT STEP
        if next_step_goal_id:
            session[GOAL_ID_PREVIOUS_STEP] = goal.id
            session[GOAL_ID_CURRENT_STEP] = next_step_goal_id
            session[PERFORMANCE_RECORDS_CAPTURED_IDS].append(performance.id)
            return redirect('/goal/performance-step')

        # IF THERE IS NOT A NEXT STEP - FINISH THIS WORKOUT STEP-THROUGH
        else:
            return redirect('/finish')

    return render_template('performance/performance-step-single.html', form=form, goal=goal)


##############################################################################

# VIEW GRAPHICS SHOWING PERFORMANCE RECORD GRAPHS PER WORKOUT
# PERFORMANCE UP TO INDIVIDUAL PERFORMANCE RECORD FROM CALENDAR
# PEFRORMANCE UP TO TODAY


##############################################################################


##############################################################################
##############################################################################
##############################################################################

# HELP! - THIS WOULD BE GREAT FUNCTIONALITY FOR EDITING PERFORMANCE RECORDS FOR A WORKOUT (ALTHOUGH RIGHT NOW IT IS SET UP AS A RECORD-ADDER)
# INITIALLY IMPLEMENTED TO CREATE A FORM TO USE BOOTSTRAP STEPPER - DIFFICULTY WORKING WITH IT
# USING WTF INTENTED TECHNIQUES -

# ISSUES -
    # DIFFICULTY WITH FORMATTING - CREATES TABLES OF FORMS - DOES NOT RESPOND WELL TO BOOTSTRAP FORMATTING
    # DIFFICULTY WITH FORMATTING - AUTO-GENERATES TITLE CONSISTING OF INDEX OF "PERFORMANCE RECORDS"

# PERFORMING A WORKOUT - ALL IN ONE ROUTE
@app.route('/workout/<int:workout_id>/performance-add', methods=["GET", "POST"])
def create_performance_records(workout_id):

    """
    Displays & hanldes a form to create a performance record for every goal in a workout.
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    workout = Workout.query.get_or_404(workout_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner.id):
        return redirect("/")

    performance_records = []

    for goal in workout.goals:
        record = {
            "performance_reps":goal.goal_reps,
            "performance_sets":goal.goal_sets,
            "performance_time_sec":goal.goal_time_sec,
            "performance_weight_lbs":goal.goal_weight_lbs
        }

        performance_records.append(record)

    data = {"performance_records":performance_records}

    form = PerformanceAddBulk(data=data)

    if form.validate_on_submit():
        for field in form.performance_records:
            try:
                performance = Performance(

                    goal_id=goal.id,

                    performance_reps=field.performance_reps.data,
                    performance_sets=field.performance_sets.data,
                    performance_time_sec=field.performance_time_sec.data,
                    performance_weight_lbs=field.performance_weight_lbs.data

                )

                db.session.add(performance)
                db.session.commit()

            except IntegrityError:
                flash("Unknown Integrity Error - /workout/add - POST", 'danger')
                return redirect(f'/workout/{performance.goal.workout.id}/performance')

        return redirect(f'/')

    return render_template('performance/performance-add.html', form=form, workout=workout)


##############################################################################
##############################################################################
##############################################################################


##############################################################################

# ROOT ROUTES / HOME

@app.route('/')
def home():
    """
    Show a page with
    user info
    user workouts
    """



    if check_for_user():

        # All workouts, but filter out copied workouts and users own workouts
        workouts = (Workout
                    .query
                    .filter((Workout.owner_user_id == Workout.author_user_id) & (Workout.owner_user_id != g.user.id))
                    .order_by(Workout.id.desc())
                    .all())

        my_workouts = (Workout
                    .query
                    .filter(Workout.owner_user_id == g.user.id)
                    .order_by(Workout.id.desc())
                    .all())

        return render_template('home.html', user=g.user, workouts=workouts, my_workouts=my_workouts)

    else:

        # All workouts, but filter out copied workouts
        workouts = (Workout
                    .query.
                    filter(Workout.owner_user_id == Workout.author_user_id)
                    .order_by(Workout.id.desc())
                    .all())

        return render_template('home-anon.html', workouts=workouts)