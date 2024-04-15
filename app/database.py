from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# (1) 비동기 방식 - Starlette
# (2) 데이터 검증 - pydantic

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:kr14021428@localhost/psycho_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def get_db():  # db 세션 객체를 리턴
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
