import streamlit as st              # Streamlit for UI
import serial                       # Serial communication with Arduino
import json                         # JSON handling for data
import re                           # Regular expressions for data parsing
import plotly.graph_objects as go   # Plotly for graphing
import time                         # Time handling for delays
from collections import deque       # Deque for efficient data buffer
from streamlit_lottie import st_lottie  # Lottie animations
from sentence_transformers import SentenceTransformer  # NLP model
from sklearn.metrics.pairwise import cosine_similarity  # Similarity calculation
import numpy as np                  # Numerical operations
import nltk                         # Natural Language Toolkit
from nltk.corpus import stopwords   # Stopwords for text preprocessing
from nltk.tokenize import word_tokenize  # Tokenization
from nltk.stem import WordNetLemmatizer  # Lemmatization
from pymongo import MongoClient     # MongoDB connection
from datetime import datetime       # Date and time handling
from cryptography.fernet import Fernet  # Encryption

# Download NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Encryption Setup
# Generate a key (replace with secure key in production, e.g., from env variable)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Encrypt data function
def encrypt_data(data):
    if isinstance(data, list):
        data_str = json.dumps(data)  # Convert list to JSON string
        return cipher_suite.encrypt(data_str.encode()).decode()
    return cipher_suite.encrypt(str(data).encode()).decode()

# Decrypt data function with error handling
def decrypt_data(encrypted_data):
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode()).decode()
        return json.loads(decrypted_data) if decrypted_data.startswith('[') else decrypted_data
    except Exception as e:
        return []

# MongoDB Setup
MONGODB_URI = "mongodb://localhost:27017/heartbot"  # MongoDB connection string
DB_NAME = "heartbot_db"  # Database name

@st.cache_resource  # Cache MongoDB client to avoid repeated connections
def get_mongo_client():
    return MongoClient(MONGODB_URI)

client = get_mongo_client()
db = client[DB_NAME]
chat_collection = db["chat_history"]  # Collection for chat history
readings_collection = db["bpm_readings"]  # Collection for BPM readings

# Save encrypted chat history to MongoDB
def save_chat_history(username, chat_history):
    if chat_history:
        encrypted_data = encrypt_data(chat_history)
        chat_collection.delete_many({"username": username})
        chat_docs = [{"username": username, "timestamp": datetime.now(), "chat": encrypted_data}]
        chat_collection.insert_many(chat_docs)

# Load decrypted chat history from MongoDB
def load_chat_history(username):
    chat_doc = chat_collection.find_one({"username": username})
    if chat_doc and "chat" in chat_doc:
        return decrypt_data(chat_doc["chat"])
    return []

# Save encrypted BPM readings to MongoDB
def save_bpm_readings(username, readings):
    if readings:
        encrypted_data = encrypt_data(readings)
        readings_collection.delete_many({"username": username})
        readings_doc = {"username": username, "timestamp": datetime.now(), "readings": encrypted_data}
        readings_collection.insert_one(readings_doc)

# Load decrypted BPM readings from MongoDB
def load_bpm_readings(username):
    reading_doc = readings_collection.find_one({"username": username})
    if reading_doc and "readings" in reading_doc:
        return decrypt_data(reading_doc["readings"])
    return []

# Page Setup
st.set_page_config(page_title="HeartBot Live", page_icon="💓", layout="wide")  # Configure app layout

# Hide Streamlit's default sidebar navigation
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# Check Login Status
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access the dashboard.")
    st.markdown("[Go to Login](./login)")
    st.stop()

# Logout and Restart Buttons Side by Side
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Logout"):  # Logout button action
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.chat_history = []
        st.switch_page("pages/login.py")
with col2:
    if st.button("Restart"):  # Restart button action
        st.session_state.chat_history = []
        st.session_state.count = 0
        st.session_state.x_data = deque(maxlen=50)
        st.session_state.y_data = deque(maxlen=50)
        st.rerun()

# Custom Sidebar with Title and Description
st.sidebar.title(f"💬 HeartBot - {st.session_state.username}")
st.sidebar.markdown("**Your AI Heart Health Companion**")

# Load Lottie Animation for Heartbeat
try:
    with open("ECG.json", "r") as f:
        heart_anim = json.load(f)
except FileNotFoundError:
    heart_anim = None

# Chatbot Setup
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history(st.session_state.username)
if "dynamic_faq" not in st.session_state:
    st.session_state.dynamic_faq = []
if "context" not in st.session_state:
    st.session_state.context = ""

