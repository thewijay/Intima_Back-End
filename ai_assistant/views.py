from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from openai import OpenAI
from django.conf import settings
from .utils.weaviate_client import WeaviateManager
from knowledgebase.vectorization import generate_embedding
import logging
import os
from typing import List, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

class SearchRateThrottle(UserRateThrottle):
    scope = 'search'
    rate = '100/hour'

class ChatRateThrottle(UserRateThrottle):
    scope = 'chat'
    rate = '50/hour'

class SearchAPIView(APIView):
    """API endpoint for searching documents using text-embedding-3-large"""
    
    throttle_classes = [SearchRateThrottle]
    
    def post(self, request):
        try:
            # Validate input
            question = request.data.get('question', '').strip()
            if not question:
                return Response(
                    {"error": "Question is required and cannot be empty"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(question) > 1000:
                return Response(
                    {"error": "Question is too long. Maximum 1000 characters allowed."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate limit parameter
            limit = request.data.get('limit', 5)
            try:
                limit = int(limit)
                if limit < 1 or limit > 20:
                    limit = 5
            except (ValueError, TypeError):
                limit = 5
            
            # Optional: Allow custom embedding dimensions for cost optimization
            embedding_dimensions = request.data.get('embedding_dimensions')
            if embedding_dimensions:
                try:
                    embedding_dimensions = int(embedding_dimensions)
                    if embedding_dimensions < 256 or embedding_dimensions > 3072:
                        embedding_dimensions = None
                except (ValueError, TypeError):
                    embedding_dimensions = None
            
            logger.info(f"Search request: '{question[:50]}...' with limit {limit}")
            
            # Search for relevant documents using text-embedding-3-large
            with WeaviateManager(admin_access=True) as manager:
                results = manager.search_documents(question, limit=limit, embedding_dimensions=embedding_dimensions)
                
                # Format the response
                response_data = []
                for i, result in enumerate(results):
                    try:
                        response_data.append({
                            "rank": i + 1,
                            "title": result.properties.get("title", "Unknown"),
                            "content": result.properties.get("content", ""),
                            "file_path": result.properties.get("file_path", ""),
                            "content_preview": self._get_content_preview(
                                result.properties.get("content", ""), 200
                            ),
                            "score": getattr(result, "score", None)
                        })
                    except Exception as e:
                        logger.warning(f"Error processing search result {i}: {e}")
                        continue
                
                logger.info(f"Search completed: {len(response_data)} results returned")
                
                return Response({
                    "results": response_data,
                    "total_results": len(response_data),
                    "query": question,
                    "embedding_model": "text-embedding-3-large"
                })
                
        except Exception as e:
            logger.error(f"Search API error: {e}", exc_info=True)
            return Response(
                {"error": "An error occurred while searching. Please try again."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_content_preview(self, content: str, max_length: int = 200) -> str:
        """Get a preview of the content with proper truncation"""
        if not content:
            return ""
        
        if len(content) <= max_length:
            return content
        
        # Find the last complete word within the limit
        truncated = content[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:
            return truncated[:last_space] + "..."
        else:
            return truncated + "..."

class ChatAPIView(APIView):
    """API endpoint for chat using gpt-4o-mini with text-embedding-3-large for context retrieval"""
    
    throttle_classes = [ChatRateThrottle]
    
    def post(self, request):
        try:
            # Validate input
            question = request.data.get('question', '').strip()
            if not question:
                return Response(
                    {"error": "Question is required and cannot be empty"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(question) > 1000:
                return Response(
                    {"error": "Question is too long. Maximum 1000 characters allowed."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate limit parameter
            limit = request.data.get('limit', 3)
            try:
                limit = int(limit)
                if limit < 1 or limit > 10:
                    limit = 3
            except (ValueError, TypeError):
                limit = 3
            
            # Use gpt-4o-mini as the default model (cost-efficient)
            model = request.data.get('model', 'gpt-4o-mini')
            allowed_models = ['gpt-4o-mini']
            if model not in allowed_models:
                model = 'gpt-4o-mini'
            
            logger.info(f"Chat request: '{question[:50]}...' with {limit} context docs using {model}")
            
            # Search for relevant documents using text-embedding-3-large
            with WeaviateManager(admin_access=True) as manager:
                results = manager.search_documents(question, limit=limit)
                
                # Extract content from results to use as context
                context_parts = []
                sources = []
                
                for i, result in enumerate(results):
                    try:
                        content = result.properties.get("content", "").strip()
                        title = result.properties.get("title", f"Document {i+1}")
                        
                        if content:
                            context_parts.append(f"Document {i+1} ({title}):\n{content}")
                            sources.append(title)
                    except Exception as e:
                        logger.warning(f"Error processing context result {i}: {e}")
                        continue
                
                context = "\n\n".join(context_parts)
                
                if not context:
                    return Response({
                        "answer": "I couldn't find any relevant documents to answer your question. Please try rephrasing your question or check if the relevant documents have been uploaded.",
                        "sources": [],
                        "context_used": False,
                        "model_used": model
                    })
                
                # Initialize OpenAI client
                openai_api_key = os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)
                if not openai_api_key:
                    logger.error("OpenAI API key not found")
                    return Response(
                        {"error": "AI service is not configured properly"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                client = OpenAI(api_key=openai_api_key)
                
                # Prepare messages for OpenAI
                system_message = """You are a helpful AI assistant. Answer questions based on the provided context documents. 

Guidelines:
- Use only the information from the provided context
- If the context doesn't contain enough information to answer the question, say so clearly
- Be concise but comprehensive
- If you're uncertain about something, express that uncertainty
- Cite which document(s) you're referencing when possible"""

                user_message = f"""Context Documents:
{context}

Question: {question}

Please answer the question based on the context provided above."""

                # Generate response using gpt-4o-mini (cost-efficient model)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,  # Lower temperature for more focused responses
                    max_tokens=1000,  # Limit response length
                )
                
                answer = response.choices[0].message.content
                
                logger.info(f"Chat completed successfully with {len(sources)} sources using {model}")
                
                # Return the response
                return Response({
                    "answer": answer,
                    "sources": sources,
                    "context_used": True,
                    "model_used": model,
                    "embedding_model": "text-embedding-3-large",
                    "query": question,
                    "cost_info": {
                        "embedding_model": "text-embedding-3-large ($0.00013/1K tokens)",
                        "chat_model": f"{model} ({'$0.15/1M input, $0.60/1M output tokens' if model == 'gpt-4o-mini' else 'varies'}"
                    }
                })
                
        except Exception as e:
            logger.error(f"Chat API error: {e}", exc_info=True)
            return Response(
                {"error": "An error occurred while processing your request. Please try again."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HealthCheckAPIView(APIView):
    """Health check endpoint to verify system status"""
    
    def get(self, request):
        try:
            # Test Weaviate connection
            with WeaviateManager(admin_access=False) as manager:
                collections = manager.collections
                weaviate_status = "healthy"
        except Exception as e:
            logger.error(f"Weaviate health check failed: {e}")
            weaviate_status = "unhealthy"
        
        # Test OpenAI API key
        openai_api_key = os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)
        openai_status = "configured" if openai_api_key else "not_configured"
        
        overall_status = "healthy" if weaviate_status == "healthy" and openai_status == "configured" else "degraded"
        
        return Response({
            "status": overall_status,
            "services": {
                "weaviate": weaviate_status,
                "openai": openai_status
            },
            "models": {
                "embedding": "text-embedding-3-large",
                "chat": "gpt-4o-mini (default)"
            },
            "timestamp": "2025-05-22T22:36:00+05:30"
        })

class DocumentStatsAPIView(APIView):
    """API endpoint to get document statistics"""
    
    def get(self, request):
        try:
            with WeaviateManager(admin_access=True) as manager:
                documents = manager.collections.get("Document")
                
                # Get total count
                total_count = documents.aggregate.over_all().total_count
                
                # Get sample documents for preview
                sample_docs = documents.query.fetch_objects(
                    limit=5,
                    return_properties=["title", "file_path"]
                )
                
                sample_list = []
                for doc in sample_docs.objects:
                    sample_list.append({
                        "title": doc.properties.get("title", "Unknown"),
                        "file_path": doc.properties.get("file_path", "")
                    })
                
                return Response({
                    "total_documents": total_count,
                    "sample_documents": sample_list,
                    "embedding_model": "text-embedding-3-large",
                    "vector_dimensions": 3072
                })
                
        except Exception as e:
            logger.error(f"Document stats error: {e}", exc_info=True)
            return Response(
                {"error": "Unable to retrieve document statistics"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
