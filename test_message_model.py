"""User model tests."""

from app import app
import os
from unittest import TestCase

from sqlalchemy import exc
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 94566
        u = User.signup("testing", "testing@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does message model work?"""
        m = Message(text='testMesssage', user_id=self.uid)

        db.session.add(m)
        db.session.commit()

        self.assertIsNotNone(m.id)
        self.assertEqual(len(self.u.messages), 1)

    def test_user_likes(self):
        """Test likes of user on messages"""

        m1 = Message(text='testMesssage1', user_id=self.uid)
        m2 = Message(text='testMesssage2', user_id=self.uid)

        db.session.add_all([m1, m2])
        db.session.commit()

        self.u.likes.append(m1)
        self.u.likes.append(m2)

        self.assertEqual(len(self.u.likes), 2)
