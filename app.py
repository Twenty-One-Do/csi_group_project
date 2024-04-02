from flask import Flask, render_template, request, session
from util import db_initialization, add_sample, search_query_execute
import requests
import sqlite3

app = Flask(__name__)
connection = sqlite3.connect('database.db', check_same_thread=False)

cur = connection.cursor()

db_initialization(cur)
# add_sample(connection, cur) # 실행 후 주석처리

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
        'search' : {
                'table' : 'Posts',
                'attributes': ['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],
                'condition' : None},   
        'lists': {
                'table' : 'Posts',
                'attributes' :['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],}
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


@app.route("/register")
def register():
    context = None
    return render_template("register.html", data=context)


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
