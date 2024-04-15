# 투자성향테스트 

1. 환경세팅
    - pip install -r requirements.txt
    - FastAPI, alembic, ...
    - MySQL과 연결(alembic)

2. 기능
    - Admin User 생성 및 로그인 기능
        - create admin user: /admin
        - login : /admin/login
    - 질문 API: 로그인한 Admin User만 Question API Access 가능
        - Create : /question/{question_id}
        - 질문 전체 리스트 조회: /question

    - Quiz API
        - home('/')에서 참여자가 form을 작성해서 submit 하면 DB에 참여자 정보 insertion이 일어남 : /quiz 
        - 그리고 설문 작성을 위한 form.html로 이동
        - 설문 작성(총 7개의 질문) 완료 후 submit 하면 작성한 설문내용이 quiz table에 insertion 됨: /quiz/submit
        - 설문 submit되면 thanks.html로 이동
        - '분석보기' 버튼 누르면 graph를 보여준다 : /quiz/graph


- 현재 문제점
    1. 참여자 정보를 cookie에 생성후, 설문이 끝나면 참여자 정보 cookie에서 제거를 시도하였으나, 
    브라우저상에 cookie가 남아있지 않음
    2. 참여자 이름이 한글일 경우, unicodeencodeerror: 'latin-1' codec can't encode characters in position 18-21: ordinal not in range(256) 에러 발생 
    3. 설문지의 질문 3번은 체크박스 type으로 중복 선택 가능하나 -> 현재 두개 이상을 선택할 경우 리스트를 db에 받아올 수 없는 문제
    4. visualization 추가 