# Cached Model for NLP
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# FAQ List
faq = [
    {"question": "Hello!", "answer": "Hey there! Welcome to HeartBot, your AI heart health buddy. How can I help you today?"},
    {"question": "Hi!", "answer": "Hi! Glad you're here with HeartBot. What's on your mind about your heart?"},
    {"question": "Good morning!", "answer": "Good morning! Nice to see you. How can HeartBot assist you with your heart health today?"},
    {"question": "Good afternoon!", "answer": "Good afternoon! I'm HeartBot, here to help. What would you like to know about your heart?"},
    {"question": "Good evening!", "answer": "Good evening! Welcome to HeartBot. How can I support your heart health tonight?"},
    {"question": "What is normal BPM?", "answer": "A normal heart rate is between 60 and 100 BPM when you're resting."},
    {"question": "What is bpm?", "answer": "BPM means 'beats per minute' — how many times your heart beats in one minute."},
    {"question": "My heart rate is 120, is that bad?", "answer": "120 BPM is a bit high if you're resting. Try sitting calmly and taking deep breaths. If it stays high, you should talk to a doctor."},
    {"question": "What happens if my bpm is too low?", "answer": "If your BPM is below 60 and you feel dizzy or tired, you should get it checked. But some fit people naturally have low BPM."},
    {"question": "Why does my heart beat fast sometimes?", "answer": "It can happen due to stress, fear, exercise, or caffeine. Usually it's normal if it slows down after some rest."},
    {"question": "How can I calm my heart rate?", "answer": "Sit down, relax, take slow deep breaths, and drink some water. Avoid stress or caffeine."},
    {"question": "Does coffee increase bpm?", "answer": "Yes! Coffee has caffeine, which can make your heart beat faster for a while."},
    {"question": "Why does my heart race when I'm scared?", "answer": "That's normal! Your body releases adrenaline when you're scared, making your heart beat faster."},
    {"question": "What should I do if my heart rate is too high?", "answer": "Sit quietly, breathe slowly, and relax. If it doesn't come down or you feel unwell, contact a doctor."},
    {"question": "Is 70 bpm good?", "answer": "Yes! 70 BPM is perfectly normal for most people."},
    {"question": "What is a healthy heart rate for adults?", "answer": "Most adults have a healthy resting heart rate between 60 and 100 BPM."},
    {"question": "Can emotions change heart rate?", "answer": "Yes! Happiness, anger, or fear can make your heart beat faster or slower."},
    {"question": "Does exercise increase bpm?", "answer": "Yes. When you exercise, your heart beats faster to send oxygen to your muscles."},
    {"question": "Why does my heart beat fast after climbing stairs?", "answer": "That's normal! Your body needs more oxygen, so your heart beats faster to keep up."},
    {"question": "Can dehydration cause fast heart rate?", "answer": "Yes, if you're dehydrated your heart works harder to pump blood, so BPM can go up."},
    {"question": "Can I check my bpm with my finger?", "answer": "Yes, you can feel your pulse on your wrist or neck and count beats for 60 seconds."},
    {"question": "What causes irregular heartbeats?", "answer": "Irregular heartbeats can be caused by stress, lack of sleep, alcohol, or medical conditions like arrhythmia. Consult a doctor if it persists."},
    {"question": "Is it normal to feel my heart pounding?", "answer": "Yes, if you're active or excited, but if it happens at rest or with dizziness, see a doctor."},
    {"question": "How can I improve my heart health?", "answer": "Eat a balanced diet, exercise regularly, avoid smoking, and manage stress for better heart health."},
    {"question": "What is a heart attack?", "answer": "A heart attack occurs when blood flow to the heart is blocked. Symptoms include chest pain, shortness of breath—seek emergency help immediately."},
    {"question": "What are signs of a heart attack?", "answer": "Look for chest pain, shortness of breath, arm or jaw discomfort, or nausea—call emergency services (e.g., 108 in India) right away if you notice these."},
    {"question": "Should I exercise if my heart rate is high?", "answer": "No, rest and hydrate. If it doesn't normalize, contact a doctor or emergency services."},
    {"question": "What to do if I feel chest pain?", "answer": "Stop what you're doing, sit down, and call emergency services (e.g., 108 in India) if the pain lasts more than a few minutes or worsens."}
]

# Combine FAQs with dynamic FAQs
def update_faq_embeddings():
    all_faq = faq + st.session_state.dynamic_faq
    questions = [item['question'] for item in all_faq]
    q_embeddings = model.encode(questions)
    return all_faq, questions, q_embeddings

all_faq, questions, q_embeddings = update_faq_embeddings()

# Preprocess Input for NLP
def preprocess_input(text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalnum() and token not in stop_words]
    return ' '.join(tokens)

# Get Answer from FAQ based on input similarity
def get_answer(user_input):
    global all_faq, questions, q_embeddings
    processed_input = preprocess_input(user_input)
    u_emb = model.encode([processed_input])
    sims = cosine_similarity(u_emb, q_embeddings)[0]
    idx = np.argmax(sims)
    
    context = st.session_state.context
    if "bpm" in processed_input.lower() and "high" in context.lower():
        return "It sounds like you're concerned about a high heart rate. Try relaxing, hydrating, and avoiding stimulants like caffeine. If it persists, please consult a doctor."
    
    if sims[idx] < 0.5:
        fallback = "I'm not sure about that, but it sounds important! Can you tell me more, or try rephrasing your question?"
        if len(processed_input) > 10:
            st.session_state.dynamic_faq.append({"question": user_input, "answer": fallback})
            all_faq, questions, q_embeddings = update_faq_embeddings()
        return fallback
    
    st.session_state.context = processed_input
    return all_faq[idx]['answer']

