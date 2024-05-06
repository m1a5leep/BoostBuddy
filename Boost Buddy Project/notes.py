from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


notes = []

@app.route('/')
def index():
    return render_template('notes.html', notes=notes)

@app.route('/add_note', methods=['POST'])
def add_note():
    note = request.form.get('note')
    if note:
        notes.append(note)
    return redirect(url_for('index'))

@app.route('/delete_note/<int:note_index>', methods=['POST'])
def delete_note(note_index):
    if note_index < len(notes):
        del notes[note_index]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)