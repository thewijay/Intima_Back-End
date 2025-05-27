import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PromptManager:
    def __init__(self):
        # Define the prompts directory path
        self.prompts_dir = os.path.join(settings.BASE_DIR, 'prompts')
        
        # Ensure prompts directory exists
        if not os.path.exists(self.prompts_dir):
            os.makedirs(self.prompts_dir)
            logger.info(f"Created prompts directory: {self.prompts_dir}")
    
    def load_prompt(self, prompt_name):
        """Load a custom prompt from a .txt file"""
        try:
            # Add .txt extension if not provided
            if not prompt_name.endswith('.txt'):
                prompt_name += '.txt'
            
            prompt_path = os.path.join(self.prompts_dir, prompt_name)
            
            if not os.path.exists(prompt_path):
                logger.warning(f"Prompt file not found: {prompt_path}")
                return None
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read().strip()
            
            logger.info(f"Successfully loaded prompt from: {prompt_name}")
            return prompt_content
            
        except Exception as e:
            logger.error(f"Error loading prompt from {prompt_name}: {e}")
            return None
    
    def list_available_prompts(self):
        """List all available prompt files"""
        try:
            prompt_files = []
            for filename in os.listdir(self.prompts_dir):
                if filename.endswith('.txt'):
                    prompt_files.append(filename[:-4])  # Remove .txt extension
            return prompt_files
        except Exception as e:
            logger.error(f"Error listing prompt files: {e}")
            return []
    
    def save_prompt(self, prompt_name, content):
        """Save a new prompt or update existing one"""
        try:
            if not prompt_name.endswith('.txt'):
                prompt_name += '.txt'
            
            prompt_path = os.path.join(self.prompts_dir, prompt_name)
            
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Successfully saved prompt to: {prompt_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving prompt to {prompt_name}: {e}")
            return False
    
    def get_default_prompt(self):
        """Return a default prompt if no custom prompt is specified"""
        return """You are a helpful AI assistant. Answer questions based on the provided context documents.

GUIDELINES:
- Use only the information from the provided context
- If the context doesn't contain enough information, clearly state this
- Be accurate, helpful, and comprehensive
- Cite specific documents when referencing information
- Maintain a professional yet approachable tone"""
