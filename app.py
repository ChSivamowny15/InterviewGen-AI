import sqlite3
from datetime import datetime
import cv2
import numpy as np
import base64
from flask import jsonify
import os
import json
import uuid
import io
import requests
from flask import request, abort
from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    url_for,
    session,
    flash
)
from werkzeug.utils import secure_filename
from io import BytesIO
from flask import send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from werkzeug.security import generate_password_hash, check_password_hash
from evaluator import evaluate_answer
from ai_modules.answer_evaluator import evaluate_interview
from ai_modules.resume_intelligence import analyze_resume

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)


# ==================================================
# FLASK CONFIGURATION
# ==================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "interviewgen-local-development-secret"
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads",
    "resumes"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
# ==================================================
# INTERVIEW HISTORY DATABASE
# ==================================================

# ==================================================
# INTERVIEW HISTORY DATABASE
# ==================================================

# ==================================================
# INTERVIEW HISTORY DATABASE
# ==================================================

DATABASE_PATH = os.path.join(BASE_DIR, "interviewgen.db")


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS interview_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                interview_type TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                average_score REAL NOT NULL,
                total_questions INTEGER NOT NULL,
                results_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        columns = [
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(interview_history)"
            ).fetchall()
        ]

        if "reward_points" not in columns:
            connection.execute("""
                ALTER TABLE interview_history
                ADD COLUMN reward_points INTEGER NOT NULL DEFAULT 0
            """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
                # Add additional profile fields if they do not exist
        user_columns = [
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(users)"
            ).fetchall()
        ]

        profile_fields = {
            "phone": "TEXT",
            "college": "TEXT",
            "degree": "TEXT",
            "department": "TEXT",
            "study_year": "TEXT",
            "graduation_year": "TEXT",
            "cgpa": "TEXT",
            "skills": "TEXT",
            "career_goal": "TEXT",
            "linkedin": "TEXT",
            "github": "TEXT",
            "bio": "TEXT"
        }

        for column, data_type in profile_fields.items():
            if column not in user_columns:
                connection.execute(
                    f"ALTER TABLE users ADD COLUMN {column} {data_type}"
                )

        connection.commit()

    finally:
        connection.close()
        

initialize_database()


def calculate_reward_points(score):
    if score >= 90:
        return 100
    elif score >= 75:
        return 80
    elif score >= 60:
        return 60
    elif score >= 40:
        return 40
    else:
        return 20
    # ==================================================
# DYNAMIC IMPROVEMENT PLAN
# ==================================================

def get_question_category(question):
    question = question.lower()

    categories = {
        "Python": ["python", "decorator", "generator", "list", "tuple"],
        "Java": ["java", "jvm", "jdk", "jre", "hashmap"],
        "SQL & Database": ["sql", "database", "query", "normalization", "nosql"],
        "Machine Learning": [
            "machine learning", "supervised", "unsupervised",
            "regression", "classification", "overfitting",
            "underfitting", "neural network", "gradient descent"
        ],
        "Web Development": [
            "html", "css", "javascript", "website",
            "frontend", "backend", "dom", "rest api"
        ],
        "Data Structures": [
            "array", "linked list", "stack", "queue",
            "tree", "graph", "sorting", "searching"
        ],
        "Software Engineering": [
            "software", "testing", "debugging", "deployment",
            "development life cycle", "microservices"
        ],
        "HR & Communication": [
            "tell me about yourself", "strengths", "weaknesses",
            "team", "leadership", "career goals", "motivation",
            "pressure", "failure", "feedback"
        ]
    }

    for category, keywords in categories.items():
        if any(keyword in question for keyword in keywords):
            return category

    return "General Interview Skills"


def generate_improvement_plan(interviews):

    category_scores = {}
    total_scores = []
    all_suggestions = []

    for interview in interviews:

        try:
            results = json.loads(interview["results_json"])

            if not isinstance(results, list):
                continue

        except (ValueError, TypeError):
            continue

        for result in results:

            if not isinstance(result, dict):
                continue

            question = result.get("question", "")
            score = safe_number(
                result.get("score", 0),
                default=0,
                minimum=0,
                maximum=100
            )

            category = get_question_category(question)

            if category not in category_scores:
                category_scores[category] = {
                    "total": 0,
                    "count": 0
                }

            category_scores[category]["total"] += score
            category_scores[category]["count"] += 1

            total_scores.append(score)

            suggestion = clean_text(
                result.get("suggestions", ""),
                300
            )

            if suggestion and suggestion not in all_suggestions:
                all_suggestions.append(suggestion)

    strengths = []
    areas_to_improve = []

    for category, data in category_scores.items():

        average = round(
            data["total"] / data["count"],
            1
        )

        category_info = {
            "name": category,
            "score": average
        }

        if average >= 70:
            strengths.append(category_info)

        elif average < 60:
            areas_to_improve.append(category_info)

    strengths.sort(key=lambda item: item["score"], reverse=True)
    areas_to_improve.sort(key=lambda item: item["score"])

    if not strengths and not areas_to_improve:
        if total_scores:
            strengths.append({
                "name": "Overall Interview Practice",
                "score": round(
                    sum(total_scores) / len(total_scores),
                    1
                )
            })

    recommendations = []

    for area in areas_to_improve[:3]:
        recommendations.append(
            f"Practise more questions in {area['name']}."
        )

    if all_suggestions:
        recommendations.extend(all_suggestions[:3])

    if not recommendations and total_scores:
        recommendations.append(
            "Continue practising mock interviews to improve your consistency."
        )

    if not total_scores:
        recommendations = [
            "Complete your first mock interview to receive personalised recommendations."
        ]

    if total_scores:
        weekly_goals = [
            "Practise 3 mock interviews this week.",
            "Solve 15 coding or technical questions.",
            "Review your incorrect answers and AI feedback."
        ]

        if areas_to_improve:
            weekly_goals.append(
                f"Spend extra time practising {areas_to_improve[0]['name']}."
            )
    else:
        weekly_goals = [
            "Complete your first mock interview.",
            "Practise 10 basic technical questions.",
            "Review your interview report and feedback."
        ]

    return {
        "strengths": strengths[:4],
        "areas_to_improve": areas_to_improve[:4],
        "recommendations": recommendations[:5],
        "weekly_goals": weekly_goals
    }

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx"}

