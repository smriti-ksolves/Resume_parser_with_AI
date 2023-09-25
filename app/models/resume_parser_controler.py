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
        data_dict = {"file_name": file}
        prompt_file_path = r"app/db/resume_parser_prompt.txt"
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
                    res = Data_Parser(text_data, prompt_file_path)

                    # Validate and filter the parsed response
                    if res is not None:
                        data = response_validation(res)
                        if data:
                            # # Remove the local PDF file
                            # response = resume_data_create(params, data)
                            # if response is not None:
                            merged_dict = {**data_dict, **data, "file_status": "success"}
                            # data_dict[file] = data
                            candidates_data.append(merged_dict)
                            # else:
                            #     candidates_data.append({file: {"error": "Error while storing data in database"}})
                        else:
                            error_data = {"error": "Parser Data has some incorrect data format", "file_status": "error"}
                            merged_dict = {**data_dict, **error_data}
                            candidates_data.append(merged_dict)
                    else:
                        error_data = {"error": "Error While parsing data from open AI", "file_status": "error"}
                        merged_dict = {**data_dict, **error_data}
                        candidates_data.append(merged_dict)

                else:
                    error_data = {"error": "Error while Extracting data from pdf", "file_status": "error"}
                    merged_dict = {**data_dict, **error_data}
                    candidates_data.append(merged_dict)

            except Exception as err:
                logger.error(err)
                error_data = {"error": str(err), "status": "error"}
                merged_dict = {**data_dict, **error_data}
                candidates_data.append(merged_dict)

            finally:
                if os.path.exists(file_obj):
                    os.remove(file_obj)
        else:
            error_data = {"error": "Please upload pdf only under 50 kb"}
            merged_dict = {**data_dict, **error_data}
            candidates_data.append(merged_dict)
    return candidates_data
