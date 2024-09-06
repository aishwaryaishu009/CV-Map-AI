import pdfkit
from flask import Flask, request, render_template, flash, redirect, url_for, send_file
from PyPDF2 import PdfReader
from subjective import SubjectiveTest
import re
import os

app = Flask(__name__)
app.secret_key = 'aica2'

# Specify the path to wkhtmltopdf
path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

@app.route('/')
def index():
    return render_template('front.html')

@app.route('/predict')
def index1():
    return render_template('predict.html')

@app.route('/test_generate', methods=["POST"])
def test_generate():
    if 'pdf_file' not in request.files:
        flash("No file part")
        return redirect(url_for('index1'))
    
    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        flash("No selected file")
        return redirect(url_for('index1'))
    
    if pdf_file:
        pdf = PdfReader(pdf_file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    
    valid_keywords = ["Python", "programming", "machine learning", "data analysis", "NLP", "OOPs", "Java"]
    no_of_questions = 50  # Adjust this number as needed

    try:
        subjective_generator = SubjectiveTest(text, no_of_questions, valid_keywords)
        question_list = subjective_generator.generate_questions()
        
        return render_template('predict.html', cresults=question_list)
    except Exception as e:
        flash(f'Error Occurred: {str(e)}')
        return redirect(url_for('index1'))

@app.route("/generate")
def gen():
    return render_template('generate.html')

@app.route("/generatepdf", methods=['POST'])
def generatepdf():
    if request.method == "POST":
        # Collect form data
        form_data = request.form
        name = form_data['Name']
        email = form_data['Email']
        linkedin = form_data['LinkedIn']
        experience = form_data['Experience']
        graduation = form_data['Graduation']
        cgpa = form_data['CGPA']
        university = form_data['University']
        skills = form_data['Skills']
        internship = form_data['Internship']
        achievements = form_data['Achievements']
        course1 = form_data['course1']
        course2 = form_data['course2']
        course3 = form_data['course3']
        projects = form_data['projects']

        # Generate HTML content for PDF
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resume</title>
        </head>
        <body>
            <div class="container">
                <h1 style="font-size: 45px;">{name}</h1>
                <p>Email: {email}</p>
                <p>{linkedin}</p>
                <p>Experience: {experience} years</p>
                <hr style="height: 2px; background-color: #000; border: none; margin-top: 20px; margin-bottom: 20px;">
                <h2>Education</h2>
                <p>{graduation} - {university}</p>
                <p>CGPA - {cgpa}</p>
                <hr style="height: 2px; background-color: #000; border: none; margin-top: 20px; margin-bottom: 20px;">
                <h2>Projects</h2>
                <p>{projects}</p>
                <hr style="height: 2px; background-color: #000; border: none; margin-top: 20px; margin-bottom: 20px;">
                <h2>Skills</h2>
                <p>{skills}</p>
                <hr style="height: 2px; background-color: #000; border: none; margin-top: 20px; margin-bottom: 20px;">
                <h2>Internships</h2>
                <p>{internship}</p>
                <hr style="height: 2px; background-color: #000; border: none; margin-top: 20px; margin-bottom: 20px;">
                <h2>Achievements</h2>
                <p>{achievements}</p>
                <hr style="height: 2px; background-color: #000; border: none; margin-top: 20px; margin-bottom: 20px;">
                <h2>Courses</h2>
                <p>{course1}</p>
                <p>{course2}</p>
                <p>{course3}</p>
            </div>
        </body>
        </html>
        """

        # Generate PDF from HTML content
        pdf_path = 'resume.pdf'
        try:
            pdfkit.from_string(html_content, pdf_path, configuration=config)
            return send_file(pdf_path, as_attachment=True)
        except Exception as e:
            flash(f'Error generating PDF: {str(e)}')
            return redirect(url_for('gen'))

    return render_template('cantdownload.html')

@app.route("/score_resume", methods=["GET", "POST"])
def score_resume():
    if request.method == "POST":
        if 'pdf_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        pdf_file = request.files['pdf_file']
        if pdf_file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if pdf_file:
            pdf = PdfReader(pdf_file)
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
            resume_data = {
                'Name': extract_name(text),
                'Email': extract_email(text),
                'LinkedIn': extract_linkedin(text),
                'Experience': extract_experience(text),
                'Graduation': extract_graduation(text),
                'CGPA': extract_cgpa(text),
                'University': extract_university(text),
                'Skills': extract_skills(text),
                'Internship': extract_internship(text),
                'Achievements': extract_achievements(text),
                'Projects': extract_projects(text)
            }
            resume_score = calculate_score(resume_data)
            return render_template('score_result.html', score=resume_score)
    
    return render_template('score_upload.html')

def extract_name(text):
    match = re.search(r"([A-Z][a-z]+(?: [A-Z][a-z]+)+)", text)
    return match.group(1).strip() if match else "Name not found"

def extract_email(text):
    match = re.search(r"([\w\.-]+@[\w\.-]+)", text)
    return match.group(1).strip() if match else "Email not found"

def extract_linkedin(text):
    match = re.search(r"(https?://www\.linkedin\.com/in/[A-Za-z0-9-]+)", text)
    return match.group(1).strip() if match else "LinkedIn not found"

def extract_github(text):
    match = re.search(r"(https?://github\.com/[A-Za-z0-9-]+)", text)
    return match.group(1).strip() if match else "GitHub not found"

def extract_experience(text):
    experience_pattern = r"(?:April|May|June|July|August|September|October|November|December) \d{4}"
    matches = re.findall(experience_pattern, text)
    return len(matches) if matches else 0

def extract_graduation(text):
    match = re.search(r"([Bb]achelor of Technology|[Dd]iploma in [A-Za-z ]+)", text)
    return match.group(1).strip() if match else "Graduation not found"

def extract_cgpa(text):
    match = re.search(r"(\d+\.\d+)", text)
    return float(match.group(1)) if match else 0.0

def extract_university(text):
    match = re.search(r"([A-Za-z ]+(?:Institute|University|College))", text)
    return match.group(1).strip() if match else "University not found"

def extract_skills(text):
    match = re.search(r"Programming Languages :\s*([A-Za-z, ]+)", text)
    return match.group(1).strip() if match else "Skills not found"

def extract_internship(text):
    match = re.search(r"(Trainee|Intern|Internship)", text)
    return match.group(1).strip() if match else "Internship not found"

def extract_achievements(text):
    match = re.search(r"Achievements\n\n•\s*([A-Za-z, 0-9]+(?:\n• [A-Za-z, 0-9]+)*)", text)
    return match.group(1).strip() if match else "Achievements not found"

def extract_projects(text):
    match = re.search(r"Projects\n\n(?:.+?\n)+", text)
    return match.group(0).strip() if match else "Projects not found"

def calculate_score(resume_data):
    score = 0
    if resume_data['Name'] != "Name not found":
        score += 10
    if resume_data['Email'] != "Email not found":
        score += 10
    if resume_data['LinkedIn'] != "LinkedIn not found":
        score += 10
    if resume_data['Experience'] > 0:
        score += 20
    if resume_data['Graduation'] != "Graduation not found":
        score += 10
    if resume_data['CGPA'] > 0:
        score += 10
    if resume_data['University'] != "University not found":
        score += 10
    if resume_data['Skills'] != "Skills not found":
        score += 10
    if resume_data['Internship'] != "Internship not found":
        score += 5
    if resume_data['Achievements'] != "Achievements not found":
        score += 5
    if resume_data['Projects'] != "Projects not found":
        score += 10

    return score

if __name__ == "__main__":
    app.run(debug=True)
