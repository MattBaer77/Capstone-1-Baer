"""View Functions for Routine."""

import os
import pdb
import copy
from datetime import datetime

from secrets import sneakybeaky

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import *
from models import db, connect_db, Exercise, User, Workout, Goal, Performance
from helpers import scrub_default_image_url, replace_default_image_url


CURR_USER_KEY = "curr_user"
GOAL_ID_PREVIOUS = "previous_step"
GOAL_ID_CURRENT = "current_step"

PERFORMANCE_RECORDS_CAPTURED_IDS = "performance_records_captured"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///routine'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = sneakybeaky
# toolbar = DebugToolbarExtension(app)

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


def session_step_data_clearout():
    if PERFORMANCE_RECORDS_CAPTURED_IDS in session:
        del session[PERFORMANCE_RECORDS_CAPTURED_IDS]
    
    if GOAL_ID_PREVIOUS in session:
        del session[GOAL_ID_PREVIOUS]

    if GOAL_ID_CURRENT in session:
        del session[GOAL_ID_CURRENT]


def check_if_editing_existing(goal):
    for performance_record_id in session[PERFORMANCE_RECORDS_CAPTURED_IDS]:
        record = Performance.query.get(performance_record_id)
        if record.goal_id == goal.id:
            return record


def title_form(action, workout_description, goal_exercise_name):
    return f"{action} Record For: {workout_description} - Goal: {goal_exercise_name}"


def determine_next_step(goals, goal):
    try:
        return goals[(goals.index(goal) + 1)].id

    except IndexError:
        return None


def determine_previous_step(goals, goal):
    try:
        if ((goals.index(goal) - 1)) > -1:
            return (goals[(goals.index(goal) - 1)].id)
        else:
            return None

    except IndexError:
        return None


def increment_step(goal_id, next_step_goal_id, performance_record_id):
    session[GOAL_ID_PREVIOUS] = goal_id
    session[GOAL_ID_CURRENT] = next_step_goal_id
    session[PERFORMANCE_RECORDS_CAPTURED_IDS].append(performance_record_id)

