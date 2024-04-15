import pymysql
from faker import Faker
import random
from datetime import datetime

# Faker 객체 초기화
fake = Faker()

# 데이터베이스 연결 설정
conn = pymysql.connect(
    host="localhost",  # 데이터베이스 서버 주소
    user="root",  # 데이터베이스 사용자 이름
    password="kr14021428",  # 데이터베이스 비밀번호
    db="psycho_test",  # 데이터베이스 이름
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)


# participant 테이블을 위한 더미 데이터 생성
def generate_participant_data(n):
    for _ in range(n):
        name = fake.word().capitalize() + " " + fake.word().capitalize()
        age = random.randint(10, 100)  # 10살이상 100세 이하
        gender = random.choice(["male", "female"])
        created_at = datetime.now()
        yield (name, age, gender, created_at)


# quiz 테이블을 위한 더미 데이터 생성
def answer_pool(question_id: int, age: int):

    if question_id == 1:
        if age < 20:
            pool = ["19세 이하"]
        elif age < 41:
            pool = ["20세~40세"]
        elif age < 51:
            pool = ["41세~50세"]
        elif age < 61:
            pool = ["51세~60세"]
        else:
            pool = ["61세 이상"]

    elif question_id == 2:
        pool = [
            "less_six_months",
            "less_one_year",
            "less_two_year",
            "less_three_year",
            "more_than_three",
        ]
    elif question_id == 3:
        pool = ["opt1", "opt2", "opt3", "opt4", "opt5"]
    elif question_id == 4:
        pool = ["very_low", "low", "intermediate", "high"]
    elif question_id == 5:
        pool = [
            "less_10_percent",
            "less_20_percent",
            "less_30_percent",
            "less_40_percent",
            "more_40_percent",
        ]
    elif question_id == 6:
        pool = ["increase", "decrease", "retirement_fund"]
    else:
        pool = ["no_loss", "less_10", "less_20", "high_risk"]

    return pool


def generate_quiz_data(start=12, num=100):
    for p_id in range(start, start + num):

        with conn.cursor() as cursor:
            age_sql = "SELECT age FROM participant WHERE id = (%s)"
            cursor.execute(age_sql, (p_id,))
            age = cursor.fetchone()["age"]

        for q_id in range(1, 8):  # question 1 ~ 7
            participant_id = p_id
            question_id = q_id
            chosen_answer = random.choice(answer_pool(q_id, age))
            yield (participant_id, question_id, chosen_answer)


# 데이터베이스에 데이터 삽입
with conn.cursor() as cursor:
    # participant 데이터 삽입
    sql = "INSERT INTO participant (name, age, gender, created_at) VALUES (%s, %s, %s, %s)"
    for data in generate_participant_data(100):
        cursor.execute(sql, data)
    conn.commit()

    # quiz data insertion
    quiz_sql = "INSERT INTO quiz (participant_id, question_id, chosen_answer) VALUES (%s, %s, %s)"
    for data in generate_quiz_data(12, 100):
        cursor.execute(quiz_sql, data)
    conn.commit()

# 데이터베이스 연결 종료
conn.close()
