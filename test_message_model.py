"""Message Model tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
with app.app_context():
    db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class MessageModelTestCase(TestCase):
    
    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        
        db.drop_all()
        db.create_all()
        
        user1 = User.signup("User1","user1@gmail.com","password1", None)
        user1.id = 1
        
        user2 = User.signup("User1","user1@gmail.com","password1", None)
        user2.id = 2
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        self.user1 = User.query.get(1)
        self.user1 = User.query.get(2)

        self.client = app.test_client()
        
        
    def test_message_model(self):
        message = Message(text = "Testing" , user_id = self.user1.id)
        db.session.add(message)
        db.session.commit()
        self.assertEqual(len(self.user1.messages), 1)
        self.assertEqual(self.user1.messages[0].text, "Testing")
        
        
    def test_message_likes(self):
        message1 = Message(text = "Test1" , user_id = self.user1.id)
        message2 = Message(text = "Test2" , user_id = self.user1.id)
        db.session.add(message1)
        db.session.add(message2)
        db.session.commit()
        
        self.user2.likes.append(message1)
        db.session.commit()
        
        likes = Likes.query.filter(Likes.user_id == self.user2.id).all()
        like_count = len(likes)
        self.assertEqual(like_count, 1)
        self.assertEqual(likes[0].message_id, message1.id)