import base64

from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from main import PDFTranslator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Initialize the PDF translator with your Hugging Face API key
API_KEY = os.getenv('HUGGINGFACE_API_KEY')
pdf_translator = PDFTranslator(api_key=API_KEY)

def pdf_to_base64(pdf_path):
    """
    Convert PDF file to base64 encoded string
    """
    try:
        with open(pdf_path, 'rb') as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error converting PDF to base64: {e}")
        return None# Simulating base64 encoding

def unified_response(original_text=None, original_file=None, translated_text=None, translated_file=None):
    return {
        "original": {
            "text": original_text,
            "file": original_file
        },
        "translated": {
            "text": translated_text,
            "file": translated_file
        }
    }

@app.route('/translate/text', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data or 'target_language' not in data:
            return jsonify({"error": "Missing required parameters."}), 400

        translated_text = pdf_translator.translate_text(text=data['text'], target_language=data['target_language'])

        return jsonify(unified_response(
            original_text=data['text'],
            translated_text=translated_text
        ))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/translate/pdf', methods=['POST'])
def translate_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        target_language = request.form.get('target_language', 'arabic')

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"translated_{filename}")

        file.save(input_path)
        translated_path = pdf_translator.translate_pdf(input_pdf_path=input_path, target_language=target_language, output_pdf_path=output_path)
        base64_pdf = pdf_to_base64(translated_path)

        return jsonify(unified_response(
            original_file=filename,
            translated_file=base64_pdf
        ))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/translate/multiple', methods=['POST'])
def translate_multiple():
    try:
        target_language = request.form.get('target_language', 'arabic')

        original_text = None
        translated_text = None
        original_file = None
        translated_file = None

        if 'text' in request.form:
            text = request.form.get('text')
            translated_text = pdf_translator.translate_text(text=text, target_language=target_language)
            original_text = text

        if 'file' in request.files:
            file = request.files['file']
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"translated_{filename}")

            file.save(input_path)
            translated_path = pdf_translator.translate_pdf(input_pdf_path=input_path, target_language=target_language, output_pdf_path=output_path)
            base64_pdf = pdf_to_base64(translated_path)
            original_file = filename
            translated_file = base64_pdf

        return jsonify(unified_response(
            original_text=original_text,
            original_file=original_file,
            translated_text=translated_text,
            translated_file=translated_file
        ))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
