
import unittest
from app import app, SessionLocal
from data_model import User
from werkzeug.security import generate_password_hash

class VMTAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Create a test user
        session = SessionLocal()
        test_user = User(username='testuser', password=generate_password_hash('testpass', method='pbkdf2:sha256'), role='mentee')
        session.add(test_user)
        session.commit()
        session.close()

    def tearDown(self):
        # Clean up the database
        session = SessionLocal()
        session.query(User).delete()
        session.commit()
        session.close()

    def test_register_user(self):
        response = self.app.post('/register', json={
            'username': 'newuser',
            'password': 'newpass',
            'role': 'mentor'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'User registered successfully', response.data)

    def test_login_user(self):
        response = self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'token', response.data)

if __name__ == '__main__':
    unittest.main()

    def test_view_profile(self):
        # Log in to get a token
        response = self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        token = response.get_json()['token']

        # View profile
        response = self.app.get('/profile', headers={'x-access-token': token})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'testuser', response.data)

    def test_update_profile(self):
        # Log in to get a token
        response = self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        token = response.get_json()['token']

        # Update profile
        response = self.app.put('/profile', headers={'x-access-token': token}, json={
            'linkedin': 'https://linkedin.com/in/testuser',
            'preferences': 'Test preferences',
            'pitch_deck': 'Test pitch deck'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile updated successfully', response.data)

    def test_add_availability(self):
        # Log in as a mentor to get a token
        session = SessionLocal()
        mentor_user = User(username='mentoruser', password=generate_password_hash('mentorpass', method='pbkdf2:sha256'), role='mentor')
        session.add(mentor_user)
        session.commit()
        session.close()

        response = self.app.post('/login', json={
            'username': 'mentoruser',
            'password': 'mentorpass'
        })
        token = response.get_json()['token']

        # Add availability
        response = self.app.post('/calendar', headers={'x-access-token': token}, json={
            'date_time': '2024-10-20 10:00:00'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Availability added successfully', response.data)

    def test_view_availability(self):
        # Log in to get a token
        response = self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        token = response.get_json()['token']

        # View availability
        response = self.app.get('/calendar', headers={'x-access-token': token})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'date_time', response.data)

    def test_book_slot(self):
        # Log in as a mentor to add availability
        session = SessionLocal()
        mentor_user = User(username='mentoruser2', password=generate_password_hash('mentorpass2', method='pbkdf2:sha256'), role='mentor')
        session.add(mentor_user)
        session.commit()
        session.close()

        response = self.app.post('/login', json={
            'username': 'mentoruser2',
            'password': 'mentorpass2'
        })
        mentor_token = response.get_json()['token']

        # Add availability
        response = self.app.post('/calendar', headers={'x-access-token': mentor_token}, json={
            'date_time': '2024-10-21 10:00:00'
        })
        self.assertEqual(response.status_code, 201)

        # Log in as a mentee to book the slot
        response = self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        mentee_token = response.get_json()['token']

        # View availability to get slot ID
        response = self.app.get('/calendar', headers={'x-access-token': mentee_token})
        slot_id = response.get_json()[0]['id']

        # Book the slot
        response = self.app.post('/calendar/book', headers={'x-access-token': mentee_token}, json={
            'slot_id': slot_id
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Slot booked successfully', response.data)
