from flask import Flask, redirect, url_for, render_template, request, flash

app = Flask(__name__)

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

@app.route('/add_note', methods=['POST'])
def add_note():
    note = request.form.get('note')
    if note:
        notes.append(note)
    return redirect(url_for('note'))

@app.route('/delete_note/<int:note_index>', methods=['POST'])
def delete_note(note_index):
    if note_index < len(notes):
        del notes[note_index]
    return redirect(url_for('note'))

if __name__ == '__main__':
    app.run(debug=True)
