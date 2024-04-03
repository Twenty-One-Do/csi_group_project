from flask import Flask, flash, render_template, request, session, redirect, url_for, jsonify
from util import db_initialization, add_sample, search_query_execute
from datetime import datetime, timedelta
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = 'csi_project'
connection = sqlite3.connect('database.db', check_same_thread=False)

cur = connection.cursor()

db_initialization(cur)
# add_sample(connection, cur)  # 실행 후 주석처리

# Session 관련 변수 지정
# Test for 15 Seconds
SESSION_TIMEOUT: int = 30


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=SESSION_TIMEOUT)


@app.route("/")
def home():
    search_queries = {
        'latest_til': {
            'table': 'Posts',
            'attributes': ['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],
            'condition': None},
    }
    context = search_query_execute(cur, search_queries)
    if context['latest_til'][0] is not None:
        context['latest_til'].sort(key=lambda x: x['reg_date'], reverse=True)
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
            'attributes': ['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],
            'condition': None},
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
    context['session'] = session
    return render_template("post.html", data=context)


@app.route("/write", methods=['GET', 'POST'])
def write():
    if request.method == "GET":
        if 'meminfo' in session:
            return render_template("write.html", data=session['meminfo'])
        else:
            flash("로그인 먼저 해주세요!")
            return redirect(url_for('login'))
    elif request.method == "POST":
        title = request.form['title']
        contents = request.form['content']
        user_id = session['meminfo']['id']
        cur.execute("""
        INSERT INTO Posts (title, contents, user_id)
        VALUES ('{}', '{}', {})
        """.format(title, contents, user_id))
        connection.commit()
        return redirect(url_for('til_list'))


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
            flash("계정 정보가 일치하지 않습니다.")
            return redirect(url_for('login'))

        # 최근 로그인 시간 업데이트
        user_id = result[0]['id']
        username = result[0]['username']
        login_time: datetime = datetime.now()
        login_time_str: str = login_time.strftime(
            "%Y-%m-%d %H:%M:%S").split(".")[0]

        query = f"UPDATE Members SET last_acc_date = ? WHERE id = ?;"
        cur.execute(query, (login_time_str, user_id))
        connection.commit()
        # 로그인 시간 업데이트 끝

        # 세션 처리 및 user_id 보유를 위한 context 처리
        if "meminfo" not in session:
            session["meminfo"] = {
                "id": user_id,
                "name": username
            }

        return redirect(url_for(endpoint="home"))


@app.route("/register", methods=['GET', 'POST'])
def register():
    context = None
    if request.method == 'GET':
        return render_template("register.html", data=context)
    elif request.method == 'POST':
        username = request.form['username']
        pw = request.form['password']
        search_query = {
            'user': {
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

@app.route('/like_check', methods=['POST'])
def like_check():
    data = request.get_json()
    user_id = str(session['meminfo']['id'])
    post_id = data["post_id"]

    search_query = {
        'likes':{
            "table": "Post_Like",
            "attributes": ["id", "user_id", "post_id"],
            "condition": f"user_id={user_id}"
        }
    }
    user_likes = search_query_execute(cur, search_query)
    liked = False
    if user_likes['likes'][0] is not None:
        for rec in user_likes['likes']:
            if int(post_id) == rec['post_id']:
                liked = True
                break

    response = {'isLiked': liked}

    return jsonify(response)

@app.route('/push_like', methods=['POST'])
def push_like():
    data = request.get_json()
    user_id = str(session['meminfo']['id'])
    post_id = data["post_id"]
    liked = data["isLiked"]
    if liked:
        cur.execute(f"""DELETE FROM Post_Like WHERE user_id = {user_id} AND post_id = {post_id}""")
        cur.execute(f"""UPDATE Posts SET like_cnt= like_cnt-1 WHERE id= {post_id}""")
        connection.commit()
    else:
        cur.execute(f"""INSERT INTO Post_Like (user_id, post_id) VALUES ({user_id}, {post_id})""")
        cur.execute(f"""UPDATE Posts SET like_cnt= like_cnt+1 WHERE id= {post_id}""")
        connection.commit()
    return jsonify({'push':True})

if __name__ == "__main__":
    app.run()
