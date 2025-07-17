# knowledgebase/vectorization.py
import os
from openai import OpenAI
from django.conf import settings

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_embedding(text, dimensions=1536):
    """Generate embeddings using OpenAI's text-embedding-3-large model with consistent dimensions"""
    # Ensure dimensions is always an integer
    if dimensions is None:
        dimensions = 1536
    
    # Clean the text by replacing newlines with spaces
    text = text.replace("\n", " ")
    
    # Create the embedding request with consistent dimensions for cost efficiency
    embedding_params = {
        "model": "text-embedding-3-large",
        "input": text,
        "dimensions": dimensions  # Always specify dimensions for consistency
    }
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_embedding(text, dimensions=1536):
    """Generate embeddings using OpenAI's text-embedding-3-large model with consistent dimensions"""
    # Clean the text by replacing newlines with spaces
    text = text.replace("\n", " ")
    
    # Create the embedding request with consistent 1536 dimensions for cost efficiency
    embedding_params = {
        "model": "text-embedding-3-large",
        "input": text,
        "dimensions": dimensions  # Always specify dimensions for consistency
    }
    
    try:
        # Generate the embedding
        response = client.embeddings.create(**embedding_params)
        
        # Extract and return the embedding vector
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        # Return a zero vector as fallback (not ideal for production)
        return [0.0] * dimensions
