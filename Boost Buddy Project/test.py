from flask import Flask, redirect, url_for, render_template, request, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
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

with app.app_context():
    db.create_all()

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('homepage.html', title='Home')

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


@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

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

if __name__ == '__main__':
    app.run(debug=True)