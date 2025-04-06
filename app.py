from flask import Flask, render_template, request
import os
import PyPDF2
import docx

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text(file):
    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    text = ""
    if filename.endswith('.pdf'):
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    elif filename.endswith('.docx'):
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif filename.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = "Unsupported file format."
    
    return text

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        resume = request.files['resume']
        jobdesc = request.files['jobdesc']

        if not resume or not jobdesc:
            return "No file uploaded", 400

        resume_text = extract_text(resume).lower()
        jobdesc_text = extract_text(jobdesc).lower()

        # Split job description into words (simple keyword extraction)
        jd_words = set(jobdesc_text.split())
        resume_words = set(resume_text.split())

        # Find common words (keywords matched)
        matched_keywords = jd_words.intersection(resume_words)
        matched_keywords = sorted(matched_keywords)

        match_percentage = (len(matched_keywords) / len(jd_words)) * 100 if jd_words else 0

        result = f"""
            ✅ Match Score: {match_percentage:.2f}%<br>
            📄 Resume Length: {len(resume_text)} characters<br>
            📝 Job Description Length: {len(jobdesc_text)} characters<br>
            🔍 Matched Keywords ({len(matched_keywords)}): <br> {', '.join(matched_keywords)}
        """

        return render_template('index.html', result=result)

    except Exception as e:
        print("Error occurred:", str(e))
        return f"An error occurred: {str(e)}", 500



if __name__ == '__main__':
    app.run(debug=True)
