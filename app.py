from flask import Flask, flash, render_template, request, session, redirect, url_for
from util import db_initialization, add_sample, search_query_execute
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
            'table': 'Posts',
            'attributes': ['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'], }
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


@app.route("/login")
def login():
    context = None
    return render_template("login.html", data=context)


@app.route("/register", methods = ['GET', 'POST'])
def register():
    context = None
    if request.method == 'GET':
        return render_template("register.html", data=context)
    elif request.method == 'POST':
        username = request.form['username']
        pw = request.form['pw']
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
    print(leaderboard_data)
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
