"""SQLAlchemy models for Routine."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

##############################################################################

###

# Level 1 - General Workout Info

class Workout(db.Model):
    """Workouts from API"""

    __tablename__ = 'workouts'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    
class Metric(db.Model):
    """Metrics to measure workout performance"""

    __tablename__ = 'metrics'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

class WorkoutMetric(db.Model):
    """JOIN TABLE workout_metrics"""

    __tablename__ = 'workout_metrics'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

###

# Level 2 - User & Workout Planning

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    bio = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

class Day(db.Model):
    """A Day - a group of workouts"""

    __tablename__ = 'days'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

class DayWorkout(db.Model):
    """JOIN TABLE day_workout"""

    __tablename__ = 'day_workouts'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

class Goal(db.Model):
    """JOIN workout_metric and day_workout then add a goal_value"""

    __tablename__ = 'goal'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

###

class Performance(db.model):
    """JOIN record a day's actual performance to the day's goals"""

    __tablename__ = 'performance'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )


##############################################################################
def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)