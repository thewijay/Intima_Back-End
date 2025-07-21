import weaviate
from django.conf import settings
from weaviate.connect import ConnectionParams
from weaviate.classes.config import Configure
from weaviate.auth import AuthApiKey  # Correct import to avoid deprecation warning
from uuid import uuid5, NAMESPACE_URL
import os
from django.utils import timezone
import logging

# Set up logging
logger = logging.getLogger(__name__)

class WeaviateManager:
    def __init__(self, admin_access=False):
        # Set the appropriate API key based on access level
        if admin_access:
            self.api_key = os.environ.get('WEAVIATE_ADMIN_KEY')
        else:
            self.api_key = os.environ.get('WEAVIATE_USER_KEY')
            
        self.admin_access = admin_access
        self.client = None
        self.collections = None
        self.connect()
        
    def connect(self):
        """Explicitly connect to Weaviate"""
        try:
            connection_params = ConnectionParams.from_url(
                url=settings.WEAVIATE_URL,
                grpc_port=50051  # Default gRPC port for Weaviate
            )

            # Connect with authentication
            self.client = weaviate.WeaviateClient(
                connection_params=connection_params,
                auth_client_secret=AuthApiKey(api_key=self.api_key)
            )

            # Explicitly connect the client
            self.client.connect()
            
            # Get the collections object for easier access
            self.collections = self.client.collections
            
        except Exception as e:
            print(f"Error initializing Weaviate connection: {e}")
            raise

    def __enter__(self):
        """Support for context manager pattern"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection is closed when exiting context"""
        self.close()
            
    def close(self):
        """Explicitly close the client connection"""
        if hasattr(self, 'client') and self.client is not None:
            try:
                self.client.close()
                self.client = None
                self.collections = None
            except Exception as e:
                print(f"Error closing Weaviate connection: {e}")

    def __del__(self):
        """Ensure client is closed when object is destroyed"""
        self.close()

    def ensure_connected(self):
        """Ensure the client is connected, reconnect if necessary"""
        if self.client is None:
            self.connect()
            return
            
        try:
            # Simple operation to test connection
            self.client.get_meta()
        except weaviate.exceptions.WeaviateClosedClientError:
            print("Reconnecting to Weaviate...")
            self.connect()
        except Exception as e:
            print(f"Error checking Weaviate connection: {e}")
            # Attempt to reconnect
            self.connect()

    def create_document_schema(self):
        """Create schema for document storage if it doesn't exist"""
        # Best practice: Explicitly define schema rather than using auto-schema
        try:
            self.ensure_connected()
            self.collections.get("Document")
            print("Document collection already exists")
        except weaviate.exceptions.WeaviateQueryError:
            # Create the collection with explicit properties
            self.collections.create(
                name="Document",
                description="A document in the knowledge base",
                vectorizer_config=Configure.Vectorizer.none(),  # We'll provide our own vectors
                properties=[
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "The content of the document"
                    },
                    {
                        "name": "title", 
                        "dataType": ["string"],
                        "description": "The title of the document"
                    },
                    {
                        "name": "file_path",
                        "dataType": ["string"],
                        "description": "Path to the original document"
                    }
                ]
            )
            print("Created Document collection")
    
    def store_document(self, title, content, file_path):
        """Store a document with its embedding in Weaviate"""
        from knowledgebase.vectorization import generate_embedding
        
        try:
            # Ensure connection is active
            self.ensure_connected()
                
            # Normalize the file path to ensure consistency
            normalized_path = os.path.normpath(file_path)
                
            # Generate a deterministic UUID based on the file path
            deterministic_uuid = str(uuid5(NAMESPACE_URL, normalized_path))
                
            # Check if document with this UUID already exists
            documents = self.collections.get("Document")
                
            # Use exists() method instead of get_by_id()
            exists = documents.data.exists(deterministic_uuid)
                
            if exists:
                print(f"Document {title} already exists with UUID: {deterministic_uuid}")
                return deterministic_uuid
                    
            # Generate embedding
            embedding = generate_embedding(content)
            print(f"Generated embedding with {len(embedding)} dimensions")
                
            # Insert the document with its vector and deterministic UUID
            result = documents.data.insert(
                properties={
                    "title": title,
                    "content": content,
                    "file_path": normalized_path
                },
                vector=embedding,
                uuid=deterministic_uuid
            )
                
            print(f"Document {title} stored with UUID: {deterministic_uuid}")
            return deterministic_uuid
        
        except weaviate.exceptions.UnexpectedStatusCodeError as e:
            # Handle the case where the object already exists (status 422)
            if "already exists" in str(e):
                print(f"Document {title} already exists with UUID: {deterministic_uuid}")
                return deterministic_uuid
            else:
                print(f"Error storing document: {e}")
                raise
        except Exception as e:
            print(f"Error storing document: {e}")
            raise

    def search_documents(self, query, limit=5, embedding_dimensions=None):
        """Search for documents similar to the query using text-embedding-3-large"""
        from knowledgebase.vectorization import generate_embedding
        
        try:
            # Ensure connection is active
            self.ensure_connected()
            
            # Use consistent 1536 dimensions if none specified
            if embedding_dimensions is None:
                embedding_dimensions = 1536
            
            # Generate embedding for the query with optional dimensions
            query_embedding = generate_embedding(query, dimensions=embedding_dimensions)
            logger.info(f"Generated query embedding with {len(query_embedding)} dimensions")
            
            # Get the Document collection
            documents = self.collections.get("Document")
            
            # Search for similar documents
            result = documents.query.near_vector(
                near_vector=query_embedding,
                limit=limit,
                return_properties=["title", "content", "file_path"],
                include_vector=False
            )
            
            print(f"Search completed: found {len(result.objects)} results")
            
            # Return the objects
            return result.objects

            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            import traceback
            traceback.print_exc()
            return []
