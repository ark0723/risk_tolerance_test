from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

# 라우터 불러오기
from routers.admin import admin_router
from routers.question import question_router
from routers.quiz import quiz_router

BASE_DIR = Path(__file__).resolve().parent

# templates 경로 지정
templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

app = FastAPI()
# app.router.redirect_slashes = False

# static 폴더 위치 지정
app.mount(
    "/static", StaticFiles(directory=str(Path(BASE_DIR, "static"))), name="static"
)

# load routers
app.include_router(admin_router, tags=["admin"])
app.include_router(question_router, tags=["question"])
app.include_router(quiz_router, tags=["quiz"])


# index.html : participant data를 입력받음
# 퀴즈 시작하기 버튼을 누르면 participant data를 db로 저장(post)
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, log_level="info")
