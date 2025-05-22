from .weaviate_client import WeaviateManager

def initialize_schemas():
    """Initialize all required schemas in Weaviate"""
    try:
        manager = WeaviateManager(admin_access=True)
        manager.create_document_schema()
        print("Schema initialization completed successfully")
    except Exception as e:
        print(f"Error initializing schemas: {e}")
