"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase

from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test model for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "email2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(u.id, u.id)

    def test_user_repr(self):
        """Does basic model work?"""

        u = User(
            email="test1@test.com",
            username="test1user",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User representaion should contain
        self.assertEqual(
            u.__repr__(), f"<User #{u.id}: {u.username}, {u.email}>")

    def test_is_following(self):
        """Does following attribute work?"""

        u1 = User(
            email="test1@test.com",
            username="test1user",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="test2user",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        u1.following.append(u2)
        db.session.commit()

        # Users relationship should follow u1 is following u2
        self.assertEqual(u1.is_following(u2), True)
        self.assertEqual(u2.is_followed_by(u1), True)

    def test_is_following_False(self):
        """Does following attribute fail?"""

        u1 = User(
            email="test1@test.com",
            username="test1user",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="test2user",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        db.session.commit()

        # Users relationship should follow u1 is not following u2
        self.assertEqual(u1.is_following(u2), False)
        self.assertEqual(u2.is_followed_by(u1), False)

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None)
        uid = 123789
        invalid.id = uid

        # Invalid signup attempt returns integrity error.
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_authentication(self):
        u = User.authenticate(self.u1.username, "password")

        # If valid, returns user
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)
        # If invalid returns false
        self.assertFalse(User.authenticate("badusername", "password"))
