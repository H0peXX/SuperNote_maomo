import os
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
from PyPDF2 import PdfReader

from typhoon_ocr.ocr_utils import render_pdf_to_base64png, get_anchor_text

def get_prompt(prompt_name):
    PROMPTS = {
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
    return PROMPTS.get(prompt_name, lambda x: "Invalid PROMPT_NAME provided.")

# --- CONFIG ---
#แก้filename
filename = "C:\\Users\\Maya\\Documents\\ThaiLifeInsurance-Projects\\OCR-Testing\\ocr_to_web\\ocr\\note_ink.png"  # รองรับ .pdf, .png, .jpg, .jpeg
task_type = "default"
api_key = "sk-JNfGWhdMy8LrmZAIRjG9Ff6dSxudOF6Sv5k4IHrnnbv2tKdM"  # ใส่ Typhoon API
max_tokens_summary_chunk = 500

# --- INIT Typhoon Client ---
client = OpenAI(base_url="https://api.opentyphoon.ai/v1", api_key=api_key)

ocr_all_text = ""

def is_pdf(file_path):
    return file_path.lower().endswith(".pdf")

def is_image(file_path):
    return any(file_path.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"])

if is_pdf(filename):
    reader = PdfReader(filename)
    num_pages = len(reader.pages)

    for page_num in range(1, num_pages + 1):
        print(f"📄 Processing PDF page {page_num}/{num_pages}")

        img_b64 = render_pdf_to_base64png(filename, page_num - 1)
        img = Image.open(BytesIO(base64.b64decode(img_b64)))
        anchor_text = get_anchor_text(filename, page_num, "pdfreport", 8000)

        prompt = get_prompt(task_type)(anchor_text)

        response = client.chat.completions.create(
            model="typhoon-ocr-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                ],
            }],
            max_tokens=16384,
            temperature=0.1,
            top_p=0.6,
            extra_body={"repetition_penalty": 1.2},
        )

        output_text = response.choices[0].message.content
        ocr_all_text += output_text + "\n"

elif is_image(filename):
    print(f"🖼️ Processing image: {os.path.basename(filename)}")

    with open(filename, "rb") as f:
        img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")


    prompt = get_prompt(task_type)("")

    response = client.chat.completions.create(
        model="typhoon-ocr-preview",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
            ],
        }],
        max_tokens=16384,
        temperature=0.1,
        top_p=0.6,
        extra_body={"repetition_penalty": 1.2},
    )

    output_text = response.choices[0].message.content
    ocr_all_text = output_text

else:
    raise ValueError("❌ รองรับเฉพาะไฟล์ PDF, PNG, JPG, JPEG เท่านั้น")

# --- OCR เสร็จแล้ว เก็บไว้ในตัวแปร ocr_all_text ---
print("✅ OCR done.")
print(ocr_all_text)
