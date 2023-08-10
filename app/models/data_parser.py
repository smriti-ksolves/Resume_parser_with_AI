import os
import openai
from dotenv import load_dotenv
import regex

pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
my_keys = ['name', 'email_id', 'phone_no', 'total_experience', 'current_employer', 'current_designation', 'skills',
           'current_skills', 'location']
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path)
openai.api_key = os.environ.get("OPENAI_API_KEY")


def Data_Parser(data):
    try:
        required_field_prompt = '''
        Please provide these details in python json format from given data---> Name, Email ID,Phone Number,Location, Total Experience, Current Employer, Current Designation, Skills, Current Employer Project Skills, URLs ID, college finised year
        and the keys name will be following--> Name-->name, Email ID--> email_id,Phone Number-->phone_no,Location-->location,Total Experience-->total_experience, Current Employer-->current_employer, Current Designation-->current_designation, Skills--> skills,  Current Employer Project Skills --> current_skills,URLs ID-->urls, college finised year-->college_finised_year
        here are the datatypes I need for each keys--> Name: string, Email: string, Phone Number: string, Total Experience: Interger(years) , Current Employer: string, Current Designation: string, Skills: python list,Current Employer Project Skills: python list, URLs: python list

        and the most important thing is don't give any comment things just provide only json data

        '''
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                messages=[
                                                    {"role": "user", "content": required_field_prompt + data[:6000]}],
                                                temperature=0.3,
                                                max_tokens=1000)

        msg = response.get('choices')[0]['message']['content']
        return msg
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


