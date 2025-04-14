import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import subprocess
import nltk
import time  # Add this import
from nltk import pos_tag, word_tokenize
from nltk.chunk import ne_chunk
from nltk.tree import Tree
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

nltk.data.path.append(os.path.join(os.path.expanduser("~"), "nltk_data"))

# API and URL constants
GOOGLE_SEARCH_URL = "https://www.google.com/search?q={}"
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={}"
GEMINI_API_KEY = "AIzaSyApOFY-y1kuo5XBvHpcvZg6uJqVmXUyMsA"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Email constants - Replace these with your actual credentials
# NOTE: Storing credentials in code is not secure for production use
EMAIL_ADDRESS = "aniketsinghs7188@gmail.com"  # Replace this after copying the code
EMAIL_PASSWORD = "gkduheaufntfzkbd"    # Replace this after copying the code

class TerminalAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.setup_nltk()
        self.setup_engine()

    def setup_nltk(self):
        required_resources = {
            'punkt': 'tokenizers/punkt',
            'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger',
            'maxent_ne_chunker': 'chunkers/maxent_ne_chunker',
            'words': 'corpora/words'
        }

        for resource_id, resource_path in required_resources.items():
            try:
                nltk.data.find(resource_path)
            except LookupError:
                print(f"Downloading missing NLTK resource: {resource_id}")
                nltk.download(resource_id, quiet=False)

    def setup_engine(self):
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id)
        self.engine.setProperty('rate', 250)

    def speak(self, text):
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_command(self):
        try:
            with sr.Microphone() as source:
                print("\nListening... (Ctrl+C to exit)")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                command = self.recognizer.recognize_google(audio).lower()
                print(f"You said: {command}")
                return command
        except sr.WaitTimeoutError:
            print("Listening timed out. Please try again.")
            return ""
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

    if action is None:
        for action_type, synonyms in action_map.items():
            for keyword in synonyms:
                if keyword in command:
                    action = action_type
                    break
            if action:
                break

    target = " ".join([word for word, pos in tagged if pos.startswith('NN')])

    return action, entities, target

def ask_gemini(question, summary=True):
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        # Modify the prompt based on whether we want a summary or full response
        if summary and any(word in question.lower() for word in ["what", "who", "where", "when", "why", "how"]):
            modified_question = f"Give a brief 2-3 sentence summary about: {question}"
        else:
            modified_question = question
            
        request_data = {
            "contents": [
                {
                    "parts": [
                        {"text": modified_question}
                    ]
                }
            ]
        }
        
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        response = requests.post(url, headers=headers, json=request_data)
        
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return "I'm sorry, I encountered an error with the Gemini API."
            
        response_data = response.json()
        
        if "candidates" in response_data and len(response_data["candidates"]) > 0:
            if "content" in response_data["candidates"][0]:
                content = response_data["candidates"][0]["content"]
                if "parts" in content and len(content["parts"]) > 0:
                    return content["parts"][0]["text"].strip()
        
        print("Unexpected response format:", response_data)
        return "I received a response but couldn't parse it correctly."
    except Exception as e:
        print(f"Error querying Gemini: {str(e)}")
        return "I'm sorry, I couldn't process that request."

