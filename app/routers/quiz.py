from fastapi import APIRouter, Depends, Request, Response, Cookie
from fastapi.responses import HTMLResponse
from typing import Annotated
from starlette import status
from sqlalchemy.orm import Session
from database import get_db
import schemas, crud
from pathlib import Path
from models import Quiz


# HTML, CSS, JS 사용을 위한 라이브러리
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

BASE_DIR = "/Users/mac/Desktop/fastapi_miniproject/app"

# templates 경로 지정
templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

quiz_router = APIRouter(prefix="/quiz")


@quiz_router.get("/participants", response_model=list[schemas.ParticipantCreate])
def get_participants_list(db: Session = Depends(get_db)):
    # db: Session -> db 객체가 Session타입임을 의미
    participants_list = crud.get_participants_list(db)
    return participants_list


quiz_router.mount(
    "/static", StaticFiles(directory=str(Path(BASE_DIR, "static"))), name="static"
)


@quiz_router.get("/")
def get_answer_form(request: Request, response_class=HTMLResponse):
    return templates.TemplateResponse("form.html", context={"request": request})


@quiz_router.post("/", response_model=schemas.ParticipantForm)
def create_participant(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    form_data: schemas.ParticipantForm = Depends(schemas.ParticipantForm.as_form),
):
    # new registed participant insert into database
    crud.create_participant_form(db=db, participant=form_data)
    # db.refresh()

    # get newly created participant
    participant = crud.get_new_participant(db)

    # 쿠키설정: 방금 등록한 participant id 및 이름 기록
    # todo: 현재 participant_name을 한글로 쿠기 생성시, 유니코드 에러 발생
    # 에러내용: unicodeencodeerror: 'latin-1' codec can't encode characters in position 18-21: ordinal not in range(256)
    # https://fastapi.tiangolo.com/reference/response/
    # https://dasima.co.kr/785/fastapi-%EC%BF%A0%ED%82%A4-%EB%B0%8F-%ED%97%A4%EB%8D%94-%EB%A7%A4%EA%B0%9C%EB%B3%80%EC%88%98-fastapi-%EA%B0%80%EC%9D%B4%EB%93%9C-12/
    # https://www.geeksforgeeks.org/fastapi-cookie-parameters/
    response.charset = "utf-8"
    response.set_cookie(key="participant_id", value=participant.id)
    response.set_cookie(key="participant_name", value=form_data.name)

    print({"msg": "cookie has been set."})
    return templates.TemplateResponse(name="form.html", context={"request": request})


@quiz_router.post("/submit", response_model=schemas.QuizCreate)
def send_answer_to_server(
    request: Request,
    db: Session = Depends(get_db),
    form_data: schemas.AnswerForm = Depends(schemas.AnswerForm.as_form),
):

    print(type(form_data))
    print(form_data)

    # save answers from a participant
    participant = crud.get_new_participant(db)
    crud.save_answers(db, participant, form_data)

    return templates.TemplateResponse(name="thanks.html", context={"request": request})


# todo: visualization 완성
@quiz_router.get("/graph", response_class=HTMLResponse)
def show_graphs(request: Request):
    from result import chart_html

    # return templates.TemplateResponse(name="inv_type.html", context={"request": request})
    return HTMLResponse(content="".join(chart_html))
