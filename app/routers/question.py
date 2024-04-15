from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Question
import schemas, crud
from starlette import status

# question 조회 및 관리를 위한 router
question_router = APIRouter(prefix="/question")


# response_model=list[question_schema.Question]
# question_list 함수의 리턴값은 Question 스키마로 구성된 리스트임을 의미.
@question_router.get("/", response_model=list[schemas.QuestionCreate])
def question_list(db: Session = Depends(get_db)):
    # db: Session -> db 객체가 Session타입임을 의미
    question_list = crud.get_question_list(db)
    return question_list


@question_router.post("/create/{order_num}", response_model=schemas.QuestionCreate)
def create_question(
    order_num: int, _question: schemas.QuestionCreate, db: Session = Depends(get_db)
):
    db_question = crud.create_question(db, question=_question, order_num=order_num)
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Question Created Successfully",
    )
