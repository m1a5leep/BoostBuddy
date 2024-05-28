from flask import Flask, render_template 
from flask_sqlalchemy import SQLAlchemy
from views import auth_bp

app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#user model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

#database table
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

app.register_blueprint(auth_bp)


if __name__ == '__main__':
    app.run(debug=True)