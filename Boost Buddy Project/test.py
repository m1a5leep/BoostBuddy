from flask import Flask, redirect, url_for, render_template, request, flash, send_from_directory, Blueprint, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import time, schedule, calendar, os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import threading



app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
UPLOAD_FOLDER = 'uploads'

db = SQLAlchemy(app)
notes = []
tasks = []



class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(150), nullable=False)
    task_description = db.Column(db.Text, nullable=False)
    task_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completion_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    bio = db.Column(db.String(100), nullable=True)  
    email = db.Column(db.String(120), nullable=False, unique=True)  
    phone = db.Column(db.String(15), nullable=True)

    def _repr_(self):
        return f"User('{self.username}')"
    
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    description = db.Column(db.String(255), nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)


with app.app_context():
    db.create_all()

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists! Please choose a different username.")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

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
            session['username'] = username
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
    user = User.query.filter_by(username=session.get('username')).first()
    if user:
        notifications = Notification.query.filter_by(user_id=user.id, read=False).all()
        for notification in notifications:
            flash(notification.message, 'info')
            notification.read = True  
        db.session.commit()
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
    status = request.form['status']
    task_date = datetime.strptime(task_date, '%Y-%m-%dT%H:%M')
    new_task = Task(task_name=task_name, task_description=task_description, task_date=task_date, status=status)
    db.session.add(new_task)
    db.session.commit()
    flash('Task created successfully.', 'success')
    return redirect(url_for('task'))

@app.route('/addtask',methods=['GET', 'POST'] )
def addtask():
     if request.method == 'POST':
        task_name = request.form['task_name']
        task_description = request.form['task_description']
        task_date = datetime.strptime(request.form['task_date'], '%Y-%m-%dT%H:%M')
        status = request.form['status']
        user = User.query.filter_by(username=session['username']).first()

        new_task = Task(task_name=task_name, task_description=task_description,
                        task_date=task_date, status=status, owner=user)
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for('index'))
     
     return render_template('addtask.html')

@app.route('/update_task_status/<int:task_id>', methods=['POST'])
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.form['status']
    task.status = new_status
    db.session.commit()
    flash('Task status updated successfully.', 'success')
    return redirect(url_for('task'))


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

@app.route('/calendar', methods=['GET', 'POST'])
def calendar_view():
    now = datetime.now()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    
    appointments = Appointment.query.filter(
        db.extract('year', Appointment.appointment_date) == year,
        db.extract('month', Appointment.appointment_date) == month
    ).all()
    
    appointments_by_day = {}
    for appointment in appointments:
        day = appointment.appointment_date.day
        if day not in appointments_by_day:
            appointments_by_day[day] = []
        appointments_by_day[day].append(appointment)
    
    month_days, tasks_by_day = generate_calendar(year, month)
    month_name = datetime(year, month, 1).strftime('%B')
    
    return render_template('calendar.html', year=year, month=month, month_name=month_name, 
                           month_days=month_days, tasks_by_day=tasks_by_day, 
                           appointments_by_day=appointments_by_day, datetime=datetime)

@app.route('/schedule_appointment', methods=['POST'])
def schedule_appointment():
    appointment_date = request.form['appointment_date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    description = request.form['description']

    new_appointment = Appointment(
        appointment_date=datetime.strptime(appointment_date, '%Y-%m-%d').date(),
        start_time=datetime.strptime(start_time, '%H:%M').time(),
        end_time=datetime.strptime(end_time, '%H:%M').time(),
        description=description
    )
    
    db.session.add(new_appointment)
    db.session.commit()
    
    return redirect(url_for('calendar_view'))

@app.route('/cancel_appoint', methods=['POST'])
def cancel_appoint():
   return render_template('calendar.html')

@app.route('/rank')
def rank():
   
    tasks = Task.query.all()

    sorted_tasks = []
    for task in tasks:
        if task.completion_time is not None:
            procrastination_level = task.completion_time - task.task_date
            sorted_tasks.append((task, procrastination_level))

    sorted_tasks.sort(key=lambda x: x[1], reverse=True)

    return render_template('rank.html', tasks=sorted_tasks)

@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/edit_profile')
def edit_profile():
    return render_template('edit_profile.html')


@app.route('/security', methods=['GET', 'POST'])
def security():
    if request.method == 'POST':
        if 'current_password' in request.form and 'new_password' in request.form and 'confirm_password' in request.form:
        
            username = session.get('username')
            user = User.query.filter_by(username=username).first()
            if user:
                if check_password_hash(user.password, request.form['current_password']):
                    new_password = request.form['new_password']
                    confirm_password = request.form['confirm_password']
                    if new_password == confirm_password:
                        new_password_hashed = generate_password_hash(new_password, method='pbkdf2:sha256')
                        user.password = new_password_hashed
                        db.session.commit()
                        flash('Password changed successfully!', 'success')
                        return redirect(url_for('auth.login'))
                    else:
                        flash('New password and confirm password do not match. Please try again.', 'danger')
                else:
                    flash('Current password is incorrect. Please try again.', 'danger')
            else:
                flash('User not found or not logged in. Please log in first.', 'danger')

        elif 'new_username' in request.form:
           
            new_username = request.form['new_username']
            user = User.query.filter_by(username=session['username']).first()
            if user:
                user.username = new_username
                db.session.commit()
                session['username'] = new_username 
                flash('Username changed successfully!', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('User not found or not logged in. Please log in first.', 'danger')
                
    return render_template('security.html')




@app.route('/about_me', methods=['GET', 'POST'])
def about_me():
    user = User.query.filter_by(username=session.get('username')).first()
    if not user:
        flash('User not found or not logged in.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        user.bio = request.form['bio']
        user.email = request.form['email']
        user.phone = request.form['phone']
        db.session.commit()
        flash('Contact information updated successfully!', 'success')
        return redirect(url_for('about_me'))

    return render_template('about_me.html', user=user, edit_mode=request.args.get('edit', 'false') == 'true')

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

def check_due_tasks():
    with app.app_context():
        now = datetime.utcnow()
        upcoming_tasks = Task.query.filter(Task.task_date > now, Task.task_date <= now + timedelta(hours=1)).all()
        for task in upcoming_tasks:
            user = User.query.filter_by(username=session['username']).first() 
            if user:
                message = f"Hey, your task '{task.task_name}' is due soon."
                notification = Notification(user_id=user.id, message=message)
                db.session.add(notification)
                db.session.commit()

schedule.every(30).minutes.do(check_due_tasks)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()



if __name__ == '__main__':
    app.run(debug=True)