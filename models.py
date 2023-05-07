"""SQLAlchemy models for Routine."""

import copy

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

    image_url = db.Column(
        db.Text,
        default="/static/images/noun-weights-49996.png",
    )

    bio = db.Column(
        db.Text,
        nullable=True
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    workouts = db.relationship('Workout', foreign_keys="[Workout.owner_user_id]", backref='owner', cascade='all, delete-orphan')
    workouts_authored = db.relationship('Workout', foreign_keys="[Workout.author_user_id]", backref='author')
    
    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.
        Hashes password and adds user to db session.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        Search for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


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
        db.ForeignKey('users.id'),
        nullable=True
    )

    goals  = db.relationship('Goal', backref='workout', cascade='all, delete-orphan')

    def get_author(self):
        """Returns the author based on the author_user_id"""
        author = User.query.get(self.author_user_id)
        return author

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
            Copies the workout's goals.
        """

        copied_workout = Workout(
            description=workout_to_copy.description,
            owner_user_id=owner_user_id,
            author_user_id=workout_to_copy.author_user_id
        )

        # Copy Goals

        db.session.add(copied_workout)
        db.session.commit()

        for goal in workout_to_copy.goals:
            copy = Goal(
                workout_id=copied_workout.id,
                exercise_id=goal.exercise_id,
                goal_reps=goal.goal_reps,
                goal_sets=goal.goal_sets,
                goal_weight_lbs=goal.goal_weight_lbs,
                goal_time_sec=goal.goal_time_sec
            )

            copied_workout.goals.append(copy)

        db.session.commit()
        return copied_workout


class Goal(db.Model):
    """JOIN exercise_metric and workout_exercise then add a goal_value"""

    __tablename__ = 'goals'

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
        db.ForeignKey('exercises.id', ondelete="CASCADE")
    )

    goal_reps = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    goal_sets = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    goal_time_sec = db.Column(
        db.Integer,
        nullable=True
    )

    goal_weight_lbs = db.Column(
        db.Integer,
        nullable=True
    )

    exercise = db.relationship('Exercise')
    performance = db.relationship('Performance', backref='goal', cascade='all, delete-orphan')

    def serialize(self):
        """Returns a dict representation of goal."""
        return {
            'id': self.id,
            'workout_id': self.workout_id,
            'exercise_id': self.exercise_id,
            'goal_reps': self.goal_reps,
            'goal_sets': self.goal_sets,
            'goal_time_sec': self.goal_time_sec,
            'goal_weight_lbs': self.goal_weight_lbs
        }
 


###



# Level 3 - User Performs Exercise and records Performance

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

    performance_reps = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    performance_sets = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    performance_time_sec = db.Column(
        db.Integer,
        nullable=True
    )

    performance_weight_lbs = db.Column(
        db.Integer,
        nullable=True
    )

    def serialize(self):
        """Returns a dict representation of performance record."""
        return {
            'id': self.id,
            'date': self.date,
            'last_edited_date': self.last_edited_date,
            'goal_id': self.goal_id,
            'performance_reps': self.performance_reps,
            'performance_sets': self.performance_sets,
            'performance_time_sec': self.performance_time_sec,
            'performance_weight_lbs': self.performance_weight_lbs
        }



##############################################################################
def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)