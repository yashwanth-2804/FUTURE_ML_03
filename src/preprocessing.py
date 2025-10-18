import pandas as pd
import re
import json
from typing import List, Dict

class DataPreprocessor:
    """Preprocess customer support conversation data from Kaggle"""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        
    def load_data(self):
        """Load dataset based on file type"""
        if self.data_path.endswith('.csv'):
            self.df = pd.read_csv(self.data_path)
        elif self.data_path.endswith('.json'):
            self.df = pd.read_json(self.data_path)
        else:
            raise ValueError("Unsupported file format")
        
        print(f"Loaded {len(self.df)} records")
        print(f"Columns: {list(self.df.columns)}")
        return self.df
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if pd.isna(text):
            return ""
        
        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'[^\w\s.,!?]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_intents(self, query_column: str, response_column: str = None) -> List[Dict]:
        """Extract intents from conversations for training"""
        intents = []
        
        for idx, row in self.df.iterrows():
            query = self.clean_text(str(row[query_column]))
            
            if query:
                intent_data = {
                    'text': query,
                    'intent': self.classify_intent(query),
                }
                
                if response_column and response_column in row:
                    intent_data['response'] = self.clean_text(str(row[response_column]))
                
                intents.append(intent_data)
        
        return intents
    
    def classify_intent(self, text: str) -> str:
        """Basic rule-based intent classification"""
        text_lower = text.lower()
        
        intent_patterns = {
            'order_status': ['order', 'tracking', 'shipment', 'delivery', 'where is my'],
            'refund': ['refund', 'return', 'money back', 'reimburse'],
            'technical_issue': ['not working', 'error', 'bug', 'problem', 'issue', 'broken'],
            'account': ['account', 'login', 'password', 'sign in', 'register'],
            'pricing': ['price', 'cost', 'charge', 'fee', 'payment'],
            'product_info': ['what is', 'how does', 'features', 'specifications'],
            'complaint': ['disappointed', 'frustrated', 'unhappy', 'terrible', 'worst'],
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return intent
        
        return 'general_inquiry'
    
    def create_training_data(self, query_column: str, save_path: str = None):
        """Create structured training data"""
        intents = self.extract_intents(query_column)
        
        intent_groups = {}
        for item in intents:
            intent = item['intent']
            if intent not in intent_groups:
                intent_groups[intent] = []
            intent_groups[intent].append(item['text'])
        
        training_data = {
            'intents': [
                {
                    'tag': intent,
                    'patterns': examples[:50],
                    'responses': [f"I can help you with {intent.replace('_', ' ')}. Let me assist you."]
                }
                for intent, examples in intent_groups.items()
            ]
        }
        
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(training_data, f, indent=2)
            print(f"Training data saved to {save_path}")
        
        return training_data
    
    def get_statistics(self):
        """Get dataset statistics"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        stats = {
            'total_records': len(self.df),
            'columns': list(self.df.columns),
            'missing_values': self.df.isnull().sum().to_dict(),
            'sample_data': self.df.head(3).to_dict()
        }
        
        return stats


if __name__ == "__main__":
    # Load Twitter customer support dataset
    preprocessor = DataPreprocessor('data/raw/twcs/twcs.csv')
    df = preprocessor.load_data()
    
    # Filter only customer messages (inbound = True)
    preprocessor.df = df[df['inbound'] == True].copy()
    print(f"\nFiltered to {len(preprocessor.df)} customer messages")
    
    # Get statistics
    stats = preprocessor.get_statistics()
    print(f"\nDataset has {stats['total_records']} customer queries")
    
    # Create training data from customer messages
    preprocessor.create_training_data(
        query_column='text',
        save_path='models/intents.json'
    )
    
    print("\n✅ Training data created successfully!")