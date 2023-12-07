import openai
from openai import OpenAI
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
import io
#https://www.singlestore.com/spaces/resume-evaluator/

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="TEST_KEY",
)

def add_data_to_db(input_dict):
    # Create the SQLAlchemy engine
    # engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database_name}')

    engine = create_engine(connection_url)
    # Get the embedding for the summary text
    summary = input_dict['summary']
    embedding = get_embedding(summary)
    # Create the SQL query for inserting the data
    query_sql = f"""
        INSERT INTO resumes_profile_data (names, email, phone_no, years_of_experience, skills, profile_name, resume_summary, resume_embeddings)
        VALUES ("{input_dict['name']}", "{input_dict['email']}", "{input_dict['phone_no']}", "{input_dict['years_of_expiernce']}",
        "{input_dict['skills']}", "{input_dict['profile']}", "{summary}", JSON_ARRAY_PACK('{embedding}'));
    """
    with engine.connect() as connection:
        connection.execute(text(query_sql))
        connection.commit()
    print("\nData Written to resumes_profile_data_2 table")
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def parse_resume(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()

    return text

def pinfo_extractor(resume_text):
    context = f"Resume text: {resume_text}"
    question = """ From above candidate's resume text, extract the only following details:
                Name: (Find the candidate's full name. If not available, specify "not available.")
                Email: (Locate the candidate's email address. If not available, specify "not available.")
                Phone Number: (Identify the candidate's phone number. If not found, specify "not available.")
                Years of Experience: (If not explicitly mentioned, calculate the years of experience by analyzing the time durations at each company or position listed. Sum up the total durations to estimate the years of experience. If not determinable, write "not available.")
                Skills Set: Extract the skills which are purely technical and represent them as: [skill1, skill2,... <other skills from resume>]. If no skills are provided, state "not available."
                Profile: (Identify the candidate's job profile or designation. If not mentioned, specify "not available.")
                Summary: provide a brief summary of the candidate's profile without using more than one newline to segregate sections.
                """

    prompt = f"""
        Based on the below given candidate information, only answer asked question:
        {context}
        Question: {question}
    """
    # print(prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful HR recruiter."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=700,
        temperature=0.5,
        n=1  # assuming you want one generation per document
    )
    # Extract the generated response
    response_text = response.choices[0].message.content # response['choices'][0]['message']['content']
    print(response_text)
    # Split the response_text into lines
    lines = response_text.strip().split('\n')

    # Now, split each line on the colon to separate the labels from the values
    # Extract the values
    name = lines[0].split(': ')[1]
    email = lines[1].split(': ')[1]
    phone_no = lines[2].split(': ')[1]
    years_of_expiernce = lines[3].split(': ')[1]
    skills = lines[4].split(': ')[1]
    profile = lines[5].split(': ')[1]
    summary = lines[6].split(': ')[1]
    data_dict = {
        'name': name,
        'email': email,
        'phone_no': phone_no,
        'years_of_expiernce': years_of_expiernce,
        'skills': skills,
        'profile': profile,
        'summary': summary
    }
    print(data_dict, "\n")
    return data_dict;

def search_resumes(query):
    query_embed = get_embedding(query)
    query_sql = f"""
            SELECT names, resume_summary, dot_product(
                    JSON_ARRAY_PACK('{query_embed}'),
                    resume_embeddings
                ) AS similarity
                FROM resumes_profile_data
                ORDER BY similarity DESC
                LIMIT 5;
    """
    # print(query_sql,"\n")
    # engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database_name}')
    engine = create_engine(connection_url)
    connection = engine.connect()
    result = connection.execute(text(query_sql)).fetchall()
    connection.close()
    engine.dispose()
    return result


def evaluate_candidates(query):
    result = search_resumes(query)
    responses = []  # List to store responses for each candidate
    for resume_str in result:
        name = resume_str[0]
        context = f"Resume text: {resume_str[1]}"
        question = f"What percentage of the job requirements does the candidate meet for the following job description? answer in 3 lines only and be effcient while answering: {query}."
        prompt = f"""
            Read below candidate information about the candidate:
            {context}
            Question: {question}
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a expert HR analyst and recuriter."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.2,
            n=1  # assuming you want one generation per document
        )
        # Extract the generated response
        response_text = response.choices[0].message.content # response['choices'][0]['message']['content']
        responses.append((name, response_text))  # Append the name and response_text to the responses list
    return responses

txt = parse_resume('D:\\delete\\resume.pdf')
pi_info = pinfo_extractor(txt)
print("------------")
print(pi_info)


job_description = input("Enter Job description : \n")
evaluate_candidates(job_description)