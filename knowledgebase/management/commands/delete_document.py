from django.core.management.base import BaseCommand
from ai_assistant.utils.weaviate_client import WeaviateManager

class Command(BaseCommand):
    help = 'Delete specific documents from Weaviate by their UUIDs'
    
    def add_arguments(self, parser):
        parser.add_argument('uuids', nargs='+', type=str, help='UUIDs of documents to delete')
    
    def handle(self, *args, **options):
        uuids = options['uuids']
        
        self.stdout.write(f"Preparing to delete {len(uuids)} document(s)")
        
        with WeaviateManager(admin_access=True) as manager:
            documents = manager.collections.get("Document")
            
            success_count = 0
            for uuid in uuids:
                try:
                    # First, verify the document exists
                    try:
                        doc = documents.data.get_by_id(uuid)
                        title = doc.properties.get('title', 'Unknown')
                    except Exception:
                        self.stdout.write(self.style.ERROR(f"Document with UUID {uuid} not found"))
                        continue
                    
                    # Delete the document
                    documents.data.delete_by_id(uuid)
                    success_count += 1
                    self.stdout.write(f"Deleted document: {title} (UUID: {uuid})")
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error deleting document {uuid}: {e}"))
            
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {success_count} out of {len(uuids)} document(s)"))
