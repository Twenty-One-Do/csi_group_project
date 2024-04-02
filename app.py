from flask import Flask, flash, render_template, request, session, redirect, url_for
from util import db_initialization, add_sample, search_query_execute
from datetime import datetime
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = 'csi_project'
connection = sqlite3.connect('database.db', check_same_thread=False)

cur = connection.cursor()

db_initialization(cur)
# add_sample(connection, cur)  # 실행 후 주석처리


@app.route("/")
def home():
    search_queries = {
        'today_til': {
            'table': 'Posts',
            'attributes': ['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],
            'condition': 'date(reg_date) = date(CURRENT_DATE)'},
    }
    context = search_query_execute(cur, search_queries)

    return render_template("main.html", data=context)


@app.route("/my_page")
def my_page():
    context = None
    return render_template("my_page.html", data=context)


@app.route("/til_list")
def til_list():
    filter_list = {
        'search': {
            'table': 'Posts',
            'attributes': ['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],
            'condition': None},
        'lists': {
                'table' : 'Posts',
                'attributes' :['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],
                'condition' : None},
    }
    context = search_query_execute(cur, filter_list)
    
    return render_template("til_list.html", data=context)


@app.route("/post/<post_id>")
def post(post_id):
    search_queries = {
        'post': {
            'table': 'Posts',
            'attributes': ['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],
            'condition': 'id = {}'.format(post_id)},
        'comments': {
            'table': 'Comments',
            'attributes': ['id', 'user_id', 'contents', 'post_id', 'reg_date'],
            'condition': 'post_id = {}'.format(post_id)},
    }
    context = search_query_execute(cur, search_queries)

    return render_template("post.html", data=context)


@app.route("/write")
def write():
    context = None
    return render_template("write.html", data=context)


@app.route(rule="/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template(template_name_or_list="login.html")

    elif request.method == "POST":
        data = request.form
        select_queries = {
            "Members":
                {
                    "table": "Members",
                    "attributes": ["username", "password", "id"],
                    "condition": f"username='{data.get('username')}' AND password='{data.get('password')}'"
                }
        }

        result = search_query_execute(cur, select_queries)['Members']
        if result == [None]:
            return render_template(template_name_or_list="login.html", error_message="Password not match")

        # 최근 로그인 시간 업데이트
        user_id = result[0]['id']
        login_time: datetime = datetime.now()
        login_time_str: str = login_time.strftime("%Y-%m-%d %H:%M:%S").split(".")[0]

        query = f"UPDATE Members SET last_acc_date = ? WHERE id = ?;"
        cur.execute(query, (login_time_str, user_id))
        connection.commit()
        # 로그인 시간 업데이트 끝

        # 세션 처리 및 user_id 보유를 위한 context 처리
        # 세션 사용 방법 확인
        context = {
            "id": user_id
        }

        return redirect(url_for(endpoint="home"))


@app.route("/register", methods = ['GET', 'POST'])
def register():
    context = None
    if request.method == 'GET':
        return render_template("register.html", data=context)
    elif request.method == 'POST':
        username = request.form['username']
        pw = request.form['password']
        search_query = {
            'user':{
                'table': 'Members',
                'attributes': ['username'],
                'condition': "username == '{}'".format(username)
            }
        }

        if search_query_execute(cur, search_query)['user'][0] is not None:
            flash("이미 존재하는 username입니다!")
            return redirect(url_for('register')) 
        else:
            register_query = '''
                            INSERT INTO Members (username, password, admin, reg_date, last_acc_date, is_deleted)
                            VALUES ('{}', '{}', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
                            '''.format(username, pw)
            cur.execute(register_query)
            connection.commit()
            flash("회원가입이 완료되었습니다! 다시 로그인해주세요")
            return redirect(url_for('home'))



@app.route("/leaderboard")
def leaderboard():
    cur.execute(""" 
                SELECT DISTINCT Members.username, Posts.consecutive_cnt
                FROM Members
                INNER JOIN Posts ON Members.id = Posts.user_id
                ORDER BY Posts.consecutive_cnt DESC
    """)  # Members에 있는 username을 id라는 공통키 활용 내부 조인, Posts.consecutive_cnt 내림차순 정렬
    leaderboard_data = cur.fetchall()  # 해당 리스트 반환
    leaderboard_message = []

    rank = 1
    for row in leaderboard_data:
        username = row[0]
        consecutive_cnt = row[1]

        message = f"{rank}등, {username}님 연속 {consecutive_cnt} 출석!"
        leaderboard_message.append(message)
        rank += 1

    return render_template("leaderboard.html", data=leaderboard_message)


if __name__ == "__main__":
    app.run()
