import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gemini_client import GeminiClient
from audio import play_audio
from languages import languages_dict
import pygame
from datetime import datetime
import queue
import time

class MultilingualGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        self.setup_voice_components()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Multilingual Communication Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2d2d30')
        self.root.minsize(800, 600)
        
        # Configure style for ttk widgets
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors to match dark theme
        style.configure('Dark.TNotebook', background='#2d2d30', borderwidth=0)
        style.configure('Dark.TNotebook.Tab', 
                       background='#3c3c3c', 
                       foreground='white',
                       padding=[12, 8])
        style.map('Dark.TNotebook.Tab',
                 background=[('selected', '#4d4d4d')])
                 
    def setup_variables(self):
        """Initialize variables"""
        self.is_listening = False
        self.current_language = "English"
        self.input_language = ["English", "en-US", "en"]
        self.output_language = ["English", "en-US", "en"] 
        self.conversation_active = False
        self.message_queue = queue.Queue()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2d2d30', height=80)
        header_frame.pack(fill='x', padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Globe icon and title
        title_frame = tk.Frame(header_frame, bg='#2d2d30')
        title_frame.pack(expand=True)
        
        title_label = tk.Label(title_frame, 
                              text="🌍 Multilingual Communication Assistant", 
                              font=('Segoe UI', 18, 'bold'),
                              fg='white', bg='#2d2d30')
        title_label.pack(pady=20)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root, style='Dark.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Voice Chat Tab
        self.create_voice_chat_tab()
        
        # Language Settings Tab
        self.create_language_settings_tab()
        
        # About Tab
        self.create_about_tab()
        
    def create_voice_chat_tab(self):
        """Create the voice chat tab"""
        voice_frame = tk.Frame(self.notebook, bg='#2d2d30')
        self.notebook.add(voice_frame, text='Voice Chat')
        
        # Status bar
        status_frame = tk.Frame(voice_frame, bg='#3c3c3c', height=40)
        status_frame.pack(fill='x', padx=5, pady=5)
        status_frame.pack_propagate(False)
        
        # Current language and status
        left_status = tk.Frame(status_frame, bg='#3c3c3c')
        left_status.pack(side='left', fill='y')
        
        tk.Label(left_status, text="Current Language:", 
                font=('Segoe UI', 10), fg='#cccccc', bg='#3c3c3c').pack(side='left', padx=10, pady=10)
        
        self.lang_label = tk.Label(left_status, text=self.current_language,
                                  font=('Segoe UI', 10, 'bold'), fg='#4CAF50', bg='#3c3c3c')
        self.lang_label.pack(side='left', pady=10)
        
        right_status = tk.Frame(status_frame, bg='#3c3c3c')
        right_status.pack(side='right', fill='y')
        
        tk.Label(right_status, text="Status:", 
                font=('Segoe UI', 10), fg='#cccccc', bg='#3c3c3c').pack(side='right', padx=(0, 10), pady=10)
        
        self.status_label = tk.Label(right_status, text="🎤 Ready", 
                                    font=('Segoe UI', 10), fg='#4CAF50', bg='#3c3c3c')
        self.status_label.pack(side='right', pady=10)
        
        # Chat area
        chat_frame = tk.Frame(voice_frame, bg='#2d2d30')
        chat_frame.pack(fill='both', expand=True, padx=5)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame,
                                                     bg='#1e1e1e',
                                                     fg='white',
                                                     font=('Consolas', 10),
                                                     wrap=tk.WORD,
                                                     state='disabled',
                                                     selectbackground='#404040')
        self.chat_display.pack(fill='both', expand=True, pady=(5, 10))
        
        # Configure text tags for different message types
        self.chat_display.tag_configure('timestamp', foreground='#808080', font=('Consolas', 9))
        self.chat_display.tag_configure('user', foreground='#00BFFF', font=('Consolas', 10))
        self.chat_display.tag_configure('assistant', foreground='#90EE90', font=('Consolas', 10))
        self.chat_display.tag_configure('error', foreground='#FF6B6B', font=('Consolas', 10))
        self.chat_display.tag_configure('system', foreground='#FFA500', font=('Consolas', 10))
        
        # Control buttons
        button_frame = tk.Frame(voice_frame, bg='#2d2d30')
        button_frame.pack(fill='x', padx=5, pady=(0, 10))
        
        # Stop and Clear buttons
        self.stop_btn = tk.Button(button_frame, text="🛑 Stop Conversation",
                                 bg='#FF6B6B', fg='white', font=('Segoe UI', 10, 'bold'),
                                 border=0, padx=20, pady=8,
                                 command=self.stop_conversation)
        self.stop_btn.pack(side='left', padx=(0, 10))
        
        self.clear_btn = tk.Button(button_frame, text="🗑 Clear Chat",
                                  bg='#FF8A95', fg='white', font=('Segoe UI', 10),
                                  border=0, padx=20, pady=8,
                                  command=self.clear_chat)
        self.clear_btn.pack(side='left')
        
        # Start conversation button
        self.start_btn = tk.Button(button_frame, text="🎤 Start Conversation",
                                  bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                                  border=0, padx=30, pady=10,
                                  command=self.start_conversation)
        self.start_btn.pack(side='right')
        
        # Text input area (like in the image)
        input_frame = tk.Frame(voice_frame, bg='#2d2d30')
        input_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        self.text_input = tk.Entry(input_frame, bg='#3c3c3c', fg='white',
                                  font=('Segoe UI', 11), border=0,
                                  insertbackground='white')
        self.text_input.pack(side='left', fill='x', expand=True, padx=(0, 10), ipady=8)
        self.text_input.insert(0, "Type message")
        self.text_input.bind('<FocusIn>', self.clear_placeholder)
        self.text_input.bind('<FocusOut>', self.add_placeholder)
        self.text_input.bind('<Return>', self.send_text_message)
        
        self.send_text_btn = tk.Button(input_frame, text="Send",
                                      bg='#0078D4', fg='white', font=('Segoe UI', 10),
                                      border=0, padx=20, pady=8,
                                      command=self.send_text_message)
        self.send_text_btn.pack(side='right')
        
    def create_language_settings_tab(self):
        """Create the language settings tab"""
        lang_frame = tk.Frame(self.notebook, bg='#2d2d30')
        self.notebook.add(lang_frame, text='Language Settings')
        
        # Title
        tk.Label(lang_frame, text="Language Configuration", 
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#2d2d30').pack(pady=20)
        
        # Input language section
        input_section = tk.LabelFrame(lang_frame, text="Input Language (What you speak)",
                                     font=('Segoe UI', 12, 'bold'), fg='white', bg='#2d2d30',
                                     bd=2, relief='groove')
        input_section.pack(fill='x', padx=20, pady=10)
        
        self.input_lang_var = tk.StringVar(value="english")
        input_combo = ttk.Combobox(input_section, textvariable=self.input_lang_var,
                                  values=list(languages_dict.keys()),
                                  font=('Segoe UI', 11), state='readonly')
        input_combo.pack(pady=15, padx=20, fill='x')
        input_combo.bind('<<ComboboxSelected>>', self.update_input_language)
        
        # Output language section  
        output_section = tk.LabelFrame(lang_frame, text="Output Language (Assistant's response)",
                                      font=('Segoe UI', 12, 'bold'), fg='white', bg='#2d2d30',
                                      bd=2, relief='groove')
        output_section.pack(fill='x', padx=20, pady=10)
        
        self.output_lang_var = tk.StringVar(value="english")
        output_combo = ttk.Combobox(output_section, textvariable=self.output_lang_var,
                                   values=list(languages_dict.keys()),
                                   font=('Segoe UI', 11), state='readonly')
        output_combo.pack(pady=15, padx=20, fill='x')
        output_combo.bind('<<ComboboxSelected>>', self.update_output_language)
        
        # Apply button
        tk.Button(lang_frame, text="Apply Language Settings",
                 bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                 border=0, padx=30, pady=10,
                 command=self.apply_language_settings).pack(pady=20)
        
        # Current settings display
        settings_frame = tk.LabelFrame(lang_frame, text="Current Settings",
                                      font=('Segoe UI', 12, 'bold'), fg='white', bg='#2d2d30',
                                      bd=2, relief='groove')
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        self.settings_text = tk.Text(settings_frame, height=4, bg='#1e1e1e', fg='white',
                                    font=('Consolas', 10), state='disabled')
        self.settings_text.pack(pady=10, padx=20, fill='x')
        self.update_settings_display()
        
    def create_about_tab(self):
        """Create the about tab"""
        about_frame = tk.Frame(self.notebook, bg='#2d2d30')
        self.notebook.add(about_frame, text='About')
        
        # About content
        about_text = """
🌍 Multilingual Communication Assistant

A sophisticated voice-to-voice translation system that enables 
seamless communication across language barriers.

Features:
• Real-time voice translation between 80+ languages
• Powered by Google Gemini Flash AI
• Text and voice input support
• High-quality text-to-speech output
• Dark modern interface

How to use:
1. Set your input and output languages in Language Settings
2. Click 'Start Conversation' in Voice Chat
3. Speak naturally - the assistant will translate and respond
4. Use text input for typing messages instead of voice

Supported Languages:
English, Spanish, French, German, Italian, Portuguese, Russian,
Chinese, Japanese, Korean, Hindi, Arabic, and many more...

Created for seamless multilingual communication.
        """
        
        tk.Label(about_frame, text=about_text, font=('Segoe UI', 11),
                fg='white', bg='#2d2d30', justify='left').pack(pady=30, padx=30)
        
    def setup_voice_components(self):
        """Initialize voice recognition and AI components"""
        try:
            self.recognizer = sr.Recognizer()
            
            # Check for Gemini API key
            if not os.environ.get('GEMINI_API_KEY'):
                self.add_message("system", "❌ GEMINI_API_KEY not found. Please set your API key.")
                return
                
            self.gemini_client = GeminiClient(api_key=os.environ.get('GEMINI_API_KEY'))
            self.add_message("system", "✅ Voice assistant initialized successfully!")
            
        except Exception as e:
            self.add_message("error", f"❌ Failed to initialize: {e}")
    
    def add_message(self, msg_type, message, show_time=True):
        """Add a message to the chat display"""
        self.chat_display.config(state='normal')
        
        if show_time:
            timestamp = datetime.now().strftime("[%H:%M:%S]")
            self.chat_display.insert(tk.END, f"{timestamp} ", 'timestamp')
        
        if msg_type == "user":
            self.chat_display.insert(tk.END, "🎤 You said: ", 'user')
        elif msg_type == "assistant":
            self.chat_display.insert(tk.END, "🤖 Assistant: ", 'assistant')
        elif msg_type == "error":
            self.chat_display.insert(tk.END, "❌ ", 'error')
        elif msg_type == "system":
            self.chat_display.insert(tk.END, "", 'system')
        elif msg_type == "clear":
            self.chat_display.insert(tk.END, "Chat cleared.", 'system')
            
        self.chat_display.insert(tk.END, f"{message}\n", msg_type)
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
        
    def clear_placeholder(self, event):
        """Clear placeholder text when focused"""
        if self.text_input.get() == "Type message":
            self.text_input.delete(0, tk.END)
            self.text_input.config(fg='white')
    
    def add_placeholder(self, event):
        """Add placeholder text when unfocused and empty"""
        if not self.text_input.get():
            self.text_input.insert(0, "Type message")
            self.text_input.config(fg='#808080')
    
    def send_text_message(self, event=None):
        """Send text message for processing"""
        message = self.text_input.get().strip()
        if message and message != "Type message":
            self.text_input.delete(0, tk.END)
            self.text_input.insert(0, "Type message")
            self.text_input.config(fg='#808080')
            
            # Process the text message
            threading.Thread(target=self.process_text_message, args=(message,), daemon=True).start()
    
    def process_text_message(self, message):
        """Process text message through translation and AI"""
        try:
            self.add_message("user", message)
            
            # Translate to English if needed
            if self.input_language[2] != 'en':
                message_english = GoogleTranslator(source='auto', target='en').translate(message)
            else:
                message_english = message
            
            # Get AI response
            response = self.gemini_client.chat_with_gemini(message_english)
            
            # Translate response if needed
            if self.output_language[2] != 'en':
                translated_response = GoogleTranslator(source='en', target=self.output_language[2]).translate(response)
            else:
                translated_response = response
            
            self.add_message("assistant", translated_response)
            
            # Generate and play audio
            audio_file = self.gemini_client.text_to_speech(translated_response, self.output_language[2])
            if audio_file:
                play_audio(audio_file)
                
        except Exception as e:
            self.add_message("error", f"Error processing message: {e}")
    
    def start_conversation(self):
        """Start voice conversation"""
        if not hasattr(self, 'gemini_client'):
            messagebox.showerror("Error", "Assistant not initialized. Please check your API key.")
            return
            
        if not self.conversation_active:
            self.conversation_active = True
            self.start_btn.config(text="🎤 Listening...", bg='#FFA500')
            self.status_label.config(text="🎤 Listening...", fg='#FFA500')
            self.add_message("system", "🎤 Voice conversation started. Speak now...")
            
            # Start voice listening in a separate thread
            threading.Thread(target=self.voice_loop, daemon=True).start()
    
    def stop_conversation(self):
        """Stop voice conversation"""
        self.conversation_active = False
        self.start_btn.config(text="🎤 Start Conversation", bg='#4CAF50')
        self.status_label.config(text="Ready", fg='#4CAF50')
        self.add_message("system", "🛑 Voice conversation stopped.")
    
    def voice_loop(self):
        """Main voice recognition loop"""
        while self.conversation_active:
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    
                    # Recognize speech
                    user_text = self.recognizer.recognize_google(audio, language=self.input_language[1])
                    
                    if user_text.lower() in ['stop', 'exit', 'quit', 'goodbye']:
                        self.root.after(0, self.stop_conversation)
                        break
                    
                    # Process the voice message
                    self.root.after(0, lambda: self.add_message("user", user_text))
                    self.process_voice_message(user_text)
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                self.root.after(0, lambda: self.add_message("error", "Could not understand audio"))
            except Exception as e:
                self.root.after(0, lambda: self.add_message("error", f"Voice error: {e}"))
                time.sleep(1)
    
    def process_voice_message(self, message):
        """Process voice message"""
        try:
            # Translate to English if needed
            if self.input_language[2] != 'en':
                message_english = GoogleTranslator(source='auto', target='en').translate(message)
            else:
                message_english = message
            
            # Get AI response
            response = self.gemini_client.chat_with_gemini(message_english)
            
            # Translate response if needed
            if self.output_language[2] != 'en':
                translated_response = GoogleTranslator(source='en', target=self.output_language[2]).translate(response)
            else:
                translated_response = response
            
            self.root.after(0, lambda: self.add_message("assistant", translated_response))
            
            # Generate and play audio
            audio_file = self.gemini_client.text_to_speech(translated_response, self.output_language[2])
            if audio_file:
                play_audio(audio_file)
                
        except Exception as e:
            self.root.after(0, lambda: self.add_message("error", f"Processing error: {e}"))
    
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        self.add_message("clear", "", show_time=True)
    
    def update_input_language(self, event=None):
        """Update input language selection"""
        lang_name = self.input_lang_var.get()
        if lang_name in languages_dict:
            self.input_language = [lang_name.title()] + languages_dict[lang_name]
            self.update_settings_display()
    
    def update_output_language(self, event=None):
        """Update output language selection"""
        lang_name = self.output_lang_var.get()
        if lang_name in languages_dict:
            self.output_language = [lang_name.title()] + languages_dict[lang_name]
            self.update_settings_display()
    
    def apply_language_settings(self):
        """Apply the language settings"""
        self.current_language = f"{self.input_language[0]} → {self.output_language[0]}"
        self.lang_label.config(text=self.current_language)
        self.add_message("system", f"✅ Languages updated: {self.current_language}")
        messagebox.showinfo("Success", "Language settings applied successfully!")
    
    def update_settings_display(self):
        """Update the settings display"""
        self.settings_text.config(state='normal')
        self.settings_text.delete(1.0, tk.END)
        
        settings_info = f"""Input Language: {self.input_language[0]} ({self.input_language[1]})
Output Language: {self.output_language[0]} ({self.output_language[1]})

Translation: {self.input_language[0]} → {self.output_language[0]}"""
        
        self.settings_text.insert(1.0, settings_info)
        self.settings_text.config(state='disabled')


def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = MultilingualGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")

if __name__ == "__main__":
    main()