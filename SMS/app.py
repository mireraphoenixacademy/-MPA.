from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS learners (
        admission_no TEXT PRIMARY KEY,
        name TEXT,
        grade TEXT,
        fees_due REAL,
        date_admitted TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS fee_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admission_no TEXT,
        amount REAL,
        payment_date TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS books (
        grade TEXT,
        book_count INTEGER
    )''')
    conn.commit()
    conn.close()

# Generate admission number
def generate_admission_no():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM learners")
    count = c.fetchone()[0] + 1
    admission_no = f"MPA/{str(count).zfill(5)}"
    conn.close()
    return admission_no

# Routes
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM learners")
    learners = c.fetchall()
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    conn.close()
    return render_template('index.html', learners=learners, books=books)

@app.route('/admit', methods=['GET', 'POST'])
def admit_learner():
    if request.method == 'POST':
        name = request.form['name']
        grade = request.form['grade']
        fees_due = float(request.form['fees_due'])
        admission_no = generate_admission_no()
        date_admitted = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO learners (admission_no, name, grade, fees_due, date_admitted) VALUES (?, ?, ?, ?, ?)",
                  (admission_no, name, grade, fees_due, date_admitted))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('admit_learner.html')

@app.route('/fees', methods=['GET', 'POST'])
def manage_fees():
    if request.method == 'POST':
        admission_no = request.form['admission_no']
        amount = float(request.form['amount'])
        payment_date = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO fee_payments (admission_no, amount, payment_date) VALUES (?, ?, ?)",
                  (admission_no, amount, payment_date))
        c.execute("UPDATE learners SET fees_due = fees_due - ? WHERE admission_no = ?", (amount, admission_no))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('fees.html')

@app.route('/books', methods=['GET', 'POST'])
def manage_books():
    if request.method == 'POST':
        grade = request.form['grade']
        book_count = int(request.form['book_count'])

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO books (grade, book_count) VALUES (?, ?)", (grade, book_count))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('books.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)