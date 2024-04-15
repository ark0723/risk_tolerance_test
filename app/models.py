from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from database import Base


class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True)
    username = Column(String(length=50))
    password = Column(String(length=255))


class Participant(Base):
    __tablename__ = "participant"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=50), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    created_at = Column(DateTime, nullable=False)


class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True)
    content = Column(String(length=255), nullable=False)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class Quiz(Base):
    __tablename__ = "quiz"
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey("participant.id"))
    question_id = Column(Integer, ForeignKey("question.id"))
    chosen_answer = Column(String(length=225))

    participant = relationship("Participant", backref="quizzes")
    question = relationship("Question", backref="quizzes")
