"""
Typhoon OCR Service Integration for SuperNote Project

This service integrates the advanced Typhoon OCR functionality 
with the existing SuperNote application.
"""

import os
import base64
import json
import tempfile
from io import BytesIO
from PIL import Image
from openai import OpenAI
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load typhoon_ocr utilities
from .typhoon_ocr.ocr_utils import render_pdf_to_base64png, get_anchor_text

load_dotenv()

class TyphoonOCRService:
    def __init__(self):
        # Get API key from environment
        self.api_key = os.getenv('TYPHOON_API_KEY')
        if not self.api_key:
            print("Warning: TYPHOON_API_KEY not found in environment variables")
            self.client = None
            return
        
        try:
            # Initialize Typhoon client
            self.client = OpenAI(
                base_url="https://api.opentyphoon.ai/v1", 
                api_key=self.api_key
            )
            
            # Default configuration
            self.max_tokens = 16384
            self.temperature = 0.1
            self.top_p = 0.6
            self.repetition_penalty = 1.2
            
        except Exception as e:
            print(f"Warning: Failed to initialize Typhoon OCR client: {e}")
            self.client = None

    def get_prompt(self, prompt_name="default"):
        """Get OCR prompts for different task types"""
        prompts = {
            "default": lambda base_text: (
                f"Below is an image of a document page along with its dimensions. "
                f"Simply return the markdown representation of this document, presenting tables in markdown format as they naturally appear.\n"
                f"If the document contains images, use a placeholder like dummy.png for each image.\n"
                f"Your final output must be in JSON format with a single key `natural_text` containing the response.\n"
                f"RAW_TEXT_START\n{base_text}\nRAW_TEXT_END"
            ),
            "structure": lambda base_text: (
                f"Below is an image of a document page, along with its dimensions and possibly some raw textual content previously extracted from it. "
                f"Note that the text extraction may be incomplete or partially missing. Carefully consider both the layout and any available text to reconstruct the document accurately.\n"
                f"Your task is to return the markdown representation of this document, presenting tables in HTML format as they naturally appear.\n"
                f"If the document contains images or figures, analyze them and include the tag <figure>IMAGE_ANALYSIS</figure> in the appropriate location.\n"
                f"Your final output must be in JSON format with a single key `natural_text` containing the response.\n"
                f"RAW_TEXT_START\n{base_text}\nRAW_TEXT_END"
            ),
        }
        return prompts.get(prompt_name, lambda x: "Invalid PROMPT_NAME provided.")

    def is_pdf(self, file_path):
        """Check if file is PDF"""
        return file_path.lower().endswith(".pdf")

    def is_image(self, file_path):
        """Check if file is image"""
        return any(file_path.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"])

    def is_available(self):
        """Check if Typhoon OCR service is available"""
        return self.client is not None

    def process_pdf_file(self, file_path, task_type="default"):
        """Process PDF file with Typhoon OCR"""
        if not self.is_available():
            raise Exception("Typhoon OCR service is not available")
        
        try:
            reader = PdfReader(file_path)
            num_pages = len(reader.pages)
            all_text = ""

            for page_num in range(num_pages):
                print(f"📄 Processing PDF page {page_num + 1}/{num_pages}")

                # Render PDF page to base64 image
                img_b64 = render_pdf_to_base64png(file_path, page_num)
                
                # Get anchor text for better OCR
                anchor_text = get_anchor_text(file_path, page_num + 1, "pdfreport", 8000)
                
                # Get prompt
                prompt = self.get_prompt(task_type)(anchor_text)

                # Call Typhoon OCR API
                response = self.client.chat.completions.create(
                    model="typhoon-ocr-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                        ],
                    }],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    extra_body={"repetition_penalty": self.repetition_penalty},
                )

                output_text = response.choices[0].message.content
                
                # Try to parse JSON response
                try:
                    parsed_response = json.loads(output_text)
                    if 'natural_text' in parsed_response:
                        all_text += parsed_response['natural_text'] + "\n"
                    else:
                        all_text += output_text + "\n"
                except json.JSONDecodeError:
                    all_text += output_text + "\n"

            return all_text.strip()

        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

    def process_image_file(self, file_path, task_type="default"):
        """Process image file with Typhoon OCR"""
        if not self.is_available():
            raise Exception("Typhoon OCR service is not available")
        
        try:
            print(f"🖼️ Processing image: {os.path.basename(file_path)}")

            # Read and encode image
            with open(file_path, "rb") as f:
                img_bytes = f.read()
                img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            # Get prompt
            prompt = self.get_prompt(task_type)("")

            # Call Typhoon OCR API
            response = self.client.chat.completions.create(
                model="typhoon-ocr-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    ],
                }],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                extra_body={"repetition_penalty": self.repetition_penalty},
            )

            output_text = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                parsed_response = json.loads(output_text)
                if 'natural_text' in parsed_response:
                    return parsed_response['natural_text']
                else:
                    return output_text
            except json.JSONDecodeError:
                return output_text

        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    def process_file(self, file_path, task_type="default"):
        """Process file (PDF or image) with Typhoon OCR"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if self.is_pdf(file_path):
            return self.process_pdf_file(file_path, task_type)
        elif self.is_image(file_path):
            return self.process_image_file(file_path, task_type)
        else:
            raise ValueError("❌ Only PDF, PNG, JPG, JPEG files are supported")

    def process_uploaded_file(self, file_obj, filename, task_type="default"):
        """Process uploaded file object"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            file_obj.save(temp_file.name)
            temp_path = temp_file.name

        try:
            # Process the temporary file
            result = self.process_file(temp_path, task_type)
            return result
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


# Create a global instance
typhoon_ocr_service = TyphoonOCRService()