MODEL_NAME = "qwen2.5:3b"

QUESTION_TIME_LIMIT = 120

# Ollama chatbot configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
CHAT_MODEL_NAME = "qwen2.5:3b"


# ==================================================
# INTERVIEW OPTIONS
# ==================================================

ROLES = [
    "Python Developer",
    "Software Engineer",
    "AI/ML Engineer",
    "Data Scientist",
    "Web Developer",
    "Java Developer"
]

INTERVIEW_TYPES = [
    "Technical",
    "HR",
    "Behavioral",
    "Mixed"
]

DIFFICULTIES = [
    "Beginner",
    "Intermediate",
    "Advanced"
]

QUESTION_COUNTS = {
    "Beginner": 10,
    "Intermediate": 15,
    "Advanced": 20
}


# ==================================================
# TECHNICAL QUESTION BANK
# ==================================================

QUESTION_BANK = {

    "Python Developer": [
        "What is Python and what are its main features?",
        "What is the difference between a list and a tuple?",
        "Explain Python variables and data types.",
        "What is the purpose of indentation in Python?",
        "What is the difference between == and is?",
        "What are Python dictionaries?",
        "Explain list comprehensions with an example.",
        "What is exception handling in Python?",
        "What are decorators in Python?",
        "Explain generators and iterators.",
        "What is the difference between shallow copy and deep copy?",
        "Explain object-oriented programming in Python.",
        "What is the Global Interpreter Lock?",
        "How does Python manage memory?",
        "Explain multithreading and multiprocessing.",
        "What is asynchronous programming?",
        "How would you optimize a slow Python application?",
        "Explain Python modules and packages.",
        "What are lambda functions?",
        "How do you test a Python application?"
    ],

    "Software Engineer": [
        "What is software engineering?",
        "Explain the software development life cycle.",
        "What is the difference between frontend and backend?",
        "What is object-oriented programming?",
        "What is the difference between a compiler and interpreter?",
        "Explain the four principles of OOP.",
        "What is the difference between an array and linked list?",
        "Explain stack and queue data structures.",
        "What is database normalization?",
        "What are REST APIs?",
        "Explain the SOLID principles.",
        "What is a design pattern?",
        "Explain microservices architecture.",
        "How do you identify performance bottlenecks?",
        "What is version control?",
        "Explain unit testing and integration testing.",
        "How would you design a scalable application?",
        "What is the difference between SQL and NoSQL?",
        "Explain software deployment.",
        "How do you debug a complex software issue?"
    ],

    "AI/ML Engineer": [
        "What is artificial intelligence?",
        "What is machine learning?",
        "Explain supervised and unsupervised learning.",
        "What is the difference between classification and regression?",
        "What is a training dataset?",
        "Explain overfitting and underfitting.",
        "What is the bias-variance trade-off?",
        "How does a decision tree work?",
        "What is cross-validation?",
        "Explain precision and recall.",
        "What is gradient descent?",
        "How does a neural network learn?",
        "Explain the vanishing gradient problem.",
        "How would you handle an imbalanced dataset?",
        "What is a confusion matrix?",
        "Explain feature engineering.",
        "What is regularization in machine learning?",
        "Explain ensemble learning.",
        "What is the purpose of an activation function?",
        "Explain the transformer architecture."
    ],

    "Data Scientist": [
        "What is data science?",
        "What is the difference between data and information?",
        "What is data preprocessing?",
        "Explain mean, median and mode.",
        "What is data visualization?",
        "How do you handle missing values?",
        "Explain correlation and covariance.",
        "What is feature engineering?",
        "What is hypothesis testing?",
        "Explain SQL and NoSQL databases.",
        "What is principal component analysis?",
        "How would you build a predictive model?",
        "Explain ensemble learning techniques.",
        "What is data leakage?",
        "How do you evaluate an imbalanced dataset?",
        "Explain statistical significance.",
        "What is exploratory data analysis?",
        "What is the difference between a population and a sample?",
        "How do you detect outliers?",
        "Explain model evaluation metrics."
    ],

    "Web Developer": [
        "What is HTML?",
        "What is the difference between HTML and CSS?",
        "What is JavaScript?",
        "What is the difference between id and class?",
        "What is responsive web design?",
        "Explain let, const and var.",
        "What is the Document Object Model?",
        "Explain synchronous and asynchronous JavaScript.",
        "What are JavaScript promises?",
        "How do REST APIs work?",
        "What is the virtual DOM?",
        "How would you optimize website performance?",
        "Explain authentication and authorization.",
        "What is cross-site scripting?",
        "What is responsive design?",
        "Explain CSS Flexbox and Grid.",
        "What is event bubbling?",
        "How does browser rendering work?",
        "What is a web server?",
        "How would you design a scalable website?"
    ],

    "Java Developer": [
        "What is Java?",
        "What are the main features of Java?",
        "Explain JDK, JRE and JVM.",
        "What is a class and an object?",
        "What is the difference between == and equals()?",
        "Explain inheritance and polymorphism.",
        "What is an interface?",
        "What is an abstract class?",
        "Explain exception handling in Java.",
        "What is the Java Collections Framework?",
        "Explain Java memory management.",
        "How does garbage collection work?",
        "Explain the internal working of HashMap.",
        "What is the difference between synchronized and volatile?",
        "Explain the Java Stream API.",
        "What is multithreading?",
        "What are constructors in Java?",
        "Explain method overloading and overriding.",
        "What is encapsulation?",
        "How does Java achieve platform independence?"
    ]
}


# ==================================================
# HR QUESTION BANK
# ==================================================

