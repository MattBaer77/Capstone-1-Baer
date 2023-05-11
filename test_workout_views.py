"""
Workout view tests.

Run with:
python -m unittest test_workout_views.py
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

class WorkoutViewsTestCase(TestCase):
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

    def test_view_workouts(self):
        """Test /workouts route if user signed in"""

    def test_view_workouts_search(self):
        """Test /workouts route if user signed in + search params"""

    def test_view_workouts_no_user(self):
        """Test /workouts route if user not signed in"""

    
    def test_add_workout_get(self):
        """Test /workout/add route GET produces correct form""""

    def test_add_workout_get_no_user(self):
        """Test /workout/add route GET if user not signed in""""

    def test_add_workout_post(self):
        """Test /workout/add route POST""""


    def test_view_workout_get(self):
        """Test /workout/id route"""

    def test_view_workout_get_no_user(self):
        """Test /workout/id route if no user logged in"""


    def test_copy_workout_post(self):
        """Test /workout/id/copy route"""

    def test_copy_workout_post_no_user(self):
        """Test /workout/id/copy route if no user logged in"""

    
    def test_add_workout_goal_get(self):
        """Test /workout/id/goal-add route - produces correct form"""
    
    def test_add_workout_goal_get_no_user(self):
        """Test /workout/id/goal-add route - produces correct form if user not signed in"""

    def test_add_workout_goal_get_wrong_user(self):
        """Test /workout/id/goal-add route - produces correct form if correct user not signed in"""
    
    def test_add_workout_goal_post(self):
        """Test /workout/id/goal-add route"""
    
    def test_add_workout_goal_post_no_user(self):
        """Test /workout/id/goal-add route - if user not signed in"""

    def test_add_workout_goal_post_wrong_user(self):
        """Test /workout/id/goal-add route - if correct user not signed in"""

    
    def test_edit_workout_get(self):
        """Test /workout/id/edit route - produces correct form"""

    def test_edit_workout_get_no_user(self):
        """Test /workout/id/edit route - produces correct form if user not logged in"""

    def test_edit_workout_get_wrong_user(self):
        """Test /workout/id/edit route - produces correct form if correct user not logged in"""
    
    def test_edit_workout_post(self):
        """Test /workout/id/edit route"""

    def test_edit_workout_post_no_user(self):
        """Test /workout/id/edit route - if user not logged in"""

    def test_edit_workout_post_wrong_user(self):
        """Test /workout/id/edit route - if correct user not logged in"""

    
    def test_delete_workout_post(self):
        """Test /workout/id/delete"""

    def test_delete_workout_post_no_user(self):
        """Test /workout/id/delete - if user not logged in"""

    def test_delete_workout_post_wrong_user(self):
        """Test /workout/id/delete - if correct user not logged in"""


    def test_start_workout_stepthrough(self):
        """Test /workout/id/step begins a step"""

    def test_start_workout_stepthrough_no_user(self):
        """Test /workout/id/step redirects if no user"""

    def test_start_workout_stepthrough_wrong_user(self):
        """Test /workout/id/step redirects if wrong user"""

    
    # def test_user_signup_get(self):
    #     """Can a user view sign up page"""

    #     with self.client as c:

    #         resp = c.get("/signup")

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('<button class="btn btn-primary my-4">Signup</button>', html)

    # def test_user_signup_post_success(self):
    #     """Can a user sign up"""

    #     with self.client as c:

    #         resp = c.post("/signup", data={"username" : "test3user", "email" : "test3@test.com", "password" : "testuser3"})

    #         self.assertEqual(resp.status_code, 302)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('<a href="/">/</a>', html)
    

    # def test_user_signup_post_success_redirect(self):
    #     """Is a user appropriately redirected if successful signup"""

    #     with self.client as c:

    #         resp = c.post("/signup", data={"username" : "test3user", "email" : "test3@test.com", "password" : "testuser3"}, follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn("Let's do this test3user!", html)

    # def test_user_signup_post_already_logged_in_redirect(self):
    #     """User redirected away from login page if logged in"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user1.id
            
    #         resp = c.get("/login", follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('You are already logged in!', html)

    # def test_user_signup_post_duplicate_username(self):
    #     """Is a user appropriately redirected if using duplicate username"""

    #     with self.client as c:

    #         resp = c.post("/signup", data={"username" : "test2user", "email" : "test3@test.com", "password" : "testuser3"}, follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('Username or email already taken', html)

    # def test_user_signup_post_duplicate_email(self):
    #     """Is a user appropriately redirected if using duplicate email"""

    #     with self.client as c:

    #         resp = c.post("/signup", data={"username" : "test3user", "email" : "test2@test.com", "password" : "testuser3"}, follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('Username or email already taken', html)

    # def test_user_login_get_success(self):
    #     """Can a user view sign up page"""

    #     with self.client as c:

    #         resp = c.get("/login")

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('<button class="btn btn-primary my-4">Login</button>', html)
    
    # def test_user_already_logged_in_get(self):
    #     """User redirected away from login page if logged in"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user1.id
            
    #         resp = c.get("/login", follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('You are already logged in!', html)

    # def test_user_login_post_success(self):
    #     """Can a user log in"""

    #     with self.client as c:

    #         resp = c.post("/login", data={"username" : "test1user", "password" : "HASHED_PASSWORD1"})

    #         self.assertEqual(resp.status_code, 302)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('<a href="/">/</a>', html)

    # def test_user_login_post_success_redirect(self):
    #     """Can a user log in"""

    #     with self.client as c:

    #         resp = c.post("/login", data={"username" : "test1user", "password" : "HASHED_PASSWORD1"}, follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn("Let's do this test1user!", html)

    # def test_user_login_post_wrong_username(self):
    #     """Is a user redirected and informed if username is incorrect"""

    #     with self.client as c:

    #         resp = c.post("/login", data={"username" : "testuser", "password" : "HASHED_PASSWORD1"}, follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('Invalid credentials.', html)


    # def test_user_login_post_wrong_password(self):
    #     """Is a user redirected and informed if password is incorrect"""

    #     with self.client as c:

    #         resp = c.post("/login", data={"username" : "test1user", "password" : "HASHED_PASSWORD_WRONG"}, follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('Invalid credentials.', html)

    # def test_user_logout(self):
    #     """Can a user log out?"""

    #     with self.client as c:

    #         resp = c.post("/logout", follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('Goodbye!', html)

    # def test_user_edit_get_success(self):
    #     """Test GET for the user edit page"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user1.id

    #         resp = c.get("/user/edit")

    #         self.assertEqual(resp.status_code, 200)

    #         html = resp.get_data(as_text=True)

    #         self.assertIn('<h1 class="mb-4">Edit Your Details</h1>', html)

    # def test_user_edit_get_not_user(self):
    #     """Test GET for the user edit page if user is not logged in"""

    #     with self.client as c:
    #         resp = c.get("/user/edit")

    #         self.assertEqual(resp.status_code, 302)

    # def test_user_edit_get_not_user_redirect(self):
    #     """Test GET for the user edit page if user is not logged in - FOLLOW REDIRECT"""

    #     with self.client as c:
    #         resp = c.get("/user/edit", follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)

    #         html = resp.get_data(as_text=True)

    #         self.assertIn('Access unauthorized', html)

    # def test_user_edit_post(self):
    #     """Test POST for the user edit page"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user1.id

    #         resp = c.post("/user/edit", data={"username" : "Edited_test1user", "password" : "HASHED_PASSWORD1"}, follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)

    #         self.assertIn("Edited_test1user", html)

    # def test_user_delete_post(self):
    #     """Test POST for the user delete route"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user1.id

    #         resp = c.post("/user/delete", follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)

    #         self.assertIn("Join Routine and Get In The Game!", html)

    # def test_user_logged_in_root(self):
    #     """Test GET for the / route if logged in"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user1.id

    #         resp = c.get("/")
    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)

    #         self.assertIn("Let's do this test1user!", html)

    # def test_user_logged_out_root(self):
    #     """Test GET for the / route if logged out"""

    #     with self.client as c:

    #         resp = c.get("/")
    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)

    #         self.assertIn("Join Routine and Get In The Game!", html)