from app.models.data_parser import Data_Parser
import regex
import json
from app.app import logger

pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')


def validate_quests_resp(generated_text):
    try:
        start_index = generated_text.index("[")
        end_index = generated_text.rindex("]") + 1
        relevant_json = generated_text[start_index:end_index]

        # Parse the JSON data
        generated_data = json.loads(relevant_json)
        logger.info("Generated Text successfully loaded in json")
        return generated_data
    except json.JSONDecodeError:
        logger.error("Failed to decode generated JSON data:")
        return []
    except Exception as err:
        logger.error(str(err))
        return []


def jp_parser(jb_data):
    jb_prompt_path = r"app/db/jb_parser_prompt.txt"
    data = Data_Parser(jb_data, jb_prompt_path)


def prepare_questions(candidate_data):
    prompt_path = r"app/db/prepare_interview_question_prompt.txt"
    if candidate_data:
        data = Data_Parser(str(candidate_data), prompt_path)
        data = eval(pattern.findall(data)[0])
        return data
    else:
        return {"error": "No data found"}


def get_questions(params):
    prompt_path = r"app/db/Skills_based_questions_generator_prompt.txt"
    try:
        if "skills" in params:
            skills = params.get("skills")
            question_cnt = 10
            params = {
                "skills": skills,
                "question_count": question_cnt
            }
            data = Data_Parser(str(params), prompt_path)
            quest = data.strip()
            return quest
        else:
            return {"error": "skills field missing"}
    except Exception as err:
        logger.error(str(err))
        return {"error": str(err)}


def question_validator_and_gererator(params):
    try:
        data = get_questions(params)
        if "error" in data:
            return data
        validated_data = validate_quests_resp(data)
        if validated_data:
            return {"data": validated_data}
        else:
            second_op = get_questions(params)
            valid_Data = validate_quests_resp(second_op)
            if valid_Data:
                return {"data": valid_Data}
            else:
                return {"error": "Error While validating the response."}
    except Exception as err:
        logger.error(str(err))
        return {"error": str(err)}
