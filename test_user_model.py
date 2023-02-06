"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


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

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
with app.app_context():
    db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        
        db.drop_all()
        db.create_all()
        
        user1 = User.signup("User1","user1@gmail.com","password1", None)
        user1.id = 1
        
        user2 = User.signup("User2","user2@gmail.com","password2", None)
        user2.id = 2
        
        user3 = User.signup("User3","user3@gmail.com","password3", None)
        user3.id = 3
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.commit()
        
        self.user1 = User.query.get(1)
        self.user2 = User.query.get(2)
        self.user3 = User.query.get(3)

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

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
        
    def test_user_follow(self):
        self.user1.following.append(self.user2)
        self.user3.following.append(self.user2)
        db.session.commit()
        
        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user1.followers), 0)
        
        self.assertEqual(len(self.user3.following), 1)
        self.assertEqual(len(self.user3.followers), 0)
        
        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 2)
        
        
    def test_user_is_following(self):
        self.user2.following.append(self.user1)
        self.user2.following.append(self.user3)
        db.session.commit()
        
        self.assertTrue(self.user2.is_following(self.user1))
        self.assertFalse(self.user2.is_following(self.user3))    
        
    def test_user_is_followed_by(self):
        self.user1.following.append(self.user2)
        self.user3.following.append(self.user2)
        db.session.commit()
        
        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user2.is_followed_by(self.user3))
        
        
    def test_user_create(self):
        testuser = User.signup("Test1","Test1@gmail.com","testword1", None)
        testuser.id = 4
        db.session.commit()
        testuser = User.query.get(4)
        self.assertEqual(testuser.username, "Test1")
        self.assertEqual(testuser.email, "Test1@gmail.com")
        #Should be encrypted
        self.assertNotEqual(testuser.password, "testword1")
        
        
    def test_user_username_fail(self):
        testuser = User.signup(None ,"Test1@gmail.com","testword1", None)
        testuser.id = 4
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
            
            
    def test_user_email_fail(self):
        testuser = User.signup("Test1" ,None,"testword1", None)
        testuser.id = 4
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
            
            
        
    def test_user_authenticate(self):
        user = User.authenticate(self.user1.username, "password1")
        self.assertEqual(user.username, self.user1.username)
        
        user = User.authenticate(self.user2.username, "password1")
        self.assertFalse(user)
        
        user = User.authenticate(self.user2.username, None)
        self.assertFalse(user)