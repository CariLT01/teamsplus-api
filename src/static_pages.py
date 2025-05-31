from flask import render_template

def home()->str:
    return render_template("home/index.html")

def login_page()->str:
    return render_template("loginPage/index.html")

def dashboard_page()->str:
    return render_template("dashboard/index.html")

def register_page()->str:
    return render_template("registerPage/index.html")

def game_of_life_page()->str:
    return render_template("game_of_life/index.html")
def tos_page()->str:
    return render_template("tos/index.html")