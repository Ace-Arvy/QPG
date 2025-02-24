import os
from fpdf import FPDF
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug statement to check the value of GEMINI_API_KEY
print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')}")

# Configure the generative AI model with the API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_questions_for_paper(grade, subject, total_marks, difficulty_split, num_questions, syllabus_text=None, sample_text=None):
    # Debug statement to check the value of difficulty_split
    print(f"difficulty_split in generate_questions_for_paper: {difficulty_split}")
    
    prompt = f"""Generate an ICSE-style exam question paper for Cambridge {grade} grade {subject} with a total of {total_marks} marks. 
    Number Of Questions: {num_questions}.
    Difficulty Distribution: Easy: {difficulty_split['easy']}, Medium: {difficulty_split['medium']}, Hard: {difficulty_split['hard']}.
    Each question should include the marks indicator. Ensure the title is centered and instructions are clear without unnecessary asterisks.
    Include a mix of question types that are well-distributed and properly structured across the syllabus as per common exam paper patterns."""

    if syllabus_text:
        prompt += f" \nRefer to this syllabus : \n{syllabus_text}"
    if sample_text:
        prompt += f" \n Also consider the following sample paper as inspiration : \n{sample_text}"
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    # Assume the response is a well formatted text that can be used as the question paper
    return response.text if response else "Error generating question paper!"

def generate_question_paper(grade, subject, total_marks, difficulty_split, num_questions, syllabus_path=None, sample_path=None):
    # Debug statement to check the value of difficulty_split
    print(f"difficulty_split at start of generate_question_paper: {difficulty_split}")

    syllabus_text = sample_text = None
    if syllabus_path:
        with open(syllabus_path, "rb") as file:
            syllabus_text = file.read().decode("utf-8", errors="ignore")
    if sample_path:
        with open(sample_path, "rb") as file:
            sample_text = file.read().decode("utf-8", errors="ignore")
    
    # Debug Statement
    print(f"difficulty_split before passing to generate_questions_for_paper: {difficulty_split}")

    # Generate the question paper text using Gemini API
    paper_text = generate_questions_for_paper(grade, subject, total_marks, difficulty_split, num_questions, syllabus_text, sample_text)

    # Save the paper text as a PDF file
    pdf_path = f"uploads/Grade{grade}_{subject}_question_paper.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Center the title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Grade {grade} {subject} Question Paper", 0, 1, 'C')
    pdf.set_font("Arial", size=12)
    
    # Write the generated text; for a more sophisticated layout, consider integrating LaTeX
    pdf.multi_cell(0, 10, paper_text.encode('latin-1', 'replace').decode('latin-1'))
    pdf.output(pdf_path)

    # For a preview, wrap the paper text in a simple HTML template
    preview_html = f"<div style='white-space: pre-wrap; font-family: Arial;'>{paper_text}</div>"

    return pdf_path, preview_html, None