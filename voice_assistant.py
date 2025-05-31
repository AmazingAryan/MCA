import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import queue
import time
from datetime import datetime

# Try importing speech recognition with fallback
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("❌ speech_recognition not available")

# Try importing PyAudio with graceful fallback
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio not available - voice input disabled")

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("❌ deep_translator not available")

try:
    from gemini_client import GeminiClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("❌ gemini_client not available")

try:
    from audio import play_audio
    AUDIO_PLAYBACK_AVAILABLE = True
except ImportError:
    AUDIO_PLAYBACK_AVAILABLE = False
    print("⚠️ Audio playback not available")

try:
    from languages import languages_dict
    LANGUAGES_AVAILABLE = True
except ImportError:
    LANGUAGES_AVAILABLE = False
    # Fallback language dictionary
    languages_dict = {
        "english": ["en-US", "en"],
        "spanish": ["es-ES", "es"],
        "french": ["fr-FR", "fr"],
        "german": ["de-DE", "de"],
        "italian": ["it-IT", "it"],
        "portuguese": ["pt-PT", "pt"],
        "russian": ["ru-RU", "ru"],
        "chinese": ["zh-CN", "zh"],
        "japanese": ["ja-JP", "ja"],
        "korean": ["ko-KR", "ko"],
        "hindi": ["hi-IN", "hi"],
        "arabic": ["ar-SA", "ar"]
    }

class ImprovedMultilingualGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        self.setup_voice_components()
        self.check_dependencies()
        
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
        self.voice_enabled = SPEECH_AVAILABLE and PYAUDIO_AVAILABLE
        
    def check_dependencies(self):
        """Check and report missing dependencies"""
        missing_deps = []
        
        if not SPEECH_AVAILABLE:
            missing_deps.append("speech_recognition")
        if not PYAUDIO_AVAILABLE:
            missing_deps.append("pyaudio")
        if not TRANSLATOR_AVAILABLE:
            missing_deps.append("deep_translator")
        if not GEMINI_AVAILABLE:
            missing_deps.append("gemini_client")
        if not AUDIO_PLAYBACK_AVAILABLE:
            missing_deps.append("audio playback")
            
        if missing_deps:
            self.add_message("system", f"⚠️ Missing dependencies: {', '.join(missing_deps)}")
            
            if not self.voice_enabled:
                self.add_message("system", "🔇 Voice input disabled. Text input only.")
                self.start_btn.config(state='disabled', text="Voice Unavailable")
        
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
        
        # Create tabs
        self.create_voice_chat_tab()
        self.create_language_settings_tab()
        self.create_diagnostics_tab()
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
        
        status_text = "🎤 Ready" if self.voice_enabled else "⌨️ Text Only"
        status_color = '#4CAF50' if self.voice_enabled else '#FFA500'
        
        self.status_label = tk.Label(right_status, text=status_text, 
                                     font=('Segoe UI', 10), fg=status_color, bg='#3c3c3c')
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
        start_text = "🎤 Start Conversation" if self.voice_enabled else "Voice Unavailable"
        self.start_btn = tk.Button(button_frame, text=start_text,
                                   bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
                                   border=0, padx=30, pady=10,
                                   command=self.start_conversation)
        self.start_btn.pack(side='right')
        
        # Text input area
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
        
    def create_diagnostics_tab(self):
        """Create the diagnostics tab"""
        diag_frame = tk.Frame(self.notebook, bg='#2d2d30')
        self.notebook.add(diag_frame, text='Diagnostics')
        
        # Title
        tk.Label(diag_frame, text="System Diagnostics", 
                 font=('Segoe UI', 16, 'bold'), fg='white', bg='#2d2d30').pack(pady=20)
        
        # Diagnostics display
        self.diag_display = scrolledtext.ScrolledText(diag_frame,
                                                      bg='#1e1e1e',
                                                      fg='white',
                                                      font=('Consolas', 10),
                                                      wrap=tk.WORD,
                                                      state='disabled')
        self.diag_display.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(diag_frame, bg='#2d2d30')
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(btn_frame, text="🔄 Refresh Diagnostics",
                  bg='#0078D4', fg='white', font=('Segoe UI', 10),
                  border=0, padx=20, pady=8,
                  command=self.run_diagnostics).pack(side='left')
        
        tk.Button(btn_frame, text="🎤 Test Microphone",
                  bg='#4CAF50', fg='white', font=('Segoe UI', 10),
                  border=0, padx=20, pady=8,
                  command=self.test_microphone).pack(side='left', padx=(10, 0))
        
        # Run initial diagnostics
        self.run_diagnostics()
        
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
• Real-time voice translation between 12+ languages
• Powered by Google Gemini AI
• Text and voice input support
• High-quality text-to-speech output
• Dark modern interface
• Robust error handling

