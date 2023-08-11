import os
import openai
from dotenv import load_dotenv
import regex
import time

pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
my_keys = ['name', 'email_id', 'phone_no', 'total_experience', 'current_employer', 'current_designation', 'skills',
           'current_skills', 'location']
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path)
openai.api_key = os.environ.get("OPENAI_API_KEY")


def Data_Parser(data):
    try:
        prompt = f'''Please extract the following details from the provided resume text and present them in Python JSON format:
        - Name
        - Email ID
        - Phone Number
        - Location
        - Total Experience
        - Current Employer (Identify the candidate's most recent workplace, focusing on keywords like "Current Employer," "Recent Job," or "Present Company")
        - Current Designation
        - Skills
        - Current Employer Project Skills
        - URLs ID
        - College Finished Year
        
        For each detail, please use the following keys in the JSON:
        - Name: name (string)
        - Email ID: email_id (string)
        - Phone Number: phone_no (string)
        - Location: location (string)
        - Total Experience: total_experience (integer in years)
        - Current Employer: current_employer (string)
        - Current Designation: current_designation (string)
        - Skills: skills (list of strings)
        - Current Employer Project Skills: current_skills (list of strings)
        - URLs ID: urls (list of strings)
        - College Finished Year: college_finished_year (string)
        Please note that the resume may have formatting variations that affect text extraction. To address this:
        
        1.  perform text cleaning to remove unwanted characters, extra spaces, and line breaks.
        2. Utilize regular expressions (regex) to match patterns for fields like names, email IDs, phone numbers, etc., considering possible variations.
        
        Feel free to experiment with your parsing logic and test it on various resumes to improve accuracy. Avoid including any comment or code in the JSON output.
        
        For the "name" field, please employ advanced text processing techniques to identify patterns resembling names, even if they are presented in separate characters or unusual formats. Regular expressions or pattern matching can be useful for this purpose.
        
        To identify the current employer, focus on sections titled "Work Experience," "Employment History," or similar headings. Avoid including any comments in the JSON output. Provide only the JSON data.
        
                
        Resume:-
        
        {data[:6000]}

        '''

        def make_openai_request():
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=1000  # Adjust as needed
            )
            return response

        while True:
            try:
                parsed_data = make_openai_request()
                break  # If successful, break the loop
            except openai.error.OpenAIError as e:
                if "rate_limit_exceeded" in str(e):
                    wait_time = 20  # seconds
                    print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise e

        parsed_data = parsed_data.choices[0].text
        return parsed_data
    except Exception as err:
        msg = Data_Parser(data)
        return msg


def response_validation(response):
    data = {}
    try:
        data = eval(pattern.findall(response)[0])
        filtered_data = {key: data[key] for key in my_keys}

        return filtered_data
    except Exception as err:
        return data


