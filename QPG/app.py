import os
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from qg_model import generate_question_bank
from qp_model import generate_question_paper

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Set upload folder and allowed file extensions
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Home Page
@app.route("/")
def index():
    return render_template("index.html")

# QB
@app.route("/generate_questions", methods = ["GET", "POST"])
def generate_questions():
    if request.method == "POST":
        grade = request.form.get("grade")
        subject = request.form.get("subject")
        topic = request.form.get("topic")
        question_type = request.form.get("question_type")
        difficulty = request.form.get("difficulty")
        marks = int(request.form.get("marks"))
        num_questions = int(request.form.get("num_questions"))
        syllabus = request.files.get("syllabus")

        syllabus_path = None
        if syllabus and allowed_file(syllabus.filename):
            filename = secure_filename(syllabus.filename)
            syllabus_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            syllabus.save(syllabus_path)

        elif syllabus:
            flash("Invalid file format. Please upload a PDF file.")
            return redirect(url_for("generate_questions"))
        
        # Call the question generation model to create/update the question bank Excel file
        excel_path = generate_question_bank(grade, subject, topic, question_type, difficulty, marks, num_questions, syllabus_path)

        flash("Question Bank generated successfully!", "success")
        return send_file(excel_path, as_attachment = True)
    return render_template("question_generation.html")

# Route for generating question paper (PDF) with preview  
@app.route("/generate_paper", methods=["GET", "POST"])
def generate_qp():
    if request.method == "POST":
        grade = request.form.get("grade")
        subject = request.form.get("subject")
        total_marks = int(request.form.get("total_marks"))
        num_questions = int(request.form.get("num_questions"))
        easy_questions = int(request.form.get("easy_questions"))
        medium_questions = int(request.form.get("medium_questions"))
        hard_questions = int(request.form.get("hard_questions"))
        difficulty_split = {"easy": easy_questions, "medium": medium_questions, "hard": hard_questions}
        syllabus = request.files.get("syllabus")
        sample_paper = request.files.get("sample_paper")

        # Debug statement to check the value of difficulty_split
        print(f"difficulty_split before calling generate_question_paper: {difficulty_split}")
        
        syllabus_path = sample_path = None
        if syllabus and allowed_file(syllabus.filename):
            filename = secure_filename(syllabus.filename)
            syllabus_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            syllabus.save(syllabus_path)

        elif syllabus:
            flash("Invalid file format. Please upload a PDF file.")
            return redirect(url_for("generate_qp"))
        
        if sample_paper and allowed_file(sample_paper.filename):
            filename = secure_filename(sample_paper.filename)
            sample_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            sample_paper.save(sample_path)

        elif sample_paper:  
            flash("Invalid file format. Please upload a PDF file.")
            return redirect(url_for("generate_qp"))

        # Call the question paper generation model to create the question paper PDF
        pdf_path, preview_html, Warning = generate_question_paper(grade, subject, total_marks, difficulty_split, num_questions, syllabus_path, sample_path)

        if Warning:
            flash(Warning, "warning")
            return redirect(url_for("generate_qp"))
        
        return render_template("preview.html", preview_html=preview_html, pdf_filename=os.path.basename(pdf_path))
    return render_template("question_paper.html")

# Route for downloading the generated question paper PDF
@app.route("/download_paper/<filename>")
def download(filename):
    return send_file(os.path.join("uploads", filename), as_attachment = True)

if __name__ == "__main__":
    app.run(debug = True)