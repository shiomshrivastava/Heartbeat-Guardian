import streamlit as st
import serial
import json
import re
import plotly.graph_objects as go
import time
from collections import deque
from streamlit_lottie import st_lottie
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from pymongo import MongoClient
from datetime import datetime
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

# ====================== LOAD ENV & ENCRYPTION ======================
load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "").strip()
if not ENCRYPTION_KEY or len(ENCRYPTION_KEY) != 44:
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    with open(".env", "w") as f:
        f.write(f"ENCRYPTION_KEY={ENCRYPTION_KEY}\n")
        f.write("MONGODB_URI=mongodb://localhost:27017/heartbot\n")
    st.success("NEW ENCRYPTION KEY GENERATED & SAVED!")
else:
    pass  # Clean UI

cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(data):
    if isinstance(data, list):
        data_str = json.dumps(data)
        return cipher_suite.encrypt(data_str.encode()).decode()
    return cipher_suite.encrypt(str(data).encode()).decode()

def decrypt_data(encrypted_data):
    try:
        decrypted = cipher_suite.decrypt(encrypted_data.encode()).decode()
        return json.loads(decrypted) if decrypted.startswith('[') else decrypted
    except:
        return []

# ====================== MONGODB SETUP ======================
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/heartbot")
DB_NAME = "heartbot_db"

@st.cache_resource
def get_mongo_client():
    return MongoClient(MONGODB_URI)

client = get_mongo_client()
db = client[DB_NAME]
chat_collection = db["chat_history"]
readings_collection = db["bpm_readings"]

def save_chat_history(username, chat_history):
    if chat_history:
        encrypted = encrypt_data(chat_history)
        chat_collection.delete_many({"username": username})
        chat_collection.insert_one({
            "username": username,
            "timestamp": datetime.now(),
            "chat": encrypted
        })

def load_chat_history(username):
    doc = chat_collection.find_one({"username": username})
    return decrypt_data(doc["chat"]) if doc and "chat" in doc else []

def save_bpm_readings(username, readings):
    if readings:
        encrypted = encrypt_data(readings)
        readings_collection.delete_many({"username": username})
        readings_collection.insert_one({
            "username": username,
            "timestamp": datetime.now(),
            "readings": encrypted
        })

def load_bpm_readings(username):
    doc = readings_collection.find_one({"username": username})
    return decrypt_data(doc["readings"]) if doc and "readings" in doc else []

# ====================== NLTK & MODEL ======================
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

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

def update_faq_embeddings():
    dynamic = st.session_state.get("dynamic_faq", [])
    all_faq = faq + dynamic
    questions = [item['question'] for item in all_faq]
    q_embeddings = model.encode(questions)
    return all_faq, questions, q_embeddings

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="HeartBot Live", page_icon="Heart", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# ====================== LOGIN CHECK ======================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access the dashboard.")
    st.markdown("[Go to Login](./login)")
    st.stop()

# ====================== SESSION INIT ======================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history(st.session_state.username)
if "dynamic_faq" not in st.session_state:
    st.session_state.dynamic_faq = []
if "context" not in st.session_state:
    st.session_state.context = ""
if "count" not in st.session_state:
    st.session_state.count = 0
if "x_data" not in st.session_state:
    st.session_state.x_data = deque(maxlen=50)
if "y_data" not in st.session_state:
    st.session_state.y_data = deque(maxlen=50)
if "readings" not in st.session_state:
    st.session_state.readings = load_bpm_readings(st.session_state.username)

# Load previous data if exists
if st.session_state.readings:
    st.session_state.count = len(st.session_state.readings)
    st.session_state.x_data = deque(range(1, st.session_state.count + 1), maxlen=50)
    st.session_state.y_data = deque(st.session_state.readings, maxlen=50)

# Update embeddings
all_faq, questions, q_embeddings = update_faq_embeddings()

# ====================== CHATBOT FUNCTIONS ======================
def preprocess_input(text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t.isalnum() and t not in stop_words]
    return ' '.join(tokens)

def get_answer(user_input):
    global all_faq, questions, q_embeddings
    processed = preprocess_input(user_input)
    u_emb = model.encode([processed])
    sims = cosine_similarity(u_emb, q_embeddings)[0]
    idx = np.argmax(sims)
    
    if sims[idx] < 0.5:
        fallback = "I'm not sure about that, but it sounds important! Can you tell me more?"
        if len(processed) > 10:
            st.session_state.dynamic_faq.append({"question": user_input, "answer": fallback})
            all_faq, questions, q_embeddings = update_faq_embeddings()
        return fallback
    
    st.session_state.context = processed
    return all_faq[idx]['answer']

def send_message():
    user_input = st.session_state.chat_input.strip()
    if user_input:
        reply = get_answer(user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("HeartBot", reply))
        save_chat_history(st.session_state.username, st.session_state.chat_history)
        st.session_state.chat_input = ""

# ====================== SIDEBAR ======================
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.logged_in = False
        st.switch_page("pages/login.py")
with col2:
    if st.button("Restart"):
        if st.session_state.get("ser") and st.session_state.ser.is_open:
            st.session_state.ser.close()
            st.session_state.ser = None
        st.session_state.chat_history = []
        st.session_state.count = 0
        st.session_state.x_data = deque(maxlen=50)
        st.session_state.y_data = deque(maxlen=50)
        st.session_state.readings = []
        st.rerun()

st.sidebar.title(f"HeartBot - {st.session_state.username}")
st.sidebar.markdown("**Your AI Heart Health Companion**")

# Lottie Animation
try:
    with open("ECG.json", "r") as f:
        heart_anim = json.load(f)
