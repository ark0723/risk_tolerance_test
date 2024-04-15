from models import Admin, Participant, Question, Quiz
from schemas import (
    AdminCreate,
    QuestionCreate,
    QuizCreate,
    AnswerForm,
    ParticipantForm,
    ParticipantCreate,
    ParticipantAll,
)
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime

# bcrypt 알고리즘을 사용하는 pwd_context 객체를 생성
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_admin(db: Session, admin: AdminCreate):
    # pwd_context 객체를 사용하여 비밀번호를 암호화하여 저장
    db_admin = Admin(username=admin.username, password=pwd_context.hash(admin.password))
    db.add(db_admin)
    db.commit()
    return db_admin


def get_admin(db: Session, admin: AdminCreate):
    return db.query(Admin).filter(Admin.username == admin.username).first()


def get_admin_user(db: Session, username: str):
    return db.query(Admin).filter(Admin.username == username).first()


# question
def get_question_list(db: Session):
    question_list = db.query(Question).order_by(Question.order.asc()).all()
    return question_list


def create_question(db: Session, question: QuestionCreate, order_num: int):
    db_question = Question(content=question.content, order=order_num)
    db.add(db_question)
    db.commit()
    return db_question


# participant
def create_participant_form(db: Session, participant: ParticipantForm):
    db_participant = Participant(
        name=participant.name,
        age=participant.age,
        gender=participant.gender,
        created_at=datetime.now(),
    )
    db.add(db_participant)
    db.commit()
    return db_participant


def get_participants_list(db: Session):
    participants_list = db.query(Participant).all()
    return participants_list


def get_new_participant(db: Session):
    return db.query(Participant).order_by(Participant.id.desc()).first()


def get_age_category(age: int) -> str:
    if age < 20:
        return "19세 이하"
    elif age < 41:
        return "20세~40세"
    elif age < 51:
        return "41세~50세"
    elif age < 61:
        return "51세~60세"
    else:
        return "61세 이상"


# quiz
def save_answers(db: Session, participant: ParticipantAll, answer: AnswerForm):

    # answers from one participant
    age = get_age_category(participant.age)
    period = answer.period  # Q2
    experience = answer.experience
    level = answer.level
    investment_ratio = answer.investment_ratio
    income = answer.income
    loss_allowed = answer.loss_allowed

    answer_dict = {
        1: age,
        2: period,
        3: experience,
        4: level,
        5: investment_ratio,
        6: income,
        7: loss_allowed,
    }

    for k, v in answer_dict.items():
        db_answer = Quiz(participant_id=participant.id, question_id=k, chosen_answer=v)
        db.add(db_answer)
    db.commit()
