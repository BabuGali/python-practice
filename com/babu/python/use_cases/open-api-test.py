from openai import OpenAI

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="API_KEY",
)

def invoke_open_api_and_return_response(prompt):
  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user",
        "content": prompt,
      },
    ],
  )
  return completion.choices[0].message.content

prompt = "how to identify equivalent fractions?"
response = invoke_open_api_and_return_response(prompt)
print(response)
