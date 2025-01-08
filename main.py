# main.py

import tkinter as tk
from ui import VoiceTypingAppUI

def main():
    # Initialize the main Tkinter window
    root = tk.Tk()
    
    # Create an instance of the VoiceTypingAppUI
    app = VoiceTypingAppUI(root)
    
    # Run the application
    app.run()

if __name__ == "__main__":
    main()
