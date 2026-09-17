import os
import random
from functools import wraps
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from cryptography.fernet import Fernet, InvalidToken

from database import supabase


load_dotenv()


app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY",
    "change-this-secret"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv("COOKIE_SECURE", "false").lower() == "true"
)


ENCRYPTION_KEY = os.getenv("QUESTION_ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise RuntimeError(
        "QUESTION_ENCRYPTION_KEY is missing from .env"
    )

cipher = Fernet(ENCRYPTION_KEY.encode())


def encrypt_text(value):
    return cipher.encrypt(
        (value or "").encode()
    ).decode()


def decrypt_text(value):
    try:
        return cipher.decrypt(
            value.encode()
        ).decode()
    except (InvalidToken, AttributeError):
        return "[Encrypted data unavailable]"


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))

            if session.get("role") not in roles:
                flash("Access denied for your role.", "danger")
                return redirect(url_for("dashboard"))

            return view(*args, **kwargs)

        return wrapped

    return decorator


def decrypt_question(row):
    row = dict(row)

    encrypted_fields = [
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer"
    ]

    for field in encrypted_fields:
        row[field] = decrypt_text(row[field])

    return row


@app.context_processor
def inject_year():
    return {
        "current_year": datetime.now().year
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        result = (
            supabase
            .table("users")
            .select("*")
            .eq("username", username)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )

        user = result.data[0] if result.data else None

        if user and check_password_hash(
            user["password_hash"],
            password
        ):
            session.clear()

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            flash("Login successful.", "success")

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid username or password.",
            "danger"
        )

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            ""
        ).strip().upper()

        valid_roles = {
            "ADMIN",
            "QUESTION_SETTER",
            "CUSTODIAN",
            "EXAM_CENTER"
        }

        if (
            len(password) < 8
            or role not in valid_roles
        ):
            flash(
                "Use a valid role and a password of at least 8 characters.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        exists = (
            supabase
            .table("users")
            .select("id")
            .eq("username", username)
            .limit(1)
            .execute()
        )

        if exists.data:
            flash(
                "Username already exists.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        supabase.table("users").insert({
            "username": username,
            "password_hash": generate_password_hash(
                password
            ),
            "role": role,
            "is_active": True
        }).execute()

        flash(
            "Account created. You can now log in.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(
        url_for("login")
    )


@app.route("/dashboard")
@login_required
def dashboard():
    total = len(
        supabase
        .table("questions")
        .select("id")
        .execute()
        .data
    )

    pending = len(
        supabase
        .table("questions")
        .select("id")
        .eq("status", "PENDING")
        .execute()
        .data
    )

    approved = len(
        supabase
        .table("questions")
        .select("id")
        .eq("status", "APPROVED")
        .execute()
        .data
    )

    papers = len(
        supabase
        .table("generated_papers")
        .select("id")
        .execute()
        .data
    )

    recent = (
        supabase
        .table("generated_papers")
        .select("*")
        .order("id", desc=True)
        .limit(5)
        .execute()
        .data
    )

    statistics = {
        "total_questions": total,
        "pending_questions": pending,
        "approved_questions": approved,
        "generated_papers": papers
    }

    return render_template(
        "dashboard.html",
        statistics=statistics,
        recent_papers=recent
    )


@app.route("/add-question", methods=["GET", "POST"])
@role_required("ADMIN", "QUESTION_SETTER")
def add_question():
    if request.method == "POST":
        data = {
            "subject": request.form.get(
                "subject",
                ""
            ).strip(),

            "unit": request.form.get(
                "unit",
                ""
            ).strip(),

            "question_text": encrypt_text(
                request.form.get(
                    "question_text",
                    ""
                ).strip()
            ),

            "option_a": encrypt_text(
                request.form.get(
                    "option_a",
                    ""
                ).strip()
            ),

            "option_b": encrypt_text(
                request.form.get(
                    "option_b",
                    ""
                ).strip()
            ),

            "option_c": encrypt_text(
                request.form.get(
                    "option_c",
                    ""
                ).strip()
            ),

            "option_d": encrypt_text(
                request.form.get(
                    "option_d",
                    ""
                ).strip()
            ),

            "correct_answer": encrypt_text(
                request.form.get(
                    "correct_answer",
                    ""
                ).strip().upper()
            ),

            "difficulty": request.form.get(
                "difficulty",
                "Medium"
            ),

            "created_by": session["user_id"],

            "status": (
                "APPROVED"
                if session["role"] == "ADMIN"
                else "PENDING"
            )
        }

        if (
            not data["subject"]
            or not data["question_text"].strip()
        ):
            flash(
                "Subject and question text are required.",
                "danger"
            )

            return render_template(
                "add_question.html"
            )

        supabase.table("questions").insert(
            data
        ).execute()

        flash(
            "Question encrypted and stored securely.",
            "success"
        )

        return redirect(
            url_for("question_bank")
        )

    return render_template(
        "add_question.html"
    )


