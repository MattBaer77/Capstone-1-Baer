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

    name = db.Column(
        db.Text,
        default="No Name"
        # nullable=False # Add this in later if neccessary.
    )

    description = db.Column(
        db.Text,
        default="No Description"
        # nullable=False # Add this in later if neccessary.
    )
 
    metrics = db.relationship('Metric', secondary='exercise_metrics', backref='exercises')
    
class Metric(db.Model):
    """Metrics to measure exercise performance"""

    __tablename__ = 'metrics'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    kind = db.Column(
        db.Text,
        nullable=False
    )

    units = db.Column(
        db.Text,
        nullable=False
    )

class ExerciseMetric(db.Model):
    """JOIN TABLE exercise_metrics"""

    __tablename__ = 'exercise_metrics'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey('exercises.id', ondelete='CASCADE'),
        nullable=False
    )

    metric_id = db.Column(
        db.Integer,
        db.ForeignKey('metrics.id', ondelete='CASCADE'),
        nullable=False
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

    workouts = db.relationship('Workout', backref='owner', cascade='all, delete-orphan')
    # workouts_authored = db.relationship('Workout', backref='author')



class Workout(db.Model):
    """A Workout - a group of exercises"""

    __tablename__ = 'workouts'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    description = db.Column(
        db.Text,
        default="No Description"
    )

    owner_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False
    )

    author_user_id = db.Column(
        db.Integer,
        nullable=True
    )

    exercises = db.relationship('Exercise', secondary='workout_exercises', backref='on_workouts')
    goals = db.relationship('Goal', secondary='workout_exercises', backref='from_workouts')
    
    # # REVIEW THIS
    # author = db.relationship('User', backref='workouts_authored')
    # # REVIEW THIS

    @classmethod
    def create(cls, description, owner_user_id):
        """
            Creates a new workout.
            Sets author_user_id to creator.
        """

        workout = Workout(
            description=description,
            owner_user_id=owner_user_id,
            author_user_id=owner_user_id
        )

        db.session.add(workout)
        return workout

    @classmethod
    def copy(cls, workout_to_copy, owner_user_id):
        """
            Creates a copied workout.
            Sets author_user_id to original author.
        """

        workout = Workout(
            description=workout_to_copy.description,
            owner_user_id=owner_user_id,
            author_user_id=workout_to_copy.author_user_id
        )

        # copy exercises
        # copy goals

        db.session.add(workout)
        return workout

class WorkoutExercise(db.Model):
    """JOIN TABLE workout_exercise"""

    __tablename__ = 'workout_exercises'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    workout_id = db.Column(
        db.Integer,
        db.ForeignKey('workouts.id', ondelete="CASCADE"),
        nullable=False
    )

    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey('exercises.id', ondelete="CASCADE"),
        nullable=False
    )

class Goal(db.Model):
    """JOIN exercise_metric and workout_exercise then add a goal_value"""

    __tablename__ = 'goals'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    exercise_metric_id = db.Column(
        db.Integer,
        db.ForeignKey('exercise_metrics.id', ondelete="CASCADE")
    )

    workout_exercise_id = db.Column(
        db.Integer,
        db.ForeignKey('workout_exercises.id', ondelete="CASCADE")
    )

    goal_value = db.Column(
        db.Integer,
        nullable=False
    )

    exercises = db.relationship('Exercise', secondary = 'exercise_metrics', backref = 'goals')

class Performance(db.Model):
    """JOIN record a workout's actual performance to the workout's goals"""

    __tablename__ = 'performance'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )

    last_edited_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )

    goal_id = db.Column(
        db.Integer,
        db.ForeignKey('goals.id', ondelete="CASCADE")
    )

    performance = db.Column(
        db.Integer,
        nullable=False
    )

    goals = db.relationship('Goal', backref = 'performance')

##############################################################################
def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)