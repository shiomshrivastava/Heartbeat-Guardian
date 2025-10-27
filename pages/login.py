import streamlit as st
from pymongo import MongoClient
import bcrypt
import time

# MongoDB Setup
MONGODB_URI = "mongodb://localhost:27017/heartbot"  # Replace with your MongoDB Atlas URI
DB_NAME = "heartbot_db"

@st.cache_resource
def get_mongo_client():
    return MongoClient(MONGODB_URI)

client = get_mongo_client()
db = client[DB_NAME]
users_collection = db["users"]

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def authenticate_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return True
    return False

# Create default admin user
if users_collection.count_documents({}) == 0:
    users_collection.insert_one({"username": "admin", "password": hash_password("admin123")})

# Page Setup
st.set_page_config(page_title="HeartBot Login", page_icon="🔐", layout="centered")

# Hide Streamlit's default sidebar navigation
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# Custom Sidebar (optional branding)
st.sidebar.title("💓 HeartBot")
st.sidebar.markdown("Heart Health Companion")

# Login UI
st.title("🔐 HeartBot Login")
st.markdown("**Access your heart health dashboard**")

with st.form("login_form"):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    submit = st.form_submit_button("Login")
    if submit:
        if authenticate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            # Small delay to ensure session state updates
            time.sleep(0.1)
            # Switch to dashboard page
            st.switch_page("app.py")  # Use this if Streamlit >= 1.35, else use st.experimental_rerun()
        else:
            st.error("Invalid username or password!")

st.markdown("New user? [Sign Up](./signup)")
st.info("Default: admin / admin123")