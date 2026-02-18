from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Care123",
    database="quiz_app"
)

cursor = db.cursor(dictionary=True)

# ----------------- Student Registration -----------------
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        reg_no = request.form['reg_no']
        email = request.form['email']
        year = request.form['year']
        dept = request.form['dept']

        cursor.execute("SELECT * FROM students WHERE email=%s", (email,))
        existing = cursor.fetchone()
        if existing:
            return "This email has already submitted the quiz."

        cursor.execute(
            "INSERT INTO students (name, reg_no, email, year, dept) VALUES (%s,%s,%s,%s,%s)",
            (name, reg_no, email, year, dept)
        )
        db.commit()
        student_id = cursor.lastrowid
        return redirect(url_for('quiz', student_id=student_id))

    return render_template("register.html")

# ----------------- Quiz Page -----------------
@app.route('/quiz/<int:student_id>', methods=['GET', 'POST'])
def quiz(student_id):
    if request.method == 'POST':
        cursor.execute("SELECT * FROM questions")
        questions = cursor.fetchall()

        for q in questions:
            selected = request.form.get(f"q{q['id']}")
            if selected:
                cursor.execute(
                    "INSERT INTO responses (student_id, question_id, selected_option) VALUES (%s,%s,%s)",
                    (student_id, q['id'], selected)
                )
        db.commit()
        return redirect(url_for('result', student_id=student_id))

    cursor.execute("SELECT * FROM questions ORDER BY unit")
    questions = cursor.fetchall()
    return render_template("quiz.html", questions=questions, student_id=student_id)

# ----------------- Result Page -----------------
@app.route('/result/<int:student_id>')
def result(student_id):
    cursor.execute("""
        SELECT q.unit, q.correct_option, r.selected_option
        FROM responses r
        JOIN questions q ON r.question_id = q.id
        WHERE r.student_id=%s
    """, (student_id,))
    data = cursor.fetchall()

    marks = {}
    total = 0
    for row in data:
        unit = row['unit']
        if unit not in marks:
            marks[unit] = 0
        if row['correct_option'] == row['selected_option']:
            marks[unit] += 1
            total += 1

    cursor.execute("SELECT name FROM students WHERE id=%s", (student_id,))
    student = cursor.fetchone()
    return render_template("result.html", name=student['name'], marks=marks, total=total)

# ----------------- Staff Login -----------------
@app.route('/staff', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        if admin:
            session['staff_logged_in'] = True
            return redirect(url_for('staff_dashboard'))
        else:
            return "Invalid Credentials"
    return render_template("staff_login.html")

# ----------------- Staff Dashboard -----------------
@app.route('/staff/dashboard')
def staff_dashboard():
    if not session.get('staff_logged_in'):
        return redirect(url_for('staff_login'))

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    student_results = []
    for s in students:
        cursor.execute("""
            SELECT q.correct_option, r.selected_option
            FROM responses r
            JOIN questions q ON r.question_id = q.id
            WHERE r.student_id=%s
        """, (s['id'],))
        responses = cursor.fetchall()
        total = sum(1 for r in responses if r['correct_option']==r['selected_option'])
        student_results.append({
            "name": s['name'],
            "reg_no": s['reg_no'],
            "email": s['email'],
            "year": s['year'],
            "dept": s['dept'],
            "marks": total
        })

    return render_template("staff_dashboard.html", student_results=student_results)

# ----------------- Staff Logout -----------------
@app.route('/staff/logout')
def staff_logout():
    session.pop('staff_logged_in', None)
    return redirect(url_for('staff_login'))

# ----------------- Run -----------------
if __name__ == "__main__":
    app.run(debug=True)
