"""SQLAlchemy models for Routine."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

##############################################################################

###

# Level 1 - General Exercise Info

class Exercise(db.Model):
    """Exercises from API"""

    __tablename__ = 'exercises'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    
class Metric(db.Model):
    """Metrics to measure exercise performance"""

    __tablename__ = 'metrics'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

class ExerciseMetric(db.Model):
    """JOIN TABLE exercise_metrics"""

    __tablename__ = 'exercise_metrics'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

###

# Level 2 - User & Exercise Planning

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

class Workout(db.Model):
    """A Workout - a group of exercises"""

    __tablename__ = 'workouts'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

class WorkoutExercise(db.Model):
    """JOIN TABLE workout_exercise"""

    __tablename__ = 'workout_exercises'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

class Goal(db.Model):
    """JOIN exercise_metric and workout_exercise then add a goal_value"""

    __tablename__ = 'goal'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

###

class Performance(db.model):
    """JOIN record a workout's actual performance to the workout's goals"""

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