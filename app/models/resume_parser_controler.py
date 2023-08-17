import os
from app.models.data_parser import Data_Parser, response_validation
from app.models.data_extraction import extract_text_from_pdf
from app.app import logger


def get_extracted_data(params):
    """
    Extract and process data from PDF files.

    This function takes a dictionary `params` as input, which contains a list of file names to process.
    For each file, it extracts text content from a PDF, parses the text data, validates the response,
    and returns the processed data. It also deletes the local PDF file after processing.

    Args:
        params (dict): A dictionary containing a list of file names to process.

    Returns:
        dict: Processed data extracted from PDF files.
    """
    for file in params.get("files"):
        try:
            folder = os.environ.get("FOLDER_NAME")
            file_obj = folder + file

            # Extract text data from the PDF file
            text_data = extract_text_from_pdf(file_obj, folder)
            if "error" in text_data:
                return text_data

            # Parse the extracted text data
            res = Data_Parser(text_data)
            if "error" in res:
                return res

            # Validate and filter the parsed response
            response = response_validation(res)
            if response:
                # Remove the local PDF file
                os.remove(file_obj)

                return response  # Return the processed response
            else:
                return {"error": "Error during response validation"}
        except Exception as err:
            logger.error(err)
            return {"error": "An error occurred during processing."}

    return {"error": "No files found for processing."}