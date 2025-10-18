import json
import random
import re
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

class CustomerSupportChatbot:
    """Smart customer support chatbot with intent recognition and fallback handling"""
    
    def __init__(self, intents_path: str = None, use_openai: bool = False):
        self.intents_path = intents_path
        self.intents = self.load_intents()
        self.use_openai = use_openai
        self.conversation_history = []
        
        if use_openai:
            try:
                import openai
                openai.api_key = os.getenv('OPENAI_API_KEY')
                self.openai_client = openai
            except ImportError:
                print("OpenAI not installed. Install with: pip install openai")
                self.use_openai = False
    
    def load_intents(self) -> Dict:
        """Load intents from JSON file"""
        if self.intents_path and os.path.exists(self.intents_path):
            with open(self.intents_path, 'r') as f:
                return json.load(f)
        
        return {
            'intents': [
                {
                    'tag': 'greeting',
                    'patterns': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
                    'responses': ['Hello! How can I help you today?', 'Hi there! What can I do for you?']
                },
                {
                    'tag': 'order_status',
                    'patterns': ['order status', 'track order', 'where is my order', 'delivery status'],
                    'responses': ['I can help you track your order. Please provide your order number.']
                },
                {
                    'tag': 'refund',
                    'patterns': ['refund', 'return', 'money back', 'cancel order'],
                    'responses': ['I understand you want a refund. Let me help you with the return process.']
                },
                {
                    'tag': 'technical_issue',
                    'patterns': ['not working', 'error', 'problem', 'issue', 'broken'],
                    'responses': ['I\'m sorry you\'re experiencing technical issues. Can you describe the problem?']
                },
                {
                    'tag': 'goodbye',
                    'patterns': ['bye', 'goodbye', 'see you', 'thank you', 'thanks'],
                    'responses': ['You\'re welcome! Have a great day!', 'Goodbye! Feel free to reach out anytime.']
                }
            ]
        }
    
    def preprocess_input(self, user_input: str) -> str:
        """Clean and normalize user input"""
        text = user_input.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def calculate_similarity(self, input_text: str, pattern: str) -> float:
        """Improved word-based similarity score with exact phrase matching"""
        input_lower = input_text.lower()
        pattern_lower = pattern.lower()
        
        # Exact phrase match gets highest score
        if pattern_lower in input_lower:
            return 1.0
        
        if input_lower in pattern_lower:
            return 0.95
        
        # Word-based similarity
        input_words = set(input_lower.split())
        pattern_words = set(pattern_lower.split())
        
        if not input_words or not pattern_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = input_words.intersection(pattern_words)
        union = input_words.union(pattern_words)
        
        base_score = len(intersection) / len(union)
        
        # Bonus for multiple matching words
        if len(intersection) >= 2:
            base_score = min(base_score + 0.3, 1.0)
        
        # Bonus for key word matches
        key_words = ['order', 'refund', 'return', 'track', 'login', 'password', 'error', 'not working', 'broken', 'hello', 'hi']
        for word in key_words:
            if word in input_lower and word in pattern_lower:
                base_score = min(base_score + 0.2, 1.0)
        
        return base_score
    
    def detect_intent(self, user_input: str) -> Tuple[str, float]:
        """Detect user intent with confidence score"""
        processed_input = self.preprocess_input(user_input)
        best_intent = None
        best_score = 0.0
        
        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                score = self.calculate_similarity(processed_input, pattern)
                
                if score > best_score:
                    best_score = score
                    best_intent = intent['tag']
        
        return best_intent, best_score
    
    def get_response(self, intent: str) -> str:
        """Get response for detected intent"""
        for intent_data in self.intents['intents']:
            if intent_data['tag'] == intent:
                return random.choice(intent_data['responses'])
        
        return None
    
    def fallback_response(self, user_input: str) -> str:
        """Handle cases where no intent is detected"""
        if self.use_openai:
            return self.get_openai_response(user_input)
        
        fallback_messages = [
            "I'm not sure I understand. Could you please rephrase that?",
            "I'm still learning. Can you provide more details?",
            "I didn't quite catch that. Could you clarify what you need help with?",
            "Let me connect you with a human agent who can better assist you."
        ]
        
        return random.choice(fallback_messages)
    
    def get_openai_response(self, user_input: str) -> str:
        """Use OpenAI GPT for fallback responses"""
        try:
            system_prompt = """You are a helpful customer support assistant. 
            Provide concise, friendly, and professional responses. 
            If you cannot help, suggest escalating to a human agent."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "I'm having trouble processing your request. Please try again."
    
    def chat(self, user_input: str, confidence_threshold: float = 0.3) -> Dict:
        """Main chat function"""
        intent, confidence = self.detect_intent(user_input)
        
        self.conversation_history.append({
            'user_input': user_input,
            'intent': intent,
            'confidence': confidence
        })
        
        if confidence >= confidence_threshold and intent:
            response = self.get_response(intent)
        else:
            response = self.fallback_response(user_input)
            intent = 'fallback'
        
        return {
            'response': response,
            'intent': intent,
            'confidence': confidence,
            'requires_human': confidence < 0.2
        }
    
    def get_conversation_history(self) -> List[Dict]:
        """Return conversation history"""
        return self.conversation_history
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []


if __name__ == "__main__":
    bot = CustomerSupportChatbot(
        intents_path='models/intents.json',
        use_openai=False
    )
    
    test_queries = [
        "Hello, I need help",
        "Where is my order?",
        "I want a refund",
        "The app is not working",
        "What is the meaning of life?"
    ]
    
    print("=== Customer Support Chatbot Test ===\n")
    for query in test_queries:
        print(f"User: {query}")
        result = bot.chat(query)
        print(f"Bot: {result['response']}")
        print(f"[Intent: {result['intent']}, Confidence: {result['confidence']:.2f}]\n")