HR_QUESTIONS = [
    "Tell me about yourself.",
    "Why should we hire you?",
    "What are your strengths and weaknesses?",
    "Where do you see yourself in five years?",
    "Why do you want to work for our company?",
    "How do you handle pressure and deadlines?",
    "Describe your ideal work environment.",
    "What motivates you to perform well?",
    "How do you manage multiple responsibilities?",
    "What are your career goals?",
    "How do you respond to constructive feedback?",
    "What makes you a good team member?",
    "How would you handle a disagreement with your manager?",
    "Why did you choose this career?",
    "What do you expect from your first job?",
    "How do you adapt to new environments?",
    "What is your biggest professional achievement?",
    "How do you handle failure?",
    "Are you comfortable learning new technologies?",
    "Do you have any questions for the interviewer?"
]


# ==================================================
# BEHAVIORAL QUESTION BANK
# ==================================================

BEHAVIORAL_QUESTIONS = [
    "Describe a challenging situation you faced and how you handled it.",
    "Tell me about a time you worked successfully in a team.",
    "Describe a mistake you made and what you learned.",
    "How do you handle disagreements with teammates?",
    "Tell me about a time you showed leadership.",
    "Describe a time when you had to learn something quickly.",
    "Tell me about a time you solved a difficult problem.",
    "Describe a situation where you worked under pressure.",
    "Tell me about a time you received critical feedback.",
    "Describe a project where you took responsibility.",
    "Tell me about a time you helped another person.",
    "Describe a situation where you had to adapt to change.",
    "How did you handle a missed deadline?",
    "Tell me about a time you made an important decision.",
    "Describe a situation where you showed initiative.",
    "Tell me about a time you had conflicting priorities.",
    "Describe a time you resolved a team conflict.",
    "Tell me about a time you achieved a difficult goal.",
    "How do you respond when a plan does not work?",
    "Describe a time you went beyond your responsibilities."
]


# ==================================================
# QUESTION GENERATION
# FAST QUESTION LOADING - NO OLLAMA WAITING
# ==================================================

def get_question_count(difficulty):
    return QUESTION_COUNTS.get(difficulty, 10)


def get_fallback_questions(role, interview_type, difficulty):

    count = get_question_count(difficulty)

    technical = QUESTION_BANK.get(
        role,
        QUESTION_BANK["Software Engineer"]
    )

    if interview_type == "Technical":
        source = technical

    elif interview_type == "HR":
        source = HR_QUESTIONS

    elif interview_type == "Behavioral":
        source = BEHAVIORAL_QUESTIONS

    else:
        source = []

        for index in range(count):

            if index % 3 == 0:
                source.append(
                    technical[index % len(technical)]
                )

            elif index % 3 == 1:
                source.append(
                    HR_QUESTIONS[index % len(HR_QUESTIONS)]
                )

            else:
                source.append(
                    BEHAVIORAL_QUESTIONS[
                        index % len(BEHAVIORAL_QUESTIONS)
                    ]
                )

        return source[:count]

    return source[:count]


def generate_ai_questions(role, interview_type, difficulty):
    """
    Questions are loaded from the local question bank.
    Ollama is not called during interview startup.
    """

    questions = get_fallback_questions(
        role,
        interview_type,
        difficulty
    )

    print(
        f"Loaded {len(questions)} questions "
        f"for {role} - {interview_type} - {difficulty}"
    )

    return questions, "Question Bank"


# ==================================================
# COMMON HELPERS
# ==================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def clean_text(value, max_length=5000):

    if not isinstance(value, str):
        return ""

    return value.strip()[:max_length]


def safe_number(value, default=0, minimum=0, maximum=100000):

    try:
        number = float(value)

        if not (number >= minimum and number <= maximum):
            return default

        return number

    except (ValueError, TypeError):
        return default


def build_report_payload(
    results,
    average_score,
    role,
    interview_type,
    difficulty
):

    return {
        "results": results,
        "average_score": average_score,
        "role": role,
        "interview_type": interview_type,
        "difficulty": difficulty,
        "model_name": MODEL_NAME
    }


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():
    return render_template("welcome.html")

# ==================================================
# DASHBOARD
# ==================================================

# ==================================================
# DASHBOARD
# ==================================================


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        # Fetch logged-in user's details
        user = connection.execute("""
            SELECT id, name, email
            FROM users
            WHERE id = ?
        """, (session["user_id"],)).fetchone()

        if user is None:
            session.clear()
            return redirect(url_for("login"))

        total_interviews = connection.execute("""
            SELECT COUNT(*) AS total
            FROM interview_history
        """).fetchone()["total"]

        total_points = connection.execute("""
            SELECT COALESCE(SUM(reward_points), 0) AS points
            FROM interview_history
        """).fetchone()["points"]

        interviews = connection.execute("""
            SELECT *
            FROM interview_history
            ORDER BY id DESC
        """).fetchall()

        total_certificates = total_interviews

    finally:
        connection.close()

    improvement_plan = generate_improvement_plan(interviews)

    return render_template(
        "dashboard.html",
        user=user,
        total_interviews=total_interviews,
        total_points=total_points,
        total_certificates=total_certificates,
        improvement_plan=improvement_plan
    )

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:

        if request.method == "POST":

            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            college = request.form.get("college", "").strip()
            degree = request.form.get("degree", "").strip()
            department = request.form.get("department", "").strip()
            study_year = request.form.get("study_year", "").strip()
            graduation_year = request.form.get("graduation_year", "").strip()
            cgpa = request.form.get("cgpa", "").strip()
            skills = request.form.get("skills", "").strip()
            career_goal = request.form.get("career_goal", "").strip()
            linkedin = request.form.get("linkedin", "").strip()
            github = request.form.get("github", "").strip()
            bio = request.form.get("bio", "").strip()

            if not name:
                flash("Name cannot be empty.", "error")
            else:
                connection.execute("""
                    UPDATE users
                    SET name = ?,
                        phone = ?,
                        college = ?,
                        degree = ?,
                        department = ?,
                        study_year = ?,
                        graduation_year = ?,
                        cgpa = ?,
                        skills = ?,
                        career_goal = ?,
                        linkedin = ?,
                        github = ?,
                        bio = ?
                    WHERE id = ?
                """, (
                    name, phone, college, degree, department,
                    study_year, graduation_year, cgpa, skills,
                    career_goal, linkedin, github, bio,
                    session["user_id"]
                ))

                connection.commit()
                session["user_name"] = name
                flash("Your profile has been updated successfully!", "success")

            return redirect(url_for("profile"))

        user = connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

    finally:
        connection.close()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)


