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

    bio = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    workouts = db.relationship('Workout', backref='owner', cascade='all, delete-orphan')
    
    @classmethod
    def signup(cls, username, email, bio, password):
        """Sign up user.
        Hashes password and adds user to db session.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            bio=bio,
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
        nullable=True
    )

    goals  = db.relationship('Goal', backref='on_workouts')
    # exercieses = db.relationship('Exercise', secondary='goals')

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

    # ADD COPY HERE

    # @classmethod
    # def copy(cls, workout_to_copy, owner_user_id):
    #     """
    #         Creates a copied workout.
    #         Sets author_user_id to original author.
    #         Copies the workout's exercises and goals.
    #     """

    #     workout = Workout(
    #         description=workout_to_copy.description,
    #         owner_user_id=owner_user_id,
    #         author_user_id=workout_to_copy.author_user_id
    #     )

    #     # Copy Exercises

    #     workout.exercises = workout_to_copy.exercises

    #     # for exercise in workout_to_copy.exercises:
    #     #     workout.exercises.append(exercise)

    #     # Copy Goals - Implement Future

    #     # for goals in workout_to_copy.goals:
    #     #     new_goal = Goal(
    #     #         exercise_metric_id=workout_to_copy.goals.exercise_metric_id,
    #     #         workout_exercise_id=workout.exercises,
    #     #         goal_value=workout_to_copy.goals.goal_value
    #     #     )

    #     # workout.exercises.goals = workout_to_copy.exercises.goals

    #     db.session.add(workout)

    #     return workout

    # ADD COPY HERE


class Goal(db.Model):
    """JOIN exercise_metric and workout_exercise then add a goal_value"""

    __tablename__ = 'goals'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    workout_id = db.Column(
        db.Integer,
        db.ForeignKey('workouts.id', ondelete="CASCADE")
    )

    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey('exercise.id', ondelete="CASCADE")
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
        nullable=True,
        default=NULL
    )

    goal_weight_lbs = db.Column(
        db.Integer,
        nullable=True,
        default=NULL
    )

    exercise = db.relationship('Exercise')
    performance = db.relationship('Performance', backref='goals')



# 



# Level 3 - User Performs Exercise and records Performacne

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

    performance_id = db.Column(
        db.Integer,
        db.ForeignKey('goals.id', ondelete="CASCADE")
    )

        goal_reps = db.Column(
        db.Integer,
        nullable=False
    )

    performance_sets = db.Column(
        db.Integer,
        nullable=False
    )

    performance_time_sec = db.Column(
        db.Integer,
        nullable=True,
        default=NULL
    )

    performance_weight_lbs = db.Column(
        db.Integer,
        nullable=True,
        default=NULL
    )

    # goals = db.relationship('Goal', backref = 'performance')

##############################################################################
def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)