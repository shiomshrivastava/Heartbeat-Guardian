import streamlit as st
from pymongo import MongoClient
import bcrypt
import os
from dotenv import load_dotenv

# ====================== ENV & DB ======================
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/heartbot")
DB_NAME = "heartbot_db"

@st.cache_resource
def get_mongo_client():
    return MongoClient(MONGODB_URI)

client = get_mongo_client()
db = client[DB_NAME]
users_collection = db["users"]

def authenticate_user(username: str, password: str) -> bool:
    user = users_collection.find_one({"username": username})
    return user and bcrypt.checkpw(password.encode('utf-8'), user["password"])

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="HeartBot | Login", page_icon="Heart", layout="centered")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# ====================== CSS (EYE ICON FIXED) ======================
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: #fff;
        min-height: 100vh;
        padding: 3rem 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    [data-testid="stVerticalBlock"] > [data-testid="stBlock"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 450px;
        width: 100%;
        margin: 0 auto;
    }
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        color: #f72585;
        margin: 0 0 0.5rem 0;
    }
    .subtitle {
        text-align: center;
        color: #cccccc;
        margin-bottom: 2.5rem;
        font-size: 1.1rem;
    }
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        border-radius: 12px;
        padding: 14px;
        font-size: 1rem;
    }
    .stTextInput > div > div > input::placeholder {color: #aaa;}

    /* EYE ICON VISIBLE & PINK */
    button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        color: #f72585 !important;
        padding: 0 8px !important;
    }
    button[kind="secondary"]:hover {
        color: #ff6bcb !important;
    }

    .stButton > button {
        background: linear-gradient(45deg, #f72585, #7209b7);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px;
        font-weight: 600;
        width: 100%;
        margin-top: 1.5rem;
        font-size: 1.1rem;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 25px rgba(247, 37, 133, 0.4);
    }
    .link {
        text-align: center;
        margin-top: 2rem;
        font-size: 1rem;
    }
    .link a {
        color: #f72585;
        text-decoration: none;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ====================== LOGIN FORM ======================
with st.container():
    st.markdown("<h1 class='title'>HeartBot Login</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Welcome back! Access your heart health dashboard</p>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login")

        if submit:
            if not username or not password:
                st.error("Please fill both fields")
            elif authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, **{username}**!")
                st.balloons()
                st.switch_page("app.py")
            else:
                st.error("Invalid credentials")

    st.markdown("""
    <div class='link'>
        New here? <a href='./signup'>Create an account</a>
    </div>
    """, unsafe_allow_html=True)