import os
from django.conf import settings
from ai_assistant.utils.weaviate_client import WeaviateManager

# Define documents directory
DOCUMENTS_DIR = os.path.join(settings.BASE_DIR, 'documents')

def process_all_text_documents():
    """Process all text documents in the documents directory"""
    weaviate_manager = WeaviateManager(admin_access=True)
    processed_count = 0
    
    # Check if directory exists
    if not os.path.exists(DOCUMENTS_DIR):
        print(f"Directory not found: {DOCUMENTS_DIR}")
        return 0
    
    for filename in os.listdir(DOCUMENTS_DIR):
        if filename.endswith('.txt'):
            file_path = os.path.join(DOCUMENTS_DIR, filename)
            print(f"Processing {filename}...")
            process_text_document(file_path, weaviate_manager)
            processed_count += 1
            
    return processed_count

def process_text_document(file_path, weaviate_manager=None):
    """Process a single text document and store it in Weaviate"""
    # Get the file name as title
    title = os.path.basename(file_path)
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create manager if not provided
    if weaviate_manager is None:
        # Use context manager for automatic cleanup
        with WeaviateManager(admin_access=True) as manager:
            document_uuid = manager.store_document(title, content, file_path)
            return document_uuid
    else:
        # Use the provided manager
        document_uuid = weaviate_manager.store_document(title, content, file_path)
        return document_uuid

