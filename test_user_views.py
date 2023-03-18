"""User View tests."""

from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="test1user",
                                    email="test1@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_list_users(self):
        """Does page show listing of users?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            user = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD"
                        )
            db.session.add(user)
            db.session.commit()

            follows = Follows(user_following_id=self.testuser.id,
                              user_being_followed_id=user.id)
            db.session.add(follows)
            db.session.commit()

            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)

    def test_users_show(self):
        """Does page show user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test1user", html)

    def test_show_following(self):
        """Does page show users user is following?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            user = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD"
                        )
            db.session.add(user)
            db.session.commit()

            follows = Follows(user_following_id=self.testuser.id,
                              user_being_followed_id=user.id)
            db.session.add(follows)
            db.session.commit()

            resp = c.get(f"/users/{self.testuser.id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)

    def test_users_followers(self):
        """Does page show user's followers?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            user = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD"
                        )
            db.session.add(user)
            db.session.commit()

            follows = Follows(user_following_id=user.id,
                              user_being_followed_id=self.testuser.id)
            db.session.add(follows)
            db.session.commit()

            resp = c.get(f"/users/{self.testuser.id}/followers")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)

    def test_add_follow(self):
        """Does user get added to followers?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            user = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD"
                        )
            db.session.add(user)
            db.session.commit()

            follows = Follows(user_following_id=self.testuser.id,
                              user_being_followed_id=user.id)
            db.session.add(follows)
            db.session.commit()

            resp = c.post(f"/users/follow/{user.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)

    def test_profile(self):
        """Does page show user profile?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/profile")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test1user", html)

    def test_profile(self):
        """Does page update user profile?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(
                f"/users/profile", data={'username': 'updatedUsername', 'password': 'testuser'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('updatedUsername', html)

    def test_delete_user(self):
        """Does page delete user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(
                f"/users/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Join Warbler today.', html)
