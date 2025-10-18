import os
import json
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def create_default_intents():
    print_header("Creating Default Intents")
    
    default_intents = {
        "intents": [
            {
                "tag": "greeting",
                "patterns": [
                    "hello", "hi", "hey", "good morning", "good afternoon",
                    "good evening", "greetings", "what's up", "howdy"
                ],
                "responses": [
                    "Hello! How can I help you today?",
                    "Hi there! What can I do for you?",
                    "Greetings! How may I assist you?"
                ]
            },
            {
                "tag": "goodbye",
                "patterns": [
                    "bye", "goodbye", "see you", "talk to you later",
                    "thanks", "thank you", "that's all"
                ],
                "responses": [
                    "Goodbye! Have a great day!",
                    "See you later! Feel free to reach out anytime.",
                    "Thank you for contacting us!"
                ]
            },
            {
                "tag": "order_status",
                "patterns": [
                    "where is my order", "order status", "track order",
                    "tracking number", "delivery status", "when will it arrive",
                    "shipping status", "has my order shipped"
                ],
                "responses": [
                    "I can help you track your order. Please provide your order number.",
                    "Let me check your order status. What's your order number?"
                ]
            },
            {
                "tag": "refund",
                "patterns": [
                    "refund", "return", "money back", "cancel order",
                    "get my money back", "return policy", "refund request"
                ],
                "responses": [
                    "I understand you want a refund. Please provide your order number and I'll help you with the return process.",
                    "I can assist with returns. What's your order number?"
                ]
            },
            {
                "tag": "technical_issue",
                "patterns": [
                    "not working", "error", "bug", "problem", "issue",
                    "broken", "crash", "frozen", "won't load", "can't access"
                ],
                "responses": [
                    "I'm sorry you're experiencing technical issues. Can you describe the problem in more detail?",
                    "Let me help you troubleshoot. What exactly is happening?"
                ]
            },
            {
                "tag": "account",
                "patterns": [
                    "account", "login", "password", "sign in", "register",
                    "forgot password", "can't login", "reset password",
                    "create account", "username"
                ],
                "responses": [
                    "I can help with account issues. What do you need assistance with?",
                    "Let me help you with your account. What's the problem?"
                ]
            }
        ]
    }
    
    intents_path = Path('models/intents.json')
    with open(intents_path, 'w') as f:
        json.dump(default_intents, f, indent=2)
    
    print(f"✅ Created default intents file: {intents_path}")
    print(f"   Total intents: {len(default_intents['intents'])}")

def main():
    print("\n" + "🤖" * 30)
    print("  CUSTOMER SUPPORT CHATBOT - QUICK START")
    print("🤖" * 30)
    
    create_default_intents()
    
    print_header("Setup Complete!")
    print("""
✅ Default intents file created!

📋 Next Steps:

1. Test the Chatbot:
   python src\\chatbot.py

2. Run Streamlit App:
   streamlit run app\\streamlit_app.py

3. Download Kaggle Dataset (Optional):
   kaggle datasets download -d thoughtvector/customer-support-on-twitter

Happy coding! 🚀
""")

if __name__ == "__main__":
    main()