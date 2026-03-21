import streamlit as st
import json
import os
import google.generativeai as genai
from PIL import Image

# --- ১. ইউজার ডাটা ফাংশন ---
USER_DATA_FILE = "users.json"

def load_users():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user(email, password):
    users = load_users()
    users[email] = {"password": password, "status": "pending"} 
    with open(USER_DATA_FILE, "w", encoding='utf-8') as f:
        json.dump(users, f, indent=4)

# --- ২. পেজ কনফিগারেশন ---
st.set_page_config(page_title="SIGRAPHICEONE AI", layout="wide")

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("API Key missing in Secrets!")

# --- ৩. ডিজাইন (CSS) ---
st.markdown("""
    <style>
    .stAppViewMain { background-color: #050A0F !important; }
    .block-container {
        max-width: 90% !important;
        padding-top: 80px !important;
        background: transparent !important;
    }
    .main-title {
        color: white;
        text-align: center;
        font-size: 26px !important;
        font-weight: 800;
        margin-bottom: 15px !important;
    }
    /* ইনপুট বক্সের টেক্সট কালার ঠিক করা */
    input {
        color: white !important;
    }
    div.stButton > button:first-child {
        background-color: #00D1FF !important;
        color: black !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ৪. লগইন এবং সাইনআপ লজিক (নিখুঁতভাবে সাজানো) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # এখানে ট্যাব তৈরি করা হয়েছে
    choice = st.radio("Select Action:", ["Login", "Sign Up"], horizontal=True)
    
    if choice == "Login":
        st.subheader("🔐 Login")
        l_email = st.text_input("Email Address", key="unique_login_email")
        l_pass = st.text_input("Password", type="password", key="unique_login_pass")
        if st.button("Login Now"):
            users = load_users()
            if l_email in users:
                u_info = users[l_email]
                if u_info["password"] == l_pass:
                    if u_info["status"] == "approved":
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.warning("⚠️ Pending admin approval.")
                else:
                    st.error("❌ Wrong password.")
            else:
                st.error("❌ Email not found.")
        st.stop()

    else:
        st.subheader("📝 Request Access (Sign Up)")
        s_email = st.text_input("New Email", key="unique_signup_email")
        s_pass = st.text_input("New Password", type="password", key="unique_signup_pass")
        if st.button("Send Request"):
            if s_email and s_pass:
                save_user(s_email, s_pass)
                st.success("✅ Request sent! Contact admin for approval.")
            else:
                st.error("❌ Please fill all fields.")
        st.stop()

# --- ৫. মেইন অ্যাপ (লগইন হলে চলবে) ---
with st.sidebar:
    st.markdown("<h3 style='color:#00D1FF; text-align:center;'>SIGRAPHICEONE</h3>", unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    st.write("---")
    app_mode = st.radio("Mode Selection", ["Metadata", "Image to Prompt"])
    title_words = st.slider("Title limit", 10, 100, 40)
    keyword_count = st.slider("Tag limit", 10, 50, 40)

st.markdown('<p class="main-title">SIGRAPHICEONE METADATA GENERATOR</p>', unsafe_allow_html=True)

left, right = st.columns([1, 1.2], gap="medium")

with left:
    st.markdown("##### 📤 Upload Image")
    uploaded_file = st.file_uploader("", type=['jpg','png','jpeg'], label_visibility="collapsed")
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)
        generate_clicked = st.button("🚀 GENERATE NOW")

with right:
    if uploaded_file and generate_clicked:
        with st.spinner("AI is working..."):
            try:
                if app_mode == "Metadata":
                    prompt = f"Give me a Professional SEO Title (max {title_words} words) and {keyword_count} keywords. Separated by commas."
                    res = model.generate_content([prompt, img])
                    st.code(res.text, language="text")
                else:
                    res = model.generate_content(["Create a midjourney style prompt for this image.", img])
                    st.code(res.text.strip(), language="text")
            except:
                st.warning("⚠️ API Quota Full.")
