from app.models.data_parser import Data_Parser


def jp_parser(jb_data):
    jb_prompt_path = r"app/db/jb_parser_prompt.txt"
    data = Data_Parser(jb_data, jb_prompt_path)
