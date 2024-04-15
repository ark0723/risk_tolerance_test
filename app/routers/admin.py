from fastapi import APIRouter, Depends, HTTPException, Request, Header, Response
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from starlette import status
from datetime import datetime, timedelta
from typing import Optional

# password hashing context
from crud import pwd_context

from sqlalchemy.orm import Session
from database import get_db
import schemas
import crud

import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# create a set to stroe revoked tokens
revoked_token_set = set()

# admin user 관리를 위한 라우터
admin_router = APIRouter(prefix="/admin")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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
    response: Response,
    login_form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # admin user 존재 확인
    user = crud.get_admin_user(db, login_form.username)

    # check user and password
    if not user or not pwd_context.verify(login_form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # make access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 쿠키에 저장
    response.set_cookie(
        key="access_token",
        value=access_token,
        expires=access_token_expires,
        httponly=True,
    )

    return schemas.Token(access_token=access_token, token_type="bearer")


@admin_router.post("/logout")
def logout(response: Response, request: Request):
    access_token = request.cookies.get("access_token")

    # 쿠키 삭제
    response.delete_cookie(key="access_token")
    return HTTPException(status_code=status.HTTP_200_OK, detail="Logout successful")
