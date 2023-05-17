"""
Performance model tests.

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
    """Test models for Performance."""

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

    def test_performance_model(self):
        """Set up a thirty-seventh goal - Does basic model work? - Do all attributes and defaults work?"""

        goal = Goal.query.get(1)

        performance_37 = Performance(

                goal_id = goal.id,
                performance_reps = 1,
                performance_sets = 2,
                performance_weight_lbs = 3,
                performance_time_sec = 4,
                performance_distance_miles = 5.1
                
            )
        
        db.session.add(performance_37)
        db.session.commit()

        self.assertEqual(performance_37.id, 37)
        self.assertEqual(performance_37.performance_reps, 1)
        self.assertEqual(performance_37.performance_sets, 2)
        self.assertEqual(performance_37.performance_weight_lbs, 3)
        self.assertEqual(performance_37.performance_time_sec, 4)
        self.assertEqual(performance_37.performance_distance_miles, 5.1)

        self.assertEqual(performance_37.date.year, datetime.datetime.utcnow().year)
        self.assertEqual(performance_37.date.month, datetime.datetime.utcnow().month)
        self.assertEqual(performance_37.date.day, datetime.datetime.utcnow().day)
        self.assertEqual(performance_37.date.hour, datetime.datetime.utcnow().hour)
        self.assertEqual(performance_37.date.minute, datetime.datetime.utcnow().minute)

        self.assertEqual(performance_37.last_edited_date.year, datetime.datetime.utcnow().year)
        self.assertEqual(performance_37.last_edited_date.month, datetime.datetime.utcnow().month)
        self.assertEqual(performance_37.last_edited_date.day, datetime.datetime.utcnow().day)
        self.assertEqual(performance_37.last_edited_date.hour, datetime.datetime.utcnow().hour)
        self.assertEqual(performance_37.last_edited_date.minute, datetime.datetime.utcnow().minute)



        # Ensure appropriate defaults are set on unspecified vlaues
        performance_unspec_1 = Performance.query.get(6)
        self.assertEqual(performance_unspec_1.id, 6)
        self.assertEqual(performance_unspec_1.goal_id, 1)
        self.assertEqual(performance_unspec_1.performance_reps, 0)
        self.assertEqual(performance_unspec_1.performance_sets, 0)
        self.assertEqual(performance_unspec_1.performance_time_sec, None)
        self.assertEqual(performance_unspec_1.performance_weight_lbs, None)
        self.assertEqual(performance_unspec_1.performance_distance_miles, None)

        self.assertEqual(performance_unspec_1.date.year, datetime.datetime.utcnow().year)
        self.assertEqual(performance_unspec_1.date.month, datetime.datetime.utcnow().month)
        self.assertEqual(performance_unspec_1.date.day, datetime.datetime.utcnow().day)
        self.assertEqual(performance_unspec_1.date.hour, datetime.datetime.utcnow().hour)
        self.assertEqual(performance_unspec_1.date.minute, datetime.datetime.utcnow().minute)

        self.assertEqual(performance_unspec_1.last_edited_date.year, datetime.datetime.utcnow().year)
        self.assertEqual(performance_unspec_1.last_edited_date.month, datetime.datetime.utcnow().month)
        self.assertEqual(performance_unspec_1.last_edited_date.day, datetime.datetime.utcnow().day)
        self.assertEqual(performance_unspec_1.last_edited_date.hour, datetime.datetime.utcnow().hour)
        self.assertEqual(performance_unspec_1.last_edited_date.minute, datetime.datetime.utcnow().minute)
        
        # Performance_37 should be in performance
        performance_records_all = Performance.query.order_by(Performance.id.asc()).all()
        self.assertIn(performance_37, performance_records_all)

        # Peformance_37 should be the 37th performance record
        self.assertEqual(performance_records_all.index(performance_37), 36)

        # Did performance id incrememt?
        self.assertEqual(performance_37.id, (performance_records_all[35].id +1))

    def test_goal_backref(self):
        """"""

        performance_records_all = Performance.query.order_by(Performance.id.asc()).all()
        goal = Goal.query.get(1)

        self.assertEqual(performance_records_all[0].goal.id, 1)
        self.assertEqual(performance_records_all[0].goal, goal)

    def test_serialize(self):
        """"""

        performance_1 = Performance.query.get(1)
        performance_6 = Performance.query.get(6)

        self.assertEqual(performance_1.serialize(),
                {
                    'id': performance_1.id,
                    'date': performance_1.date.strftime('%Y - %m - %d'),
                    'last_edited_date': performance_1.last_edited_date.strftime('%Y - %m - %d'),
                    'goal_id': performance_1.goal_id,
                    'performance_reps': performance_1.performance_reps,
                    'performance_sets': performance_1.performance_sets,
                    'performance_time_sec': performance_1.performance_time_sec,
                    'performance_weight_lbs': performance_1.performance_weight_lbs,
                    'performance_distance_miles': performance_1.performance_distance_miles
                }
            
            )

        self.assertEqual(performance_6.serialize(),
                {
                    'id': performance_6.id,
                    'date': performance_6.date.strftime('%Y - %m - %d'),
                    'last_edited_date': performance_6.last_edited_date.strftime('%Y - %m - %d'),
                    'goal_id': performance_6.goal_id,
                    'performance_reps': performance_6.performance_reps,
                    'performance_sets': performance_6.performance_sets,
                    'performance_time_sec': performance_6.performance_time_sec,
                    'performance_weight_lbs': performance_6.performance_weight_lbs,
                    'performance_distance_miles': performance_6.performance_distance_miles
                }
            
            )

        self.assertEqual(performance_1.serialize(),
                {
                    'id': 1,
                    'date': performance_1.date.strftime('%Y - %m - %d'),
                    'last_edited_date': performance_1.last_edited_date.strftime('%Y - %m - %d'),
                    'goal_id': 1,
                    'performance_reps': 1,
                    'performance_sets': 2,
                    'performance_time_sec': 4,
                    'performance_weight_lbs': 3,
                    'performance_distance_miles': 5.1
                }
            
            )

        self.assertEqual(performance_6.serialize(),
                {
                    'id': 6,
                    'date': performance_6.date.strftime('%Y - %m - %d'),
                    'last_edited_date': performance_6.last_edited_date.strftime('%Y - %m - %d'),
                    'goal_id': 1,
                    'performance_reps': 0,
                    'performance_sets': 0,
                    'performance_time_sec': None,
                    'performance_weight_lbs': None,
                    'performance_distance_miles': None
                }
            
            )