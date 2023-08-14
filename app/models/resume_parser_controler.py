from app.models.data_parser import Data_Parser, response_validation
from app.models.data_extraction import extract_text_from_pdf


def get_extracted_data(params):
    text_data = extract_text_from_pdf(params["files"])
    res = Data_Parser(text_data)
    response = response_validation(res)
    return response
