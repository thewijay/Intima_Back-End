from django.core.management.base import BaseCommand
from ai_assistant.utils.weaviate_client import WeaviateManager
from knowledgebase.vectorization import generate_embedding

class Command(BaseCommand):
    help = 'Debug vector search functionality'
    
    def handle(self, *args, **options):
        query = "safe sex practices"
        
        with WeaviateManager(admin_access=True) as manager:
            # Step 1: Test embedding generation
            try:
                embedding = generate_embedding(query)
                self.stdout.write(f"✓ Embedding generated: {len(embedding)} dimensions")
            except Exception as e:
                self.stdout.write(f"✗ Embedding failed: {e}")
                return
            
            # Step 2: Test Weaviate connection
            try:
                documents = manager.collections.get("Document")
                self.stdout.write("✓ Weaviate connection successful")
            except Exception as e:
                self.stdout.write(f"✗ Weaviate connection failed: {e}")
                return
            
            # Step 3: Test basic document fetch
            try:
                all_docs = documents.query.fetch_objects(
                    limit=5,
                    return_properties=["title"]
                )
                self.stdout.write(f"✓ Found {len(all_docs.objects)} documents total")
                for doc in all_docs.objects:
                    self.stdout.write(f"  - {doc.properties.get('title')}")
            except Exception as e:
                self.stdout.write(f"✗ Document fetch failed: {e}")
                return
            
            # Step 4: Test vector search
            try:
                result = documents.query.near_vector(
                    near_vector=embedding,
                    limit=5,
                    return_properties=["title", "content"],
                    include_vector=False
                )
                self.stdout.write(f"✓ Vector search returned {len(result.objects)} results")
                
                for i, doc in enumerate(result.objects, 1):
                    title = doc.properties.get("title", "Unknown")
                    content_preview = doc.properties.get("content", "")[:100]
                    self.stdout.write(f"  {i}. {title}: {content_preview}...")
                    
            except Exception as e:
                self.stdout.write(f"✗ Vector search failed: {e}")
                self.stdout.write(f"Error details: {type(e).__name__}: {str(e)}")
