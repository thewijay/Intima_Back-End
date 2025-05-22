# knowledgebase/vectorization.py
import os
from openai import OpenAI
from django.conf import settings

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_embedding(text, dimensions=None):
    """Generate embeddings using OpenAI's text-embedding-3-large model"""
    # Clean the text by replacing newlines with spaces
    text = text.replace("\n", " ")
    
    # Create the embedding request
    embedding_params = {
        "model": "text-embedding-3-large",
        "input": text
    }
    
    # Add dimensions parameter if specified
    if dimensions:
        embedding_params["dimensions"] = dimensions
    
    try:
        # Generate the embedding
        response = client.embeddings.create(**embedding_params)
        
        # Extract and return the embedding vector
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        # Return a zero vector as fallback (not ideal for production)
        return [0.0] * (dimensions or 1536)
