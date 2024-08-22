import os
from pypdf import PdfReader
from anthropic import Anthropic
import tiktoken  # Token counting library


# Initialize the Anthropic client with the API key
api_key = os.environ.get('CLAUDE_API_KEY')
client = Anthropic(api_key=api_key)

MODEL_NAME = "claude-3-sonnet-20240229"
TOKEN_LIMIT = 9000
CACHE_FILE = "cached_results.json"




def cache_results(messages, filename):
    """Cache messages to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(messages, f, indent=4)
    print(f"Results cached in {filename}")
def count_tokens(text):
    """Count the number of tokens in the text."""
    enc = tiktoken.get_encoding("cl100k_base")  # Use the correct encoding for Claude
    tokens = enc.encode(text)
    return len(tokens)

def split_text_into_chunks(text, chunk_size):
    """Split text into chunks under the specified size limit."""
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]

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

def sendChunksToClaude(messages, chunk, token_count):
    """Send chunks to Claude and ensure token limit is not exceeded."""
    chunk_tokens = count_tokens(chunk)
    
    if token_count + chunk_tokens > TOKEN_LIMIT:
        # Cache results if token limit is exceeded
        cache_results(messages, CACHE_FILE)
        # Reset messages and token count
        messages.clear()
        token_count = 0

    # Add the chunk to messages
    messages.append({
        "role": "user",
        "content": (
            "You don't have to respond to these messages now. I will send the text I want you to elaborate on in chunks, "
            "and then let you know when I want you to respond. Here is the text:\n\n"
            f"{chunk}"
        )
    })
    token_count += chunk_tokens

    # Optionally send and process response
    response = getResponse(messages)
    messages.append({"role": "assistant", "content": response})

    return messages, token_count

def elaborate_on_topic(topic, messages):
    """Elaborate on a topic using Claude API."""
    messages.append({"role": 'user', "content": f"Elaborate on the topic: {topic}"})
    response = getResponse(messages)
    messages.append({"role": 'assistant', "content": response})  # Add the assistant's response to the messages
    return response
    


def generate_quiz_and_outline(messages, text, chunks): #chunks boolean
    """Generates quiz questions and a study outline using Claude API."""
    if(chunks):
        #already sent the chunks prior, so just ask for the quiz and outline
        messages.append(
        {
            "role": "user",
            "content": f"Generate 10 multiple choice quiz questions along with answers at the end for the text. Also create a study outline for the text."
        }
        )
        response = getResponse(messages)
        messages.append(
            {"role": "assistant", "content": response}
        )  # Add the assistant's response to the messages
        return response

    else:
        messages.append(
            {
                "role": "user",
                "content": f"Generate quiz questions and study outline for the text: {text}",
            }
        )
        response = getResponse(messages)
        messages.append(
            {"role": "assistant", "content": response}
        )  # Add the assistant's response to the messages
        return response
