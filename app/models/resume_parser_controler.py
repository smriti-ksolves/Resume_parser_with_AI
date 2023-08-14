import os

from app.models.data_parser import Data_Parser, response_validation
from app.models.data_extraction import extract_text_from_pdf


def get_extracted_data(params):
    for file in params.get("files"):
        try:
            folder = os.environ.get("FOLDER_NAME")
            file_obj = folder + file
            text_data = extract_text_from_pdf(file_obj, folder)
            res = Data_Parser(text_data)
            response = response_validation(res)
            os.remove(file_obj)
            return response
        except:
            pass
