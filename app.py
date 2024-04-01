from flask import Flask, render_template, request

import random
import requests
app = Flask(__name__)

@app.route("/")
def home():
    context = None
    return render_template("index.html", data=context)

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