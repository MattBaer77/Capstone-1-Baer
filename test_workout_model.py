"""
User model tests.

Run with:
python -m unittest test_workout_model.py
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

class WorkoutModelTestCase(TestCase):
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

        db.session.add(goal_1)
        db.session.commit()

        self.user1_testID = user1.id
        self.user1 = user1
        self.user2 = user2

    def tearDown(self):
        """Clean up any fouled transaction. Remove data from database after test completed."""

        db.session.rollback()
        db.drop_all()
        db.create_all()

    def test_workout_model(self):
        """Set up a fifth workout - Does basic model work? - Do all attributes and defaults work?"""

        workout_3 = Workout(

            description="Workout 3",
            owner_user_id="1",
            author_user_id="1"

        )

        db.session.add(workout_3)
        db.session.commit()

        workouts = Workout.query.order_by(Workout.id.asc()).all()

        self.assertEqual(workout_3.id, 5)
        self.assertEqual(workout_3.owner_user_id, 1)
        self.assertEqual(workout_3.author_user_id, 1)

        # Workout 3 should be in workouts
        self.assertIn(workout_3, workouts)

        # Workout 3 should be the 5th workout
        self.assertEqual(workouts.index(workout_3), 4)
        
        # Did workout index increment?
        self.assertEqual(workout_3.id, (workouts[3].id + 1))

    def test_workout_get_author(self):

        user1 = User.query.get(1)
        user2 = User.query.get(2)
        workout_1 = Workout.query.get(1)
        workout_2_1 = Workout.query.get(3)

        self.assertEqual(workout_1.get_author(), user1)
        self.assertEqual(workout_2_1.get_author(), user1)

    def test_workout_create(self):
        """Create a fifth workout - Does basic model work? - Do all attributes and defaults work?"""

        workout_3 = Workout.create(

            description="Workout 3",
            owner_user_id="1",

        )

        db.session.add(workout_3)
        db.session.commit()

        workouts = Workout.query.order_by(Workout.id.asc()).all()

        self.assertEqual(workout_3.id, 5)
        self.assertEqual(workout_3.owner_user_id, 1)
        self.assertEqual(workout_3.author_user_id, 1)

        # Workout 3 should be in workouts
        self.assertIn(workout_3, workouts)

        # Workout 3 should be the 5th workout
        self.assertEqual(workouts.index(workout_3), 4)
        
        # Did workout index increment?
        self.assertEqual(workout_3.id, (workouts[3].id + 1))

    def test_workout_copy(self):
        """Create a fifth workout - Does basic model work? - Do all attributes and defaults work?"""

        workout_1 = Workout.query.get(1)

        workout_3 = Workout.copy(

            workout_1,
            2

        )

        db.session.add(workout_3)
        db.session.commit()

        workouts = Workout.query.order_by(Workout.id.asc()).all()

        self.assertEqual(workout_3.id, 5)
        self.assertEqual(workout_3.owner_user_id, 2)
        self.assertEqual(workout_3.author_user_id, 1)

        # Workout 3 should be in workouts
        self.assertIn(workout_3, workouts)

        # Workout 3 should be the 5th workout
        self.assertEqual(workouts.index(workout_3), 4)
        
        # Did workout id increment?
        self.assertEqual(workout_3.id, (workouts[3].id + 1))

    def test_owner_and_author_backref(self):

        user1 = User.query.get(1)
        user2 = User.query.get(2)
        workout_1 = Workout.query.get(1)
        workout_2_1 = Workout.query.get(3)

        self.assertEqual(workout_1.owner, user1)
        self.assertEqual(workout_1.author, user1)

        self.assertEqual(workout_2_1.owner, user2)
        self.assertEqual(workout_2_1.author, user1)

    def test_goal_relationship(self):

        workout_1 = Workout.query.get(1)
        workout_2 = Workout.query.get(2)

        goal = Goal.query.get(1)

        self.assertEqual(workout_1.goals, [goal])
        self.assertEqual(workout_1.goals[0], goal)
        self.assertEqual(workout_2.goals, [])