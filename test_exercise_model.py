"""
Exercise model tests.

Run with:
python -m unittest test_exercise_model.py
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

class ExerciseModelTestCase(TestCase):
    """Test models for Exercise."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()

        self.client = app.test_client()

        exercise_1 = Exercise(
            name="Exercise 1",
            description="The First Exercise"
        )

        exercise_2 = Exercise(
            name="Exercise 2",
            description="The Second Exercise"
        )

        db.session.add_all([exercise_1, exercise_2])
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction. Remove data from database after test completed."""

        db.session.rollback()
        db.drop_all()
        db.create_all()

    def test_exercise_model(self):
        """Set up a third goal - Does basic model work? - Do all attributes and defaults work?"""

        exercise_3 = Exercise(
            name="Exercise 3",
            description="The Third Exercise"
        )

        db.session.add(exercise_3)
        db.session.commit()

        self.assertEqual(exercise_3.id, 3)
        self.assertEqual(exercise_3.name, "Exercise 3")
        self.assertEqual(exercise_3.description, "The Third Exercise")

        exercises = Exercise.query.order_by(Exercise.id.asc()).all()

        # Exercise 3 should be in exercises
        self.assertIn(exercise_3, exercises)
        # Exercise 3 should be the 3rd exercise
        self.assertEqual(exercise_3, exercises[2])
        # Did Exercise id increment
        self.assertEqual(exercise_3.id, (exercises[1].id + 1))