import os
import json
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from huggingface_hub import InferenceClient


class PDFTranslator:
    def __init__(self, api_key):
        """
        Initialize the PDF translator with a Hugging Face API key.

        :param api_key: Hugging Face API key
        """
        self.client = InferenceClient(api_key=api_key)

        # Register Arabic font to support Arabic translation
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        except Exception:
            print("Warning: Could not register Arabic font. Using default font.")

    # meta-llama/Llama-3.2-3B-Instruct
    #mistralai/Mistral-7B-Instruct-v0.3

    def translate_text(self, text, target_language, model="meta-llama/Llama-3.2-3B-Instruct"):
        """
        Translate text to the specified language with a strict translation-only system prompt.

        :param text: Text to translate
        :param target_language: Target language for translation
        :param model: Hugging Face model to use for translation
        :return: Translated text
        """
        # Strict system prompt that enforces translation-only behavior
        system = f"""You are a professional translator with ONE AND ONLY ONE task:
- Translate the given text EXACTLY as it appears into {target_language}
- Do NOT add any commentary, explanation, or additional information
- Do NOT modify the text beyond translation
- Translate ONLY the text provided, nothing more or less
- Respond ONLY with the translated text

Text to translate: {text}"""

        messages = [
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": text
            }
        ]

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=500
            )

            # Extract and return the translated text
            return completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original text if translation fails

    def translate_pdf(self, input_pdf_path, target_language, output_pdf_path=None):
        """
        Translate a PDF document and save as a new PDF.

        :param input_pdf_path: Path to input PDF
        :param target_language: Target language for translation
        :param output_pdf_path: Path to save translated PDF (optional)
        :return: Path to the translated PDF
        """
        # If no output path is specified, create one
        if not output_pdf_path:
            base, ext = os.path.splitext(input_pdf_path)
            output_pdf_path = f"{base}_translated_{target_language}{ext}"

        # Open the input PDF
        with open(input_pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            # Create a new PDF for translated content
            c = canvas.Canvas(output_pdf_path, pagesize=letter)
            width, height = letter

            # Translate and write each page
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]

                # Extract text (improved extraction)
                text = page.extract_text()

                # Translate the text
                translated_text = self.translate_text(text, target_language)

                # Reset canvas for each page
                c.setFont('Arial', 10)  # Use Arial for better language support

                # Write translated text
                text_object = c.beginText(50, height - 50)  # Start near top-left
                lines = translated_text.split('\n')
                for line in lines:
                    text_object.textLine(line)
                c.drawText(text_object)

                # Move to next page
                c.showPage()

            # Save the PDF
            c.save()

            print(f"Translated PDF saved to: {output_pdf_path}")
            return output_pdf_path


def main():
    # Replace with your actual Hugging Face API key
    API_KEY = ""

    # Create translator instance
    translator = PDFTranslator(API_KEY)

    # Translate PDF
    try:
        translated_pdf_path = translator.translate_pdf(
            input_pdf_path="input.pdf",  # Replace with your input PDF path
            target_language="french",
            output_pdf_path="translated_french_mistral.pdf"
        )

        # Print translation result
        print(f"PDF translation complete. Saved to: {translated_pdf_path}")

    except Exception as e:
        print(f"Translation failed: {e}")


if __name__ == "__main__":
    main()