@app.route("/settings")
def settings():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        user = connection.execute(
            "SELECT name, email FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

    finally:
        connection.close()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template("settings.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ==================================================
# ANALYTICS DASHBOARD
# ==================================================

@app.route("/analytics")
def analytics():

    connection = get_db_connection()

    try:
        interviews = connection.execute("""
            SELECT *
            FROM interview_history
            ORDER BY id DESC
        """).fetchall()

    finally:
        connection.close()

    total_interviews = len(interviews)

    average_score = (
        round(
            sum(item["average_score"] for item in interviews)
            / total_interviews,
            1
        )
        if total_interviews else 0
    )

    total_questions = sum(
        item["total_questions"] for item in interviews
    )

    recent_interviews = []

    for item in interviews[:10]:
        recent_interviews.append({
            "id": item["id"],
            "role": item["role"],
            "interview_type": item["interview_type"],
            "difficulty": item["difficulty"],
            "average_score": item["average_score"],
            "total_questions": item["total_questions"],
            "created_at": item["created_at"]
        })

    score_history = [
        {
            "date": item["created_at"],
            "score": item["average_score"]
        }
        for item in reversed(interviews)
    ]

    return render_template(
        "analytics.html",
        total_interviews=total_interviews,
        average_score=average_score,
        total_questions=total_questions,
        recent_interviews=recent_interviews,
        score_history=score_history
    )

# ==================================================
# CERTIFICATES AND GRADE POINTS
# ==================================================

@app.route("/certificates")
def certificates():

    connection = get_db_connection()

    try:
        interviews = connection.execute("""
            SELECT *
            FROM interview_history
            ORDER BY id DESC
        """).fetchall()

        total_points = connection.execute("""
            SELECT COALESCE(SUM(reward_points), 0) AS points
            FROM interview_history
        """).fetchone()["points"]

    finally:
        connection.close()

    total_certificates = len(interviews)

    return render_template(
        "certificates.html",
        interviews=interviews,
        total_points=total_points,
        total_certificates=total_certificates
    )
# ==================================================
# DOWNLOAD INTERVIEW CERTIFICATE
# ==================================================

@app.route("/download-certificate/<int:interview_id>", methods=["POST"])
def download_certificate(interview_id):

    # Get the student's name from the form
    student_name = request.form.get("student_name", "").strip()

    if not student_name:
        return "Please enter your name before downloading the certificate.", 400

    if len(student_name) > 100:
        return "Student name is too long.", 400

    # Fetch the selected completed interview
    connection = get_db_connection()

    try:
        interview = connection.execute("""
            SELECT *
            FROM interview_history
            WHERE id = ?
        """, (interview_id,)).fetchone()

    finally:
        connection.close()

    if interview is None:
        abort(404, description="Interview record not found.")

    # Read interview details
    role = interview["role"]
    interview_type = interview["interview_type"]
    difficulty = interview["difficulty"]
    score = float(interview["average_score"])
    points = interview["reward_points"]
    interview_date = interview["created_at"]

    # Determine performance level
    if score >= 90:
        performance_level = "Outstanding Performance"
    elif score >= 75:
        performance_level = "Excellence"
    elif score >= 60:
        performance_level = "Good Performance"
    else:
        performance_level = "Participation"

    # Create the PDF in memory
    pdf_buffer = BytesIO()

    page_size = landscape(A4)
    pdf = canvas.Canvas(pdf_buffer, pagesize=page_size)

    page_width, page_height = page_size

    # Background
    pdf.setFillColor(colors.white)
    pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    # Outer certificate border
    pdf.setStrokeColor(colors.HexColor("#172554"))
    pdf.setLineWidth(5)
    pdf.rect(25, 25, page_width - 50, page_height - 50)

    # Inner gold border
    pdf.setStrokeColor(colors.HexColor("#D4AF37"))
    pdf.setLineWidth(2)
    pdf.rect(36, 36, page_width - 72, page_height - 72)

    # Organization name
    pdf.setFillColor(colors.HexColor("#6D28D9"))
    pdf.setFont("Helvetica-Bold", 25)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 90,
        "INTERVIEWGEN AI"
    )

    # Certificate heading
    pdf.setFillColor(colors.HexColor("#172554"))
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 140,
        "CERTIFICATE OF ACHIEVEMENT"
    )

    # Subtitle
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 170,
        "This certificate is proudly presented to"
    )

    # Student name
    pdf.setFillColor(colors.HexColor("#6D28D9"))
    pdf.setFont("Helvetica-Bold", 27)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 220,
        student_name
    )

    # Description
    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 255,
        "For successfully completing a mock interview on InterviewGen AI."
    )

    # Performance level
    pdf.setFillColor(colors.HexColor("#172554"))
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 300,
        performance_level
    )

    # Interview details
    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica", 12)

    details = [
        f"Role: {role}",
        f"Interview Type: {interview_type}",
        f"Difficulty: {difficulty}",
        f"Final Score: {score:.1f}%",
        f"Grade Points Earned: {points}",
        f"Completion Date: {interview_date}"
    ]

    y_position = page_height - 340

    for detail in details:
        pdf.drawCentredString(
            page_width / 2,
            y_position,
            detail
        )
        y_position -= 19

    # Unique certificate ID
    certificate_id = f"IGA-{interview_id}-{uuid.uuid4().hex[:8].upper()}"

    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(
        page_width / 2,
        75,
        f"Certificate ID: {certificate_id}"
    )

    pdf.drawCentredString(
        page_width / 2,
        58,
        "Generated by InterviewGen AI"
    )

    # Finish PDF
    pdf.save()
    pdf_buffer.seek(0)

    # Download the certificate
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"InterviewGenAI_Certificate_{interview_id}.pdf"
    )
# ==================================================
# AI INTERVIEWER SELECTION
# ==================================================

@app.route("/interviewer-selection")
def interviewer_selection():
    return render_template("interviewer_selection.html")


