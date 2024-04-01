from flask import Flask, render_template, request

import requests
import sqlite3

app = Flask(__name__)
connection = sqlite3.connect('database/database.db')

cur = connection.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS Members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username CHAR(25) NOT NULL UNIQUE,
    password CHAR(65) NOT NULL,
    admin INTEGER NOT NULL DEFAULT 0,
    reg_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_acc_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS Posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title CHAR(25),
    contents TEXT,
    user_id INTEGER,
    reg_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    mod_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    consecutive_cnt INTEGER DEFAULT 1,
    like_cnt INTEGER DEFAULT 1,
    cnt INTEGER DEFAULT 1,
    FOREIGN KEY(user_id) REFERENCES Members(id)
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS Comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    user_id INTEGER,
    contents TEXT,
    reg_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    mod_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES Members(id),
    FOREIGN KEY(post_id) REFERENCES Posts(id)
)
''')


@app.route("/")
def home():
    context = None
    return render_template("main.html", data=context)


@app.route("/my_page")
def my_page():
    context = None
    return render_template("my_page.html", data=context)


@app.route("/til_list")
def til_list():
    context = None
    return render_template("til_list.html", data=context)


@app.route("/post/<post_id>")
def post():
    context = None
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
    context = None
    return render_template("leaderboard.html", data=context)


if __name__ == "__main__":
    app.run()