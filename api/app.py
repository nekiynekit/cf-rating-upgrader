from flask import Flask, redirect, render_template, request
from tools import select_task_by_rating, get_best_rating

# from config import Config


app = Flask(__name__)
# app.config.from_object(Config)


@app.route("/", methods=["GET", "POST"])
def start_page():
    return render_template("index.html")


@app.route("/get_task", methods=["GET", "POST"])
def get_task():
    handle = request.form["handle"]
    best_rating = get_best_rating(handle, increment=200)
    problems = select_task_by_rating(rating=best_rating, shuffle=True, handle=handle)
    return redirect(problems[0].address)
