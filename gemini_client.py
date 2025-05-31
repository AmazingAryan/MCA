import google.generativeai as genai
import os
from gtts import gTTS
from pathlib import Path
import tempfile

class GeminiClient:
    """
    A client for interacting with Google's Gemini API for conversational AI and text-to-speech functionalities.
    """
    def __init__(self, api_key):
        """
        Initialize the Gemini client with API key.
        
        Args:
            api_key (str): Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def chat_with_gemini(self, prompt):
        """
        Generate a response using Gemini Flash model.
        
        Args:
            prompt (str): The user's input prompt
            
        Returns:
            str: Generated response from Gemini
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, I couldn't process that request."
    
    def text_to_speech(self, text, language='en'):
        """
        Convert text to speech using Google Text-to-Speech.
        
        Args:
            text (str): Text to convert to speech
            language (str): Language code for TTS
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            filename = temp_file.name
            temp_file.close()
            
            tts.save(filename)
            return filename
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None