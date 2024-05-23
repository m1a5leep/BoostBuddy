from flask import Flask, redirect, url_for, render_template, request, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

notes = []
tasks = []

@app.route('/')
def index():
    return render_template('homepage.html', title='Home')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/task')
def task():
    return render_template('task.html', tasks=tasks)

@app.route('/cancel', methods=['GET'])
def cancel_add():
    return render_template('task.html')

@app.route('/delete_task/<int:task_index>', methods=['POST'])
def delete_task(task_index):
    if request.method == 'POST':
        if task_index < len(tasks):
            del tasks[task_index]
            flash('Task deleted successfully.', 'success')
    return redirect(url_for('task'))

@app.route('/complete_task/<int:task_index>', methods=['POST'])
def complete_task(task_index):
    if request.method == 'POST':
        if task_index < len(tasks):
            tasks[task_index]['completed'] = True
            flash('Task marked as complete.', 'success')
    return redirect(url_for('task'))

@app.route('/task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        task_name = request.form['task_name']
        task_description = request.form['task_description']
        task_due_date = request.form['task_due_date']

        task = {
            'name': task_name,
            'description': task_description,
            'due_date': task_due_date
        }

        tasks.append(task)
        print(tasks)

        return redirect(url_for('task'))
    return render_template('task.html')

@app.route('/addtask')
def addtask():
    return render_template('addtask.html')

@app.route('/notes')
def note():
    return render_template('notes.html', notes=notes)


@app.route('/cancel_note', methods=['GET'])
def cancel_note():
   return render_template('notes.html')


@app.route('/delete_notes/<int:notes_index>', methods=['POST'])
def delete_notes(notes_index):
    if request.method == 'POST':
        if notes_index < len(notes):
           del notes[notes_index]
           flash('Note deleted successfully.', 'success')
    return redirect(url_for('note'))


@app.route('/notes', methods=['GET', 'POST'])
def create_notes():
    if request.method == 'POST':
        note_title = request.form['note_title']
        note_content = request.form['note_content']

        note = {
            'title': note_title,
            'content': note_content
        }

        notes.append(note)
        print(note)

        return redirect(url_for('note'))
    return render_template('notes.html', notes=notes)


@app.route('/add_note')
def add_note():
    return render_template('add_note.html')


@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

if __name__ == '__main__':
    app.run(debug=True)
