from flask import Flask, render_template, request
import os
import PyPDF2
from skills_db import SKILLS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- AI LOGIC ----------------
def analyze_skills(text):
    text = text.lower()
    found_skills = []
    missing_skills = []

    for category, skills in SKILLS.items():
        for skill in skills:
            if skill in text:
                found_skills.append(skill)

    for category, skills in SKILLS.items():
        for skill in skills:
            if skill not in found_skills:
                missing_skills.append(skill)

    return found_skills, missing_skills[:8]


def calculate_score(found_skills):
    score = len(found_skills) * 8
    return min(score, 100)


def suggest_career(found_skills):
    if "python" in found_skills and "machine learning" in found_skills:
        return "AI / ML Engineer"
    elif "python" in found_skills and "flask" in found_skills:
        return "Python Backend Developer"
    elif "html" in found_skills and "css" in found_skills:
        return "Frontend Developer"
    else:
        return "Software Developer (Entry Level)"


def generate_questions(role):
    questions = {
        "python": [
            "What is Python?",
            "Explain list vs tuple.",
            "What is virtual environment?",
            "What are decorators?",
            "Explain Flask."
        ],
        "ai": [
            "What is Machine Learning?",
            "Difference between supervised and unsupervised learning.",
            "What is overfitting?",
            "Explain NLP.",
            "What is model evaluation?"
        ],
        "frontend": [
            "What is HTML5?",
            "What is CSS Flexbox?",
            "Explain JavaScript DOM.",
            "What is responsive design?",
            "Difference between class and id?"
        ]
    }
    return questions.get(role, [])


# ---------------- RESUME ANALYZER ----------------
@app.route("/resume", methods=["GET", "POST"])
def resume():
    extracted_text = ""
    found_skills = []
    missing_skills = []
    score = None
    career = None

    if request.method == "POST":
        file = request.files["resume"]

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            if file.filename.endswith(".pdf"):
                with open(filepath, "rb") as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    for page in reader.pages:
                        extracted_text += page.extract_text()

            elif file.filename.endswith(".txt"):
                with open(filepath, "r") as txt_file:
                    extracted_text = txt_file.read()

            found_skills, missing_skills = analyze_skills(extracted_text)
            score = calculate_score(found_skills)
            career = suggest_career(found_skills)

    return render_template(
        "resume.html",
        text=extracted_text,
        found_skills=found_skills,
        missing_skills=missing_skills,
        score=score,
        career=career
    )


# ---------------- INTERVIEW PREP ----------------
@app.route("/interview", methods=["GET", "POST"])
def interview():
    questions = []

    if request.method == "POST":
        role = request.form.get("role")
        questions = generate_questions(role)

    return render_template("interview.html", questions=questions)


# ---------------- SKILLS PAGE ----------------
@app.route("/skills")
def skills():
    return render_template("skills.html")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)


