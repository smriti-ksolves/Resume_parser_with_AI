import os
from app.models.data_parser import Data_Parser, response_validation
from app.models.data_extraction import extract_text_from_pdf
from app.app import logger
from app.models.resumedata import resume_data_create
from app.models.get_presigned_url import get_file


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
    candidates_data = []
    for file in params.get("files"):
        data_dict = dict()
        if isinstance(file, str) and file.endswith(".pdf"):
            folder = os.environ.get("FOLDER_NAME")
            file_obj = folder + file
            bucket_name = os.environ.get("S3_BUCKET_NAME")

            try:
                get_file(file_obj, bucket_name, folder)

                # Extract text data from the PDF file
                text_data = extract_text_from_pdf(file_obj)

                if text_data:
                    # Parse the extracted text data
                    res = Data_Parser(text_data)

                    # Validate and filter the parsed response
                    if res is not None:
                        data = response_validation(res)
                        if data:
                            # Remove the local PDF file
                            response = resume_data_create(params, data)
                            if response is not None:
                                data_dict[file] = response
                                candidates_data.append(data_dict)

            except Exception as err:
                logger.error(err)
                candidates_data.append({file: {}})

            finally:
                if os.path.exists(file_obj):
                    os.remove(file_obj)
        else:
            candidates_data.append({file: {}})
    return candidates_data