Dependencies:
• speech_recognition - Voice input
• pyaudio - Microphone access
• deep_translator - Language translation
• google-generativeai - AI responses
• pygame - Audio playback

Installation Help:
If voice input is unavailable, install PyAudio:
• Windows: pip install pyaudio
• macOS: brew install portaudio && pip install pyaudio
• Linux: sudo apt-get install python3-pyaudio

Created for seamless multilingual communication.
        """
        
        tk.Label(about_frame, text=about_text, font=('Segoe UI', 11),
                 fg='white', bg='#2d2d30', justify='left').pack(pady=30, padx=30)
        
    def setup_voice_components(self):
        """Initialize voice recognition and AI components"""
        try:
            if self.voice_enabled:
                self.recognizer = sr.Recognizer()
                self.add_message("system", "✅ Voice recognition initialized")
            
            # Check for Gemini API key
            if not os.environ.get('GEMINI_API_KEY'):
                self.add_message("system", "❌ GEMINI_API_KEY not found. Please set your API key.")
                return
                
            if GEMINI_AVAILABLE:
                self.gemini_client = GeminiClient(api_key=os.environ.get('GEMINI_API_KEY'))
                self.add_message("system", "✅ AI assistant initialized successfully!")
            else:
                self.add_message("error", "❌ Gemini client not available")
            
        except Exception as e:
            self.add_message("error", f"❌ Failed to initialize: {e}")
    
    def run_diagnostics(self):
        """Run system diagnostics"""
        self.diag_display.config(state='normal')
        self.diag_display.delete(1.0, tk.END)
        
        diag_text = f"""System Diagnostics Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== Dependency Status ===
Speech Recognition: {'✅ Available' if SPEECH_AVAILABLE else '❌ Missing'}
PyAudio: {'✅ Available' if PYAUDIO_AVAILABLE else '❌ Missing'}
Deep Translator: {'✅ Available' if TRANSLATOR_AVAILABLE else '❌ Missing'}
Gemini Client: {'✅ Available' if GEMINI_AVAILABLE else '❌ Missing'}
Audio Playback: {'✅ Available' if AUDIO_PLAYBACK_AVAILABLE else '❌ Missing'}
Languages Dict: {'✅ Available' if LANGUAGES_AVAILABLE else '⚠️ Using fallback'}

=== Environment Variables ===
GEMINI_API_KEY: {'✅ Set' if os.environ.get('GEMINI_API_KEY') else '❌ Missing'}

=== Voice Capabilities ===
Voice Input: {'✅ Enabled' if self.voice_enabled else '❌ Disabled'}
Voice Output: {'✅ Available' if AUDIO_PLAYBACK_AVAILABLE else '❌ Unavailable'}

=== System Info ===
Operating System: {os.name}
Python Path: {os.sys.executable}

