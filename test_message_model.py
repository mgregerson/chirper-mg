import os
from unittest import TestCase
from flask_bcrypt import Bcrypt


from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

app.config['WTF_CSRF_ENABLED'] = False


db.drop_all()
db.create_all()

bcrypt = Bcrypt()
PASSWORD = bcrypt.generate_password_hash("password", rounds=5).decode("utf-8")

class MessageModelTestCase(TestCase):
    def setUp(self):
        Message.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
       
        m1 = Message(text='test message', user_id=self.u1_id)
        db.session.add(m1)
        db.session.commit()

        self.client = app.test_client()


    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have 1 message & no followers
        self.assertEqual(len(u1.messages), 1)
        self.assertEqual(len(u1.followers), 0)

    def test_is_message_instance(self):
        """Tests whether a new message is an instance of the Message class."""

        m2 = Message(text='testing', user_id=self.u1_id)

        db.session.add(m2)
        db.session.commit()

        self.assertIsInstance(m2, Message)
        self.assertNotIsInstance(m2, User)


    # def test_invalid_message_instance(self):
    #     """Tests that a an invalid message instance can not be created."""

        
    #     m3 = Message(text='test')
    #     print(m3, "TESTINGIAFS")
    #     db.session.add(m3)
    #     db.session.commit()
        

        
