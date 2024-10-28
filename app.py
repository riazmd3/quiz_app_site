from flask import Flask, render_template, request, redirect, url_for, session 
import mysql.connector

app = Flask(__name__)
app.secret_key = '70867086'  # Change this to a more secure key
user1 = 'root'  # MySQL username
password1 = 'Riaz@3456'  # MySQL password

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user=user1,
    password=password1,
    database="quiz_app2"
)
cursor = db.cursor()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']
    role = request.form.get('role')  # Get the role from the radio button

    if role == 'student':
        # Check for student login
        cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            session['role'] = 'student'
            return redirect(url_for('quiz'))

    elif role == 'faculty':
        # Check for faculty login
        cursor.execute("SELECT id FROM faculty WHERE username=%s AND password=%s", (username, password))
        faculty = cursor.fetchone()

        if faculty:
            session['user_id'] = faculty[0]
            session['role'] = 'faculty'
            return redirect(url_for('faculty_dashboard'))

    return "Invalid credentials or role not selected!"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role')

        if role == 'student':
            # Register a student
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        elif role == 'faculty':
            # Register a faculty
            cursor.execute("INSERT INTO faculty (username, password) VALUES (%s, %s)", (username, password))

        db.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/quiz')
def quiz():
    cursor.execute("SELECT * FROM questions LIMIT 10")
    questions = cursor.fetchall()
    return render_template('quiz.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    correct_count = 0
    for question in request.form:
        if question.startswith('question_'):
            q_id = int(question.split('_')[1])
            selected_option = request.form[question]
            cursor.execute("SELECT correct_option FROM questions WHERE question_id=%s", (q_id,))
            correct_answer = cursor.fetchone()[0]
            if selected_option == correct_answer:
                correct_count += 1

    cursor.execute("INSERT INTO scores (user_id, score) VALUES (%s, %s)", (session['user_id'], correct_count))
    db.commit()
    return redirect(url_for('result', score=correct_count))

@app.route('/result')
def result():
    score = request.args['score']
    return render_template('result.html', score=score)

@app.route('/faculty_dashboard')
def faculty_dashboard():
    cursor.execute("SELECT u.username, s.score FROM users u JOIN scores s ON u.id = s.user_id")
    students_scores = cursor.fetchall()
    return render_template('faculty_dashboard.html', students_scores=students_scores)

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        question_text = request.form['question']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_option = request.form['correct_option']

        cursor.execute("INSERT INTO questions (question_text, option_a, option_b, option_c, option_d, correct_option) VALUES (%s, %s, %s, %s, %s, %s)",
                       (question_text, option_a, option_b, option_c, option_d, correct_option))
        db.commit()
        return redirect(url_for('faculty_dashboard'))

    return render_template('add_question.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
