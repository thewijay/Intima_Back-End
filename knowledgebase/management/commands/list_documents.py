from django.core.management.base import BaseCommand
from ai_assistant.utils.weaviate_client import WeaviateManager

class Command(BaseCommand):
    help = 'List all documents in Weaviate'
    
    def handle(self, *args, **options):
        # Use admin_access=True to ensure proper permissions
        with WeaviateManager(admin_access=True) as manager:
            documents = manager.collections.get("Document")
            result = documents.query.fetch_objects(
                limit=100,
                return_properties=["title", "file_path"]
            )
            
            self.stdout.write(f"Found {len(result.objects)} documents:")
            for doc in result.objects:
                self.stdout.write(f"- {doc.properties['title']} (UUID: {doc.uuid})")
