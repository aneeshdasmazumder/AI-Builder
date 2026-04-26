#imports

import os
from dotenv import load_dotenv
from scraper import fetch_website_contents
from IPython.display import Markdown, display
from openai import OpenAI
# Load environment variables

# Load environment variables

# Load environment variables in a file called .env

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

# Check the key

client = None
valid_api_key = False

if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.isascii():
    bad_chars = [(index, f"U+{ord(char):04X}") for index, char in enumerate(api_key) if not char.isascii()]
    print(f"An API key was found, but it contains non-ASCII characters at: {bad_chars}. Please re-copy it from OpenAI and replace the value in your .env file.")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    client = OpenAI(api_key=api_key)
    valid_api_key = True
    print("API key found and looks good so far!")

#message = "Hi there, this is the first time I'm using the OpenAI API - can you say hi back to me?"

#messages = [{"role": "user", "content": message}]

"""
if api_key and api_key.startswith("sk-proj-") and api_key.strip() == api_key:
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(model="gpt-5-nano", messages=messages)
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI request failed: {e}")
"""

ed = fetch_website_contents("https://www.hyland.com/en")
print(ed)
"""
messages = [
    {"role": "system", "content": "You're a snarky assistant"},
    {"role": "user", "content": "What is 2+2?"}
]

if api_key and api_key.startswith("sk-proj-") and api_key.strip() == api_key:
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(model="gpt-4.1-nano", messages=messages)
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI request failed: {e}")
"""
# Define our system prompt - you can experiment with this later, changing the last sentence to 'Respond in markdown in Spanish."

system_prompt = """
You are a snarky assistant that analyzes the contents of a website,
and provides a short, snarky, humorous summary, ignoring text that might be navigation related.
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""

# Define our user prompt

user_prompt_prefix = """
Here are the contents of a website.
Provide a short summary of this website.
If it includes news or announcements, then summarize these too.

"""

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_prefix + website}
    ]

messages_for(ed)

# And now: call the OpenAI API. You will get very familiar with this!

def summarize(url):
    if not valid_api_key:
        return "Skipping the OpenAI request until the API key is fixed."

    website = fetch_website_contents(url)
    response = client.chat.completions.create(
        model = "gpt-4.1-mini",
        messages = messages_for(website)
    )
    return response.choices[0].message.content

summarize("https://www.hyland.com/en")

# A function to display this nicely in the output, using markdown

def display_summary(url):
    summary = summarize(url)
    display(Markdown(summary))

display_summary("https://www.hyland.com/en")
