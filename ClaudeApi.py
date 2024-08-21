import os
from pypdf import PdfReader
from anthropic import Anthropic

# Initialize the Anthropic client with the API key
api_key = os.environ.get('CLAUDE_API_KEY')
client = Anthropic(api_key=api_key)

MODEL_NAME = "claude-3-sonnet-20240229"


def getResponse(messages):

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1024,
        messages=messages
    )
    return response.content[0].text

def extract_pdf_text(pdf_data):
    try:
        reader = PdfReader(pdf_data)
        text = ''.join(page.extract_text() for page in reader.pages)
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise

def elaborate_on_topic(topic, messages):
    """Elaborate on a topic using Claude API."""
    messages.append({"role": 'user', "content": f"Elaborate on the topic: {topic}"})
    response = getResponse(messages)
    messages.append({"role": 'assistant', "content": response})  # Add the assistant's response to the messages
    return response
    


def generate_quiz_and_outline( messages, text):
    """Generates quiz questions and a study outline using Claude API."""
    messages.append({"role": 'user', "content": f"Generate 10 multiple choice quiz questions and study outline for the text, include answers at the end as well: {text}"})
    response = getResponse(messages)
    messages.append({"role": 'assistant', "content": response})  # Add the assistant's response to the messages
    return response
