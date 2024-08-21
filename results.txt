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
            file_name = 'GreatDepression.pdf'
            # Fetch the PDF data from storage
            pdf_data_io = get_pdf_data_from_storage(file_name)
            # Extract text from the PDF
            text = extract_pdf_text(pdf_data_io)
            topic = "The impact of Keynesian economics on the Great Depression"
            # topic = "The Indo-Europeans, and their diverse languages, cultures, and living locations"
            
            messages = []
            quiz_outline_response = generate_quiz_and_outline(messages, text)
            # Elaborate on the topic
            elaboration_response = elaborate_on_topic(topic, messages)
            # Create a JSON object with separate sections
            response_json = {
                "GreatDepressionQuizOutline": quiz_outline_response,
                "GreatDepressionElaboration": elaboration_response
            }

            return response_json
    
    except Exception as e:
        error_message = f"Error processing request: {e}"
        print(error_message)
        return make_response(jsonify({"error": error_message}), 500)

