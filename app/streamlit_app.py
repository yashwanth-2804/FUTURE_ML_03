import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chatbot import CustomerSupportChatbot

st.set_page_config(
    page_title="Customer Support Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        align-items: flex-end;
        color: #000000;
    }
    .user-message strong {
        color: #000000;
    }
    .bot-message {
        background-color: #f5f5f5;
        align-items: flex-start;
        color: #000000;
    }
    .bot-message strong {
        color: #000000;
    }
    .confidence-badge {
        font-size: 0.8rem;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
        color: white;
    }
    .high-confidence {
        background-color: #4caf50;
        color: white;
    }
    .medium-confidence {
        background-color: #ff9800;
        color: white;
    }
    .low-confidence {
        background-color: #f44336;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = CustomerSupportChatbot(
        intents_path='models/intents.json',
        use_openai=False
    )
    st.session_state.messages = []

st.title("🤖 Customer Support Chatbot")
st.markdown("Welcome! I'm here to help you with your queries.")

with st.sidebar:
    st.header("⚙️ Settings")
    
    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Minimum confidence score to use intent-based response"
    )
    
    use_openai = st.checkbox(
        "Use OpenAI Fallback",
        value=False,
        help="Use GPT for unknown queries (requires API key)"
    )
    
    st.session_state.chatbot.use_openai = use_openai
    
    st.divider()
    
    st.header("📊 Statistics")
    history = st.session_state.chatbot.get_conversation_history()
    st.metric("Total Messages", len(history))
    
    if history:
        avg_confidence = sum(h['confidence'] for h in history) / len(history)
        st.metric("Avg Confidence", f"{avg_confidence:.2%}")
    
    st.divider()
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.chatbot.reset_conversation()
        st.rerun()
    
    st.divider()
    
    st.header("💡 Quick Questions")
    faq_questions = [
        "Track my order",
        "Request a refund",
        "Report a technical issue",
        "Update my account"
    ]
    
    for question in faq_questions:
        if st.button(question, key=f"faq_{question}"):
            st.session_state.messages.append({"role": "user", "content": question})
            result = st.session_state.chatbot.chat(question, confidence_threshold)
            st.session_state.messages.append({
                "role": "assistant",
                "content": result['response'],
                "intent": result['intent'],
                "confidence": result['confidence']
            })
            st.rerun()

chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            confidence = message.get('confidence', 0)
            intent = message.get('intent', 'unknown')
            
            if confidence >= 0.5:
                badge_class = "high-confidence"
                badge_text = "High Confidence"
            elif confidence >= 0.3:
                badge_class = "medium-confidence"
                badge_text = "Medium Confidence"
            else:
                badge_class = "low-confidence"
                badge_text = "Low Confidence"
            
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>Bot:</strong> {message['content']}
                <div class="confidence-badge {badge_class}">
                    {intent} | {badge_text} ({confidence:.2%})
                </div>
            </div>
            """, unsafe_allow_html=True)

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.spinner("Thinking..."):
        result = st.session_state.chatbot.chat(user_input, confidence_threshold)
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": result['response'],
        "intent": result['intent'],
        "confidence": result['confidence']
    })
    
    if result.get('requires_human', False):
        st.warning("⚠️ This query might require human assistance.")
    
    st.rerun()

st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9rem;'>
    Powered by AI | Built with Streamlit
</div>
""", unsafe_allow_html=True)