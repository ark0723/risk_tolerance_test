from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

# password hashing context
from crud import pwd_context

from sqlalchemy.orm import Session
from database import get_db
import schemas
import crud


# admin user 관리를 위한 라우터
admin_router = APIRouter(prefix="/admin")


@admin_router.post("/", status_code=status.HTTP_204_NO_CONTENT)
def create_admin(_admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    db_admin = crud.get_admin(db, admin=_admin)
    if db_admin:  # 생성하고자 하는 admin이 이미 존재하면, 409 코드를 내려줄것
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin user already exists!",
        )
    # 해당 admin이 없으면, 새로 생성
    crud.create_admin(db=db, admin=_admin)
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Admin User Has Been Created Successfully",
    )


@admin_router.post("/login")
def login(
    login_form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # admin user 존재 확인
    user = crud.get_admin_user(db, login_form.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user or password"
        )

    # 로그인
    res = crud.verify_password(login_form.password, user.password)

    if not res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user or password"
        )

    return HTTPException(status_code=status.HTTP_200_OK, detail="login success!")