@app.route("/question-bank")
@login_required
def question_bank():
    subject = request.args.get(
        "subject",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip().upper()

    query = supabase.table(
        "questions"
    ).select("*")

    if subject:
        query = query.ilike(
            "subject",
            subject
        )

    if status in {
        "PENDING",
        "APPROVED",
        "REJECTED"
    }:
        query = query.eq(
            "status",
            status
        )

    rows = (
        query
        .order("id", desc=True)
        .execute()
        .data
    )

    questions = [
        decrypt_question(row)
        for row in rows
    ]

    return render_template(
        "question_bank.html",
        questions=questions,
        subject=subject,
        status=status
    )


@app.route(
    "/review-question/<int:question_id>/<action>",
    methods=["POST"]
)
@role_required("ADMIN")
def review_question(question_id, action):
    if action not in {
        "approve",
        "reject"
    }:
        flash(
            "Invalid action.",
            "danger"
        )

        return redirect(
            url_for("question_bank")
        )

    status = (
        "APPROVED"
        if action == "approve"
        else "REJECTED"
    )

    (
        supabase
        .table("questions")
        .update({
            "status": status
        })
        .eq("id", question_id)
        .execute()
    )

    flash(
        f"Question {status.lower()}.",
        "success"
    )

    return redirect(
        url_for("question_bank")
    )


@app.route("/generate-paper", methods=["GET", "POST"])
@role_required("ADMIN")
def generate_paper():
    if request.method == "POST":
        title = request.form.get(
            "exam_title",
            ""
        ).strip()

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        exam_date = request.form.get(
            "exam_date",
            ""
        ).strip()

        total_marks = int(
            request.form.get(
                "total_marks",
                "1"
            )
        )

        duration = request.form.get(
            "duration",
            ""
        ).strip()

        count = min(
            max(
                int(
                    request.form.get(
                        "question_count",
                        "10"
                    )
                ),
                1
            ),
            100
        )

        rows = (
            supabase
            .table("questions")
            .select("*")
            .ilike("subject", subject)
            .eq("status", "APPROVED")
            .execute()
            .data
        )

        random.shuffle(rows)

        selected = [
            decrypt_question(row)
            for row in rows[:count]
        ]

        if not selected:
            flash(
                "No approved questions found for this subject.",
                "warning"
            )

            return render_template(
                "generate_paper.html"
            )

        paper = (
            supabase
            .table("generated_papers")
            .insert({
                "exam_title": title,
                "subject": subject,
                "exam_date": exam_date,
                "total_marks": total_marks,
                "duration": duration,
                "question_count": len(selected),
                "created_by": session["user_id"]
            })
            .execute()
            .data[0]
        )

        paper_rows = [
            {
                "paper_id": paper["id"],
                "question_id": question["id"],
                "position": index
            }
            for index, question in enumerate(
                selected,
                start=1
            )
        ]

        (
            supabase
            .table("paper_questions")
            .insert(paper_rows)
            .execute()
        )

        flash(
            "Question paper generated and stored securely.",
            "success"
        )

        return redirect(
            url_for(
                "view_paper",
                paper_id=paper["id"]
            )
        )

    return render_template(
        "generate_paper.html"
    )


@app.route("/paper/<int:paper_id>")
@login_required
def view_paper(paper_id):
    paper_result = (
        supabase
        .table("generated_papers")
        .select("*")
        .eq("id", paper_id)
        .limit(1)
        .execute()
    )

    if not paper_result.data:
        return "Paper not found", 404

    paper = paper_result.data[0]

    links = (
        supabase
        .table("paper_questions")
        .select("position, question_id")
        .eq("paper_id", paper_id)
        .order("position")
        .execute()
        .data
    )

    questions = []

    for link in links:
        result = (
            supabase
            .table("questions")
            .select("*")
            .eq("id", link["question_id"])
            .limit(1)
            .execute()
        )

        if result.data:
            question = decrypt_question(
                result.data[0]
            )

            question["position"] = link["position"]

            questions.append(question)

    return render_template(
        "generated_paper.html",
        paper=paper,
        questions=questions
    )


@app.route("/papers")
@login_required
def papers():
    data = (
        supabase
        .table("generated_papers")
        .select("*")
        .order("id", desc=True)
        .execute()
        .data
    )

    return render_template(
        "papers.html",
        papers=data
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )