
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_model import Base, User

app = Flask(__name__)

# Database setup
DATABASE_URL = "sqlite:///vmt.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create database tables
Base.metadata.create_all(bind=engine)

@app.route('/')
def index():
    return "VMT Office Hour Reservation System is running!"

if __name__ == '__main__':
    app.run(debug=True)

from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    session = SessionLocal()
    new_user = User(username=username, password=hashed_password, role=role)
    session.add(new_user)
    session.commit()
    session.close()

    return jsonify({"message": "User registered successfully"}), 201

import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing required fields"}), 400

    session = SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    session.close()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        'user_id': user.id,
'exp': datetime.utcnow() + timedelta(hours=1)
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({"token": token}), 200

from flask import g
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({"error": "Token is missing!"}), 403
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            session = SessionLocal()
            current_user = session.query(User).filter_by(id=data['user_id']).first()
            session.close()
            if not current_user:
                return jsonify({"error": "User not found!"}), 403
        except Exception as e:
            return jsonify({"error": "Token is invalid!"}), 403
        g.user = current_user
        return f(*args, **kwargs)
    return decorated

@app.route('/profile', methods=['GET', 'PUT'])
@token_required
def profile():
    if request.method == 'GET':
        user_data = {
            "username": g.user.username,
            "role": g.user.role,
            "linkedin": g.user.linkedin,
            "preferences": g.user.preferences,
            "pitch_deck": g.user.pitch_deck
        }
        return jsonify(user_data), 200

    if request.method == 'PUT':
        data = request.get_json()
        session = SessionLocal()
        user = session.query(User).filter_by(id=g.user.id).first()
        user.linkedin = data.get('linkedin', user.linkedin)
        user.preferences = data.get('preferences', user.preferences)
        user.pitch_deck = data.get('pitch_deck', user.pitch_deck)
        session.commit()
        session.close()
        return jsonify({"message": "Profile updated successfully"}), 200

from datetime import datetime

@app.route('/calendar', methods=['POST'])
@token_required
def add_availability():
    if g.user.role != 'mentor':
        return jsonify({"error": "Only mentors can add availability"}), 403

    data = request.get_json()
    date_time_str = data.get('date_time')
    try:
        date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"}), 400

    session = SessionLocal()
    new_slot = Calendar(mentor_id=g.user.id, date_time=date_time)
    session.add(new_slot)
    session.commit()
    session.close()

    return jsonify({"message": "Availability added successfully"}), 201

@app.route('/calendar', methods=['GET'])
@token_required
def view_availability():
    session = SessionLocal()
    available_slots = session.query(Calendar).filter_by(booked=False).all()
    session.close()

    slots_data = [
        {
            "id": slot.id,
            "mentor_id": slot.mentor_id,
            "date_time": slot.date_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        for slot in available_slots
    ]

    return jsonify(slots_data), 200



@app.route('/zoom_rooms', methods=['GET'])
@token_required
def view_zoom_rooms():
    if g.user.role != 'admin':
        return jsonify({"error": "Only admins can view Zoom rooms"}), 403

    session = SessionLocal()
    zoom_rooms = session.query(ZoomRoom).all()
    session.close()

    rooms_data = [
        {
            "id": room.id,
            "room_name": room.room_name,
            "license_available": room.license_available
        }
        for room in zoom_rooms
    ]

    return jsonify(rooms_data), 200

@app.route('/zoom_rooms', methods=['POST'])
@token_required
def add_zoom_room():
    if g.user.role != 'admin':
        return jsonify({"error": "Only admins can add Zoom rooms"}), 403

    data = request.get_json()
    room_name = data.get('room_name')

    if not room_name:
        return jsonify({"error": "Room name is required"}), 400

    session = SessionLocal()
    new_room = ZoomRoom(room_name=room_name)
    session.add(new_room)
    session.commit()
    session.close()

    return jsonify({"message": "Zoom room added successfully"}), 201

def check_zoom_availability():
    session = SessionLocal()
    available_rooms = session.query(ZoomRoom).filter_by(license_available=True).count()
    session.close()
    return available_rooms > 0

@app.route('/calendar/book', methods=['POST'])
@token_required
def book_slot():
    if g.user.role != 'mentee':
        return jsonify({"error": "Only mentees can book slots"}), 403

    if not check_zoom_availability():
        return jsonify({"error": "No Zoom licenses available"}), 403

    data = request.get_json()
    slot_id = data.get('slot_id')

    session = SessionLocal()
    slot = session.query(Calendar).filter_by(id=slot_id, booked=False).first()

    if not slot:
        session.close()
        return jsonify({"error": "Slot not available"}), 404

    slot.booked = True
    slot.mentee_id = g.user.id

    # Mark a Zoom room as used
    zoom_room = session.query(ZoomRoom).filter_by(license_available=True).first()
    zoom_room.license_available = False
    slot.zoom_room_id = zoom_room.id

    session.commit()
    session.close()

    return jsonify({"message": "Slot booked successfully"}), 200

import requests

JOTFORM_API_KEY = "your_jotform_api_key"
JOTFORM_FORM_ID = "your_jotform_form_id"

def send_feedback_survey(mentor_email, mentee_email):
    url = f"https://api.jotform.com/form/{JOTFORM_FORM_ID}/submissions"
    headers = {
        "Content-Type": "application/json",
        "APIKEY": JOTFORM_API_KEY
    }
    data = {
        "submission": {
            "mentor_email": mentor_email,
            "mentee_email": mentee_email
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

@app.route('/feedback', methods=['POST'])
@token_required
def send_feedback():
    if g.user.role != 'admin':
        return jsonify({"error": "Only admins can send feedback surveys"}), 403

    data = request.get_json()
    mentor_id = data.get('mentor_id')
    mentee_id = data.get('mentee_id')

    session = SessionLocal()
    mentor = session.query(User).filter_by(id=mentor_id).first()
    mentee = session.query(User).filter_by(id=mentee_id).first()
    session.close()

    if not mentor or not mentee:
        return jsonify({"error": "Invalid mentor or mentee ID"}), 404

    if send_feedback_survey(mentor.username, mentee.username):
        return jsonify({"message": "Feedback survey sent successfully"}), 200
    else:
        return jsonify({"error": "Failed to send feedback survey"}), 500
