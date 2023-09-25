import os
import openai
from dotenv import load_dotenv
import regex
import time
import re
from app.app import logger

# Define a regular expression pattern to match JSON-like structures within curly braces
pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')

# Define a list of keys for the filtered data
my_keys = ['name', 'email_id', 'phone_no', 'total_experience', 'current_employer', 'current_designation', 'skills',
           'current_skills', 'location']

# Construct the path to the .env file
dotenv_path = os.path.join(os.getcwd(), '.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path)

# Set the OpenAI API key using the environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")


def Data_Parser(data, prompt_file_path):
    """
    Parse resume data using OpenAI's text generation engine.

    This function takes resume data as input and generates a prompt for extracting various details
    such as name, email, phone number, skills, etc., using OpenAI's text-davinci-003 engine. The parsed
    data is returned in JSON format.

    Args:
        data (str): The resume data to be parsed.

    Returns:
        str: Parsed resume data in JSON format.
    """
    try:
        # Read the prompt instructions from a file
        with open(prompt_file_path) as prompt_file:
            prompt = prompt_file.read()

        # Construct the prompt by appending data
        if len(data) > 6000:
            prompt += data[:6000]
        else:
            prompt += data
        # Make a request to OpenAI's text-davinci-003 engine
        parsed_data = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000  # Adjust as needed
        )

        return parsed_data.choices[0].text  # Extract the generated text

    except openai.error.OpenAIError as e:
        if "rate_limit_exceeded" in str(e):
            logger.info("Rate limit exceeded.")
        elif "You exceeded your current quota" in str(e):
            logger.error("Exceeded OpenAI API quota. Please check your plan and billing details.")
        else:
            logger.error(e)
        return None


def clean_name(name):
    """
    Clean a name by removing non-alphanumeric characters.

    This function takes a name as input and removes any characters that are not letters,
    spaces, dots, or hyphens. It also strips any leading or trailing whitespace.

    Args:
        name (str): The name to be cleaned.

    Returns:
        str: The cleaned name.
    """
    cleaned_name = re.sub(r'[^a-zA-Z\s\.\-]', '', name)  # Replace non-alphanumeric characters
    return cleaned_name.strip()  # Remove leading and trailing whitespace


def response_validation(response):
    """
       Validate and process a response.

       This function takes a response, extracts data from it using a regular expression pattern,
       cleans the extracted name if present, and filters the data based on a predefined set of keys.

       Args:
           response (str): The response containing data to be processed.

       Returns:
           dict: Processed and filtered data from the response.
    """
    data = {}
    try:
        data = eval(pattern.findall(response)[0])  # Extract and evaluate data using the pattern
        if data["name"]:
            data["name"] = clean_name(data["name"])  # Clean the name if present

        filtered_data = {key: data[key] for key in my_keys}  # Filter the data based on keys

        return filtered_data

    except (IndexError, KeyError, SyntaxError) as err:

        logger.error(f"Error during response validation: {err}")

    except Exception as err:
        logger.error(f"An unexpected error occurred during response validation: {err}")
        return data  # Return data even if an exception occurs (for error handling)
