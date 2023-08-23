from app.models.data_parser import Data_Parser
import regex
import json
from app.app import logger

pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')


def validate_quests_resp(generated_text):
    """
    Validate Generated Interview Questions Response.

    This function validates and extracts interview questions from generated text.

    Args:
        generated_text (str): The generated text containing interview questions.

    Returns:
        dict or None: A dictionary containing interview questions or None if validation fails.

    Algorithm:
        1. Locate the start and end indexes of the JSON data within the generated text.
        2. Extract the relevant JSON data.
        3. Clean up the JSON text by removing newline and tab characters.
        4. Parse the cleaned JSON data using the 'json.loads' function.
        5. If parsing is successful, log an information message and return the parsed data.
        6. If a JSON decoding error occurs, log an error message and return None.
        7. If an exception occurs during processing, log an error message and return None.

    Notes:
        - The function assumes that the relevant JSON data is enclosed within square brackets [].
        - If an exception occurs during processing, an error message with details is logged.

    """
    try:
        start_index = generated_text.index("[")
        end_index = generated_text.rindex("]") + 1
        relevant_json = generated_text[start_index:end_index]

        # Clean up the JSON text
        clean_json = relevant_json.replace("\n", "").replace("\t", "")

        # Parse the cleaned JSON data
        generated_data = json.loads(clean_json)
        logger.info("Generated Text successfully loaded in JSON")
        return generated_data
    except json.JSONDecodeError:
        logger.error("Failed to decode generated JSON data:")
        return None
    except Exception as err:
        logger.error(str(err))
        return None


def get_questions(params):
    """
    Get Interview Questions.

    This function retrieves interview questions based on the provided parameters.

    Args:
        params (dict): A dictionary containing parameters for fetching questions.

    Returns:
        str or dict: The retrieved interview questions as a string, or an error message.

    Algorithm:
        1. Define the path to the questions prompt file.
        2. Check if the "skills" parameter is present in the provided parameters.
        3. If "skills" is present:
            - Retrieve the skills and question count from the parameters.
            - Construct a new dictionary with skills and question count.
            - Parse the data using 'Data_Parser' with constructed parameters.
            - If data is successfully parsed:
                - Strip whitespace from the parsed data.
                - Return the cleaned data as interview questions.
        4. If "skills" is not present, return an error message indicating missing skills field.

    Notes:
        - The 'Data_Parser' function is assumed to be available and handles data parsing.
        - If an exception occurs during processing, an error message with details is logged.

    """
    prompt_path = r"app/db/Skills_based_questions_generator_prompt.txt"
    try:
        if "skills" in params:
            skills = params.get("skills")
            question_cnt = params.get("question_count", 5)
            constructed_params = {
                "skills": skills,
                "question_count": question_cnt
            }
            data = Data_Parser(str(constructed_params), prompt_path)
            if data is not None:
                quest = data.strip()
                return quest
        else:
            return {"error": "skills field missing"}
    except Exception as err:
        logger.error(str(err))
        return {"error": str(err)}


def eval_and_return(data):
    """
    Evaluate and Return Data.

    This function evaluates a given string as Python code and returns the result.

    Args:
        data (str): A string containing Python code to be evaluated.

    Returns:
        Any: The result of the evaluation or an error message.

    Algorithm:
        1. Attempt to evaluate the given data using the 'eval' function.
        2. If evaluation is successful:
            - Log an information message indicating successful evaluation.
            - Return the evaluation result.
        3. If evaluation fails:
            - Log an error message with details of the error.
            - Return an error message indicating an evaluation error.

    Notes:
        - The 'eval' function can execute arbitrary code, so use this function carefully.
        - If an exception occurs during evaluation, an error message with details is logged.

    """
    try:
        result = eval(data)
        logger.info("evaluated")
        return result
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        return {"error": "Error during evaluation."}


def question_validator_and_generator(params):
    """
    Validate and Generate Interview Questions.

    This function validates and generates interview questions based on the provided parameters.

    Args:
        params (dict): A dictionary containing parameters for generating questions.

    Returns:
        dict: A dictionary containing the generated interview questions or an error message.

    Algorithm:
        1. First attempt to get questions using 'get_questions' function.
        2. If an error is present in the data received, return the error.
        3. Validate the data using 'validate_quests_resp' function.
        4. If validation succeeds:
            - If the validated data is a string, evaluate and return it using 'eval_and_return' function.
            - Otherwise, return the validated data.
        5. If validation fails, make a second attempt to get questions.
        6. Validate the data from the second attempt.
        7. If validation succeeds:
            - If the validated data is a string, evaluate and return it using 'eval_and_return' function.
            - Otherwise, return the validated data.
        8. If the second validation also fails, return an error message.

    Notes:
        - If an exception occurs during processing, an error message with details is logged,
          and an error response is returned.

    """
    try:
        # First attempt to get questions
        data = get_questions(params)
        if "error" in data:
            return data

        # Validate the data
        validated_data = validate_quests_resp(data)
        if validated_data is not None:
            if isinstance(validated_data, str):
                return eval_and_return(validated_data)
            else:
                return validated_data

        # Second attempt to get questions
        second_op = get_questions(params)
        valid_data = validate_quests_resp(second_op)
        if valid_data is not None:
            if isinstance(valid_data, str):
                return eval_and_return(valid_data)
            else:
                return valid_data

        return {"error": "Error while validating the response."}
    except Exception as err:
        logger.error(str(err))
        return {"error": str(err)}

# def jp_parser(jb_data):
#     jb_prompt_path = r"app/db/jb_parser_prompt.txt"
#     data = Data_Parser(jb_data, jb_prompt_path)
#
#
# def prepare_questions(candidate_data):
#     prompt_path = r"app/db/prepare_interview_question_prompt.txt"
#     if candidate_data:
#         data = Data_Parser(str(candidate_data), prompt_path)
#         data = eval(pattern.findall(data)[0])
#         return data
#     else:
#         return {"error": "No data found"}
