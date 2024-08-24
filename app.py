from flask import Flask, render_template, request
import os
import google.generativeai as genai
from PIL import Image
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Initialize Flask app
app = Flask(__name__)

# Function to get Gemini response
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(input)
    return response.text

# Function to extract text from uploaded PDF file
def get_pdf_content(uploaded_file):
    pdf_content = ""
    reader = pdf.PdfReader(uploaded_file)
    for page in range(len(reader.pages)):
        page_text = reader.pages[page]
        pdf_content += str(page_text.extract_text())
    return pdf_content

# Route for the main page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get job description from form input
        jd = request.form.get("job_description")
        
        # Check if a file was uploaded
        uploaded_file = request.files.get("resume")
        
        if uploaded_file and uploaded_file.filename.endswith('.pdf'):
            # Extract text from the uploaded PDF
            pdf_content = get_pdf_content(uploaded_file)
        
            res_format='''
            {
            "Name": "Gokulrajan Nagarajan",
            "Experience": "2+ years",
            "JD Match percentage": "70%",
            "MissingKeywords": [
                "Designing and developing machine learning systems",
                "Conducting experiments",
                "Researching, building, and designing artificial intelligence systems"
            ],
            "Suggestion": "The candidate has experience in developing end-to-end AI solutions, including expertise in creating impactful chatbots. The candidate also has experience in developing applications within Microsoft Azure environment and skilled in gathering, analyzing and manipulating data from various formats. The candidate is also involved in sprint activities, successfully delivering Python-based stories using Agile development methodologies. To improve the match percentage, the candidate should gain experience in designing and developing machine learning systems, conducting experiments, and researching, building, and designing artificial intelligence systems."
            }
            '''
            # Format the input prompt
            input_prompt = f"""
            You are an experienced ATS(Application Tracking System). 
            You will be provided with 'resume' and 'job_decription'.Your task is to evaluate the 'resume' based on the given 'job_decription'. 
            Assign the percentage Matching based on 'job_decription' and the missing keywords with high accuracy. 
            resume:{pdf_content}
            job_decription:{jd}
            Provide your output in this format {res_format}.
            Don't use unwanted Tags and quotation
            """
            
            # Get response from the AI model
            response = get_gemini_response(input_prompt)
            print("output from gemini****\n",response)
            
            # Render the result in the HTML template
            json_response=json.loads(response)
            return render_template("index.html", response=json_response)
        
        else:
            # If no file was uploaded, or if it wasn't a PDF, render with an error
            return render_template("index.html", error="Please upload a valid PDF file.")
    
    # Render the form initially
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
