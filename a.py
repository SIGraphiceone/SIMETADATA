import streamlit as st
from supabase import create_client, Client
import google.generativeai as genai
from PIL import Image

# --- ১. সুপাবেস কানেকশন ---
# নিশ্চিত করুন Streamlit Secrets-এ SUPABASE_URL এবং SUPABASE_KEY আছে
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def load_users():
    try:
        response = supabase.table("users").select("*").execute()
        users_dict = {}
        for user in response.data:
            users_dict[user['email']] = {"password": user['password'], "status": user['status']}
        return users_dict
    except:
        return {}

def save_user(email, password):
    data = {"email": email, "password": password, "status": "pending"}
    supabase.table("users").insert(data).execute()

# --- ২. কনফিগারেশন ---
st.set_page_config(page_title="SIGRAPHICEONE AI", layout="wide")

st.write(f"My API Key starts with: {st.secrets['GEMINI_API_KEY'][:10]}")

# জেমিনি এপিআই সেটআপ
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("❌ API Key missing in Secrets! Please check your GEMINI_API_KEY.")

# --- ৩. ডিজাইন (CSS) - গ্রে বাটন ফিক্স ---
st.markdown("""
    <style>
    .stAppViewMain { background-color: #050A0F !important; }
    .block-container { max-width: 90% !important; padding-top: 50px !important; }
    .main-title { color: white; text-align: center; font-size: 26px !important; font-weight: 800; }
    
    /* সব বাটনকে গ্রে কালার করা */
    div.stButton > button {
        background-color: #333333 !important; 
        color: white !important;
        border: 1px solid #444444 !important;
        border-radius: 5px;
        font-weight: bold;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #444444 !important;
        border-color: #00D1FF !important;
    }
    .result-card {
        background-color: #121F2B;
        border: 1px solid #3E4C59;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ৪. লগইন লজিক ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    choice = st.radio("Select Action:", ["Login", "Sign Up"], horizontal=True)
    if choice == "Login":
        l_email = st.text_input("Email Address", key="login_email")
        l_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login Now"):
            users = load_users()
            if l_email in users:
                if users[l_email]["password"] == l_pass:
                    if users[l_email]["status"] == "approved":
                        st.session_state.logged_in = True
                        st.rerun()
                    else: st.warning("⚠️ Pending admin approval.")
                else: st.error("❌ Wrong password.")
            else: st.error("❌ Email not found.")
        st.stop()
    else:
        s_email = st.text_input("New Email", key="signup_email")
        s_pass = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Request Access"):
            if s_email and s_pass:
                save_user(s_email, s_pass)
                st.success("✅ Request sent! Wait for approval.")
            else: st.error("❌ Fill all fields.")
        st.stop()

# --- ৫. মেইন অ্যাপ (লগইন হলে এটি দেখাবে) ---
with st.sidebar:
    st.markdown("<h3 style='color:#00D1FF; text-align:center;'>SIGRAPHICEONE</h3>", unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    app_mode = st.radio("Mode", ["Metadata", "Image to Prompt"])
    title_words = st.slider("Title limit", 10, 100, 40)
    keyword_count = st.slider("Tag limit", 10, 50, 40)

st.markdown('<p class="main-title">SIGRAPHICEONE METADATA GENERATOR</p>', unsafe_allow_html=True)

# প্ল্যাটফর্ম বাটন
p_cols = st.columns(3)
platforms = ["ADOBE STOCK", "FREEPIK", "SHUTTERSTOCK"]
for i, p in enumerate(platforms):
    with p_cols[i]: st.button(p, key=f"plat_{p}", use_container_width=True)

st.write("---")

left, right = st.columns([1, 1.2], gap="medium")

with left:
    st.markdown("##### 📤 Upload Image")
    uploaded_file = st.file_uploader("", type=['jpg','png','jpeg'], label_visibility="collapsed")
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)
        generate_clicked = st.button("🚀 GENERATE NOW")
with right:
    if uploaded_file and 'generate_clicked' in locals() and generate_clicked:
        with st.spinner("AI is working..."):
            try:
                prompt = f"Give me a Professional SEO Title (max {title_words} words) and {keyword_count} keywords. Separated by commas."
                if app_mode == "Image to Prompt":
                    prompt = "Create a midjourney style prompt for this image."
                
                res = model.generate_content([prompt, img])
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.write("**Results:**")
                st.code(res.text, language="text")
                st.markdown('</div>', unsafe_allow_html=True)
            except:
                st.warning("⚠️ API Quota Full or Error. Wait 30s.")
