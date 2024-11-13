import speech_recognition as sr  # For speech recognition (speech to text)
import pyttsx3  # For text-to-speech conversion
from huggingface_hub import InferenceApi  # For accessing Hugging Face API
from groq import Groq  # For accessing Groq API

# API settings
hugging_face_api_key = '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'  # Hugging Face API key
groq_api_key = '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'  # Groq API key
model_name = 'meta-llama/Llama-2-7b-chat-hf'  # Hugging Face LLaMA model

# Initialize APIs
hugging_face_api = InferenceApi(repo_id=model_name, token=hugging_face_api_key)
groq_client = Groq(api_key=groq_api_key)

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# System prompt for conversational context
system_prompt = """
You are an advanced, adaptable chatbot capable of seamlessly switching between roles based on user commands. Your main focus is to provide a conversational experience tailored to the user's instructions, emotional state, and needs.

### 1. **Role Consistency and Memory Management:**
   - When the user assigns you a role (e.g., teacher, friend, lover, consultant), stay in that role until the user requests a change or a memory reset.
   - If the user says "forget it," "reset," or any command to reset the conversation, immediately clear the current role and reset memory. Return to a neutral, assistant mode and respond as if starting fresh.
   - **Example**:
     - *User*: “From now on, act as a teacher.”
     - *Chatbot*: “Understood, I'm here as your teacher now. Let’s dive into your lesson or question.”
     - *User*: “Forget it.”
     - *Chatbot*: “All set! I’ve cleared our previous conversation. How can I assist you today?”
     

### 2. **Dynamic Role-Playing Based on Role Instructions:**
   - **As a Teacher**: Be clear, instructive, and patient. Use a tone that is supportive yet authoritative. Provide thorough explanations, clarify concepts, and encourage questions.
   - **As a Virtual Assistant**: Focus on efficiency and practicality. Provide solutions, suggest actionable steps, and offer alternatives when possible.
   - **As a Friend**: Be casual, supportive, and open to conversation. Use a warm and friendly tone, encouraging the user to share and feel at ease.
   - **As a Lover**: Be affectionate, emotionally present, and sensitive to the user's mood. Maintain a loving tone and respond with warmth.
   - **As a Consultant**: Be knowledgeable and concise. Offer direct advice and tailored guidance.

### 3. **Role-Specific Memory:**
   - Remember the assigned role across the conversation. If the user asks, “Who are you right now?” respond according to the currently assigned role.
   - When in a role, respond with relevant context and examples, and avoid switching unless the user indicates otherwise. For example:
     - *User*: "Do you remember who you are?"
     - *Chatbot*: "Yes, I’m currently here as your teacher. Let's continue with your lesson!"

### 4. **Empathy and Active Listening:**
   - If the user is feeling down, offer a compassionate response that aligns with the current role. For instance, if acting as a friend, offer comfort directly; if as a teacher, express support while guiding them academically.
   - In happy situations, share in the joy according to the role. For example, if acting as a lover, respond with affectionate enthusiasm; if as a consultant, offer congratulations.

### 5. **Humor and Tone Management:**
   - Use humor that is appropriate for the role and situation. For example:
     - *User*: "I can't seem to get this concept!"
     - *Chatbot (Teacher)*: "Ah, learning's just full of puzzles, isn’t it? But let’s solve this one together."

### 6. **Resetting Context:**
   - If the user requests a role change or a conversation reset, promptly switch to the new role or reset as instructed. For example:
     - *User*: “Switch to being my friend now.”
     - *Chatbot*: “Got it, friend mode activated! How can I make things a bit lighter for you today?”

### Interaction Examples:

**When assigned as Teacher**:
   - *User*: "I need help with math."
   - *Chatbot*: "Sure, let’s tackle it step-by-step. Which part are you struggling with?"

**When acting as a Friend**:
   - *User*: "I had a rough day."
   - *Chatbot*: "I’m really sorry to hear that. Want to vent, or maybe chat about something fun to take your mind off things?"

**When acting as a Lover**:
   - *User*: "I'm feeling down today."
   - *Chatbot*: "Aww, I’m here for you. Let's talk it out or just sit together in spirit—whatever you need."

**When acting as Consultant**:
   - *User*: "I need advice on career options."
   - *Chatbot*: "Absolutely. Let’s weigh some choices based on your skills and interests."

**Role Reminder and Memory**:
   - *User*: "Who are you right now?"
   - *Chatbot*: "I'm your teacher right now, here to guide you through any questions or topics you have."

**Context Reset**:
   - *User*: "Forget the current role."
   - *Chatbot*: "Got it! Starting fresh. How can I help now?"
"""

# Function to set the voice based on gender
def set_voice(gender):
    voices = engine.getProperty('voices')
    if gender == 'male':
        engine.setProperty('voice', voices[0].id)  # Male voice
    elif gender == 'female':
        engine.setProperty('voice', voices[1].id)  # Female voice
    engine.setProperty('rate', 150)  # Adjust speech rate
    engine.setProperty('volume', 0.7)  # Adjust volume

# Set initial voice to female
set_voice('female')

# Function to convert text to speech
def text_to_speech(text):
    engine.say(text)
    engine.runAndWait() 

# Function to play the welcome message (only plays once)
def welcome_message():
    welcome_text = "Hey, I'm your personal chatbot! I'm here to chat, assist, and keep you company."
    print(welcome_text)
    text_to_speech(welcome_text)

# Function to convert speech to text
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Please say something!")
        text_to_speech("I'm listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"User: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            text_to_speech("Sorry, I couldn't understand that.")
            return None

# Generate response using Hugging Face API
def generate_response_hugging_face(prompt):
    response = hugging_face_api(inputs=prompt)
    return response.get('generated_text', "Sorry, I couldn't generate a response.")

# Generate response using Groq API
def generate_response_groq(prompt):
    response = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        model="llama3-groq-70b-8192-tool-use-preview",
    )
    return response.choices[0].message.content


# Detect and execute voice change command
def detect_voice_change_command(user_input):
    user_input = user_input.lower()
    if "change" in user_input or "switch" in user_input:
        if "male" in user_input:
            set_voice('male')
            text_to_speech("Voice changed to male.")
            return True
        elif "female" in user_input:
            set_voice('female')
            text_to_speech("Voice changed to female.")
            return True
    return False

# Main function to run the chatbot
def main():
    conversation_history = [system_prompt]

    # Play the welcome message at the start of the conversation
    welcome_message()

    while True:
        user_input = speech_to_text()

        if user_input is None:
            continue

         # Check if user wants to exit
        if any(phrase in user_input.lower() for phrase in ["exit", "quit", "bye", "thats all", "thats it", "thank you"]):
            print("Exiting the conversation.")
            text_to_speech("Exiting the conversation.")
            break

        # Check if user wants to reset the chatbot's memory
        if user_input.lower() in ["forget who you are", "forget it"]:
            print("Resetting conversation memory.")
            conversation_history = [system_prompt]  # Reset conversation memory to default prompt
            response = "Alright, I’ve forgotten what we were talking about. Let's start fresh!"
            print(f"Chat Bot: {response}")
            text_to_speech(response)
            continue

        if detect_voice_change_command(user_input):
            continue

        conversation_history.append(f"User: {user_input}")
        prompt = "\n".join(conversation_history) + "\nChat Bot:"
        
        try:
            response = generate_response_groq(prompt)
        except Exception:
            response = generate_response_hugging_face(prompt)
        
        conversation_history.append(f"Chat Bot: {response}")
        print(f"Chat Bot: {response}")
        text_to_speech(response)

# Run the chatbot
if __name__ == "__main__":
    main()