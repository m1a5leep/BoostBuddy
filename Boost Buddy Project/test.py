from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/task')
def task():
    return render_template('task.html')

if __name__ == '__main__':
    app.run(debug=True)
  
