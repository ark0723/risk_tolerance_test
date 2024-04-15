from pydantic import BaseModel, field_validator
from fastapi import HTTPException, Form


# admin
class AdminCreate(BaseModel):
    username: str
    password: str

    @field_validator("username", "password")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise HTTPException(status_code=422, detail="필수항목을 입력해주세요.")
        return v

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise HTTPException(
                status_code=422,
                detail="비밀번호는 8자리 이상 영문과 숫자를 포함하여 작성해 주세요.",
            )
        if not any(char.isdigit() for char in v):
            raise HTTPException(
                status_code=422,
                detail="비밀번호는 8자리 이상 영문과 숫자를 포함하여 작성해 주세요.",
            )
        if not any(char.isalpha() for char in v):
            raise HTTPException(
                status_code=422,
                detail="비밀번호는 8자리 이상 영문과 숫자를 포함하여 작성해 주세요.",
            )

        return v


class Token(BaseModel):
    access_token: str
    token_type: str


# participants
class ParticipantCreate(BaseModel):
    name: str
    age: int
    gender: str


class ParticipantAll(ParticipantCreate):
    id: int


class ParticipantForm(BaseModel):
    name: str
    age: int
    gender: str

    @classmethod
    def as_form(
        cls, name: str = Form(...), age: int = Form(...), gender: str = Form(...)
    ):
        return cls(name=name, age=age, gender=gender)


# question
class QuestionCreate(BaseModel):
    content: str


# quiz
class QuizCreate(BaseModel):
    participant_id: int
    question_id: int
    chosen_answer: str


class AnswerForm(BaseModel):
    period: str
    experience: str
    level: str
    investment_ratio: str
    income: str
    loss_allowed: str

    @classmethod
    def as_form(
        cls,
        period: str = Form(...),
        experience: str = Form(...),
        level: str = Form(...),
        investment_ratio: str = Form(...),
        income: str = Form(...),
        loss_allowed: str = Form(...),
    ):
        return cls(
            period=period,
            experience=experience,
            level=level,
            investment_ratio=investment_ratio,
            income=income,
            loss_allowed=loss_allowed,
        )
