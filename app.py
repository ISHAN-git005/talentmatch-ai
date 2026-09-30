import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = "talentmatch_super_secret_key"

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "********",  
    "database": "talentmatch_db"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return ' '.join(text.split())

def calculate_match(student_profile_text, job_requirement_text):
    student_clean = clean_text(student_profile_text)
    job_clean = clean_text(job_requirement_text)

    if not student_clean.strip() or not job_clean.strip():
        return 0.0

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([student_clean, job_clean])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/student', methods=['GET', 'POST'])
def student():
    recommendations = []
    student_data = {}

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        skills = request.form.get('skills', '').strip()
        experience = request.form.get('experience', '').strip()

        combined_profile = f"{skills} {experience}"
        student_data = {'name': name, 'email': email, 'skills': skills, 'experience': experience}

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM internships")
        internships = cursor.fetchall()
        cursor.close()
        conn.close()

        for item in internships:
            job_text = f"{item['title']} {item['required_skills']} {item['description']}"
            score = calculate_match(combined_profile, job_text)
            item['match_score'] = score
            recommendations.append(item)

        # Sort internships by highest match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)

    return render_template('student_recommend.html', recommendations=recommendations, student=student_data)

@app.route('/apply', methods=['POST'])
def apply():
    internship_id = request.form.get('internship_id')
    name = request.form.get('name')
    email = request.form.get('email')
    skills = request.form.get('skills')
    experience = request.form.get('experience')
    match_score = request.form.get('match_score', 0.0)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO candidates (internship_id, name, email, skills, resume_summary, match_score)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (internship_id, name, email, skills, experience, match_score))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Application submitted successfully with your NLP match score!", "success")
    return redirect(url_for('student'))

@app.route('/employer', methods=['GET', 'POST'])
def employer():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Post new internship
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        location = request.form.get('location')
        required_skills = request.form.get('required_skills')
        description = request.form.get('description')

        cursor.execute("""
            INSERT INTO internships (title, company, location, required_skills, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, company, location, required_skills, description))
        conn.commit()
        flash("New internship posted successfully!", "success")

    # Fetch stats and applicants
    cursor.execute("SELECT COUNT(*) AS total_postings FROM internships")
    total_postings = cursor.fetchone()['total_postings']

    cursor.execute("SELECT COUNT(*) AS total_applicants FROM candidates")
    total_applicants = cursor.fetchone()['total_applicants']

    cursor.execute("SELECT COALESCE(AVG(match_score), 0) AS avg_match FROM candidates")
    avg_match = round(cursor.fetchone()['avg_match'], 1)

    cursor.execute("""
        SELECT c.*, i.title AS internship_title, i.company
        FROM candidates c
        JOIN internships i ON c.internship_id = i.id
        ORDER BY c.match_score DESC
    """)
    candidates = cursor.fetchall()

    cursor.close()
    conn.close()

    metrics = {
        'total_postings': total_postings,
        'total_applicants': total_applicants,
        'avg_match': avg_match
    }

    return render_template('employer_dashboard.html', metrics=metrics, candidates=candidates)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
