import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
import nltk
import os
from nltk import pos_tag, word_tokenize
from nltk.chunk import ne_chunk
from nltk.tree import Tree

# Ensure NLTK data is properly located
nltk.data.path.append(os.path.join(os.path.expanduser("~"), "nltk_data"))

class TerminalAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.setup_nltk()
        self.setup_engine()
        
    def setup_nltk(self):
        """Verify and download required NLTK resources"""
        required_resources = [
            'punkt',
            'averaged_perceptron_tagger',
            'maxent_ne_chunker',
            'words'
        ]
        
        for resource in required_resources:
            try:
                nltk.data.find(f"corpora/{resource}" if resource == "words" else f"tokenizers/{resource}")
            except LookupError:
                print(f"Downloading missing NLTK resource: {resource}")
                nltk.download(resource, quiet=False)

    def setup_engine(self):
        """Configure text-to-speech engine"""
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)  # Use female voice if available
        self.engine.setProperty('rate', 150)

    def speak(self, text):
        """Convert text to speech with console output"""
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_command(self):
        """Capture and process voice command"""
        try:
            with sr.Microphone() as source:
                print("\nListening... (Ctrl+C to exit)")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                command = self.recognizer.recognize_google(audio).lower()
                print(f"You said: {command}")
                return command
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError:
            print("Speech service unavailable")
            return ""
        except Exception as e:
            print(f"Error: {str(e)}")
            return ""

def analyze_command(command):
    """Process natural language command using NLP"""
    tokens = word_tokenize(command)
    tagged = pos_tag(tokens)
    ner_tree = ne_chunk(tagged)

    entities = []
    verbs = []
    
    for chunk in ner_tree:
        if isinstance(chunk, Tree):
            entity = " ".join([word for word, pos in chunk.leaves()])
            entities.append((entity, chunk.label()))
        else:
            word, pos = chunk
            if pos.startswith('VB'):
                verbs.append(word.lower())

    action_map = {
        'open': ['open', 'launch', 'start'],
        'search': ['search', 'find', 'look'],
        'play': ['play', 'listen', 'queue'],
        'exit': ['exit', 'quit', 'close']
    }
    
    action = None
    for verb in verbs:
        for action_type, synonyms in action_map.items():
            if verb in synonyms:
                action = action_type
                break
        if action:
            break

    target = " ".join([word for word, pos in tagged if pos.startswith('NN')])
    
    return action, entities, target

def process_command(command, assistant):
    """Execute command based on NLP analysis"""
    if not command:
        return

    action, entities, target = analyze_command(command)
    print(f"Action: {action}\nEntities: {entities}\nTarget: {target}")

    if action == 'open':
        if 'youtube' in target:
            handle_youtube(entities, assistant)
        elif any(app in target for app in ['notepad', 'calculator']):
            open_app(target, assistant)
        else:
            assistant.speak(f"Sorry, I can't open {target}")
    elif action == 'search':
        search_query = target or " ".join([e[0] for e in entities])
        google_search(search_query, assistant)
    elif action == 'play':
        song_name = " ".join([e[0] for e in entities if e[1] in ['PERSON', 'WORK_OF_ART']])
        play_youtube(song_name or target, assistant)
    elif action == 'exit':
        assistant.speak("Goodbye! Have a great day!")
        exit()
    else:
        assistant.speak("I'm not sure how to help with that")

def handle_youtube(entities, assistant):
    """Handle YouTube-related commands"""
    songs = [e[0] for e in entities if e[1] == 'WORK_OF_ART']
    if songs:
        play_youtube(" ".join(songs), assistant)
    else:
        webbrowser.open("https://www.youtube.com")
        assistant.speak("Opening YouTube")

def play_youtube(query, assistant):
    """Search and play YouTube content"""
    assistant.speak(f"Playing {query} on YouTube")
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(search_url)

def open_app(app_name, assistant):
    """Launch system applications"""
    app_map = {
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe'
    }
    if app_name in app_map:
        subprocess.Popen(app_map[app_name])
        assistant.speak(f"Opening {app_name}")
    else:
        assistant.speak("Application not available")

def google_search(query, assistant):
    """Perform web search"""
    assistant.speak(f"Searching for {query}")
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)

if __name__ == '__main__':
    assistant = TerminalAssistant()
    assistant.speak("Hello! I'm your voice assistant. How can I help you today?")
    
    try:
        while True:
            command = assistant.listen_command()
            if command:
                process_command(command, assistant)
    except KeyboardInterrupt:
        assistant.speak("Goodbye! Have a great day!")
