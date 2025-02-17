from flask import Flask, flash, render_template, request, session, redirect, url_for, jsonify
from util import db_initialization, add_sample, search_query_execute, search_query_execute_join, check_like
from datetime import datetime, timedelta
from threading import Thread, Event

import requests
import sqlite3
from math import ceil
from flask_paginate import Pagination, get_page_parameter

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
            'a_table': 'Posts',
            'b_table': 'Members',
            'a_attributes': ['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],
            'b_attributes': ['id', 'username'],
            'a_key': 'user_id',
            'b_key': 'id',
            'condition': None},
    }
    context = search_query_execute_join(cur, search_queries)

    if context['latest_til'][0] is not None:
        context['latest_til'].sort(key=lambda x: x['a.reg_date'], reverse=True)
    context['session'] = session
    return render_template("main.html", data=context)


@app.route(rule="/my_page", methods=["GET", "POST"])
def my_page():
    # 로그인 세션 미수립 시, 로그인 유도
    if "meminfo" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        if request.form.get("memOutPw"):

            user_id = session["meminfo"]["id"]
            pw = request.form.get("memOutPw")
            select_queries = {
                "Members":
                    {
                        "table": "Members",
                        "attributes": ["username", "password", "id"],
                        "condition": f"id='{user_id}' AND password='{pw}'"
                    }
            }
            result = search_query_execute(cur, select_queries)['Members']
            if result == [None]:
                flash("계정 정보가 일치하지 않습니다.")

            else:
                query = f"UPDATE Members SET is_deleted = ? WHERE id = ?;"
                cur.execute(query, (1, user_id))
                connection.commit()
                flash("회원 탈퇴가 완료되었습니다.")
                session.pop("meminfo")
                return redirect(url_for("home"))

        else:
            user_id = session["meminfo"]["id"]
            pre_pw = request.form.get("prePw")
            new_pw = request.form.get("newPw")
            select_queries = {
                "Members":
                    {
                        "table": "Members",
                        "attributes": ["username", "password", "id"],
                        "condition": f"id='{user_id}' AND password='{pre_pw}'"
                    }
            }

            result = search_query_execute(cur, select_queries)['Members']
            if result == [None]:
                flash("계정 정보가 일치하지 않습니다.")

            else:
                # new_pw UPDATE
                query = f"UPDATE Members SET password = ? WHERE id = ?;"
                cur.execute(query, (new_pw, user_id))
                connection.commit()
                flash("비밀번호 변경이 완료되었습니다.")

    # END IF

    # 세션 유지 시, 접속 계정 정보 DB 호출
    select_queries = {
        "Members":
            {
                "table": "Members",
                "attributes": ["username", "consecutive_cnt", "reg_date", "last_acc_date"],
                "condition": f"id='{session['meminfo']['id']}'"
            }
    }

    result = search_query_execute(cur, select_queries)["Members"]
    # 접속 계정 정보 DB 호출 완료

    # HTML 전송 DATA 작성
    context = {"username": result[0]["username"], "consecutive_cnt": result[0]["consecutive_cnt"],
               "reg_date": result[0]["reg_date"], "last_acc_date": result[0]["last_acc_date"], 'session': session}

    return render_template(template_name_or_list="my_page.html", data=context)


