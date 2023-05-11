"""
User model tests.

Run with:
python -m unittest test_user_views.py
"""

import os
from unittest import TestCase
from sqlalchemy import exc

import pdb
import datetime

from models import db, User, Exercise, Workout, Goal, Performance

os.environ['DATABASE_URL'] = "postgresql:///routine_test"

from app import app, CURR_USER_KEY

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):
    """Test models for User Views."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()

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

        self.user1_testID = user1.id
        self.user1 = user1
        self.user2 = user2
        self.exercise_1 = exercise_1
        self.workout_1 = workout_1
        self.workout_2 = workout_2
        self.workout_2_1 = workout_2_1
        self.workout_1_2 = workout_1_2

    def tearDown(self):
        """Clean up any fouled transaction. Remove data from database after test completed."""

        db.session.rollback()
        db.drop_all()
        db.create_all()

    def test_user_signup_get(self):
        """Can a user view sign up page"""

        with self.client as c:

            resp = c.get("/signup")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<button class="btn btn-primary my-4">Signup</button>', html)


    def test_user_signup_post_success(self):
        """Can a user sign up"""

        with self.client as c:

            resp = c.post("/signup", data={"username" : "test3user", "email" : "test3@test.com", "password" : "testuser3"})

            self.assertEqual(resp.status_code, 302)
            html = resp.get_data(as_text=True)
            self.assertIn('<a href="/">/</a>', html)
    

    def test_user_signup_post_success_redirect(self):
        """Is a user appropriately redirected if successful signup"""

        with self.client as c:

            resp = c.post("/signup", data={"username" : "test3user", "email" : "test3@test.com", "password" : "testuser3"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Let's do this test3user!", html)

    def test_user_signup_post_already_logged_in_redirect(self):
        """User redirected away from login page if logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            resp = c.get("/login", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('You are already logged in!', html)

    def test_user_signup_post_duplicate_username(self):
        """Is a user appropriately redirected if using duplicate username"""

        with self.client as c:

            resp = c.post("/signup", data={"username" : "test2user", "email" : "test3@test.com", "password" : "testuser3"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Username or email already taken', html)

    def test_user_signup_post_duplicate_email(self):
        """Is a user appropriately redirected if using duplicate email"""

        with self.client as c:

            resp = c.post("/signup", data={"username" : "test3user", "email" : "test2@test.com", "password" : "testuser3"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Username or email already taken', html)

    def test_user_login_get_success(self):
        """Can a user view sign up page"""

        with self.client as c:

            resp = c.get("/login")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<button class="btn btn-primary my-4">Login</button>', html)
    
    # def test_user_already_logged_in_get(self):
    #     """"""

    # def test_user_login_post_success(self):
    #     """"""
    # def test_user_login_post_success_redirect(self):
    #     """"""
    # def test_user_login_post_wrong_username(self):
    #     """"""
    # def test_user_login_post_wrong_password(self):
    #     """"""
    # def test_user_logout(self):
    #     """"""

    # def test_user_edit_get_success(self):
    #     """"""
    # def test_user_edit_get_not_user(self):
    #     """"""

    # def test_user_edit_post(self):
    #     """"""

    # def test_user_delete_post(self):
    #     """"""

    # def test_user_logged_out_root(self):
    #     """"""
    # def test_user_logged_in_root(self):
    #     """"""