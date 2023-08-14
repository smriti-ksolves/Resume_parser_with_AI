import pdfplumber
from app.models.get_presigned_url import get_file
import os


def extract_text_from_pdf(file_name, folder_name):
    bucket_name = os.environ.get("S3_BUCKET_NAME")
    response = get_file(file_name, bucket_name, folder_name)
    with pdfplumber.open(file_name) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text
