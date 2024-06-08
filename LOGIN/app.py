from flask import Flask, render_template 
from models import db
from views import auth_bp

app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db.init_app(app)

#database and tables
with app.app_context():
    db.create_all()

app.register_blueprint(auth_bp)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/homepage")
def homepage():
    return render_template("homepage.html")

if __name__ == '__main__':
    app.run(debug=True)