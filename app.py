import os
import fitz
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

# ----------------------------
# Load Environment Variables
# ----------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise Exception("GEMINI_API_KEY not found in .env")

# ----------------------------
# Gemini Client
# ----------------------------

client = genai.Client(api_key=API_KEY)

# ----------------------------
# Flask App
# ----------------------------

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Store PDF text globally
pdf_text = ""

# ----------------------------
# Home Page
# ----------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# Upload PDF
# ----------------------------

@app.route("/upload", methods=["POST"])
def upload_pdf():

    global pdf_text

    if "pdf" not in request.files:
        return jsonify({
            "message": "No PDF selected"
        }), 400

    file = request.files["pdf"]

    if file.filename == "":
        return jsonify({
            "message": "Please choose a PDF"
        }), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "message": "Only PDF files are allowed"
        }), 400

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    try:

        doc = fitz.open(filepath)

        pdf_text = ""

        for page in doc:
            pdf_text += page.get_text()

        doc.close()

        if pdf_text.strip() == "":

            return jsonify({
                "message": "No readable text found in PDF"
            }), 400

        return jsonify({
            "message": "PDF uploaded successfully!"
        })

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500
# ----------------------------
# Ask Question
# ----------------------------

@app.route("/ask", methods=["POST"])
def ask_question():

    global pdf_text

    if pdf_text == "":
        return jsonify({
            "answer": "Please upload a PDF first."
        }), 400

    data = request.get_json()

    question = data.get("question")

    if not question:
        return jsonify({
            "answer": "Please enter a question."
        }), 400

    prompt = f"""
You are an intelligent PDF assistant.

Answer the question ONLY using the information given in the PDF.

If the answer is not available in the PDF, reply:

"I couldn't find this information in the uploaded PDF."

PDF Content:

{pdf_text}

Question:

{question}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        answer = response.text

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        import traceback
        traceback.print_exc()

        return jsonify({
            "answer": str(e)
        }), 500




# ----------------------------
# Run Flask
# ----------------------------

if __name__ == "__main__":
    app.run(debug=True)