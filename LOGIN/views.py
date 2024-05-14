from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=[ "GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        #registration logic

        return redirect(url_for("auth.login"))


    return render_template("register.html")

@auth_bp.route("/login")
def login():
    return render_template("login.html")