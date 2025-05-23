# ai_assistant/management/commands/test_search.py
from django.core.management.base import BaseCommand
from ai_assistant.utils.weaviate_client import WeaviateManager

class Command(BaseCommand):
    help = 'Test vector search with a question'
    
    def add_arguments(self, parser):
        parser.add_argument('question', type=str, help='The question to search for')
        parser.add_argument('--limit', type=int, default=3, help='Number of results to return')
    
    def handle(self, *args, **options):
        question = options['question']
        limit = options['limit']
        
        self.stdout.write(f"Searching for: {question}")
        
        with WeaviateManager(admin_access=True) as manager:
            results = manager.search_documents(question, limit=limit)
            
            if not results:
                self.stdout.write(self.style.WARNING("No results found"))
                return
                
            self.stdout.write(f"Found {len(results)} results:")
            
            for i, result in enumerate(results, 1):
                title = result.properties.get("title", "Unknown")
                content = result.properties.get("content", "")
                
                self.stdout.write(f"\n{i}. {title}")
                self.stdout.write("-------------------")
                
                # Show a preview of the content (first 200 chars)
                preview = content[:200] + "..." if len(content) > 200 else content
                self.stdout.write(preview)
