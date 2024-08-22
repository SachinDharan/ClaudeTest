import functions_framework
import io
from flask import jsonify, make_response
from ClaudeApi import extract_pdf_text, elaborate_on_topic, generate_quiz_and_outline
from google.cloud import storage
import os

def get_pdf_data_from_storage(fileName):
    bucket_name = "my_pdf_bucket1"
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(fileName)
        
        pdf_data = blob.download_as_bytes()
        pdf_data_io = io.BytesIO(pdf_data)
        return pdf_data_io
    
    except Exception as e:
        print(f"Error accessing cloud storage: {e}")
        raise

@functions_framework.http
@functions_framework.http
def hello_http(request):
    # Define constants
    TOKEN_LIMIT = 9000
    CHUNK_SIZE = 50 * 1024  # 50 KB per chunk
    MAX_FILES = 5  # Maximum of 5 files at a time
    CACHE_FILE = "cached_results.json"
    try:
        file_path = "results.txt"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                content = file.read()
            # Return the content as a plain text HTTP response
            response = make_response(content, 200)
            response.headers['Content-Type'] = 'text/plain'
            return response
        else:
            # Directly use the hardcoded file name
            file_name = 'HSWorldHistory.pdf'
            # Fetch the PDF data from storage
            pdf_data_io = get_pdf_data_from_storage(file_name)
            # Extract text from the PDF
            text = extract_pdf_text(pdf_data_io)
            text_size = len(text.encode('utf-8'))
            chunks = []
            chunkCheck = 0
            # Only split into chunks if the text size exceeds the chunk size
            if text_size > CHUNK_SIZE:
                chunkCheck = 1
                chunks = list(split_text_into_chunks(text, CHUNK_SIZE))
                if len(chunks) > MAX_FILES:
                    raise ValueError(f"The PDF file is too large. It resulted in {len(chunks)} chunks, exceeding the {MAX_FILES} limit.")
            
            topic = "The Indo-Europeans, and their diverse languages, cultures, and living locations"            
            messages = []
            # Define the file path
            file_path = "cached_results.json"
            messages = None
            # Check if the file exists
            if os.path.exists(file_path):
                # Read the list from the file into variable messages
                with open(file_path, "r") as file:
                    messages = json.load(file)
            else:
                
                print("cached_results.json does not exist.")
                messages = []
                token_count = 0
            
                # Process each chunk
                if len(chunks) > 0:
                    for chunk in chunks:
                        messages, token_count = sendChunksToClaude(messages, chunk, token_count)
            
                # Final caching if there are remaining messages
                if messages:
                    cache_results(messages, CACHE_FILE)
            
            quiz_outline_response = generate_quiz_and_outline(messages, text, chunkCheck)
            #send to txt file called quizOutlineResponse.txt
            with open("quizOutlineResponse.txt", "w") as file:
                file.write(quiz_outline_response)
            
            # Elaborate on the topic
            elaboration_response = elaborate_on_topic(topic, messages)
            #send to txt file called elaborationResponse.txt
            with open("elaborationResponse.txt", "w") as file:
                file.write(elaboration_response)

    
    except Exception as e:
        error_message = f"Error processing request: {e}"
        print(error_message)
        return make_response(jsonify({"error": error_message}), 500)

