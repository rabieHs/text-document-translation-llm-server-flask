import base64
import os
import tempfile

from dotenv import load_dotenv
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename

# Import the translation class from main implementation
from main import PDFTranslator

def pdf_to_base64(pdf_path):
    """
    Convert PDF file to base64 encoded string
    """
    try:
        with open(pdf_path, 'rb') as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error converting PDF to base64: {e}")
        return None


load_dotenv()

app = Flask(__name__)

# Configuration
# IMPORTANT: Replace with secure method of storing API key
API_KEY = os.getenv('HUGGINGFACE_API_KEY')
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # Increased to 64MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# Initialize translator
translator = PDFTranslator(API_KEY)


@app.route('/translate/text', methods=['POST'])
def translate_text():
    """
    API endpoint for text translation
    Expected JSON payload:
    {
        "text": "Text to translate",
        "target_language": "arabic"
    }
    """
    try:
        # Get data from JSON request
        data = request.get_json()

        # Validate input
        if not data or 'text' not in data or 'target_language' not in data:
            return jsonify({
                "error": "Missing required parameters. Please provide 'text' and 'target_language'"
            }), 400

        # Perform translation
        translated_text = translator.translate_text(
            text=data['text'],
            target_language=data['target_language']
        )

        # Return translation as JSON
        return jsonify({
            "original_text": data['text'],
            "translated_text": translated_text,
            "target_language": data['target_language']
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/translate/pdf', methods=['POST'])
def translate_pdf():
    """
    API endpoint for PDF translation
    Expected multipart form-data with JSON body:
    {
        "target_language": "arabic"
    }
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        # Get target language from JSON body
        data = request.form
        target_language = request.json.get('target_language', 'arabic') if request.is_json else data.get(
            'target_language', 'arabic')

        # Get file
        file = request.files['file']

        # Validate file
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Secure filename and create paths
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"translated_{filename}")

        # Save uploaded file
        file.save(input_path)

        # Translate PDF
        translated_path = translator.translate_pdf(
            input_pdf_path=input_path,
            target_language=target_language,
            output_pdf_path=output_path
        )

        # Return the translated PDF file directly
        return send_file(
            translated_path,
            download_name=f'translated_{filename}',
            as_attachment=True
        )

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/translate/multiple', methods=['POST'])
def translate_multiple():
    """
    API endpoint for single text and single PDF translation
    Returns both base64 encoded PDF and translated text
    """
    try:
        # Get target language from JSON body
        target_language = request.json.get('target_language', 'arabic') if request.is_json else request.form.get(
            'target_language', 'arabic')

        # Initialize results dictionary
        results = {
            'translated_texts': [],
            'translated_pdfs': []
        }

        # Handle text translation (single text)
        if 'text' in request.form:
            text = request.form.get('text')
            translated_text = translator.translate_text(
                text=text,
                target_language=target_language
            )
            results['translated_texts'].append({
                'original': text,
                'translated': translated_text,
                'target_language': target_language
            })

        # Handle PDF translation (single PDF)
        if 'pdf' in request.files:
            file = request.files['pdf']

            # Secure filename and create paths
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"translated_{filename}")

            # Save uploaded file
            file.save(input_path)

            # Translate PDF
            translated_path = translator.translate_pdf(
                input_pdf_path=input_path,
                target_language=target_language,
                output_pdf_path=output_path
            )

            # Convert PDF to base64
            base64_pdf = pdf_to_base64(translated_path)

            results['translated_pdfs'].append({
                'original_filename': filename,
                'target_language': target_language,
                'translated_filename': os.path.basename(translated_path),
                'pdf_base64': base64_pdf
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# Updated README.md content
"""
# Enhanced Translation API Server

## Setup
1. Set Hugging Face API Key:
   export HUGGINGFACE_API_KEY='your_api_key_here'

2. Install dependencies:
   pip install -r requirements.txt

## Endpoints
- POST /translate/text
  - Translate text to target language
  - JSON payload: 
    {
        "text": "Text to translate", 
        "target_language": "arabic"
    }

- POST /translate/pdf
  - Translate PDF to target language
  - Multipart form-data with PDF file
  - JSON body: 
    {
        "target_language": "arabic"
    }
  - Returns translated PDF file

- POST /translate/multiple
  - Translate single text and/or single PDF
  - Multipart form-data with:
    * Optional 'text': Text to translate
    * Optional 'pdf': PDF file to translate
  - JSON body:
    {
        "target_language": "arabic"
    }

## Usage Examples
### Text Translation
curl -X POST http://localhost:3000/translate/text \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello World", "target_language":"arabic"}'

### PDF Translation
curl -X POST http://localhost:3000/translate/pdf \
     -F "file=@/path/to/document.pdf" \
     -H "Content-Type: application/json" \
     -d '{"target_language":"arabic"}' \
     --output translated_document.pdf

### Multiple Translation (Text)
curl -X POST http://localhost:3000/translate/multiple \
     -F "text=Hello World" \
     -H "Content-Type: application/json" \
     -d '{"target_language":"french"}'

### Multiple Translation (PDF)
curl -X POST http://localhost:3000/translate/multiple \
     -F "pdf=@/path/to/document.pdf" \
     -H "Content-Type: application/json" \
     -d '{"target_language":"arabic"}'

### Multiple Translation (Text and PDF)
curl -X POST http://localhost:3000/translate/multiple \
     -F "text=Hello World" \
     -F "pdf=@/path/to/document.pdf" \
     -H "Content-Type: application/json" \
     -d '{"target_language":"arabic"}'
"""