def write_content(topic, content_type, assistant):
    try:
        # Create prompt based on content type
        if content_type == "essay":
            prompt = f"Write a detailed essay on {topic}"
        elif content_type == "information":
            prompt = f"Provide detailed information about {topic}"
        else:
            prompt = f"Write about {topic}"

        assistant.speak(f"Writing {content_type} about {topic}. Please wait...")
        content = ask_gemini(prompt, summary=False)  # Get full response
        
        # Create unique filename based on content type and topic
        safe_topic = "".join(x for x in topic if x.isalnum() or x in (' ','-','_'))
        filename = f"{content_type}_{safe_topic}_{int(time.time())}.txt"
        
        # Create temp directory if it doesn't exist
        temp_dir = os.getenv('TEMP') or os.path.join(os.path.expanduser("~"), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_file = os.path.join(temp_dir, filename)
        
        # Write content to file
        with open(temp_file, 'w', encoding='utf-8') as file:
            file.write(f"Topic: {topic}\n")
            file.write(f"Type: {content_type}\n")
            file.write("=" * 50 + "\n\n")
            file.write(content)

        # Open with default text editor
        os.startfile(temp_file)
        assistant.speak(f"I've written the {content_type} and opened it for you.")
        
    except Exception as e:
        print(f"Error writing content: {str(e)}")
        assistant.speak(f"I'm sorry, I couldn't write the {content_type}.")

def compose_email(topic, assistant):
    try:
        # Get recipient address
        assistant.speak("Please enter the recipient's email address.")
        recipient = input("Recipient email: ")
        
        # Generate subject and content with Gemini - with more specific instructions
        subject_prompt = f"Create exactly one single-line email subject about {topic}. No bullet points or options. Just one line."
        body_prompt = f"Write a professional email about: {topic}"
        
        assistant.speak(f"Composing email about {topic}. Please wait...")
        
        subject = ask_gemini(subject_prompt, summary=True)
        # Clean up the subject line - extract just the first line and remove any special characters
        subject = subject.split('\n')[0]  # Take only first line
        subject = subject.replace('*', '').replace('#', '').strip()  # Remove markdown formatting
        # If subject still has bullets or other formatting, extract just plain text
        if ':' in subject:
            subject = subject.split(':', 1)[1].strip()
        
        body = ask_gemini(body_prompt, summary=False)
        
        # Create a preview
        preview = f"Subject: {subject}\n\n{body[:150]}...\n\nWould you like to send this email? (yes/no)"
        print(preview)
        assistant.speak("I've composed the email. Would you like to send it?")
        
        decision = input("Send email? (yes/no): ").lower()
        
        if decision == "yes":
            return send_email(recipient, subject, body, assistant)
        else:
            assistant.speak("Email canceled.")
            return False
            
    except Exception as e:
        print(f"Error composing email: {str(e)}")
        assistant.speak("I'm sorry, I couldn't compose the email.")
        return False

def send_email(recipient, subject, body, assistant):
    try:
        # Use the constants instead of asking for input each time
        sender_email = EMAIL_ADDRESS  # Use the constant defined at the top
        password = EMAIL_PASSWORD     # Use the constant defined at the top
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = subject
        
        message.attach(MIMEText(body, "plain"))
        
        # Connect to Gmail's SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient, message.as_string())
        
        assistant.speak(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        assistant.speak("I couldn't send the email. Please check your credentials or internet connection.")
        return False

def process_command(command, assistant):
    if not command:
        return

    # Handle email commands
    email_triggers = [
        'send email', 'write email', 'send an email', 'write an email',
        'compose email', 'email to', 'send mail', 'write mail'
    ]
    
    for trigger in email_triggers:
        if trigger in command.lower():
            # Extract topic after the trigger
            parts = command.lower().split(trigger)
            if len(parts) > 1:
                topic = parts[1].strip()
                # Remove "to" or "about" if present
                if topic.startswith("to "):
                    topic = topic[3:].strip()  # Fixed typo
                if topic.startswith("about "):
                    topic = topic[6:].strip()
                
                if topic:
                    compose_email(topic, assistant)
                    return
                else:
                    assistant.speak("What would you like the email to be about?")
                    topic = input("Email topic: ")
                    if topic:
                        compose_email(topic, assistant)
                        return
            else:
                assistant.speak("What would you like the email to be about?")
                topic = input("Email topic: ")
                if topic:
                    compose_email(topic, assistant)
                    return

    # Handle writing commands
    writing_triggers = {
        'essay': ['write essay', 'write an essay', 'create essay'],
        'information': ['tell me about', 'information about', 'write about'],
        'notes': ['take notes', 'write notes', 'make notes']
    }

    for content_type, triggers in writing_triggers.items():
        for trigger in triggers:
            if trigger in command.lower():
                # Extract topic after the trigger
                topic = command.lower().split(trigger)[-1].strip()
                if topic:
                    write_content(topic, content_type, assistant)
                    return

    # Add single word query handling at the beginning
    if len(command.split()) == 1 and not command.lower() in ['exit', 'quit']:
        assistant.speak("Let me tell you about that...")
        gemini_response = ask_gemini(f"What is {command}?")
        assistant.speak(gemini_response)
        return

    action, entities, target = analyze_command(command)
    print(f"Action: {action}\nEntities: {entities}\nTarget: {target}")

    if action is None and any(word in command for word in ["what", "who", "where", "when", "why", "how"]):
        assistant.speak("Let me think about that...")
        gemini_response = ask_gemini(command)
        assistant.speak(gemini_response)
        return

    if action is None:
        if "youtube" in command:
            action = "open"
            target = "youtube"
        elif "exit" in command or "quit" in command:
            action = "exit"
        elif any(app in command.lower() for app in ['notepad', 'calculator']):
            action = "open"
            for app in ['notepad', 'calculator']:
                if app in command.lower():
                    target = app
                    break

    if 'write' in command and 'essay' in command and ('on' in command or 'about' in command):
        topic = ""
        if 'on' in command:
            topic = command.split("on")[-1].strip()
        elif 'about' in command:
            topic = command.split("about")[-1].strip()
        
        if topic:
            write_essay(topic, assistant)
            return

    if action == 'open':
        if 'youtube' in command.lower():
            handle_youtube(entities, assistant)
        elif any(app in command.lower() for app in ['notepad', 'calculator', 'paint', 'word', 'excel', 'browser', 'file explorer', 'settings', 'control panel']):
            for app in ['notepad', 'calculator', 'paint', 'word', 'excel', 'browser', 'file explorer', 'settings', 'control panel']:
                if app in command.lower():
                    open_app(app, assistant)
                    break
        else:
            assistant.speak(f"Sorry, I don't know how to open that application")
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
    songs = [e[0] for e in entities if e[1] == 'WORK_OF_ART']
    if songs:
        play_youtube(" ".join(songs), assistant)
    else:
        webbrowser.open("https://www.youtube.com")
        assistant.speak("Opening YouTube")

def play_youtube(query, assistant):
    assistant.speak(f"Playing {query} on YouTube")
    search_url = YOUTUBE_SEARCH_URL.format(query.replace(' ', '+'))
    webbrowser.open(search_url)

def open_app(app_name, assistant):
    app_map = {
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'paint': 'mspaint.exe',
        'word': 'winword.exe',
        'excel': 'excel.exe',
        'browser': 'msedge.exe',
        'file explorer': 'explorer.exe',
        'settings': 'ms-settings:',
        'control panel': 'control.exe'
    }
    if app_name.lower() in app_map:
        try:
            subprocess.Popen(app_map[app_name.lower()])
            assistant.speak(f"Opening {app_name}")
        except Exception as e:
            print(f"Error opening application: {str(e)}")
            assistant.speak(f"I couldn't open {app_name}")
    else:
        assistant.speak("Application not available")

def google_search(query, assistant):
    assistant.speak(f"Searching for {query}")
    search_url = GOOGLE_SEARCH_URL.format(query.replace(' ', '+'))
    webbrowser.open(search_url)

if __name__ == '__main__':
    assistant = TerminalAssistant()
    assistant.speak("Hello! I'm your voice assistant. How can I assist you today?")
    
    try:
        while True:
            command = assistant.listen_command()
            if command:
                process_command(command, assistant)
    except KeyboardInterrupt:
        assistant.speak("Goodbye! Have a great day!")