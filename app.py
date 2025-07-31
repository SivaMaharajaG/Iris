
from flask import Flask, render_template, request, redirect, session
from iris_recognition.iris_utils import recognize_iris
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secret'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        image = request.files['iris']
        path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(path)

        voter_id = recognize_iris(path)
        if voter_id:
            session['voter_id'] = voter_id
            return redirect('/vote')
        else:
            return "Iris not recognized or not registered."
    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'voter_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect('database/voting.db')
    c = conn.cursor()
    voter_id = session['voter_id']

    c.execute("SELECT voted FROM voters WHERE voter_id=?", (voter_id,))
    if c.fetchone()[0] == 1:
        return "You have already voted."

    if request.method == 'POST':
        candidate = request.form['candidate']
        c.execute("UPDATE votes SET count = count + 1 WHERE candidate=?", (candidate,))
        c.execute("UPDATE voters SET voted = 1 WHERE voter_id=?", (voter_id,))
        conn.commit()
        return render_template('result.html', msg="Vote submitted successfully!")

    c.execute("SELECT candidate FROM votes")
    candidates = [row[0] for row in c.fetchall()]
    return render_template('vote.html', candidates=candidates)

@app.route('/admin')
def admin():
    conn = sqlite3.connect('database/voting.db')
    c = conn.cursor()
    c.execute("SELECT candidate, count FROM votes")
    data = c.fetchall()
    return render_template('admin_dashboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
