"""
User model tests.

Run with:
python -m unittest test_goal_model.py
"""

import os
from unittest import TestCase
from sqlalchemy import exc

import pdb

from models import db, User, Exercise, Workout, Goal, Performance

os.environ['DATABASE_URL'] = "postgresql:///routine_test"

from app import app

db.drop_all()
db.create_all()

class GoalModelTestCase(TestCase):
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

        performance_1 = Performance(

            goal_id = goal_1.id,
            performance_reps = 1,
            performance_sets = 2,
            performance_weight_lbs = 3,
            performance_time_sec = 4,
            performance_distance_miles = 5.1
        )

        db.session.add(performance_1)
        db.session.commit

        self.user1_testID = user1.id
        self.user1 = user1
        self.user2 = user2

    def tearDown(self):
        """Clean up any fouled transaction. Remove data from database after test completed."""

        db.session.rollback()
        db.drop_all()
        db.create_all()

    def test_goal_model(self):
        """Set up a seventh goal - Does basic model work? - Do all attributes and defaults work?"""

        workout_1 = Workout.query.get(1)
        exercise_1 = Exercise.query.get(1)

        goal_7 = Goal(

            workout_id = workout_1.id,
            exercise_id = exercise_1.id,
            goal_reps = 1,
            goal_sets = 2,
            goal_time_sec = 3,
            goal_weight_lbs = 4,
            goal_distance_miles = 5.1

        )

        db.session.add(goal_7)
        db.session.commit()

        goals = Goal.query.order_by(Goal.id.asc()).all()

        self.assertEqual(goal_7.id, 7)
        self.assertEqual(goal_7.exercise_id, 1)
        self.assertEqual(goal_7.goal_reps, 1)
        self.assertEqual(goal_7.goal_sets, 2)
        self.assertEqual(goal_7.goal_time_sec, 3)
        self.assertEqual(goal_7.goal_weight_lbs, 4)
        self.assertEqual(goal_7.goal_distance_miles, 5.1)

        # Ensure appropriate defaults are set on unspecified values
        self.assertEqual(goals[5].id, 6)
        self.assertEqual(goals[5].exercise_id, 1)
        self.assertEqual(goals[5].goal_sets, 1)
        self.assertEqual(goals[5].goal_reps, 1)
        self.assertEqual(goals[5].goal_time_sec, None)
        self.assertEqual(goals[5].goal_weight_lbs, None)
        self.assertEqual(goals[5].goal_distance_miles, None)

        # Goal 7 should be in goals
        self.assertIn(goal_7, goals)

        # Goal 7 should be the 7th goal
        self.assertEqual(goals.index(goal_7), 6)

        # Did goal id increment?
        self.assertEqual(goal_7.id, (goals[5].id + 1))

    def test_workout_backref(self):
        """"""

        goals = Goal.query.order_by(Goal.id.asc()).all()
        workout = Workout.query.get(1)

        self.assertEqual(goals[0].workout.id, 1)
        self.assertEqual(goals[0].workout, workout)

    def test_exercise_relationship(self):
        """"""

        goals = Goal.query.order_by(Goal.id.asc()).all()
        exercise = Exercise.query.get(1)

        self.assertEqual(goals[0].exercise.id, 1)
        self.assertEqual(goals[0].exercise, exercise)

    def test_performance_relationship(self):
        """"""

        goal = Goal.query.get(1)
        performance = Performance.query.get(1)

        self.assertEqual(len(goal.performance), 1)
        self.assertEqual(goal.performance, [performance])
        self.assertEqual(goal.performance[0].id, performance.id)

    def test_serialize(self):
        """"""

        goal_1 = Goal.query.get(1)
        goal_6 = Goal.query.get(6)

        self.assertEqual(goal_1.serialize(),
                {
                    'id': goal_1.id,
                    'workout_id': goal_1.workout_id,
                    'exercise_id': goal_1.exercise_id,
                    'goal_reps': goal_1.goal_reps,
                    'goal_sets': goal_1.goal_sets,
                    'goal_time_sec': goal_1.goal_time_sec,
                    'goal_weight_lbs': goal_1.goal_weight_lbs,
                    'goal_distance_miles': goal_1.goal_distance_miles
                }
            
            )

        self.assertEqual(goal_6.serialize(),
                {
                    'id': goal_6.id,
                    'workout_id': goal_6.workout_id,
                    'exercise_id': goal_6.exercise_id,
                    'goal_reps': goal_6.goal_reps,
                    'goal_sets': goal_6.goal_sets,
                    'goal_time_sec': goal_6.goal_time_sec,
                    'goal_weight_lbs': goal_6.goal_weight_lbs,
                    'goal_distance_miles': goal_6.goal_distance_miles
                }
            
            )

        self.assertEqual(goal_1.serialize(),
                {
                    'id': 1,
                    'workout_id': 1,
                    'exercise_id': 1,
                    'goal_reps': 1,
                    'goal_sets': 2,
                    'goal_time_sec': 3,
                    'goal_weight_lbs': 4,
                    'goal_distance_miles': 5.1
                }
            
            )

        self.assertEqual(goal_6.serialize(),
                {
                    'id': 6,
                    'workout_id': 1,
                    'exercise_id': 1,
                    'goal_reps': 1,
                    'goal_sets': 1,
                    'goal_time_sec': None,
                    'goal_weight_lbs': None,
                    'goal_distance_miles': None
                }
            
            )