=== Recommendations ==="""

        if not PYAUDIO_AVAILABLE:
            diag_text += "\n• Install PyAudio for voice input: pip install pyaudio"
        if not os.environ.get('GEMINI_API_KEY'):
            diag_text += "\n• Set GEMINI_API_KEY environment variable"
        if not AUDIO_PLAYBACK_AVAILABLE:
            diag_text += "\n• Install pygame for audio playback: pip install pygame"
        
        if PYAUDIO_AVAILABLE and self.voice_enabled:
            diag_text += "\n• All voice features ready!"
            
        self.diag_display.insert(1.0, diag_text)
        self.diag_display.config(state='disabled')
    
    def test_microphone(self):
        """Test microphone functionality"""
        if not self.voice_enabled:
            messagebox.showwarning("Microphone Test", "Voice input is not available.\nPlease install PyAudio first.")
            return
            
        def test_mic_thread():
            try:
                self.add_message("system", "🎤 Testing microphone... Speak now!")
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio)
                    self.add_message("system", f"✅ Microphone test successful! Heard: '{text}'")
            except sr.WaitTimeoutError:
                self.add_message("error", "❌ Microphone test timeout - no speech detected")
            except sr.UnknownValueError:
                self.add_message("error", "❌ Microphone working but speech not understood")
            except Exception as e:
                self.add_message("error", f"❌ Microphone test failed: {e}")
        
        threading.Thread(target=test_mic_thread, daemon=True).start()
    
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
            
            if not GEMINI_AVAILABLE:
                self.add_message("error", "AI assistant not available")
                return
            
            # Translate to English if needed
            if TRANSLATOR_AVAILABLE and self.input_language[2] != 'en':
                message_english = GoogleTranslator(source='auto', target='en').translate(message)
            else:
                message_english = message
            
            # Get AI response
            response = self.gemini_client.chat_with_gemini(message_english)
            
            # Translate response if needed
            if TRANSLATOR_AVAILABLE and self.output_language[2] != 'en':
                response_translated = GoogleTranslator(source='en', target=self.output_language[2]).translate(response)
            else:
                response_translated = response
                
            self.add_message("assistant", response_translated)
            
            # Play audio response if available
            if AUDIO_PLAYBACK_AVAILABLE:
                threading.Thread(target=self.play_response_audio, args=(response_translated,), daemon=True).start()
                
        except Exception as e:
            self.add_message("error", f"Failed to process message: {e}")
    
    def play_response_audio(self, text):
        """Play audio response (placeholder implementation)"""
        try:
            # This would integrate with your audio module
            if AUDIO_PLAYBACK_AVAILABLE:
                play_audio(text, language=self.output_language[2])
        except Exception as e:
            print(f"Audio playback failed: {e}")
    
    def start_conversation(self):
        """Start voice conversation"""
        if not self.voice_enabled:
            messagebox.showwarning("Voice Unavailable", "Voice input is not available.\nPlease install PyAudio and speech_recognition.")
            return
            
        if self.conversation_active:
            messagebox.showinfo("Already Active", "Conversation is already active!")
            return
            
        self.conversation_active = True
        self.start_btn.config(text="🎤 Listening...", bg='#FF6B6B')
        self.status_label.config(text="🎤 Listening", fg='#FF6B6B')
        
        # Start listening thread
        threading.Thread(target=self.voice_conversation_loop, daemon=True).start()
    
    def voice_conversation_loop(self):
        """Main voice conversation loop"""
        try:
            while self.conversation_active:
                if self.listen_for_voice():
                    time.sleep(0.5)  # Brief pause between listening sessions
                else:
                    break
        except Exception as e:
            self.add_message("error", f"Conversation loop error: {e}")
        finally:
            self.conversation_active = False
            self.start_btn.config(text="🎤 Start Conversation", bg='#4CAF50')
            self.status_label.config(text="🎤 Ready", fg='#4CAF50')
    
    def listen_for_voice(self):
        """Listen for voice input and process it"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
            # Recognize speech
            text = self.recognizer.recognize_google(audio, language=self.input_language[1])
            
            if text.strip():
                # Process the voice message
                self.process_text_message(text)
                return True
                
        except sr.WaitTimeoutError:
            # Normal timeout, continue listening
            return True
        except sr.UnknownValueError:
            self.add_message("system", "Could not understand audio, please try again")
            return True
        except Exception as e:
            self.add_message("error", f"Voice recognition error: {e}")
            return False
    
    def stop_conversation(self):
        """Stop the voice conversation"""
        self.conversation_active = False
        self.start_btn.config(text="🎤 Start Conversation", bg='#4CAF50')
        self.status_label.config(text="🎤 Ready", fg='#4CAF50')
        self.add_message("system", "Conversation stopped")
    
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        self.add_message("system", "Chat cleared", show_time=False)
    
    def update_input_language(self, event=None):
        """Update input language selection"""
        selected = self.input_lang_var.get()
        if selected in languages_dict:
            self.input_language = [selected.title(), languages_dict[selected][0], languages_dict[selected][1]]
            self.update_settings_display()
    
    def update_output_language(self, event=None):
        """Update output language selection"""
        selected = self.output_lang_var.get()
        if selected in languages_dict:
            self.output_language = [selected.title(), languages_dict[selected][0], languages_dict[selected][1]]
            self.update_settings_display()
    
    def apply_language_settings(self):
        """Apply language settings"""
        self.update_input_language()
        self.update_output_language()
        self.current_language = f"{self.input_language[0]} → {self.output_language[0]}"
        self.lang_label.config(text=self.current_language)
        self.add_message("system", f"Language settings applied: Input '{self.input_language[0]}', Output '{self.output_language[0]}'")
        self.update_settings_display()

    def update_settings_display(self):
        """Update the display of current language settings"""
        self.settings_text.config(state='normal')
        self.settings_text.delete(1.0, tk.END)
        display_text = f"Input Language: {self.input_language[0]} (Google Speech Recognition: {self.input_language[1]}, Google Translate: {self.input_language[2]})\n"
        display_text += f"Output Language: {self.output_language[0]} (Google Speech Recognition: {self.output_language[1]}, Google Translate: {self.output_language[2]})"
        self.settings_text.insert(tk.END, display_text)
        self.settings_text.config(state='disabled')

def main():
    root = tk.Tk()
    app = ImprovedMultilingualGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()