# Handle Chatbot Input
def send_message():
    user_input = st.session_state.chat_input.strip()
    if user_input:
        reply = get_answer(user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("HeartBot", reply))
        save_chat_history(st.session_state.username, st.session_state.chat_history)
        st.session_state.chat_input = ""

# Chat UI in Sidebar
st.sidebar.text_input(
    "Ask something about your heart...",
    key="chat_input",
    on_change=send_message
)

st.sidebar.markdown("### 💬 Chat History")
chat_placeholder = st.sidebar.empty()
with chat_placeholder.container():
    chats = st.session_state.chat_history
    for i in range(len(chats) - 2, -1, -2):
        sender_user, msg_user = chats[i]
        sender_bot, msg_bot = chats[i + 1]
        st.markdown(
            f"<p style='color:#00b4d8; text-align:right; margin-bottom:0;'><b>{sender_user}:</b> {msg_user}</p>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<p style='color:#f72585; text-align:left; margin-bottom:0;'><b>{sender_bot}:</b> {msg_bot}</p>",
            unsafe_allow_html=True
        )

st.sidebar.markdown("<br>" * 20, unsafe_allow_html=True)

# Main Dashboard
st.title("💓 Live Heartbeat Monitoring Dashboard")
st.caption(f"Real-Time BPM Stream from Arduino + AI Health Assistant | User: {st.session_state.username}")

if heart_anim:
    st_lottie(heart_anim, height=200, key="heart_anim", speed=1, quality="high")  # Display heartbeat animation

col1, col2, col3 = st.columns(3)
bpm_placeholder = col1.metric("Current BPM", "0")  # Display current BPM
avg_placeholder = col2.metric("Average BPM", "0")  # Display average BPM
status_placeholder = col3.metric("Status", "🩶 Waiting...")  # Display heart rate status

st.subheader("📊 Live Heart Rate Graph (Streaming Data)")
chart_placeholder = st.empty()  # Placeholder for live graph

# Serial Connection to Arduino
try:
    ser = serial.Serial('COM7', 9600, timeout=2)  # Connect to Arduino on COM7
except:
    st.error("⚠ Could not connect to Arduino. Check your COM port.")
    st.stop()

# Session Variables Initialization
if "count" not in st.session_state:
    st.session_state.count = 0
    st.session_state.x_data = deque(maxlen=50)  # X-axis data buffer
    st.session_state.y_data = deque(maxlen=50)  # Y-axis data buffer
    prev_readings = load_bpm_readings(st.session_state.username)
    if prev_readings:
        st.session_state.x_data = deque(range(1, len(prev_readings) + 1), maxlen=50)
        st.session_state.y_data = deque(prev_readings, maxlen=50)
        st.session_state.count = len(prev_readings)

max_readings = 15  # Maximum number of readings to capture

fig = go.Figure()
fig.update_layout(
    xaxis_title="Beat #",
    yaxis_title="BPM",
    template="plotly_dark",
    height=400,
    margin=dict(l=20, r=20, t=30, b=20)
)  # Configure graph layout

# Live Stream Loop
while st.session_state.count < max_readings:
    line = ser.readline().decode('utf-8', errors='ignore').strip()  # Read serial data
    match = re.search(r"BPM:\s*([\d.]+)", line)
    if match:
        bpm = float(match.group(1))  # Extract BPM value
        st.session_state.count += 1
        st.session_state.x_data.append(st.session_state.count)
        st.session_state.y_data.append(bpm)

        avg_bpm = sum(st.session_state.y_data) / len(st.session_state.y_data)  # Calculate average

        fig.data = []
        fig.add_trace(go.Scatter(
            x=list(st.session_state.x_data),
            y=list(st.session_state.y_data),
            mode='lines+markers',
            name='Heart Rate'
        ))  # Update graph with new data
        chart_placeholder.plotly_chart(fig, use_container_width=True)

        bpm_placeholder.metric("Current BPM", round(bpm, 1))  # Update current BPM
        avg_placeholder.metric("Average BPM", round(avg_bpm, 1))  # Update average BPM

        if avg_bpm < 60:
            status_placeholder.metric("Status", "🔵 Low")  # Status: Low
        elif avg_bpm > 100:
            status_placeholder.metric("Status", "🔴 High")  # Status: High
        else:
            status_placeholder.metric("Status", "🟢 Normal")  # Status: Normal

    time.sleep(0.1)  # Small delay for smooth updates

# Save Readings
final_readings = list(st.session_state.y_data)
save_bpm_readings(st.session_state.username, final_readings)

st.success("✅ 15 Readings Captured. Arduino has completed the session.")  # Notify completion