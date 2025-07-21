from django.core.management.base import BaseCommand
from ai_assistant.utils.weaviate_client import WeaviateManager
from weaviate.classes.query import Filter

class Command(BaseCommand):
    help = 'Delete all documents from Weaviate'
    
    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', help='Confirm deletion')
    
    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING("This will delete ALL documents. Run with --confirm to proceed."))
            return
            
        with WeaviateManager(admin_access=True) as manager:
            documents = manager.collections.get("Document")
            
            try:
                # Use a different approach - get all documents first
                result = documents.query.fetch_objects(
                    limit=1000,  # Adjust based on your data size
                    return_properties=["title"]
                )
                
                # Delete each document by ID
                deleted_count = 0
                for doc in result.objects:
                    documents.data.delete_by_id(doc.uuid)
                    deleted_count += 1
                    
                self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} documents successfully"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error deleting documents: {e}"))
