import os
import json
from tqdm import tqdm
from PyPDF2 import PdfReader

INPUT_FOLDER = "./data/papers"
OUTPUT_FOLDER = "./data/processed_json"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def main():
    print("📄 Extracting all PDFs to JSON...")
    for filename in tqdm(os.listdir(INPUT_FOLDER)):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(INPUT_FOLDER, filename)
            text = extract_text_from_pdf(pdf_path)
            output_path = os.path.join(OUTPUT_FOLDER, filename.replace(".pdf", ".json"))

            data = {
                "file_name": filename,
                "Sections": {
                    "FullText": {"text": text, "entities": {}}
                }
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    print("✅ All PDFs converted to JSON")

if __name__ == "__main__":
    main()
