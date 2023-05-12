"""
Stepthrough view tests.

Run with:
python -m unittest test_step_views.py
"""

import os
from unittest import TestCase
from sqlalchemy import exc

import pdb
import datetime

from models import db, User, Exercise, Workout, Goal, Performance

os.environ['DATABASE_URL'] = "postgresql:///routine_test"

from app import app, CURR_USER_KEY, GOAL_ID_CURRENT, GOAL_ID_PREVIOUS, PERFORMANCE_RECORDS_CAPTURED_IDS

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class StepViewsTestCase(TestCase):
    """Test models for User Views."""

    def setUp(self):
        """Create test client, add sample data."""

        # User.query.delete()

        self.client = app.test_client()

        # Signed up user
        user1 = User.signup(

            email="test1@test.com",
            username="test1user",
            password="HASHED_PASSWORD1"

        )

        # Declared user
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

            description="Workout Number 1",
            owner_user_id=1,
            author_user_id=1

        )

        workout_2 = Workout(

            description="Workout Number 2",
            owner_user_id=2,
            author_user_id=2

        )

        db.session.add_all([user1, user2, exercise_1, workout_1, workout_2])
        db.session.commit()

        workouts = Workout.query.all()

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

        )

        db.session.add_all([goal_1, goal_2])
        db.session.commit()

        performance_1 = Performance(

            goal_id =1,
            performance_reps=1,
            performance_sets=2,
            performance_weight_lbs=4

        )

        performance_2 = Performance(

            goal_id =1,

        )

        db.session.add_all([performance_1, performance_2])
        db.session.commit()

        self.user1_testID = user1.id
        self.user1 = user1
        self.user2 = user2
        self.exercise_1 = exercise_1
        self.workout_1 = workout_1
        self.workout_2 = workout_2
        self.test_goal = user1.workouts[0].goals[0]

    def tearDown(self):
        """Clean up any fouled transaction. Remove data from database after test completed."""

        db.session.rollback()
        db.drop_all()
        db.create_all()

    def test_start_workout_stepthrough(self):
        """Test /workout/id/step begins a step"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get("/workout/1/step", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("Create Record For: Workout Number 1 - Goal: Exercise 1", html)

    def test_start_workout_stepthrough_no_user(self):
        """Test /workout/id/step redirects if no user"""
        with self.client as c:

            resp = c.get("/workout/1/step", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Join Routine and Get In The Game!", html)
            self.assertIn("Access unauthorized.", html)

    def test_start_workout_stepthrough_wrong_user(self):
        """Test /workout/id/step redirects if wrong user"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            resp = c.get("/workout/1/step", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Let's do this test2user!", html)
            self.assertIn("Access unauthorized.", html)

    def test_step(self):
        """Test /step"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess[GOAL_ID_CURRENT] = self.test_goal.id
                sess[PERFORMANCE_RECORDS_CAPTURED_IDS] = []

            resp = c.get("/step")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("Create Record For: Workout Number 1 - Goal: Exercise 1", html)

    def test_step_2(self):
        """Test /step"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess[GOAL_ID_CURRENT] = 2
                sess[GOAL_ID_PREVIOUS] = 1
                sess[PERFORMANCE_RECORDS_CAPTURED_IDS] = [1]

            resp = c.get("/step")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("Create Record For: Workout Number 1 - Goal: Exercise 1", html)

    def test_step_edit_redirect(self):
        """Test /step"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess[GOAL_ID_CURRENT] = 1
                sess[PERFORMANCE_RECORDS_CAPTURED_IDS] = [1]

            resp = c.get("/step", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("Edit Record For: Workout Number 1 - Goal: Exercise 1", html)
    
    def test_step_redirect(self):
        """Test /step-edit redirects to /step when appropriate"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess[GOAL_ID_CURRENT] = 1
                sess[PERFORMANCE_RECORDS_CAPTURED_IDS] = []

            resp = c.get("/step-edit", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("Create Record For: Workout Number 1 - Goal: Exercise 1", html)
            
    def test_step_edit(self):
        """Test /step-edit redirects to /step when appropriate"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess[GOAL_ID_CURRENT] = 1
                sess[PERFORMANCE_RECORDS_CAPTURED_IDS] = [1]

            resp = c.get("/step-edit")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("Edit Record For: Workout Number 1 - Goal: Exercise 1", html)

    def test_step_wrong_user(self):
        """Test /step"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            resp = c.get("/step", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Let's do this test2user!", html)
            self.assertIn("You have not started a workout", html)

    def test_step_no_user(self):
        """Test /step"""
        with self.client as c:

            resp = c.get("/step", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Join Routine and Get In The Game!", html)
            self.assertIn("Access unauthorized.", html)

    def test_finish(self):
        """Test /finish"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess[GOAL_ID_CURRENT] = self.test_goal.id
                sess[PERFORMANCE_RECORDS_CAPTURED_IDS] = []

            resp = c.get("/finish", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("Great Job! Your workout: Workout Number 1 has been recorded.", html)

    def test_previous(self):
        """Test /previous"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess[GOAL_ID_CURRENT] = 2
                sess[GOAL_ID_PREVIOUS] = 1
                sess[PERFORMANCE_RECORDS_CAPTURED_IDS] = [1]

            resp = c.get("/previous", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("Edit Record For: Workout Number 1 - Goal: Exercise 1", html)