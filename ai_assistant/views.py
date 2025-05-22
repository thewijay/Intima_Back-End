from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from django.conf import settings
from .utils.weaviate_client import WeaviateManager

class ChatAPIView(APIView):
    """API endpoint for chat interactions"""
    
    def post(self, request):
        # Get the query from request
        query = request.data.get('query')
        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Search for relevant documents
        weaviate_manager = WeaviateManager(admin_access=False)
        documents = weaviate_manager.search_documents(query)
        
        # Extract content from documents to use as context
        context = "\n\n".join([doc["content"] for doc in documents])
        
        # Generate response using OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer based on the provided context."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ]
        )
        
        # Return the response
        return Response({
            "answer": response.choices[0].message.content,
            "sources": [doc["title"] for doc in documents]
        })
