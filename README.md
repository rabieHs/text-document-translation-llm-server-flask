# PDF and Text Translation API

## Overview
This Translation API provides powerful translation capabilities for both text and PDF documents using advanced machine learning models from Hugging Face.

## Features
- Text translation
- PDF translation
- Multiple translation support (text and PDF)
- Supports multiple target languages
- Base64 PDF encoding for easy transmission

## Prerequisites
- Python 3.8+
- Hugging Face API Key

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/translation-api.git
cd translation-api
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
```bash
export HUGGINGFACE_API_KEY='your_hugging_face_api_key_here'
```

## API Endpoints

### 1. Text Translation
**Endpoint:** `POST /translate/text`

**Request Body:**
```json
{
    "text": "Text to translate",
    "target_language": "french"
}
```

**Response:**
```json
{
    "original_text": "Hello World",
    "translated_text": "Bonjour Monde",
    "target_language": "french"
}
```

### 2. PDF Translation
**Endpoint:** `POST /translate/pdf`

**Request:**
- Multipart form-data with PDF file
- JSON body with target language

**Response:**
- Translated PDF file download

### 3. Multiple Translation
**Endpoint:** `POST /translate/multiple`

**Request:**
- Optional text field
- Optional PDF file
- JSON body with target language

**Response:**
```json
{
  "translated_pdfs": [
    {
      "original_filename": "input.pdf",
      "target_language": "french",
      "translated_filename": "translated_input.pdf",
      "pdf_base64": "base64_encoded_pdf_content"
    }
  ],
  "translated_texts": [
    {
      "original": "Hello World",
      "target_language": "french", 
      "translated": "Bonjour Monde"
    }
  ]
}
```

## Usage Examples

### Text Translation
```bash
curl -X POST http://localhost:3000/translate/text \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello World", "target_language":"french"}'
```

### PDF Translation
```bash
curl -X POST http://localhost:3000/translate/pdf \
     -F "file=@/path/to/document.pdf" \
     -H "Content-Type: application/json" \
     -d '{"target_language":"arabic"}' \
     --output translated_document.pdf
```

### Multiple Translation
```bash
# Text and PDF Translation
curl -X POST http://localhost:3000/translate/multiple \
     -F "text=Hello World" \
     -F "pdf=@/path/to/document.pdf" \
     -H "Content-Type: application/json" \
     -d '{"target_language":"arabic"}'
```

## Supported Languages
The API supports translation to most major languages, including but not limited to:
- Arabic
- French
- Spanish
- German
- Chinese
- Russian
- Portuguese
- Italian
- Japanese
- Korean

## Security Considerations
- Use environment variables for API keys
- Limit file upload sizes
- Implement additional authentication for production use

## Troubleshooting
- Ensure Hugging Face API key is valid
- Check file formats and sizes
- Verify network connectivity

## Performance Notes
- Translation speed depends on document complexity
- Large PDFs may take longer to process
- Recommended file size: < 64MB

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License
[Specify your license here]

## Contact
For support, please contact rabiehoussaini@gmail.com