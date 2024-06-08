from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=[ "GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        #check if user alreadu exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists! Please choose a different username.")
            return redirect(url_for("auth.register"))
    
        #hash cover password
        hashed_password = generate_password_hash(password, method='sha256')

        #creating new user and add to database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("You have registered with Boost Buddy! Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            flash("Login Successful! Welcome back!")
            return render_template("homepage.html")
        else:
            flash("Invalid username or password! Try Again!")

    return render_template("login.html")

@auth_bp.route("/")
def index():
    return render_template("login.html")

