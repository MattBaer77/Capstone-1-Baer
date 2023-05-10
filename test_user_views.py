"""
User model tests.

Run with:
python -m unittest test_performance_model.py
"""

import os
from unittest import TestCase
from sqlalchemy import exc

import pdb
import datetime

from models import db, User, Exercise, Workout, Goal, Performance

os.environ['DATABASE_URL'] = "postgresql:///routine_test"

from app import app

db.drop_all()
db.create_all()

class PerformanceModelTestCase(TestCase):
    """Test models for Workout."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()

        self.client = app.test_client()

        user1 = User(

            email="test1@test.com",
            username="test1user",
            password="HASHED_PASSWORD1"

        )

        user2 = User(

            email="test2@test.com",
            username="test2user",
            password="HASHED_PASSWORD2",
            image_url="image2.png",
            bio="Some bio text for test 2"

        )

        exercise_1 = Exercise(
            name="Exercise 1",
            description="The First Exercise"
        )

        workout_1 = Workout(

            description="Workout Number One",
            owner_user_id=1,
            author_user_id=1

        )

        workout_2 = Workout(

            description="Workout Number Two",
            owner_user_id=2,
            author_user_id=2

        )

        workout_2_1 = Workout(

            description="Workout Number 2-1",
            owner_user_id=2,
            author_user_id=1

        )

        workout_1_2 = Workout(

            description="Workout Number 1-2",
            owner_user_id=1,
            author_user_id=2

        )

        db.session.add_all([user1, user2, exercise_1, workout_1, workout_2, workout_2_1, workout_1_2])
        db.session.commit()

        goal_1 = Goal(

            workout_id = workout_1.id,
            exercise_id = exercise_1.id,
            goal_reps = 1,
            goal_sets = 2,
            goal_time_sec = 3,
            goal_weight_lbs = 4,
            goal_distance_miles = 5.1

        )

        goal_2 = Goal(

            workout_id = workout_1.id,
            exercise_id = exercise_1.id,
            goal_reps = 1,
            goal_sets = 2,
            goal_time_sec = 3,
            goal_weight_lbs = 4

        )

        goal_3 = Goal(

            workout_id = workout_1.id,
            exercise_id = exercise_1.id,
            goal_reps = 1,
            goal_sets = 2,
            goal_time_sec = 3

        )

        goal_4 = Goal(

            workout_id = workout_1.id,
            exercise_id = exercise_1.id,
            goal_reps = 1,
            goal_sets = 2

        )

        goal_5 = Goal(

            workout_id = workout_1.id,
            exercise_id = exercise_1.id,
            goal_reps = 1

        )

        goal_6 = Goal(

            workout_id = workout_1.id,
            exercise_id = exercise_1.id

        )

        db.session.add_all([goal_1, goal_2, goal_3, goal_4, goal_5, goal_6])
        db.session.commit()

        goals = Goal.query.order_by(Goal.id.asc()).all()

        for goal in goals:

            performance_1 = Performance(

                goal_id = goal.id,
                performance_reps = 1,
                performance_sets = 2,
                performance_weight_lbs = 3,
                performance_time_sec = 4,
                performance_distance_miles = 5.1
            )

            performance_2 = Performance(

                goal_id = goal.id,
                performance_reps = 1,
                performance_sets = 2,
                performance_weight_lbs = 3,
                performance_time_sec = 4
                
            )

            performance_3 = Performance(

                goal_id = goal.id,
                performance_reps = 1,
                performance_sets = 2,
                performance_weight_lbs = 3

            )

            performance_4 = Performance(

                goal_id = goal.id,
                performance_reps = 1,
                performance_sets = 2

            )

            performance_5 = Performance(

                goal_id = goal.id,
                performance_reps = 1

            )

            performance_6 = Performance(

                goal_id = goal.id

            )

            db.session.add_all([performance_1, performance_2, performance_3, performance_4, performance_5, performance_6])
            db.session.commit()

        self.user1_testID = user1.id
        self.user1 = user1
        self.user2 = user2

    def tearDown(self):
        """Clean up any fouled transaction. Remove data from database after test completed."""

        db.session.rollback()
        db.drop_all()
        db.create_all()