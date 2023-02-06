"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


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

class UserViewTestCase(TestCase):

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
            
            user4 = User.signup("Testing4","testing4@gmail.com","password4", None)
            user4.id = 4
            
            
            db.session.add(user1)
            db.session.add(user2)
            db.session.add(user3)
            db.session.commit()
            
            self.user1 = User.query.get(1)
            self.user2 = User.query.get(2)
            self.user3 = User.query.get(3)
            self.user4 = User.query.get(4)
            
            follow1=Follows(user_being_followed_id = self.user1.id, user_following_id=self.user2.id)
            follow2=Follows(user_being_followed_id = self.user1.id, user_following_id=self.user3.id)
            follow3=Follows(user_being_followed_id = self.user2.id, user_following_id=self.user3.id)
            
            db.session.add(follow1)
            db.session.add(follow2)
            db.session.add(follow3)
            db.session.commit()
            
            

            self.client = app.test_client()
            
            
    def test_users_index(self):
        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@User1", str(resp.data))
            self.assertIn("@User2", str(resp.data))
            self.assertIn("@User3", str(resp.data))


    def test_users_search(self):
        with self.client as c:
            resp = c.get("/users?q=User")

            self.assertIn("@User1", str(resp.data))
            self.assertIn("@User2", str(resp.data))
            self.assertIn("@User3", str(resp.data))
            
            self.assertNotIn("@Testing4", str(resp.data))
            
    def test_user_show(self):
        with self.client as c:
            resp = c.get(f"/users/{self.user1.id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@User1", str(resp.data))
            
    def test_add_like(self):
        message = Message(id = 1, text="testing", user_id = self.user1.id)
        db.session.add(message)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            resp = c.post("/messages/1/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            likes = Likes.query.filter(Likes.message_id==1).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.user1.id)
        
    def test_remove_like(self):
        message = Message(id = 1, text="testing", user_id = self.user1.id)
        db.session.add(message)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            resp = c.post("/messages/1/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            resp = c.post("/messages/1/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            
            likes = Likes.query.filter(Likes.message_id==1).all()
            self.assertEqual(len(likes), 0)
            
            
    def test_user_show_followers(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
        resp = c.get(f"/users/{self.user1.id}/following", follow_redirects= True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("@user1", str(resp.data))
        self.assertIn("@user2", str(resp.data))
        self.assertIn("@user3", str(resp.data))
        self.assertNotIn("unauthorized", str(resp.data))   
        
        
    def test_user_show_following(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
        resp = c.get(f"/users/{self.user1.id}/following", follow_redirects= True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("@user1", str(resp.data))
        self.assertNotIn("@user2", str(resp.data))
        self.assertNotIn("@user3", str(resp.data))
        self.assertNotIn("unauthorized", str(resp.data))   
        
    def test_user_unauthorized_follow_page(self):
        with self.client as c:
            resp = c.get(f"/users/{self.user1.id}/following", follow_redirects= True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@user1", str(resp.data))
            self.assertIn("unauthorized", str(resp.data))       
        
        
    def test_user_unauthorized_followers_page(self):
        with self.client as c:
            resp = c.get(f"/users/{self.user1.id}/followers", follow_redirects= True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@user1", str(resp.data))
            self.assertIn("unauthorized", str(resp.data))
