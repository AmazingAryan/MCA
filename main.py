from dotenv import load_dotenv
import os
import tkinter as tk
from gui_app import MultilingualGUI

# Load environment variables
load_dotenv()

def main():
    """
    Entry point for the Multilingual Communication Assistant GUI.
    """
    # Check if required environment variables are set
    if not os.environ.get('GEMINI_API_KEY'):
        # Create a simple error window
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        import tkinter.messagebox as messagebox
        messagebox.showerror(
            "Configuration Error",
            "GEMINI_API_KEY not found!\n\n"
            "Please add your Google Gemini API key to your .env file:\n"
            "GEMINI_API_KEY=your_api_key_here\n\n"
            "Get your API key from: https://makersuite.google.com/"
        )
        root.destroy()
        return
    
    # Create and run the main application
    root = tk.Tk()
    app = MultilingualGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 Application closed by user.")
    except Exception as e:
        print(f"❌ Application error: {e}")

if __name__ == "__main__":
    main()