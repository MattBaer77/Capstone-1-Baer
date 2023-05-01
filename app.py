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


@app.route('/users/<int:user_id>')
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


@app.route('/users/edit', methods=["GET", "POST"])
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
@app.route('/users/delete', methods=["POST"])
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

    workout = Workout.query.get(workout_id)

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

    workout = Workout.query.get(workout_id)

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

    goal = Goal.query.get(goal_id)

    if check_correct_user_with_message("Access unauthorized.", "danger", goal.on_workouts.owner_user_id):
        return redirect("/")

    workout = Workout.query.get(goal.workout_id)

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

    goal = Goal.query.get(goal_id)

    workout = Workout.query.get(goal.workout_id)

    db.session.delete(goal)
    db.session.commit()

    return redirect(f'/workout/{workout.id}/goal-add')


# DELETE WORKOUT
@app.route('/workout/<int:workout_id>/delete', methods=["POST"])
def delete_workout(workout_id):
    """"""

    if check_for_not_user_with_message("Access unauthorized.", "danger"):
        return redirect('/')

    workout = Workout.query.get(workout_id)

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

    workout = Workout.query.get(workout_id)

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

    goal = Goal.query.get(goal_id)

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

    performance = Performance.query.get(performance_id)

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

# PERFORMING A WORKOUT

# START NEW WORKOUT - CREATE NEW PERFORMANCE RECORDS
# GUIDED EDITOR FOR EACH EXERCISE IN WORKOUT

##############################################################################

# VIEW GRAPHICS SHOWING PERFORMANCE RECORD GRAPHS PER WORKOUT
# PERFORMANCE UP TO INDIVIDUAL PERFORMANCE RECORD FROM CALENDAR
# PEFRORMANCE UP TO TODAY

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