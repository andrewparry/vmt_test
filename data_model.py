
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'mentor', 'mentee', 'admin'
    linkedin = Column(String)
    preferences = Column(String)
    pitch_deck = Column(String)

class Calendar(Base):
    __tablename__ = 'calendar'
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey('users.id'))
    date_time = Column(DateTime, nullable=False)
    booked = Column(Boolean, default=False)
    mentee_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    zoom_room_id = Column(Integer, ForeignKey('zoom_rooms.id'), nullable=True)

class ZoomRoom(Base):
    __tablename__ = 'zoom_rooms'
    id = Column(Integer, primary_key=True)
    room_name = Column(String, unique=True, nullable=False)
    license_available = Column(Boolean, default=True)

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey('users.id'))
    mentee_id = Column(Integer, ForeignKey('users.id'))
    score = Column(Integer)
    comments = Column(String)

# Establish relationships
User.mentor_slots = relationship('Calendar', foreign_keys='Calendar.mentor_id', back_populates='mentor')
User.mentee_bookings = relationship('Calendar', foreign_keys='Calendar.mentee_id', back_populates='mentee')
Calendar.mentor = relationship('User', foreign_keys=[Calendar.mentor_id], back_populates='mentor_slots')
Calendar.mentee = relationship('User', foreign_keys=[Calendar.mentee_id], back_populates='mentee_bookings')
Calendar.zoom_room = relationship('ZoomRoom', back_populates='calendar_entries')
ZoomRoom.calendar_entries = relationship('Calendar', back_populates='zoom_room')
Feedback.mentor = relationship('User', foreign_keys=[Feedback.mentor_id])
Feedback.mentee = relationship('User', foreign_keys=[Feedback.mentee_id])
