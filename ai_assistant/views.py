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
from django.utils import timezone
from .utils.prompt_manager import PromptManager
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone
import uuid

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
    """Enhanced API endpoint for React Native chat integration"""
    
    # Add authentication for React Native
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChatRateThrottle]

    def post(self, request):
        try:
            # Get user information for React Native
            user = request.user
            
            # Validate required input
            question = request.data.get('question', '').strip()
            if not question:
                return Response({
                    "success": False,  # Add success field for React Native
                    "error": "Question is required and cannot be empty",
                    "error_code": "MISSING_QUESTION"  # Add error codes
                }, status=status.HTTP_400_BAD_REQUEST)

            # React Native specific fields
            conversation_id = request.data.get('conversation_id', str(uuid.uuid4()))
            message_id = request.data.get('message_id', str(uuid.uuid4()))

            default_prompt_file = 'default_prompt.txt'
            
            # Validate limit
            limit = request.data.get('limit', 3)
            try:
                limit = int(limit)
                if limit < 1 or limit > 10:
                    limit = 3
            except (ValueError, TypeError):
                limit = 3
            
            # Model validation
            model = request.data.get('model', 'gpt-4o-mini')
            allowed_models = ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-4']
            if model not in allowed_models:
                model = 'gpt-4o-mini'
            
            logger.info(f"Chat request from user {user.username} (mobile): '{question[:50]}...'")

            # Load prompt
            prompt_manager = PromptManager()
            custom_prompt = prompt_manager.load_prompt(default_prompt_file)
            if custom_prompt is None:
                custom_prompt = prompt_manager.get_default_prompt()
                logger.warning(f"Prompt file '{default_prompt_file}' not found, using fallback prompt")

            # Search in vector DB
            with WeaviateManager(admin_access=True) as manager:
                logger.debug(f"Searching documents for question: '{question}' with limit: {limit}")
                try:
                    results = manager.search_documents(question, limit=limit)
                    logger.debug(f"Search returned {len(results)} results")
                except Exception as search_error:
                    logger.error(f"Search failed: {search_error}", exc_info=True)
                    results = []

                # Build context from results
                context_parts = []
                sources = []

                for i, result in enumerate(results):
                    try:
                        content = result.properties.get("content", "").strip()
                        title = result.properties.get("title", f"Document {i+1}")
                        logger.debug(f"Result {i+1}: {title}, content length: {len(content)}")

                        if content:
                            context_parts.append(f"Document: {title}\n{content}")
                            sources.append(title)
                    except Exception as e:
                        logger.warning(f"Error processing result {i}: {e}")
                        continue

                if not context_parts:
                    return Response({
                        "success": False,  # React Native success indicator
                        "message": "No relevant information found",
                        "answer": "I couldn't find any relevant documents to answer your question. Please try rephrasing or check document availability.",
                        "sources": [],
                        "context_used": False,
                        "model_used": model,
                        "prompt_file_used": default_prompt_file,
                        "conversation_id": conversation_id,
                        "message_id": message_id,
                        "user_id": user.id,
                        "timestamp": timezone.now().isoformat(),
                        "error_code": "NO_CONTEXT"
                    })

                # Properly formatted context with separators
                context = "\n\n".join(["=" * 50 + "\n" + part for part in context_parts])

                # Generate response
                answer = self._generate_response_with_custom_prompt(
                    question=question,
                    context=context,
                    custom_prompt=custom_prompt,
                    model=model
                )

                # Enhanced response for React Native
                return Response({
                    "success": True,  # Success indicator
                    "message": "Response generated successfully",
                    "answer":  answer,
                    "sources": sources,
                    "context_used": True,
                    "model_used": model,
                    "embedding_model": "text-embedding-3-large",
                    "query": question,
                    "prompt_file_used": default_prompt_file,
                    "conversation_id": conversation_id,
                    "message_id": message_id,
                    "user_id": user.id,
                    "timestamp": timezone.now().isoformat(),
                    "context_summary": {
                        "total_sources": len(sources),
                        "context_length": len(context),
                        "search_results_count": len(results)
                    },
                    # React Native UI helpers
                    "ui_metadata": {
                        "show_sources": len(sources) > 0,
                        "message_type": "ai_response",
                        "requires_follow_up": False
                    }
                })

        except Exception as e:
            logger.error(f"Chat API error for user {getattr(request.user, 'username', 'anonymous')}: {e}", exc_info=True)
            return Response({
                "success": False,
                "message": "An error occurred while processing your request",
                "error": str(e),
                "error_code": "INTERNAL_ERROR",
                "conversation_id": request.data.get('conversation_id'),
                "message_id": request.data.get('message_id'),
                "timestamp": timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _generate_response_with_custom_prompt(self, question, context, custom_prompt, model):
        """Generate AI response using custom prompt and context"""
        # Enhanced system message for health assistant
        system_message = f"""{custom_prompt}

CONTEXT HANDLING RULES:
- Use ONLY the information provided in the context documents below
- If the context doesn't contain enough information, clearly state this
- Never make up information not present in the context
- Always cite which documents you're referencing
- Provide helpful, accurate, and compassionate responses
- Focus on sexual health, reproductive wellness, and contraception topics"""

        user_message = f"""CONTEXT DOCUMENTS:
{context}

QUESTION: {question}

Please answer the question based on the context provided above."""

        try:
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            client = OpenAI(api_key=openai_api_key)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating AI response: {e}", exc_info=True)
            return "I apologize, but I encountered an error while generating the response. Please try again."





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
            "timestamp": timezone.now().isoformat()
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