# ==================================================
# INTERVIEW SETUP
# ==================================================

@app.route("/interview-setup")
def interview_setup():

    selected_interviewer = request.args.get(
        "interviewer",
        "Rahul"
    )

    allowed_interviewers = [
        "Rahul",
        "Priya",
        "Arjun",
        "Meera"
    ]

    if selected_interviewer not in allowed_interviewers:
        selected_interviewer = "Rahul"

    return render_template(
        "interview_setup.html",
        roles=ROLES,
        interview_types=INTERVIEW_TYPES,
        difficulties=DIFFICULTIES,
        question_counts=QUESTION_COUNTS,
        selected_interviewer=selected_interviewer
    )


# ==================================================
# START INTERVIEW
# ==================================================

@app.route("/start-interview", methods=["POST"])
def start_interview():

    role = request.form.get(
        "role",
        "Software Engineer"
    )

    interview_type = request.form.get(
        "interview_type",
        "Technical"
    )

    difficulty = request.form.get(
        "difficulty",
        "Beginner"
    )

    interviewer = request.form.get(
        "interviewer",
        "Rahul"
    )

    # Validate role
    if role not in ROLES:
        role = "Software Engineer"

    # Validate interview type
    if interview_type not in INTERVIEW_TYPES:
        interview_type = "Technical"

    # Validate difficulty
    if difficulty not in DIFFICULTIES:
        difficulty = "Beginner"

    # Validate interviewer
    allowed_interviewers = [
        "Rahul",
        "Priya",
        "Arjun",
        "Meera"
    ]

    if interviewer not in allowed_interviewers:
        interviewer = "Rahul"

    # Generate questions only once
    questions, question_source = generate_ai_questions(
        role,
        interview_type,
        difficulty
    )

    # ADVANCED: Show mode selection first
    if difficulty == "Advanced":

        return render_template(
            "interview_mode.html",
            role=role,
            interview_type=interview_type,
            difficulty=difficulty,
            interviewer=interviewer,
            questions=questions,
            question_source=question_source,
            question_time_limit=QUESTION_TIME_LIMIT
        )

    # BEGINNER / INTERMEDIATE: Continue existing flow
    return render_template(
        "interview.html",
        questions=questions,
        role=role,
        interview_type=interview_type,
        difficulty=difficulty,
        interviewer=interviewer,
        question_source=question_source,
        question_time_limit=QUESTION_TIME_LIMIT,
        interview_mode="text"
    )


# ==================================================
# BEGIN INTERVIEW AFTER MODE SELECTION
# ==================================================

@app.route("/begin-interview", methods=["POST"])
def begin_interview():

    role = request.form.get(
        "role",
        "Software Engineer"
    )

    interview_type = request.form.get(
        "interview_type",
        "Technical"
    )

    difficulty = request.form.get(
        "difficulty",
        "Advanced"
    )

    interviewer = request.form.get(
        "interviewer",
        "Rahul"
    )

    interview_mode = request.form.get(
        "interview_mode",
        ""
    ).lower()

    # Validate selections
    if role not in ROLES:
        role = "Software Engineer"

    if interview_type not in INTERVIEW_TYPES:
        interview_type = "Technical"

    if difficulty != "Advanced":
        return "Invalid interview difficulty.", 400

    if interview_mode not in ["video", "text"]:
        return "Please select a valid interview mode.", 400

    allowed_interviewers = [
        "Rahul",
        "Priya",
        "Arjun",
        "Meera"
    ]

    if interviewer not in allowed_interviewers:
        interviewer = "Rahul"

    # Preserve the exact questions generated earlier
    try:
        questions = json.loads(
            request.form.get("questions_json", "[]")
        )

        if (
            not isinstance(questions, list)
            or not questions
            or len(questions) > 20
        ):
            raise ValueError("Invalid questions.")

        questions = [
            clean_text(question, 1000)
            for question in questions
            if isinstance(question, str) and question.strip()
        ]

        if not questions:
            raise ValueError("No valid questions.")

    except (ValueError, TypeError, json.JSONDecodeError):
        return "The interview questions could not be loaded. Please start again.", 400

    return render_template(
        "interview.html",
        questions=questions,
        role=role,
        interview_type=interview_type,
        difficulty=difficulty,
        interviewer=interviewer,
        question_source="Question Bank",
        question_time_limit=QUESTION_TIME_LIMIT,
        interview_mode=interview_mode
    )



# ==================================================
# SUBMIT COMPLETE INTERVIEW
# ==================================================

