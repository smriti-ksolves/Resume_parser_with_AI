import pdfplumber
from app.app import logger


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
        # Open the PDF file using pdfplumber
        with pdfplumber.open(file_name) as pdf:
            # Iterate through each page and extract text
            text = ''.join(page.extract_text() for page in pdf.pages)
            return text  # Return the extracted text
    except Exception as err:
        logger.error(err)
        return text