def check_for_stepthrough_with_message(message, category):
    """
    Check for a started stepthrough.
    If a stepthrough is started, return True
    """

    if GOAL_ID_CURRENT in session:
        flash(message, category)
        return True


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

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

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
            return render_template('base-form.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('base-form.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    if check_for_user_with_message("You are already logged in!", "success"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('base-form.html', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    """Handle logout of user."""

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    do_logout()
    flash("Goodbye!", "info")
    return redirect('/')


@app.route('/user/edit', methods=["GET", "POST"])
def edit_user():
    """Update profile for current user."""

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

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

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    do_logout()

    workouts_authored = Workout.query.filter(Workout.author_user_id == g.user.id).all()

    for workout in workouts_authored:
        workout.author_user_id = workout.owner_user_id

    db.session.commit()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/")


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

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    search = request.args.get('q')

    if not search:
        workouts = (Workout
            .query
            .filter((Workout.owner_user_id != g.user.id) & (Workout.author_user_id != g.user.id))
            .order_by(Workout.id.desc())
            .all())
    else:
        workouts = Workout.query.filter((Workout.description.like(f"%{search}%")) & (Workout.owner_user_id != g.user.id) & (Workout.author_user_id != g.user.id)).order_by(Workout.id.desc()).all()

    return render_template('workouts/index.html', user=g.user, workouts=workouts)


# CREATE NEW WORKOUT
@app.route('/workout/add', methods=["GET", "POST"])
def add_workout():
    """
    Creates a new workout
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    form = WorkoutAddForm()

    if form.validate_on_submit():
        try:
            workout = Workout.create(
                description=form.description.data,
                owner_user_id=g.user.id
            )
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error", 'danger')
            return redirect('/workout/add')

        return redirect(f'/workout/{workout.id}/goal-add')


    return render_template('base-form.html', form=form)

# VIEW WORKOUT
# SHOWS WORKOUT INFO WITH 1 COPY FORM
@app.route('/workout/<int:workout_id>')
def view_workout(workout_id):
    """
    Shows a page with information on a single workout by id
    Displays a form allowing a user to copy the single workout
    POST to /workout/<int:workout_id>/copy
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    workout = Workout.query.get_or_404(workout_id)

    form = WorkoutCopyForm(obj=workout)

    return render_template('/workouts/view.html', workout=workout, form=form)


# COPY WORKOUT - POST ONLY
@app.route('/workout/<int:workout_id>/copy', methods=["POST"])
def copy_workout(workout_id):
    """
    Copies a workout by id
    Runs workout copy classmethod
    POST only route
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    workout = Workout.query.get_or_404(workout_id)

    form = WorkoutCopyForm(obj=workout)

    if form.validate_on_submit():
        try:
            copied_workout = Workout.copy(workout, g.user.id)

        except IntegrityError:
            flash("Unknown Integrity Error", 'danger')
            return redirect('/')

        return redirect(f'/workout/{copied_workout.id}/edit')

    return redirect(f'/workouts/{workout_id}')


# ADD GOALS
@app.route('/workout/<int:workout_id>/goal-add', methods=["GET", "POST"])
def add_workout_goal(workout_id):
    """
    Add a goal to a workout by workout_id
    Displays and accepts a form.
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    workout = Workout.query.get_or_404(workout_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner.id):
        return redirect("/")

    form = GoalAddForm()
    delete_form = GoalDeleteForm()

    exercises = [(e.id, e.name) for e in Exercise.query.order_by(Exercise.id.asc()).all()]

    form.exercise.choices=exercises

    if form.validate_on_submit():
        try:
            workout.author_user_id = workout.owner_user_id
            goal = Goal(
                workout_id=workout.id,
                exercise_id= form.exercise.data,
                goal_reps=form.goal_reps.data,
                goal_sets=form.goal_sets.data,
                goal_time_sec=form.goal_time_sec.data,
                goal_weight_lbs=form.goal_weight_lbs.data,
                goal_distance_miles=form.goal_distance_miles.data
            )
            db.session.add(workout)
            db.session.add(goal)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error - /workout/<int:workout_id>/goal-add - POST", 'danger')
            return redirect('/workout/add')

    return render_template('goals/add.html', workout=workout, form=form, delete_form=delete_form)


# EDIT WORKOUT
@app.route('/workout/<int:workout_id>/edit', methods=["GET", "POST"])
def edit_workout(workout_id):
    """
    Edits workout by id
    Displays and accepts a form.
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    workout = Workout.query.get_or_404(workout_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner.id):
        return redirect("/")

    form = WorkoutEditForm(obj=workout)

    if form.validate_on_submit():
        try:
            workout.description=form.description.data,
            workout.author_user_id=workout.owner_user_id

            db.session.add(workout)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error", 'danger')
            return redirect('/workout/add')

        return redirect('/')

    return render_template('/workouts/edit.html', form=form, workout=workout)


# EDIT GOAL
@app.route('/goal/<int:goal_id>/edit', methods=["GET", "POST"])
def edit_goal(goal_id):
    """
    Edits goal by id
    Displays and accepts a form.
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    goal = Goal.query.get_or_404(goal_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner_user_id):
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
            goal.goal_weight_lbs=form.goal_weight_lbs.data,
            goal.goal_distance_miles=form.goal_distance_miles.data
            db.session.add(goal)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error - /workout/<int:workout_id>/goal-add - POST", 'danger')
            return redirect(f'/workout/{workout.id}/goal-add')

        return redirect(f'/workout/{workout.id}/goal-add')

    return render_template('/goals/edit.html', workout=workout, form=form)


# DELETE GOAL
@app.route('/goal/<int:goal_id>/delete', methods=["POST"])
def delete_goal(goal_id):
    """
    Deletes goal by id
    POST only to avoid issues with prefetching
    """

    form = GoalDeleteForm()

    if form.validate_on_submit():

        if check_for_not_user_with_message("Access unauthorized.", "danger"):
            return redirect('/')

        if check_for_stepthrough_with_message("You have quit your workout", "warning"):
            return redirect('/finish')

        goal = Goal.query.get_or_404(goal_id)

        if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
            return redirect("/")

        workout = Workout.query.get_or_404(goal.workout_id)

        db.session.delete(goal)
        db.session.commit()

        return redirect(f'/workout/{workout.id}/goal-add')

    flash("Access unauthorized.", "danger")
    return redirect('/')


# DELETE WORKOUT
@app.route('/workout/<int:workout_id>/delete', methods=["POST"])
def delete_workout(workout_id):
    """
    Deletes workout by id
    POST only to avoid issues with prefetching
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    workout = Workout.query.get_or_404(workout_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner.id):
        return redirect("/")

    db.session.delete(workout)
    db.session.commit()

    return redirect('/')


##############################################################################

# ROUTES PERFORMANCE

# VIEW LIST OF PERFORMANCE RECORDS - INDIVIDUAL GOAL - CONVERT TO CALENDAR IN FUTURE?
@app.route('/goal/<int:goal_id>/performance')
def view_goal_performance(goal_id):
    """
    View all of the performance toward a single goal over time.
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    goal = Goal.query.get_or_404(goal_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
        return redirect("/")

    performance_records = Performance.query.filter(Performance.goal_id == goal_id).order_by(Performance.id.asc()).all()

    goals = Goal.query.filter(Goal.workout_id == goal.workout.id).order_by(Goal.id.asc()).all()

    next_step_goal_id = determine_next_step(goals,goal)
    previous_step_goal_id = determine_previous_step(goals,goal)

    return render_template('/performance/view-chart.html', goal=goal, performance=performance_records, previous_step=previous_step_goal_id, next_step=next_step_goal_id)


# EDIT INDIVIDUAL PERFORMANCE RECORDS
@app.route('/performance/<int:performance_id>/edit', methods=["GET", "POST"])
def edit_performance_record(performance_id):
    """
    Edit an individual performance record
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    performance = Performance.query.get_or_404(performance_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", performance.goal.workout.owner.id):
        return redirect("/")

    form = PerformanceEditForm(obj=performance)

    form.form_title = title_form("Edit", performance.goal.workout.description, performance.goal.exercise.name)

    if form.validate_on_submit():
        try:
            performance.last_edited_date=datetime.utcnow(),
            performance.performance_reps=form.performance_reps.data,
            performance.performance_sets=form.performance_sets.data,
            performance.performance_time_sec=form.performance_time_sec.data,
            performance.performance_weight_lbs=form.performance_weight_lbs.data,
            performance.performance_distance_miles=form.performance_distance_miles.data

            db.session.add(performance)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error", 'danger')
            return redirect(f'/workout/{performance.goal.workout.id}/performance')

        return redirect(f'/goal/{performance.goal.id}/performance')


    return render_template('base-form.html', form=form)


##############################################################################
# API ROUTES for GOAL and PERFORMANCE

@app.route('/api/goal/<int:goal_id>')
def api_send_goal(goal_id):
    """
    Send JSON of all of the performance toward a single goal over time
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    goal = Goal.query.get_or_404(goal_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
        return redirect("/")

    goal_json = goal.serialize()

    return jsonify(goal_json=goal_json)

@app.route('/api/goal/<int:goal_id>/performance')
def api_send_goal_performance(goal_id):
    """
    Send JSON of all of the performance toward a single goal over time
    """

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    goal = Goal.query.get_or_404(goal_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
        return redirect("/")

    performance_records = Performance.query.filter(Performance.goal_id == goal_id).order_by(Performance.id.asc()).all()

    performance_json = [record.serialize() for record in performance_records]

    return jsonify(performance_json=performance_json)


##############################################################################

# ROUTES USED WHEN PERFORMING A WORKOUT

# INITIATING A STEP-THROUGH
@app.route('/workout/<int:workout_id>/step')
def begin_step(workout_id):
    """
    Adds the ID for the first workout goal of the selected workout to session
    Creates a list in session to capture the performance records generated as part of this step-through
    Redirects to start a step-through
    """

    # CHECK IF NOT USER
    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    # CHECK IF WORKOUT STARTED
    if GOAL_ID_CURRENT in session:
        return redirect('/step')

    workout = Workout.query.get_or_404(workout_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner_user_id):
        return redirect("/")

    goals = Goal.query.filter(Goal.workout_id == workout_id).order_by(Goal.id.asc()).all()

    if len(goals) <= 0:
        flash("You must add goals to a workout prior to starting.", "danger")
        return redirect('/')

    session[GOAL_ID_CURRENT] = goals[0].id

    session[PERFORMANCE_RECORDS_CAPTURED_IDS] = []

    return redirect(f"/step")


# FINISHING A STEP-THROUGH
@app.route('/finish')
def finish_step():
    """
    Clearout STEP-THROUGH data from session
    Link to stats / graphs of the workout that has been completed
    Present user with navigation to get to their home page
    """

    # CHECK IF NOT USER
    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    # CHECK IF WORKOUT NOT STARTED
    if GOAL_ID_CURRENT not in session:
        flash("You have not started a workout", "danger")
        return redirect("/")

    goal = Goal.query.get_or_404(session[GOAL_ID_CURRENT])
    goals = Goal.query.filter(Goal.workout_id == goal.workout.id).order_by(Goal.id.asc()).all()

    # DOES THIS GOAL BELONG TO THIS USER?
    if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
        return redirect("/")

    session_step_data_clearout()

    return render_template('/performance/step-finish.html', goal=goal, goals=goals)


# STEPPING TO PREVIOUS IN STEP-THROUGH
@app.route('/previous')
def previous_step():
    """
    Increments GOAL_ID_CURRENT backwards
    Increments GOAL_ID_PREVIOUS backwards
    """

    # IS A USER NOT LOGGED IN?
    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    # IS A WORKOUT NOT STARTED?
    if GOAL_ID_CURRENT not in session:
        flash("You have not started a workout", "danger")
        return redirect("/")

    # CHECK IF WE ARE ON THE FIRST STEP
    if GOAL_ID_PREVIOUS not in session:
        return redirect('/step')

    goal = Goal.query.get_or_404(session[GOAL_ID_CURRENT])
    goals = Goal.query.filter(Goal.workout_id == goal.workout.id).order_by(Goal.id.asc()).all()

    # DOES THIS GOAL BELONG TO THIS USER?
    if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
        return redirect("/")

    previous_step_goal_id = goals[(goals.index(goal) - 1)].id
    next_previous_step_goal_id = goals[(goals.index(goal) - 2)].id

    session[GOAL_ID_CURRENT] = previous_step_goal_id
    session[GOAL_ID_PREVIOUS] = next_previous_step_goal_id

    # PREVENT /previous INFINITE LOOP
    if session[GOAL_ID_PREVIOUS] > session[GOAL_ID_CURRENT]:
        del session[GOAL_ID_PREVIOUS]

    return redirect('/step-edit')


# PERFORMING A WORKOUT - SINGLE GOAL ROUTE
@app.route('/step', methods=["GET", "POST"])
def step():
    """
    Primary route for a STEP-THROUGH
    Displays & handles a form to create a performance record for a single goal in a workout
    Passes data to session in order to maintain location / state
    """


    # IS A USER NOT LOGGED IN?
    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    # IS A WORKOUT NOT STARTED?
    if GOAL_ID_CURRENT not in session:
        flash("You have not started a workout", "danger")
        return redirect("/")

    # FIND THE GOAL THAT I AM ON
    goal = Goal.query.get_or_404(session[GOAL_ID_CURRENT])

    # DOES THIS GOAL BELONG TO THIS USER?
    if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
        return redirect("/")

    record = check_if_editing_existing(goal)

    if record:
        return redirect('step-edit')

    obj = Performance(
            goal_id = goal.id,
            performance_reps = goal.goal_reps,
            performance_sets = goal.goal_sets
        )

    goals = Goal.query.filter(Goal.workout_id == goal.workout.id).order_by(Goal.id.asc()).all()

    # CREATE THE FORM AND FILL WITH THE APPROPRIATE DATA
    form = PerformanceStepForm(obj=obj)

    # CHECK FOR PREVIOUS STEP (IF THERE IS ONE) - MODIFY FORM ACCORDINGLY
    if GOAL_ID_PREVIOUS in session:
        form.previous_text = "Previous Goal"

    # FIGURE OUT THE ID OF THE NEXT STEP BASED ON YOUR CURRENT STEP
    next_step_goal_id = determine_next_step(goals,goal)

    # IF THERE IS NO NEXT STEP - FILL THE FORM WITH DATA APPROPRIATE TO FINISH
    if not next_step_goal_id:
        form.next_text = "Finish Workout"
        form.next_style = "btn-success"

    # GIVE THE FORM AN APPROPRIATE TITLE
    form.form_title = title_form("Create", goal.workout.description, goal.exercise.name)


    if form.validate_on_submit():
        try:
            performance = Performance(

                goal_id=goal.id,

                date=datetime.utcnow(),
                performance_reps=form.performance_reps.data,
                performance_sets=form.performance_sets.data,
                performance_time_sec=form.performance_time_sec.data,
                performance_weight_lbs=form.performance_weight_lbs.data,
                performance_distance_miles=form.performance_distance_miles.data

            )

            db.session.add(performance)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error", 'danger')
            return redirect(f'/workout/{performance.goal.workout.id}/performance')

        # IF THERE IS A NEXT STEP - INCREMENT APPROPRIATE VALUES UP - MOVE TO NEXT STEP
        if next_step_goal_id:
            increment_step(goal.id, next_step_goal_id, performance.id)
            return redirect('/step')

        # IF THERE IS NOT A NEXT STEP - FINISH THIS WORKOUT STEP-THROUGH
        else:
            return redirect('/finish')

    return render_template('performance/step-single.html', form=form, goal=goal)


# PERFORMING A WORKOUT - EDIT PERFORMANCE RECORD AFTER NAVIGATING TO PREVIOUS
@app.route('/step-edit', methods=["GET", "POST"])
def step_edit():
    """
    Edit route for a STEP-THROUGH
    Displays & handles a form to create a performance record for a single goal in a workout
    Passes data to session in order to maintain location / state
    """


    # IS A USER NOT LOGGED IN?
    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    # IS A WORKOUT NOT STARTED?
    if GOAL_ID_CURRENT not in session:
        flash("You have not started a workout", "danger")
        return redirect("/")

    # FIND THE GOAL THAT I AM ON
    goal = Goal.query.get_or_404(session[GOAL_ID_CURRENT])

    # DOES THIS GOAL BELONG TO THIS USER?
    if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
        return redirect("/")

    record = check_if_editing_existing(goal)

    if not record:
        return redirect('/step')

    obj=record

    goals = Goal.query.filter(Goal.workout_id == goal.workout.id).order_by(Goal.id.asc()).all()

    # CREATE THE FORM AND FILL WITH THE APPROPRIATE DATA
    form = PerformanceStepForm(obj=obj)

    # CHECK FOR PREVIOUS STEP (IF THERE IS ONE) - MODIFY FORM ACCORDINGLY
    if GOAL_ID_PREVIOUS in session:
        form.previous_text = "Previous Goal"

    # FIGURE OUT THE ID OF THE NEXT STEP BASED ON YOUR CURRENT STEP
    next_step_goal_id = determine_next_step(goals,goal)

    # IF THERE IS NO NEXT STEP - FILL THE FORM WITH DATA APPROPRIATE TO FINISH
    if not next_step_goal_id:
        form.next_text = "Finish Workout"
        form.next_style = "btn-success"

    # GIVE THE FORM AN APPROPRIATE TITLE
    form.form_title = title_form("Edit", goal.workout.description, goal.exercise.name)

    if form.validate_on_submit():
        try:
            record.goal_id=goal.id,

            record.last_edited_date=datetime.utcnow(),
            record.performance_reps=form.performance_reps.data,
            record.performance_sets=form.performance_sets.data,
            record.performance_time_sec=form.performance_time_sec.data,
            record.performance_weight_lbs=form.performance_weight_lbs.data,
            record.performance_distance_miles=form.performance_distance_miles.data

            db.session.add(record)
            db.session.commit()

        except IntegrityError:
            flash("Unknown Integrity Error", 'danger')
            return redirect(f'/workout/{performance.goal.workout.id}/performance')

        # IF THERE IS A NEXT STEP - INCREMENT APPROPRIATE VALUES UP - MOVE TO NEXT STEP
        if next_step_goal_id:
            increment_step(goal.id, next_step_goal_id, record.id)
            return redirect('/step')

        # IF THERE IS NOT A NEXT STEP - FINISH THIS WORKOUT STEP-THROUGH
        else:
            return redirect('/finish')

    return render_template('performance/step-single.html', form=form, goal=goal)


##############################################################################

# ROOT ROUTES / HOME

@app.route('/')
def home():
    """
    Check for a logged-in user.

    If a user is logged in:
    Get 20 workouts that are original to their respective owners (not copies) to avoid duplicates, and that are not owned by the logged-in user
    Get all workouts owned by logged-in user
    Return home.html with this informtion

    If a user is not logged in
    Get 20 workouts that are original to their respective owners (not copies) to avoid duplicates
    Return home-anon.html with this information
    """

    if check_for_stepthrough_with_message("You have quit your workout", "warning"):
        return redirect('/finish')

    if check_for_user():

        # All workouts, but filter out copied workouts and users own workouts
        workouts = (Workout
                    .query
                    .filter((Workout.owner_user_id == Workout.author_user_id) & (Workout.owner_user_id != g.user.id) & (Workout.author_user_id != g.user.id))
                    .order_by(Workout.id.desc())
                    .limit(20)
                    .all())

        my_workouts = (Workout
                    .query
                    .filter(Workout.owner_user_id == g.user.id)
                    .order_by(Workout.id.desc())
                    .all())

        # raise

        return render_template('home.html', user=g.user, workouts=workouts, my_workouts=my_workouts)

    else:

        # All workouts, but filter out copied workouts
        workouts = (Workout
                    .query.
                    filter(Workout.owner_user_id == Workout.author_user_id)
                    .order_by(Workout.id.desc())
                    .limit(20)
                    .all())

        return render_template('home-anon.html', workouts=workouts)


##############################################################################

# UNUSED ROUTES - REFERENCE

# @app.route('/users')
# def view_users():
#     """
#     Page with listing of users.
#     Can take a 'q' param in querystring to search by that username.
#     """

#     search = request.args.get('q')

#     if not search:
#         users = User.query.all()
#     else:
#         users = User.query.filter(User.username.like(f"%{search}%")).all()

#     return render_template('users/index.html', users=users)


# @app.route('/user')
# def view_user():
#     """Show user profile."""

#     if check_for_not_user_with_message("Access unauthorized.", "danger"):
#         return redirect('/')

#     user = g.user

#     workouts = (Workout
#                 .query
#                 .filter(Workout.owner_user_id == g.user.id)
#                 .order_by(Workout.id.desc())
#                 .all())

#     return render_template('users/user.html', user=user, workouts=workouts)


# VIEW EXERCISES
# @app.route('/exercises')
# def view_all_exercises():
#     """"""

#     if check_for_not_user_with_message("Access unauthorized.", "danger"):
#         return redirect('/')

#     search = request.args.get('q')

#     if not search:
#         exercises = Exercise.query.order_by(Exercise.id.asc()).all()

#     else:
#         exercises = Exercise.query.filter(Exercise.name.like(f"%{search}%")).order_by(Exercise.id.desc()).all()

#     return render_template('exercises.html', exercises=exercises)


# ADD SINGLE GOAL
# @app.route('/workout/<int:workout_id>/goal-add-single', methods=["GET", "POST"])
# def add_workout_goal_single(workout_id):
#     """"""

#     if check_for_not_user_with_message("Access unauthorized.", "danger"):
#         return redirect('/')

#     workout = Workout.query.get_or_404(workout_id)

#     if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner.id):
#         return redirect("/")

#     form = GoalAddForm()

#     exercises = [(e.id, e.name) for e in Exercise.query.order_by(Exercise.id.asc()).all()]

#     form.exercise.choices=exercises

#     if form.validate_on_submit():
#         try:
#             goal = Goal(
#                 workout_id=workout.id,
#                 exercise_id= form.exercise.data,
#                 goal_reps=form.goal_reps.data,
#                 goal_sets=form.goal_sets.data,
#                 goal_time_sec=form.goal_time_sec.data,
#                 goal_weight_lbs=form.goal_weight_lbs.data
#             )
#             db.session.add(goal)
#             db.session.commit()

#             return redirect(f'/workout/{workout_id}/edit')

#         except IntegrityError:
#             flash("Unknown Integrity Error - /workout/<int:workout_id>/goal-add - POST", 'danger')
#             return redirect('/workout/add')

#     return render_template('goals/add-single.html', workout=workout, form=form)


# VIEW LIST OF PERFORMANCE RECORDS - ALL GOALS in WORKOUT - CONVERT TO CALENDAR IN FUTURE?
# @app.route('/workout/<int:workout_id>/performance')
# def view_workout_goals_performance(workout_id):
#     """
#     View all of the performance toward all the goals in a workout over time.
#     """

#     if check_for_not_user_with_message("Access unauthorized.", "danger"):
#         return redirect('/')

#     workout = Workout.query.get_or_404(workout_id)

#     goals = Goal.query.filter(Goal.workout_id == workout_id).order_by(Goal.id.asc()).all()

#     # workout.goals.sort(key=lambda x: x.id, reverse=False)

#     performance_records = {}

#     for goal in goals:
#         # goal.performance.sort(key=lambda x: x.id, reverse=False)
#         performance_records[goal.id] = Performance.query.filter(Performance.goal_id == goal.id).order_by(Performance.id.asc()).all()

#     if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner.id):
#         return redirect("/")

#     # raise

#     return render_template('/performance/view-all.html', workout=workout, goals=goals, performance_records=performance_records)


# CONSIDER DELETEME IF NOT USED
# PERFORMING A WORKOUT - SINGLE GOAL ROUTE
# @app.route('/goal/<int:goal_id>/performance-add', methods=["GET", "POST"])
# def create__performance_record(goal_id):
#     """
#     Displays & handles a form to create a performance record for a single goal in a workout.
#     """

#     if check_for_not_user_with_message("Access unauthorized.", "danger"):
#         return redirect('/')

#     # performance = Performance.query.get(performance_id)
#     goal = Goal.query.get_or_404(goal_id)

#     if check_correct_user_with_message("Access unauthorized.", "danger", goal.workout.owner.id):
#         return redirect("/")

#     temp = Performance(
#         goal_id = goal.id,
#         performance_reps = goal.goal_reps,
#         performance_sets = goal.goal_sets,
#         performance_time_sec = goal.goal_time_sec,
#         performance_weight_lbs = goal.goal_weight_lbs
#     )

#     form = PerformanceAddForm(obj=temp)

#     form.form_title = title_form("Create", goal.workout.description, goal.exercise.name)

#     if form.validate_on_submit():
#         try:
#             performance = Performance(

#                 goal_id=goal.id,

#                 performance_reps=form.performance_reps.data,
#                 performance_sets=form.performance_sets.data,
#                 performance_time_sec=form.performance_time_sec.data,
#                 performance_weight_lbs=form.performance_weight_lbs.data

#             )

#             db.session.add(performance)
#             db.session.commit()

#         except IntegrityError:
#             flash("Unknown Integrity Error", 'danger')
#             return redirect(f'/workout/{performance.goal.workout.id}/performance')

#         return redirect(f'/')

#     return render_template('performance/add-single.html', form=form, goal=goal)


# UTILITY - CLEAR ALL STEP DATA IN SESSION - DELETEME BEFORE FINISHING
# @app.route('/clear')
# def clear():

#     if PERFORMANCE_RECORDS_CAPTURED_IDS in session:
#         del session[PERFORMANCE_RECORDS_CAPTURED_IDS]
    
#     if GOAL_ID_PREVIOUS in session:
#         del session[GOAL_ID_PREVIOUS]

#     if GOAL_ID_CURRENT in session:
#         del session[GOAL_ID_CURRENT]

#     return redirect('/')


# PERFORMING A WORKOUT - ALL IN ONE ROUTE
# @app.route('/workout/<int:workout_id>/performance-add', methods=["GET", "POST"])
# def create_performance_records(workout_id):

#     """
#     Displays & hanldes a form to create a performance record for every goal in a workout.
#     """

#     if check_for_not_user_with_message("Access unauthorized.", "danger"):
#         return redirect('/')

#     workout = Workout.query.get_or_404(workout_id)

#     if check_correct_user_with_message("Access unauthorized.", "danger", workout.owner.id):
#         return redirect("/")

#     performance_records = []

#     for goal in workout.goals:
#         record = {
#             "performance_reps":goal.goal_reps,
#             "performance_sets":goal.goal_sets,
#             "performance_time_sec":goal.goal_time_sec,
#             "performance_weight_lbs":goal.goal_weight_lbs
#         }

#         performance_records.append(record)

#     data = {"performance_records":performance_records}

#     form = PerformanceAddBulk(data=data)

#     if form.validate_on_submit():
#         for field in form.performance_records:
#             try:
#                 performance = Performance(

#                     goal_id=goal.id,

#                     performance_reps=field.performance_reps.data,
#                     performance_sets=field.performance_sets.data,
#                     performance_time_sec=field.performance_time_sec.data,
#                     performance_weight_lbs=field.performance_weight_lbs.data

#                 )

#                 db.session.add(performance)
#                 db.session.commit()

#             except IntegrityError:
#                 flash("Unknown Integrity Error", 'danger')
#                 return redirect(f'/workout/{performance.goal.workout.id}/performance')

#         return redirect(f'/')

#     return render_template('performance/add.html', form=form, workout=workout)