@app.route("/submit-interview", methods=["POST"])
def submit_interview():

    role = request.form.get("role", "Software Engineer")
    interview_type = request.form.get("interview_type", "Technical")
    difficulty = request.form.get("difficulty", "Beginner")

    # Validate interview details
    if role not in ROLES:
        role = "Software Engineer"

    if interview_type not in INTERVIEW_TYPES:
        interview_type = "Technical"

    if difficulty not in DIFFICULTIES:
        difficulty = "Beginner"

    questions = []
    clean_answers = []
    clean_times = []

    try:
        # ------------------------------------------
        # 1. GET INTERVIEW DATA
        # ------------------------------------------

        questions = json.loads(
            request.form.get("questions_json", "[]")
        )

        answers = json.loads(
            request.form.get("answers_json", "[]")
        )

        time_taken = json.loads(
            request.form.get("time_taken_json", "[]")
        )

        if not isinstance(questions, list):
            raise ValueError("Invalid question data.")

        if not isinstance(answers, list):
            raise ValueError("Invalid answer data.")

        if not isinstance(time_taken, list):
            time_taken = []

        questions = [
            clean_text(question, 1000)
            for question in questions
            if isinstance(question, str) and question.strip()
        ]

        if not questions:
            return "No interview questions were submitted.", 400

        if len(questions) > 20:
            return "Too many interview questions were submitted.", 400

        # ------------------------------------------
        # 2. CLEAN ANSWERS AND TIME DATA
        # ------------------------------------------

        for index in range(len(questions)):

            if index < len(answers) and isinstance(answers[index], str):
                answer = clean_text(answers[index], 10000)
            else:
                answer = ""

            clean_answers.append(answer)

            if index < len(time_taken):
                seconds = safe_number(
                    time_taken[index],
                    default=0,
                    minimum=0,
                    maximum=QUESTION_TIME_LIMIT
                )
            else:
                seconds = 0

            clean_times.append(int(seconds))

        # ------------------------------------------
        # 3. EVALUATE ANSWERS USING AI
        # ------------------------------------------

        ai_results = evaluate_interview(
            questions=questions,
            answers=clean_answers,
            role=role
        )

        if not isinstance(ai_results, list):
            raise ValueError("AI evaluation returned invalid results.")

        # ------------------------------------------
        # 4. PREPARE QUESTION-WISE RESULTS
        # ------------------------------------------

        results = []

        for index, question in enumerate(questions):

            answer = clean_answers[index]

            if not answer:

                evaluation = {
                    "score": 0,
                    "strengths": "No answer provided.",
                    "weaknesses": "The question was not answered.",
                    "suggestions": "Try to provide a clear answer with an example."
                }

            elif (
                index < len(ai_results)
                and isinstance(ai_results[index], dict)
            ):

                evaluation = ai_results[index]

            else:

                evaluation = {
                    "score": 0,
                    "strengths": "Evaluation unavailable.",
                    "weaknesses": "The AI could not evaluate this answer.",
                    "suggestions": "Please try again."
                }

            score = safe_number(
                evaluation.get("score", 0),
                default=0,
                minimum=0,
                maximum=100
            )

            results.append({
                "question": question,
                "answer": answer,
                "score": round(score, 1),
                "word_count": len(answer.split()),
                "time_taken": clean_times[index],

                "strengths": clean_text(
                    evaluation.get(
                        "strengths",
                        "No strengths identified."
                    )
                ),

                "weaknesses": clean_text(
                    evaluation.get(
                        "weaknesses",
                        "No weaknesses identified."
                    )
                ),

                "suggestions": clean_text(
                    evaluation.get(
                        "suggestions",
                        "Continue practising."
                    )
                )
            })

            # ------------------------------------------
        # 5. CALCULATE AVERAGE SCORE AND GRADE POINTS
        # ------------------------------------------

        average_score = round(
            sum(item["score"] for item in results) / len(results),
            1
        )

        reward_points = calculate_reward_points(average_score)

                # ------------------------------------------
        # 6. SAVE RESULTS AND GRADE POINTS TO DATABASE
        # ------------------------------------------

        connection = get_db_connection()

        try:
            connection.execute("""
                INSERT INTO interview_history (
                    role,
                    interview_type,
                    difficulty,
                    average_score,
                    total_questions,
                    results_json,
                    created_at,
                    reward_points
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                role,
                interview_type,
                difficulty,
                average_score,
                len(results),
                json.dumps(results),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                reward_points
            ))

            connection.commit()

            print("Interview results and grade points saved successfully!")

        finally:
            connection.close()
        # ------------------------------------------
        # 7. PREPARE REPORT DATA
        # ------------------------------------------

        report_payload = build_report_payload(
            results,
            average_score,
            role,
            interview_type,
            difficulty
        )

        # ------------------------------------------
        # 8. DISPLAY INTERVIEW REPORT
        # ------------------------------------------

        return render_template(
            "report.html",
            results=results,
            average_score=average_score,
            total_questions=len(results),
            role=role,
            interview_type=interview_type,
            difficulty=difficulty,
            model_name=MODEL_NAME,
            report_payload=report_payload
        )

    except Exception as error:

        print("INTERVIEW EVALUATION ERROR:", repr(error))

        # ------------------------------------------
        # 9. PREPARE FALLBACK RESULTS
        # ------------------------------------------

        results = []

        for index, question in enumerate(questions):

            answer = (
                clean_answers[index]
                if index < len(clean_answers)
                else ""
            )

            seconds = (
                clean_times[index]
                if index < len(clean_times)
                else 0
            )

            results.append({
                "question": question,
                "answer": answer,
                "score": 0,
                "word_count": len(answer.split()),
                "time_taken": seconds,
                "strengths": "AI evaluation could not be completed.",
                "weaknesses": "The evaluation service returned an error.",
                "suggestions": "Check Ollama and try again."
            })

        # ------------------------------------------
        # 10. DISPLAY FALLBACK REPORT
        # ------------------------------------------

        report_payload = build_report_payload(
            results,
            0,
            role,
            interview_type,
            difficulty
        )

        return render_template(
            "feedback.html",
            results=results,
            average_score=0,
            total_questions=len(results),
            role=role,
            interview_type=interview_type,
            difficulty=difficulty,
            model_name=MODEL_NAME,
            evaluation_error=True,
            report_payload=report_payload
        )
# ==================================================
# PDF REPORT DOWNLOAD
# ==================================================

@app.route("/download-report", methods=["POST"])
def download_report():

    try:

        report_data = json.loads(
            request.form.get("report_data", "{}")
        )

        if not isinstance(report_data, dict):
            raise ValueError("Invalid report data.")

        results = report_data.get("results", [])

        if not isinstance(results, list) or not results:
            return "No report data is available.", 400

        if len(results) > 20:
            return "Invalid report question count.", 400

        role = clean_text(
            report_data.get("role", "Software Engineer"),
            100
        )

        interview_type = clean_text(
            report_data.get("interview_type", "Technical"),
            50
        )

        difficulty = clean_text(
            report_data.get("difficulty", "Beginner"),
            50
        )

        valid_results = []

        for item in results:

            if not isinstance(item, dict):
                continue

            score = safe_number(
                item.get("score", 0),
                default=0,
                minimum=0,
                maximum=100
            )

            word_count = int(
                safe_number(
                    item.get("word_count", 0),
                    default=0,
                    minimum=0,
                    maximum=100000
                )
            )

            time_taken = int(
                safe_number(
                    item.get("time_taken", 0),
                    default=0,
                    minimum=0,
                    maximum=QUESTION_TIME_LIMIT
                )
            )

            valid_results.append({

                "question": clean_text(
                    item.get("question", ""),
                    1000
                ),

                "answer": clean_text(
                    item.get("answer", ""),
                    10000
                ),

                "score": score,

                "word_count": word_count,

                "time_taken": time_taken,

                "strengths": clean_text(
                    item.get("strengths", ""),
                    2000
                ),

                "weaknesses": clean_text(
                    item.get("weaknesses", ""),
                    2000
                ),

                "suggestions": clean_text(
                    item.get("suggestions", ""),
                    2000
                )

            })

        if not valid_results:
            return "No valid report results were submitted.", 400

        average_score = round(
            sum(item["score"] for item in valid_results)
            / len(valid_results),
            1
        )

        total_words = sum(
            item["word_count"]
            for item in valid_results
        )

        total_time = sum(
            item["time_taken"]
            for item in valid_results
        )

        buffer = io.BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#28245F"),
            alignment=TA_CENTER,
            spaceAfter=8
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=18
        )

        section_style = ParagraphStyle(
            "ReportSection",
            parent=styles["Heading2"],
            fontSize=14,
            leading=19,
            textColor=colors.HexColor("#4034A6"),
            spaceBefore=12,
            spaceAfter=8
        )

        question_style = ParagraphStyle(
            "ReportQuestion",
            parent=styles["Heading3"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#28245F"),
            spaceBefore=8,
            spaceAfter=7
        )

        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=14,
            spaceAfter=6,
            splitLongWords=1
        )

        small_style = ParagraphStyle(
            "ReportSmall",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#475569")
        )

        def safe_paragraph(value, style=body_style):

            value = str(value or "")

            value = (
                value.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br/>")
            )

            return Paragraph(value, style)

        def format_time(seconds):

            minutes = seconds // 60
            remaining_seconds = seconds % 60

            return f"{minutes} min {remaining_seconds} sec"

        story = []

        story.append(
            Paragraph("InterviewGen AI", title_style)
        )

        story.append(
            Paragraph(
                "AI-Based Mock Interview &amp; Performance Report",
                subtitle_style
            )
        )

        story.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=colors.HexColor("#D8D5F5")
            )
        )

        story.append(Spacer(1, 12))

        summary_data = [

            ["Job Role", role],

            ["Interview Type", interview_type],

            ["Difficulty", difficulty],

            ["Questions Evaluated", str(len(valid_results))],

            ["Total Words", str(total_words)],

            ["Total Interview Time", format_time(total_time)],

            ["Overall Score", f"{average_score}/100"]

        ]

        summary_table = Table(
            summary_data,
            colWidths=[48 * mm, 115 * mm]
        )

        summary_table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F0EEFF")
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#172033")
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),

                (
                    "FONTNAME",
                    (1, 0),
                    (1, -1),
                    "Helvetica"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#DCE1EC")
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )

            ])
        )

        story.append(
            Paragraph("Interview Summary", section_style)
        )

        story.append(summary_table)

        story.append(
            Paragraph(
                "Question-by-Question Analysis",
                section_style
            )
        )

        for index, item in enumerate(valid_results, start=1):

            section = [

                Paragraph(
                    f"Question {index} - "
                    f"Score: {item['score']:.1f}/100",
                    question_style
                ),

                safe_paragraph(
                    "<b>Question:</b> " + item["question"]
                ),

                safe_paragraph(
                    "<b>Your Answer:</b> "
                    + (
                        item["answer"]
                        or "No answer provided."
                    )
                ),

                safe_paragraph(
                    "<b>Time Taken:</b> "
                    + format_time(item["time_taken"])
                ),

                safe_paragraph(
                    "<b>Word Count:</b> "
                    + str(item["word_count"])
                ),

                safe_paragraph(
                    "<b>Strengths:</b> " + item["strengths"]
                ),

                safe_paragraph(
                    "<b>Areas to Improve:</b> "
                    + item["weaknesses"]
                ),

                safe_paragraph(
                    "<b>Suggestions:</b> "
                    + item["suggestions"]
                ),

                Spacer(1, 8),

                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=colors.HexColor("#DCE1EC")
                ),

                Spacer(1, 8)

            ]

            story.append(KeepTogether(section))

        story.append(Spacer(1, 12))

        story.append(
            Paragraph("Important Note", section_style)
        )

        story.append(
            safe_paragraph(
                "This report is generated using a locally running AI model. "
                "Scores and suggestions are estimates and should be used "
                "as guidance for interview practice, not as a guarantee "
                "of job readiness.",
                small_style
            )
        )

        def add_page_number(canvas, doc):

            canvas.saveState()

            canvas.setFont("Helvetica", 8)

            canvas.setFillColor(
                colors.HexColor("#64748B")
            )

            canvas.drawString(
                18 * mm,
                10 * mm,
                "InterviewGen AI | Practice. Improve. Succeed."
            )

            canvas.drawRightString(
                A4[0] - 18 * mm,
                10 * mm,
                f"Page {doc.page}"
            )

            canvas.restoreState()

        document.build(
            story,
            onFirstPage=add_page_number,
            onLaterPages=add_page_number
        )

        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="InterviewGen_AI_Report.pdf",
            mimetype="application/pdf"
        )

    except Exception as error:

        print("PDF REPORT ERROR:", error)

        return (
            "Unable to generate the PDF report. Please try again.",
            500
        )


# ==================================================
# SINGLE ANSWER SUBMISSION
# ==================================================

@app.route("/submit-answer", methods=["POST"])
def submit_answer():

    question = request.form.get("question", "")

    answer = request.form.get("answer", "")

    role = request.form.get(
        "role",
        "Software Engineer"
    )

    evaluation = evaluate_answer(
        question=question,
        answer=answer,
        role=role
    )

    return render_template(
        "feedback.html",
        evaluation=evaluation,
        average_score=evaluation.get("score", 0),
        results=[],
        total_questions=1,
        role=role,
        interview_type="Technical",
        difficulty="Beginner",
        model_name=MODEL_NAME
    )


# ==================================================
# RESUME ANALYSIS PAGE
# ==================================================

@app.route("/resume-analysis")
def resume_analysis():

    return render_template("resume_analysis.html")


# ==================================================
# ANALYZE RESUME
# ==================================================

@app.route("/analyze-resume", methods=["POST"])
def analyze_resume_route():

    if "resume" not in request.files:
        return render_template(
            "resume_analysis.html",
            error="Please select a resume file.",
            target_role=request.form.get("target_role", "")
        )

    file = request.files["resume"]
    target_role = request.form.get("target_role", "").strip()

    if not target_role:
        return render_template(
            "resume_analysis.html",
            error="Please select your target job role.",
            target_role=""
        )

    if file.filename == "":
        return render_template(
            "resume_analysis.html",
            error="No file selected.",
            target_role=target_role
        )

    if not allowed_file(file.filename):
        return render_template(
            "resume_analysis.html",
            error="Only PDF and DOCX files are allowed.",
            target_role=target_role
        )

    filename = secure_filename(file.filename)

    unique_filename = str(uuid.uuid4()) + "_" + filename

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_filename
    )

    try:
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        file.save(filepath)

        analysis = analyze_resume(filepath, target_role)

        return render_template(
            "resume_analysis.html",
            result=analysis,
            filename=filename,
            target_role=target_role
        )

    except Exception as error:
        print("RESUME ANALYSIS ERROR:", repr(error))

        return render_template(
            "resume_analysis.html",
            error=f"Resume analysis failed: {error}",
            target_role=target_role
        )

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
# ==================================================
# VOICE PRACTICE PAGE
# ==================================================

@app.route("/voice-practice")
def voice_practice():
    return render_template("voice_practice.html")
@app.route("/analyze-frame", methods=["POST"])
def analyze_frame():
    try:
        data = request.get_json()

        if not data or "image" not in data:
            return jsonify({
                "success": False,
                "message": "No image received"
            }), 400

        image_data = data["image"].split(",", 1)[-1]
        image_bytes = base64.b64decode(image_data)

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:
            return jsonify({
                "success": False,
                "message": "Invalid image"
            }), 400

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        cascade_path = (
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        face_detector = cv2.CascadeClassifier(
            cascade_path
        )

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60)
        )

        return jsonify({
            "success": True,
            "face_detected": len(faces) > 0,
            "face_count": len(faces),
            "message": (
                "Face detected"
                if len(faces) > 0
                else "No face detected"
            )
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500

# ==================================================
# AI INTERVIEW ASSISTANT PAGE
# ==================================================

@app.route("/chatbot")
def chatbot():

    return render_template("chatbot.html")


# ==================================================
# AI INTERVIEW ASSISTANT API
# ==================================================

@app.route("/chatbot-api", methods=["POST"])
def chatbot_api():

    try:

        data = request.get_json(silent=True) or {}

        message = clean_text(
            data.get("message", ""),
            3000
        )

        history = data.get("history", [])

        if not message:

            return {
                "reply": "Please enter a message so I can help you."
            }, 400

        if not isinstance(history, list):
            history = []

        messages = [

            {
                "role": "system",
                "content": (
                    "You are InterviewGen AI, a friendly and helpful "
                    "interview preparation assistant. Help students "
                    "prepare for technical, HR, behavioral and AI/ML "
                    "interviews. Explain concepts in simple English. "
                    "Give practical examples, sample interview answers, "
                    "coding guidance and placement preparation tips. "
                    "When explaining code, use clear step-by-step "
                    "instructions. Keep answers relevant to the "
                    "user's question. Use readable formatting."
                )
            }

        ]

        # Add recent conversation history.
        for item in history[-10:]:

            if not isinstance(item, dict):
                continue

            role = item.get("role")

            content = item.get("content", "")

            if (
                role in ["user", "assistant"]
                and isinstance(content, str)
                and content.strip()
            ):

                messages.append({

                    "role": role,

                    "content": content[:3000]

                })

        # Add the current user message.
        messages.append({

            "role": "user",

            "content": message

        })

        payload = {

            "model": CHAT_MODEL_NAME,

            "messages": messages,

            "stream": False,

            "options": {

                "temperature": 0.7

            }

        }

        response = requests.post(

            OLLAMA_URL,

            json=payload,

            timeout=180

        )

        response.raise_for_status()

        result = response.json()

        reply = result.get(
            "message", {}
        ).get(
            "content", ""
        )

        if not reply:

            reply = (
                "I couldn't generate a response. "
                "Please try asking your question again."
            )

        return {

            "reply": reply.strip()

        }

    except requests.exceptions.ConnectionError:

        print("CHATBOT ERROR: Ollama is not running.")

        return {

            "reply": (
                "I cannot connect to Ollama right now. "
                "Please make sure Ollama is running on your computer."
            )

        }, 503

    except requests.exceptions.Timeout:

        print("CHATBOT ERROR: Ollama request timed out.")

        return {

            "reply": (
                "The AI is taking too long to respond. "
                "Please try again with a shorter question."
            )

        }, 504

    except requests.exceptions.RequestException as error:

        print("CHATBOT REQUEST ERROR:", error)

        return {

            "reply": (
                "There was a problem communicating with the AI model. "
                "Please try again."
            )

        }, 500

    except Exception as error:

        print("CHATBOT ERROR:", error)

        return {

            "reply": "Something went wrong. Please try again."

        }, 500


# ==================================================
# FILE SIZE ERROR
# ==================================================

@app.errorhandler(413)
def file_too_large(error):

    return render_template(
        "resume_analysis.html",
        error="File is too large. Please upload a file below 5 MB."
    ), 413


# ==================================================
# PAGE NOT FOUND
# ==================================================

@app.errorhandler(404)
def page_not_found(error):

    return "Page not found. Please check the URL.", 404


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template(
                "register.html",
                error="Please fill in all fields."
            )

        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must contain at least 8 characters."
            )

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
                """,
                (name, email, hashed_password)
            )

            connection.commit()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="Email already registered."
            )

        finally:
            connection.close()

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = get_db_connection()

        try:
            user = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

            if user and check_password_hash(user["password"], password):

                session["user_id"] = user["id"]
                session["user_name"] = user["name"]

                return redirect(url_for("dashboard"))

            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        finally:
            connection.close()

    return render_template("login.html")
# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
    