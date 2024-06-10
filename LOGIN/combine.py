from flask import Flask, redirect, url_for, render_template, request, flash, send_from_directory, Blueprint
from flask_sqlalchemy import SQLAlchemy
import time, schedule, calendar, os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(name)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)
notes = []
tasks = []



class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(150), nullable=False)
    task_description = db.Column(db.Text, nullable=False)
    task_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completion_time = db.Column(db.DateTime, nullable=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)

    def repr(self):
        return f"User('{self.username}')"

with app.app_context():
    db.create_all()

auth_bp = Blueprint("auth", name)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # checking if user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists! Please choose a different username.")
            return redirect(url_for("auth.register"))

        #hash cover password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

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
def auth_index():
    return render_template("login.html")

app.register_blueprint(auth_bp)

@app.route("/main")
def index():
    return render_template("index.html")

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/task')
def task():
    tasks = Task.query.all()
    return render_template('task.html', tasks=tasks)

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully.', 'success')
    return redirect(url_for('task'))

@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completion_time = datetime.utcnow()
    db.session.commit()
    flash('Task marked as complete.', 'success')
    return redirect(url_for('task'))

@app.route('/create_task', methods=['POST'])
def create_task():
    task_name = request.form['task_name']
    task_description = request.form['task_description']
    task_date = request.form['task_date']
    task_date = datetime.strptime(task_date, '%Y-%m-%dT%H:%M')
    new_task = Task(task_name=task_name, task_description=task_description, task_date=task_date)
    db.session.add(new_task)
    db.session.commit()
    flash('Task created successfully.', 'success')
    return redirect(url_for('task'))

@app.route('/addtask')
def addtask():
    return render_template('addtask.html')

@app.route('/note')
def note():
    notes = Note.query.all()
    return render_template('notes.html', notes=notes)



@app.route('/cancel_note', methods=['GET'])
def cancel_note():
   return render_template('notes.html')



@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully.', 'success')
    return redirect(url_for('note'))



@app.route('/notes', methods=['GET', 'POST'])
def create_notes():
    title = request.form['note_title']
    content = request.form['note_content']
    new_note = Note(title=title, content=content)
    db.session.add(new_note)
    db.session.commit()
    flash('Note created successfully.', 'success')
    return redirect(url_for('note'))
 

@app.route('/add_note')
def add_note():
    return render_template('add_note.html')




@app.route('/doc')
def document():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('doc.html', files=files)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file'))
    
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('doc.html', files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete', methods=['POST'])
def delete_file():
    filename = request.form['filename']
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File deleted successfully.', 'success')
    except OSError:
        flash('Error deleting file.', 'danger')
    return redirect(url_for('document'))

@app.route('/generatecal/<int:year>/<int:month>')
def generate_calendar(year, month):
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    tasks = Task.query.all()
    tasks_by_day = {}

    for task in tasks:
        if task.task_date.year == year and task.task_date.month == month:
            day = task.task_date.day
            if day not in tasks_by_day:
                tasks_by_day[day] = []
            tasks_by_day[day].append(task)
    
    return month_days, tasks_by_day

@app.route('/calendar')
def calendar_view():
    now = datetime.now()
    year = now.year
    month = now.month
    month_days, tasks_by_day = generate_calendar(year, month)
    month_name = now.strftime('%B')
    return render_template('calendar.html', year=year, month=month, month_name=month_name, month_days=month_days, tasks_by_day=tasks_by_day)

@app.route('/profile')
def profile():
    return render_template('profile.html')



@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        bio = request.form['bio']

        

        return redirect(url_for('index'))
    return render_template('edit_profile.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
       
        
        return redirect(url_for('index'))
    return render_template('change_password.html')

@app.route('/logout')
def logout():
 
    
    return redirect(url_for('index'))

if name == 'main':
    app.run(debug=True)