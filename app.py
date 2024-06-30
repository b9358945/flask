import pymysql
from flask import Flask, render_template, request
from flask_paginate import Pagination, get_page_args
import re

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['JSON_AS_ASCII'] = False


# 데이터베이스 연결 정보
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Qkfan0942',
    'db': 'board',
    'charset': 'utf8'
}

# 데이터베이스 연결 함수
def connect_db():
    return pymysql.connect(**db_config)

# URL을 하이퍼링크로 변환하는 함수
def add_hyperlinks_to_comments(data):
    url_pattern = r'https?://\S+'
    processed_data = []
    for item in data:
        idx, name, score, comment, lastauth = item
        if comment:
            # 정규표현식으로 URL 추출
            urls = re.findall(url_pattern, comment)
            # 추출된 URL에 하이퍼링크 추가
            for url in urls:
                comment = comment.replace(url, f'<a href="{url}" target="_blank">{url}</a>')
        processed_data.append((idx, name, score, comment, lastauth))
    return processed_data

# 홈 페이지 라우트
@app.route('/')
def home():
    # 데이터베이스 연결
    db = connect_db()
    cursor = db.cursor()

    # 페이지네이션 설정
    per_page = 20
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')

    # 전체 데이터 개수 조회
    cursor.execute("SELECT COUNT(*) FROM board;")
    total = cursor.fetchone()[0]

    # 데이터 조회
    cursor.execute(
        "SELECT idx, name, score, IFNULL(comment, '') AS comment, lastauth FROM board ORDER BY score DESC LIMIT %s OFFSET %s;",
        (per_page, offset)
    )
    result = cursor.fetchall()

    # 하이퍼링크 추가 및 데이터 처리
    result_with_hyperlinks = add_hyperlinks_to_comments(result)

    # 데이터베이스 연결 종료
    db.close()

    # 페이지네이션 객체 생성
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')

    return render_template('index.html',
                           data=result_with_hyperlinks,
                           pagination=pagination)

if __name__ == '__main__':
    app.run('0.0.0.0', port=9999, debug=True)