except:
    heart_anim = None

# Chat UI
st.sidebar.text_input("Ask about your heart...", key="chat_input", on_change=send_message)
st.sidebar.markdown("### 💬 Chat History")
chat_container = st.sidebar.empty()
with chat_container.container():
    for i in range(len(st.session_state.chat_history)-1, -1, -2):
        if i >= 0:
            user_msg = st.session_state.chat_history[i]
            bot_msg = st.session_state.chat_history[i-1] if i > 0 else None
            if bot_msg:
                st.markdown(f"<p style='text-align:left; color:#f72585; margin:2px;'><b>{bot_msg[0]}:</b> {bot_msg[1]}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:right; color:#00b4d8; margin:2px;'><b>{user_msg[0]}:</b> {user_msg[1]}</p>", unsafe_allow_html=True)

# Auto-scroll
st.markdown("""
<script>
    const chat = window.parent.document.querySelectorAll('div[data-testid="stVerticalBlock"]')[1];
    if (chat) chat.scrollTop = chat.scrollHeight;
</script>
""", unsafe_allow_html=True)

# ====================== MAIN DASHBOARD ======================
st.title("Live Heartbeat Monitoring Dashboard")
st.caption(f"Real-Time BPM Stream | User: {st.session_state.username}")

if heart_anim:
    st_lottie(heart_anim, height=200, key="heart", speed=1)

col1, col2, col3 = st.columns(3)
bpm_placeholder = col1.empty()
avg_placeholder = col2.empty()
status_placeholder = col3.empty()

st.subheader("Live Heart Rate Graph")
chart_placeholder = st.empty()

# ====================== MAX READINGS & ARDUINO CONNECTION ======================
max_readings = 15

# Arduino connection (HAMESHA TRY KARO)
if "ser" not in st.session_state or st.session_state.ser is None:
    try:
        ser = serial.Serial('COM7', 9600, timeout=2)
        time.sleep(2)
        st.session_state.ser = ser
        st.success("Arduino Connected!")
    except Exception as e:
        st.session_state.ser = None
        st.error(f"Arduino Connection Failed: {e}")
        st.stop()
else:
    st.success("Arduino already connected.")

# ====================== LIVE DATA LOOP (ONLY IF NEEDED) ======================
if st.session_state.count < max_readings:
    try:
        while st.session_state.count < max_readings:
            if st.session_state.ser.in_waiting > 0:
                line = st.session_state.ser.readline().decode('utf-8', errors='ignore').strip()
                match = re.search(r"BPM:\s*([\d.]+)", line)
                if match:
                    bpm = float(match.group(1))
                    st.session_state.count += 1
                    st.session_state.x_data.append(st.session_state.count)
                    st.session_state.y_data.append(bpm)
                    st.session_state.readings.append(bpm)

                    avg_bpm = np.mean(st.session_state.readings)

                    fig_live = go.Figure().update_layout(
                        xaxis_title="Beat #", yaxis_title="BPM", template="plotly_dark",
                        height=400, margin=dict(l=20, r=20, t=30, b=20)
                    )
                    fig_live.add_trace(go.Scatter(
                        x=list(st.session_state.x_data),
                        y=list(st.session_state.y_data),
                        mode='lines+markers',
                        name='Heart Rate',
                        line=dict(color='#f72585')
                    ))

                    # KEY HATA DIYA — placeholder update karega
                    chart_placeholder.plotly_chart(fig_live, use_container_width=True)
                    bpm_placeholder.metric("Current BPM", round(bpm, 1))
                    avg_placeholder.metric("Average BPM", round(avg_bpm, 1))

                    status = "🔵 Low" if avg_bpm < 60 else "🔴 High" if avg_bpm > 100 else "🟢 Normal"
                    status_placeholder.metric("Status", status)

            time.sleep(0.1)

    finally:
        if st.session_state.get("ser") and st.session_state.ser.is_open:
            st.session_state.ser.close()
            st.session_state.ser = None
            st.info("Arduino port closed safely.")  # YEHI RAKHA HAI

else:
    st.info("Session complete. Data saved below.")

# ====================== SAVE & EXPORT (CLEAN) ======================
if st.session_state.readings:
    save_bpm_readings(st.session_state.username, st.session_state.readings)
    
    fig_final = go.Figure().update_layout(
        xaxis_title="Beat #", yaxis_title="BPM", template="plotly_dark",
        height=400, margin=dict(l=20, r=20, t=30, b=20)
    )
    fig_final.add_trace(go.Scatter(
        x=list(range(1, len(st.session_state.readings) + 1)),
        y=st.session_state.readings,
        mode='lines+markers',
        name='Heart Rate',
        line=dict(color='#f72585')
    ))
    
    chart_placeholder.plotly_chart(fig_final, use_container_width=True, key="final_chart")

    avg_bpm = np.mean(st.session_state.readings)
    last_bpm = st.session_state.readings[-1]
    status = "Low" if avg_bpm < 60 else "High" if avg_bpm > 100 else "Normal"
    
    bpm_placeholder.metric("Current BPM", round(last_bpm, 1))
    avg_placeholder.metric("Average BPM", round(avg_bpm, 1))
    status_placeholder.metric("Status", status)

    csv_data = "Beat,BPM\n" + "\n".join([f"{i+1},{bpm}" for i, bpm in enumerate(st.session_state.readings)])
    st.download_button(
        label="Download BPM Data (CSV)",
        data=csv_data,
        file_name=f"heartbot_{st.session_state.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
else:
    st.info("No readings captured yet.")