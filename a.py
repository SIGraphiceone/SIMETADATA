import streamlit as st
import json
import os
import google.generativeai as genai
from PIL import Image

# --- ১. ইউজার ডাটা ফাংশন (Database) ---
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
    # নতুন ইউজার ডিফল্টভাবে 'pending' থাকবে
    users[email] = {"password": password, "status": "pending"} 
    with open(USER_DATA_FILE, "w", encoding='utf-8') as f:
        json.dump(users, f, indent=4)

# --- ২. পেজ সেটআপ ও কনফিগারেশন ---
st.set_page_config(page_title="SIGRAPHICEONE AI", layout="wide")

# API কনফিগারেশন (Secrets থেকে কী নেবে)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("API Key not found in Streamlit Secrets!")

# --- ৩. ডিজাইন ফিক্স (CSS) ---
st.markdown("""
    <style>
    /* ব্যাকগ্রাউন্ড ও কন্টেইনার ফিক্স */
    .stAppViewMain { background-color: #050A0F !important; }
    .block-container {
        max-width: 90% !important;
        padding-top: 150px !important; /* ইন্টারফেস নিচে নামানোর জন্য */
        background: transparent !important;
    }

    /* টাইটেল স্টাইল */
    .main-title {
        color: white;
        text-align: center;
        font-size: 26px !important;
        font-weight: 800;
        margin-bottom: 15px !important;
    }

    /* বাটন ডিজাইন */
    div.stButton > button {
        border-radius: 5px;
        font-weight: bold;
    }
    
    /* জেনারেট বাটন কালার */
    .stButton > button:first-child {
        background-color: #00D1FF !important;
        color: black !important;
        width: 100% !important;
    }

    /* রেজাল্ট বক্স */
    .result-card {
        background-color: #121F2B;
        border: 1px solid #3E4C59;
        border-radius: 10px;
        padding: 20px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ৪. লগইন এবং সাইনআপ লজিক (Admin Approval) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.subheader("Login to your account")
        l_email = st.text_input("Email", key="l_email")
        l_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Login"):
            users = load_users()
            if l_email in users:
                u_info = users[l_email]
                if u_info["password"] == l_pass:
                    if u_info["status"] == "approved":
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.warning("⚠️ Your account is pending admin approval.")
                else:
                    st.error("❌ Invalid password.")
            else:
                st.error("❌ Email not found.")
        st.stop() # লগইন না করলে নিচের কোডগুলো চলবে না

    with tab2:
        st.subheader("Register for Access")
        s_email = st.text_input("New Email", key="s_email")
        s_pass = st.text_input("New Password", type="password", key="s_pass")
        if st.button("Request Access"):
            if s_email and s_pass:
                save_user(s_email, s_pass)
                st.success("✅ Request sent! Please wait for Admin Approval.")
            else:
                st.error("❌ Please fill all fields.")
        st.stop()

# --- ৫. মেইন অ্যাপ (লগইন সফল হলে এই অংশটি চলবে) ---
with st.sidebar:
    st.markdown("<h3 style='color:#00D1FF; text-align:center;'>SIGRAPHICEONE</h3>", unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    st.write("---")
    app_mode = st.radio("Mode Selection", ["Metadata", "Image to Prompt"])
    st.write("---")
    title_words = st.slider("Title limit", 10, 100, 40)
    keyword_count = st.slider("Tag limit", 10, 50, 40)

# হেডার ও টাইটেল
t_col, c_col = st.columns([5, 1])
with t_col:
    st.markdown('<p class="main-title">SIGRAPHICEONE METADATA GENERATOR</p>', unsafe_allow_html=True)
with c_col:
    if st.button("CONTACT", type="primary", use_container_width=True):
        st.toast("📞 Contact: +8801XXXXXXXXX")

# প্ল্যাটফর্ম বাটন
p_cols = st.columns(3)
platforms = ["ADOBE STOCK", "FREEPIK", "SHUTTERSTOCK"]
for i, p in enumerate(platforms):
    with p_cols[i]: st.button(p, key=f"btn_{p}", use_container_width=True)

st.write("---")

# ওয়ার্ক এরিয়া
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
                    
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.write("**📝 SEO Title:**")
                    st.code(res.text.split('\n')[0], language="text")
                    st.write("**🏷️ Tag Keywords:**")
                    st.code(res.text, language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    res = model.generate_content(["Create a midjourney style prompt for this image.", img])
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.write("**🎨 AI Image Prompt:**")
                    st.code(res.text.strip(), language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.warning("⚠️ API Quota Full or Error. Please wait 30 seconds.")
    elif uploaded_file:
        st.info("Click the 'GENERATE NOW' button to see results.")
    else:
        st.info("Upload an image to get started.")
