# import os

# import eel
# eel.init('web')
# os.system('start brave.exe --app="http://localhost:8000/index.html"')
# eel.start('index.html',size=(1270,960), mode = None,host='localhost',block=True)

import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
import os
from googlesearch import search

# -------------------------------
# Function to convert text to speech
# -------------------------------
def speak(text):
    engine = pyttsx3.init()  # Initialize the text-to-speech engine
    engine.say(text)         # Queue the text to be spoken
    engine.runAndWait()      # Process and play the speech

# -------------------------------
# Function to capture audio and convert it to text
# -------------------------------
def listen_command():
    r = sr.Recognizer()      # Create a Recognizer instance
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)  # Listen to the microphone for audio input
        try:
            # Use Google's speech recognition service to convert audio to text
            command = r.recognize_google(audio)
            print("You said:", command)
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            speak("Sorry, the speech service is down.")
            return ""
    return command.lower()   # Return the command in lowercase for easier processing

# -------------------------------
# Function to search for a song on YouTube and open the search results
# -------------------------------
def open_youtube_song(song_name):
    speak(f"Searching for {song_name} on YouTube")
    query = song_name + " song"  # Append "song" to improve search relevance
    # Build YouTube search URL using the query
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)

# -------------------------------
# Function to open an application based on a pre-defined mapping (Windows example)
# -------------------------------
def open_application(app_name):
    speak(f"Opening {app_name}")
    if os.name == 'nt':  # Check if the operating system is Windows
        apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            # You can add more applications here as needed
        }
        if app_name in apps:
            subprocess.Popen(apps[app_name])  # Launch the application
        else:
            speak("Application not found in mapping.")
    else:
        # For macOS or Linux, you might need to modify this part with the appropriate commands.
        speak("Application launching not configured for your OS.")

# -------------------------------
# Function to perform a Google search and open the first result
# -------------------------------
def search_google(query):
    speak(f"Searching Google for {query}")
    # The 'search' function returns URLs. We'll open the first one.
    for url in search(query, num_results=1):
        webbrowser.open(url)
        break

# -------------------------------
# Process the user's command and call the appropriate function
# -------------------------------
def process_command(command):
    if 'open youtube' in command:
        # Check if the command also mentions a song
        if 'song' in command:
            # Extract song name from the command after the word 'song'
            song_name = command.split('song')[-1].strip()
            open_youtube_song(song_name)
        else:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
    elif 'open application' in command:
        # Example command: "open application notepad"
        words = command.split()
        if len(words) >= 3:
            # The application name is assumed to be the last word
            app_name = words[-1]
            open_application(app_name)
        else:
            speak("Please specify the application name.")
    elif 'search' in command:
        # Example command: "search artificial intelligence"
        query = command.split('search')[-1].strip()
        search_google(query)
    elif 'exit' in command or 'quit' in command:
        speak("Goodbye!")
        exit()  # Terminate the program
    else:
        # If the command doesn't match any known patterns
        speak("I didn't catch that. Please try again.")

# -------------------------------
# Main loop: Greet the user and continuously listen for commands
# -------------------------------
if __name__ == '__main__':
    speak("Hello, how can I help you?")
    while True:
        command = listen_command()
        if command:
            process_command(command)
