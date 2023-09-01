import pdfplumber
from app.app import logger
import os


def file_validation(file_name):
    allowed_extension = os.getenv("ALLOWED_EXTENSION")
    max_file_size_bytes = os.getenv("MAX_FILE_SIZE")
    if os.path.getsize(file_name) > int(max_file_size_bytes):
        logger.error("File size exceeds the maximum allowed size.")
        return {"error": "File size exceeds the maximum allowed size."}
    file_extension = os.path.splitext(file_name)[1]
    if file_extension.lower() != allowed_extension:
        # File is not a PDF, handle accordingly (e.g., raise an error)
        logger.error("File is not a PDF.")
        return {"error": "File is not a PDF."}
    else:
        return {"success": "File Type and Size is correct"}


def extract_text_from_pdf(file_name):
    """
     Extract text from a PDF file.

     This function takes a PDF file name and a folder name as input, fetches the PDF file from an S3 bucket,
     and extracts text content from the PDF using the pdfplumber library.

     Args:
         file_name (str): The name of the PDF file to be extracted.
         folder_name (str): The name of the folder in the S3 bucket where the file is located.

     Returns:
         str: Extracted text content from the PDF file.
     """
    # Get the S3 bucket name from environment variable
    text = ""
    try:
        # Get the PDF file from the S3 bucket using the provided function get_file()
        logger.info("Pdf Data Extraction Started")
        message = file_validation(file_name)
        if "success" in message:
            # Open the PDF file using pdfplumber
            with pdfplumber.open(file_name) as pdf:
                # Iterate through each page and extract text
                text = ''.join(page.extract_text() for page in pdf.pages)
                return text  # Return the extracted text
        else:
            logger.error(message["error"])
            return text
    except Exception as err:
        logger.error(err)
        return text
