import streamlit as st
from supabase import create_client, Client # এটি ঠিক করা হয়েছে
import google.generativeai as genai
from PIL import Image

# --- ১. এপিআই ও মডেল কনফিগারেশন ---
# আপনার CMD রেজাল্ট অনুযায়ী সরাসরি লেটেস্ট মডেলটি ব্যবহার করছি
MODEL_NAME = 'gemini-3-pro-image-preview' 

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config={"temperature": 0.7, "top_p": 0.95, "top_k": 40}
    )
else:
    st.error("❌ API Key missing in Streamlit Secrets!")

# --- ২. সুপাবেস কানেকশন ---
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
    except: return {}

def save_user(email, password):
    data = {"email": email, "password": password, "status": "pending"}
    supabase.table("users").insert(data).execute()

# --- ৩. কনফিগারেশন ও ডিজাইন (CSS) ---
st.set_page_config(page_title="SIGRAPHICEONE AI", layout="wide")

st.markdown("""
    <style>
    .stAppViewMain { background-color: #050A0F !important; }
    .main-title { color: white; text-align: center; font-size: 26px !important; font-weight: 800; margin-bottom: 20px; }
    
    /* বাটনগুলোর গ্যাপ কমানো এবং মাঝখানে আনা */
    [data-testid="column"] { 
        display: flex; 
        justify-content: center; 
        width: fit-content !important; 
        flex: unset !important; 
    }
    [data-testid="stHorizontalBlock"] { gap: 8px !important; justify-content: center; }

    div.stButton > button {
        background-color: #333333 !important; 
        color: white !important;
        border: 1px solid #444444 !important;
        padding: 8px 12px;
        font-weight: bold;
        border-radius: 5px;
    }
    div.stButton > button:hover { border-color: #00D1FF !important; color: #00D1FF !important; }
    .result-card { background-color: #121F2B; border: 1px solid #3E4C59; border-radius: 10px; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- ৪. লগইন লজিক ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    choice = st.radio("Select Action:", ["Login", "Sign Up"], horizontal=True)
    if choice == "Login":
        l_email = st.text_input("Email Address")
        l_pass = st.text_input("Password", type="password")
        if st.button("Login Now"):
            users = load_users()
            if l_email in users and users[l_email]["password"] == l_pass:
                if users[l_email]["status"] == "approved":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.warning("⚠️ Pending admin approval.")
            else: st.error("❌ Invalid Credentials.")
        st.stop()
    else:
        s_email = st.text_input("New Email")
        s_pass = st.text_input("New Password", type="password")
        if st.button("Request Access"):
            if s_email and s_pass:
                save_user(s_email, s_pass)
                st.success("✅ Request sent! Wait for approval.")
            else: st.error("❌ Fill all fields.")
        st.stop()

# --- ৫. মেইন অ্যাপ ---
with st.sidebar:
    st.markdown("<h3 style='color:#00D1FF; text-align:center;'>SIGRAPHICEONE</h3>", unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    app_mode = st.radio("Mode", ["Metadata", "Image to Prompt"])
    title_words = st.slider("Title limit", 10, 100, 40)
    keyword_count = st.slider("Tag limit", 10, 50, 40)

st.markdown('<p class="main-title">SIGRAPHICEONE METADATA GENERATOR</p>', unsafe_allow_html=True)

# প্ল্যাটফর্ম বাটন - নতুন কলাম সেটআপ
c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1]) # বেশি কলাম নিয়ে বাটনগুলো ছোট রাখা হয়েছে
with c2: st.button("ADOBE STOCK", use_container_width=True)
with c3: st.button("FREEPIK", use_container_width=True)
with c4: st.button("SHUTTERSTOCK", use_container_width=True)

st.write("---")

left, right = st.columns([1, 1.2], gap="medium")

with left:
    st.markdown("##### 📤 Upload Image")
    uploaded_file = st.file_uploader("", type=['jpg','png','jpeg'], label_visibility="collapsed")
    if uploaded_file:
        raw_img = Image.open(uploaded_file)
        if raw_img.width > 1000:
            raw_img.thumbnail((1000, 1000))
        st.image(raw_img, use_container_width=True)
        generate_clicked = st.button("🚀 GENERATE NOW")

with right:
    if uploaded_file and 'generate_clicked' in locals() and generate_clicked:
        with st.spinner("AI is working..."):
            try:
                if app_mode == "Image to Prompt":
                    full_prompt = "Create a detailed midjourney style prompt for this image."
                else:
                    full_prompt = f"Give me a Professional SEO Title (max {title_words} words) and exactly {keyword_count} keywords separated by commas for this image."
                
                response = model.generate_content([full_prompt, raw_img])
                
                if response.text:
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.write("**Results:**")
                    st.code(response.text, language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("AI couldn't generate text. Try another image.")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
