"""
User model tests.

Run with:
python -m unittest test_user_model.py
"""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Workout, Goal, Performance

os.environ['DATABASE_URL'] = "postgresql:///routine_test"

from app import app

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test models for User."""

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
            bio="Some bio text for test 2",
        )

        db.session.add_all([user1, user2])
        db.session.commit()

        self.user1_testID = user1.id
        self.user1 = user1
        self.user2 = user2

    def tearDown(self):
        """Clean up any fouled transaction. Remove data from database after test completed."""

        db.session.rollback()
        db.drop_all()
        db.create_all()

    def test_user_model(self):
        """Set up a third user - Does basic model work? - Do all attributes and defaults work?"""

        user3 = User(
            email="test3@test.com",
            username="test3user",
            password="HASHED_PASSWORD3",
            image_url="image3.png",
            bio="Some bio text for test 3",
        )

        db.session.add(user3)
        db.session.commit()

        # "user3" should be the second user
        users = User.query.order_by(User.id.asc()).all()
        self.assertEqual(len(users), 3)

        # self.user1.id should be 1 less than self.user2.id.id
        self.assertEqual(self.user1.id, (self.user2.id - 1))

        # self.user1.id should be 2 less than user3.id
        self.assertEqual(self.user1.id, (user3.id - 2))

        # user3 attributes should equal those set above
        self.assertEqual(user3.email, "test3@test.com")
        self.assertEqual(user3.username, "test3user")
        self.assertEqual(user3.password, "HASHED_PASSWORD3")
        self.assertEqual(user3.image_url, "image3.png")
        self.assertEqual(user3.bio, "Some bio text for test 3")

        # user[0] attributes should equal those set in setUp or the model defaults
        self.assertEqual(users[0].email, "test1@test.com")
        self.assertEqual(users[0].username, "test1user")
        self.assertEqual(users[0].password, "HASHED_PASSWORD1")
        self.assertEqual(users[0].image_url, "/static/images/noun-weights-49996.png")
        self.assertEqual(users[0].bio, None)

    def test_signup_success(self):
        """Test signup classmethod"""

        user3 = User.signup("test3user", "test3@test.com", "Hash_this_pass")

        db.session.commit()

        # user3 attributes should equal those set above
        self.assertEqual(user3.email, "test3@test.com")
        self.assertEqual(user3.username, "test3user")
        self.assertEqual(user3.image_url, "/static/images/noun-weights-49996.png")
        self.assertNotEqual(user3.password, "Hash_this_pass")
        self.assertTrue("$2b$" in user3.password)

    def test_signup_username_fail_duplicate(self):
        """Test signup classmethod"""

        with self.assertRaises(exc.IntegrityError) as context:
            user2 = User.signup("test2user", "test3@test.com", "Hash_this_pass")
            db.session.commit()

    def test_signup_email_fail_duplicate(self):
        """Test signup classmethod"""

        with self.assertRaises(exc.IntegrityError) as context:
            user2 = User.signup("test3user", "test2@test.com", "Hash_this_pass")
            db.session.commit()

    def test_signup_username_fail_None(self):
        """Test signup classmethod"""

        with self.assertRaises(exc.IntegrityError) as context:
            user2 = User.signup(None, "test3@test.com", "Hash_this_pass")
            db.session.commit()

    def test_signup_email_fail_None(self):
        """Test signup classmethod"""

        with self.assertRaises(exc.IntegrityError) as context:
            user2 = User.signup("test3user", None, "Hash_this_pass")
            db.session.commit()

    def test_signup_password_fail_None(self):
        """Test signup classmethod"""

        with self.assertRaises(ValueError) as context:
            user2 = User.signup("test3user", "test3@test.com", None)
            db.session.commit()

        with self.assertRaises(ValueError) as context:
            user2 = User.signup("test3user", "test3@test.com", "")
            db.session.commit()

    def test_authenticate_success(self):
        """Test authenticate classmethod"""

        user3 = User.signup("test3user", "test3@test.com", "Hash_this_pass")
        db.session.commit()

        userCheck = User.authenticate("test3user", "Hash_this_pass")

        self.assertIsNotNone(userCheck)
        self.assertEqual(userCheck.id, user3.id)
        self.assertEqual(userCheck.username, user3.username)
        self.assertEqual(userCheck.username, "test3user")

    def test_authenticate_fail_username(self):
        """Test authenticate classmethod"""

        user3 = User.signup("test3user", "test3@test.com", "Hash_this_pass")
        db.session.commit()

        userCheck = User.authenticate("Incorrect", "Hash_this_pass")

        self.assertFalse(userCheck)

    def test_authenticate_fail_password(self):
        """Test authenticate classmethod"""

        user3 = User.signup("test3user", "test3@test.com", "Hash_this_pass")
        db.session.commit()

        userCheck = User.authenticate("test3user", "Incorrect")

        self.assertFalse(userCheck)

    ###

    # TEST USER.WORKOUTS
    def test_user_workouts(self):
        """Test workouts relationship"""

        workout_1 = Workout(

            description="Workout Number One",
            owner_user_id=1,
            author_user_id=1

        )

        db.session.add(workout_1)
        db.session.commit()

        self.assertEqual(len(self.user1.workouts), 1)
        self.assertEqual(len(self.user2.workouts), 0)

        self.assertEqual(self.user1.workouts, [workout_1])
        self.assertEqual(self.user2.workouts, [])

        self.assertEqual(self.user1.workouts[0], workout_1)

        self.assertEqual(self.user1.workouts[0].description, "Workout Number One")
        self.assertEqual(self.user1.workouts[0].owner_user_id, 1)
        self.assertEqual(self.user1.workouts[0].author_user_id, 1)

    ###

    # TEST WORKOUTS AUTHORED
    def test_user_workouts_authored(self):
        """Test workouts relationship"""

        workout_1 = Workout(

            description="Workout Number One",
            owner_user_id=1,
            author_user_id=2

        )

        db.session.add(workout_1)
        db.session.commit()

        self.assertEqual(len(self.user1.workouts_authored), 0)
        self.assertEqual(len(self.user2.workouts_authored), 1)

        self.assertEqual(self.user1.workouts_authored, [])
        self.assertEqual(self.user2.workouts_authored, [workout_1])

        self.assertEqual(self.user2.workouts_authored[0], workout_1)

        self.assertEqual(self.user2.workouts_authored[0].description, "Workout Number One")
        self.assertEqual(self.user2.workouts_authored[0].owner_user_id, 1)
        self.assertEqual(self.user2.workouts_authored[0].author_user_id, 2)