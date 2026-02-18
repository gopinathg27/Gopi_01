from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# ----------------- Database Connection -----------------
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',            
        password='Care123',
        database='project_schema'
    )

# ----------------- Grade Calculation -----------------
def get_grade(mark):
    if mark >= 91:
        return 'O'
    elif mark >= 81:
        return 'A+'
    elif mark >= 71:
        return 'A'
    elif mark >= 61:
        return 'B+'
    elif mark >= 51:
        return 'B'
    elif mark == 50:
        return 'C'
    else:
        return 'F'

# ----------------- CREATE -----------------
@app.route('/', methods=['GET', 'POST'])
def create_student():
    if request.method == 'POST':
        try:
            student_name = request.form.get('student_name', 'Anonymous')
            subjects = {
                'HCA': int(request.form['num1']),
                'MMA': int(request.form['num2']),
                'NS': int(request.form['num3']),
                'ES IoT': int(request.form['num4']),
                'RES': int(request.form['num5']),
                'ST': int(request.form['num6'])
            }

            average = sum(subjects.values()) / len(subjects)
            overall_grade = get_grade(average)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO student_marks "
                "(student_name, hca, mma, ns, esiot, res, st, average, overall_grade) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (student_name, subjects['HCA'], subjects['MMA'], subjects['NS'],
                 subjects['ES IoT'], subjects['RES'], subjects['ST'], average, overall_grade)
            )
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('view_students'))

        except ValueError:
            return render_template('getmark.html', error="Invalid input. Please enter numbers only.")
    return render_template('getmark.html')

# ----------------- READ -----------------
@app.route('/students')
def view_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student_marks ORDER BY id")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('students.html', students=students)

# ----------------- UPDATE -----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        student_name = request.form['student_name']
        subjects = {
            'HCA': int(request.form['num1']),
            'MMA': int(request.form['num2']),
            'NS': int(request.form['num3']),
            'ES IoT': int(request.form['num4']),
            'RES': int(request.form['num5']),
            'ST': int(request.form['num6'])
        }
        average = sum(subjects.values()) / len(subjects)
        overall_grade = get_grade(average)

        cursor.execute(
            "UPDATE student_marks SET student_name=%s, hca=%s, mma=%s, ns=%s, esiot=%s, res=%s, st=%s, average=%s, overall_grade=%s "
            "WHERE id=%s",
            (student_name, subjects['HCA'], subjects['MMA'], subjects['NS'],
             subjects['ES IoT'], subjects['RES'], subjects['ST'], average, overall_grade, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('view_students'))

    cursor.execute("SELECT * FROM student_marks WHERE id=%s", (id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_student.html', student=student)

# ----------------- DELETE -----------------
@app.route('/delete/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student_marks WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('view_students'))

if __name__ == '__main__':
    app.run(debug=True)
