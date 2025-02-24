import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_questions(grade, subject, topic, question_type, difficulty, marks, num_questions, syllabus_text=None, syllabus_path=None):
    prompt = f"""Generate {num_questions} {difficulty} - level {question_type} questions for Cambridge 
    {grade} grade {subject} on the topic of {topic}. Each question should be worth {marks} marks. The first line must be an introductory line for the question bank. The second line must talk about the marking scheme/marks being alloted. The questions should begin after that and end after {num_questions} questions. No further text is necessary."""
    if syllabus_text:
        prompt += f" \nRefer to this syllabus : \n{syllabus_text}"
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    # Assume the response returns questions separated by newlines
    questions = [q.strip() for q in response.text.split("\n") if q.strip()]
    
    # Extract the marking scheme and introductory lines
    marking_scheme = questions[0] if questions else ""
    introductory_lines = questions[1] if len(questions) > 1 else ""
    questions = questions[2:num_questions + 2]  # Extract only the specified number of questions

    return questions, marking_scheme, introductory_lines

def generate_question_bank(grade, subject, topic, question_type, difficulty, marks, num_questions, syllabus_path=None):
    syllabus_text = None
    if syllabus_path:
        with open(syllabus_path, "rb") as file:
            syllabus_text = file.read().decode("utf-8", errors="ignore")

    questions, marking_scheme, introductory_lines = generate_questions(grade, subject, topic, question_type, difficulty, marks, num_questions, syllabus_text)

    # Create a DataFrame to store the questions
    df = pd.DataFrame({"Grade": [grade] * len(questions), "Subject": [subject] * len(questions), "Topic": [topic] * len(questions), 
                       "Question Type": [question_type] * len(questions), "Difficulty": [difficulty] * len(questions), 
                       "Marks": [marks] * len(questions), "Question": questions})
    
    # Create a DataFrame for the marking scheme and introductory lines
    df_intro = pd.DataFrame({"Introductory Lines": [introductory_lines], "Marking Scheme": [marking_scheme]})
    
    excel_path = f"uploads/Grade{grade}_{subject}_question_bank.xlsx"
    
    # Write the DataFrame to an Excel file
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_intro.to_excel(writer, index=False, startrow=0, header=False)
        df.to_excel(writer, index=False, startrow=3, header=True)  # Start writing questions from Row 4
    
    return excel_path