@app.route('/til_list', defaults={'page_num': '1'})
@app.route('/til_list/<page_num>')
def til_list(page_num):
    if '&' in page_num:
        page_num = page_num.split('&')
        page_num, condition = int(page_num[0]), page_num[1]
    else:
        page_num, condition = int(page_num), None

    interval = 10
    if condition is not None:
        page_num = 1
        interval = 10000
        search_queries = {
        'til_list': {
            'a_table': 'Posts',
            'b_table': 'Members',
            'a_attributes': ['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],
            'b_attributes': ['id', 'username'],
            'a_key': 'user_id',
            'b_key': 'id',
            'condition': f"b.username = '{condition}'"},
        }
    else:
        search_queries = {
        'til_list': {
            'a_table': 'Posts',
            'b_table': 'Members',
            'a_attributes': ['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],
            'b_attributes': ['id', 'username'],
            'a_key': 'user_id',
            'b_key': 'id',
            'condition': None},
        }

    context = search_query_execute_join(cur, search_queries)
    if context['til_list'][0] is not None:
        til_list = sorted(context['til_list'], key=lambda x: x['a.reg_date'], reverse=True)
        num_til = len(til_list)
        start, end = interval * (page_num - 1), min(num_til, interval * (page_num))
        context['til_list'] = til_list[start:end]
        context['session'] = session
        context['now_page'] = page_num
        context['max_page'] = num_til // interval + 1
        return render_template("til_list.html", data=context)
    else:
        flash("게시글이 없습니다!")
        return redirect(url_for("home"))


@app.route("/post/<post_id>")
def post(post_id):
    search_queries = {
        'post': {
            'a_table': 'Posts',
            'b_table': 'Members',
            'a_attributes': ['title', 'thumbnail', 'like_cnt', 'user_id', 'reg_date', 'contents', 'id'],
            'b_attributes': ['id', 'username'],
            'a_key': 'user_id',
            'b_key': 'id',
            'condition': f"a.id = {post_id}"},
        'comments': {
            'a_table': 'Comments',
            'b_table': 'Members',
            'a_attributes': ['id', 'user_id', 'contents', 'post_id', 'reg_date'],
            'b_attributes': ['id', 'username'],
            'a_key': 'user_id',
            'b_key': 'id',
            'condition': f"a.post_id = {post_id}"},
    }

    context = search_query_execute_join(cur, search_queries)
    context['session'] = session
    return render_template("post.html", data=context)

@app.route("/comment_post/<post_id>", methods=['POST'])
def comment_post(post_id):
    post_id = post_id
    user_id = session['meminfo']['id']
    content = request.form['comment_content']

    cur.execute("""
    INSERT INTO Comments (post_id, user_id, contents)
    VALUES ({}, {}, '{}')
    """.format(post_id, user_id, content))
    connection.commit()
    return redirect(url_for("post", post_id=post_id))


@app.route("/write", methods=['GET', 'POST'])
def write():
    if request.method == "GET":
        if 'meminfo' in session:
            return render_template("write.html", data={'session':session})
        else:
            flash("로그인 먼저 해주세요!")
            return redirect(url_for('login'))
    elif request.method == "POST":
        title = request.form['title']
        contents = request.form['content']
        user_id = session['meminfo']['id']
        yesterday_dt_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today_dt_str = datetime.now().strftime("%Y-%m-%d")

        # 임현경: Post 업데이트 전, user_id의 최근 포스트 작성일 확인 (2024.04.04)
        select_query = f"SELECT MAX(reg_date) FROM Posts WHERE user_id={user_id}"
        result = cur.execute(select_query).fetchone()[0]
        # 임현경 작업 1차 완료 (2024.04.04)

        cur.execute("""
        INSERT INTO Posts (title, contents, user_id)
        VALUES ('{}', '{}', {})
        """.format(title, contents, user_id))
        connection.commit()

        # 임현경: Consecutive Cnt Update (2024.04.04)
        if result is None:
            result = ""

        if today_dt_str not in result:
            update_plus_query = f"UPDATE Members SET consecutive_cnt=1 WHERE id={user_id}"

            if yesterday_dt_str in result:
                update_plus_query = update_plus_query.replace("consecutive_cnt=1", "consecutive_cnt=consecutive_cnt+1")

            cur.execute(update_plus_query)
            connection.commit()
        # 임현경 작업 2차 완료 (2024.04.04)

        return redirect(url_for('home'))


@app.route("/mod/<post_id>", methods=['GET', 'POST'])
def mod(post_id):
    post_id = int(post_id)
    user_id = session['meminfo']['id']

    if request.method == "GET":
        search_query = {
            'mod_post': {
                'table': 'Posts',
                "attributes": ["id", "user_id", "contents"],
                "condition": f'id = {post_id} AND user_id = {user_id}'
            }
        }
        result = search_query_execute(cur, search_query)['mod_post'][0]

        if result is None:
            flash("권한이 없습니다!")
            return redirect(url_for('home'))
        else:
            mod_content = result['contents']
            return render_template("write.html", data={'session':session, 'mod_content': mod_content})
    elif request.method == "POST":
        title = request.form['title']
        moded_content = request.form['content']

        cur.execute(f"""UPDATE Posts SET title="{title}" WHERE id= {post_id} AND user_id={user_id}""")
        cur.execute(f"""UPDATE Posts SET contents= "{moded_content}" WHERE id= {post_id} AND user_id={user_id}""")
        connection.commit()
    return redirect(url_for('post', post_id=post_id))


@app.route('/del/<post_id>')
def del_post(post_id):
    user_id = session['meminfo']['id']

    search_query = {
            'mod_post':{
                'table':'Posts',
                "attributes": ["id", "user_id", "contents"],
                "condition": f'id = {post_id} AND user_id = {user_id}'
            }
        }
    result = search_query_execute(cur, search_query)['mod_post'][0]
    if result is None:
        flash("권한이 없습니다!")
        return redirect(url_for('home'))
    else:
        # 임현경: 오늘 날자에 등록한 포스팅 삭제 시에만 연속 작성일에 영향이 가도록 코드 작성
        today_dt_str = datetime.now().strftime("%Y-%m-%d")
        post_reg_date_chk_query = f"SELECT reg_date FROM Posts WHERE id={post_id}"
        post_reg_date = cur.execute(post_reg_date_chk_query).fetchone()[0].split(" ")[0]
        # 임현경 1차 작업 완료

        cur.execute(f"""DELETE FROM Posts WHERE user_id = {user_id} AND id = {post_id}""")
        connection.commit()

        # 오늘 일자 포스팅 삭제에 대해서 consecutive_cnt 업데이트 작업 진행
        if post_reg_date == today_dt_str:
            today_duple_post_chk_query = f"SELECT COUNT(*) FROM Posts WHERE user_id={user_id} AND reg_date LIKE '%{today_dt_str}%'"
            result = cur.execute(today_duple_post_chk_query)

            if result is not None and not result.fetchone()[0]:
                update_cnt_restore_query = f"UPDATE Members SET consecutive_cnt=consecutive_cnt-1 WHERE id={user_id} AND consecutive_cnt != 0"
                cur.execute(update_cnt_restore_query)
                connection.commit()
        # 임현경 작업 완료

        flash("삭제가 완료되었습니다.")
        return redirect(url_for('home'))


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
                    "condition": f"username='{data.get('username')}' AND password='{data.get('password')}' AND is_deleted=0"
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


# 확인 완료 by 임현경
@app.route(rule="/logout", methods=["GET"])
def logout():
    if "meminfo" in session:
        session.pop("meminfo")
        return redirect(url_for("home"))

    return redirect(url_for("login"))


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
            return redirect(url_for('login'))


@app.route("/leaderboard")
def leaderboard():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5

    offset = (page-1) * per_page  # 각 페이지 start점

    cur.execute(""" 
                SELECT DISTINCT Members.username, Members.consecutive_cnt
                FROM Members
                ORDER BY Members.consecutive_cnt DESC
                LIMIT ? OFFSET ? 
    """, (per_page, offset))

    leaderboard_data = cur.fetchall()
    leaderboard_message = []

    rank = offset+1

    for row in leaderboard_data:
        username = row[0]
        consecutive_cnt = row[1]

        message = f"{rank}등, {username}님 연속 {consecutive_cnt}일 작성!"
        leaderboard_message.append(message)
        rank += 1

    cur.execute("SELECT COUNT(*) FROM Members;")
    total_members_count = cur.fetchone()[0]  # 첫번째행, 첫번째 열 --> 전체 회원수 가져오기
    total_pages = ceil(total_members_count/per_page)

    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_members_count,
        'total_pages': total_pages
    }

    return render_template("leaderboard.html", data=leaderboard_message, pagination=pagination, session = session)
    
@app.route('/push_like', methods=['POST'])
def push_like():
    data = request.get_json()
    user_id = str(session['meminfo']['id'])
    post_id, only_check = data["post_id"], data["only_check"]
    
    liked = check_like(cur, post_id, user_id)
    if only_check:
        return jsonify({'liked': liked})

    if liked:
        cur.execute(f"""DELETE FROM Post_Like WHERE user_id = {user_id} AND post_id = {post_id}""")
        cur.execute(f"""UPDATE Posts SET like_cnt= like_cnt-1 WHERE id= {post_id}""")
        connection.commit()
    else:
        cur.execute(f"""INSERT INTO Post_Like (user_id, post_id) VALUES ({user_id}, {post_id})""")
        cur.execute(f"""UPDATE Posts SET like_cnt= like_cnt+1 WHERE id= {post_id}""")
        connection.commit()
    
    search_query = {
        'like_cnt':{
            'table':'Posts',
            'attributes':['id', 'like_cnt'],
            'condition': f'id= {post_id}'
        }
    }
    like_cnt = search_query_execute(cur, search_query)['like_cnt'][0]['like_cnt']
    return jsonify({'like_cnt':like_cnt, 'liked': liked})


# 임현경: consecutive_cnt 일괄 확인 
def scheduler(event_o: Event, schedule_time="00:00"):
    update_query = "UPDATE Members SET consecutive_cnt=0 WHERE id={}"
    select_query = \
        """SELECT Members.id, 
MAX(Posts.reg_date) 
FROM Members 
JOIN Posts 
ON Members.id=Posts.user_id 
WHERE Members.is_deleted=0
GROUP BY Members.id"""

    while True:
        now = datetime.now().strftime("%H:%M")
        yesterday_dt_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        if now == schedule_time:
            # 사용자 ID 및 ID에 따른 최근 Post 작성 일자 조회.
            all_fetch = cur.execute(select_query).fetchall()

            # 추출 정보를 토대로 연속 작성일 업데이트 작업 진행
            for info in all_fetch:
                user_id = info[0]
                latest_reg_dt = info[1]

                if yesterday_dt_str not in latest_reg_dt:
                    cur.execute(update_query.format(user_id))
                    connection.commit()
        
        # Thread Wait by Event Object
        event_o.wait(60)
# 임현경 작업 완료


if __name__ == "__main__":
    event = Event()
    t_sch = Thread(target=scheduler, args=(event,), name="t_sch", daemon=True)
    t_sch.start()
    app.run()
    event.set()
