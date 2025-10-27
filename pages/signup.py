import streamlit as st
from pymongo import MongoClient
import bcrypt

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

def create_user(username, password):
    if users_collection.find_one({"username": username}):
        return False
    hashed_pw = hash_password(password)
    users_collection.insert_one({"username": username, "password": hashed_pw})
    return True

# Page Setup
st.set_page_config(page_title="HeartBot Signup", page_icon="✨", layout="centered")

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

# Signup UI
st.title("✨ HeartBot Signup")
st.markdown("**Create a new account to track your heart health**")

with st.form("signup_form"):
    username = st.text_input("Username", placeholder="Choose a unique username")
    password = st.text_input("Password", type="password", placeholder="Choose a strong password")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
    submit = st.form_submit_button("Sign Up")
    if submit:
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters long!")
        elif create_user(username, password):
            st.success(f"Account created for {username}! Please log in.")
            st.markdown("[Go to Login](./login)")
        else:
            st.error("Username already exists!")

st.markdown("Already have an account? [Go to Login](./login)")