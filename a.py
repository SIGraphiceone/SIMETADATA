import streamlit as st
import google.generativeai as genai
from PIL import Image
from supabase import create_client, Client

# --- ১. আপনার কনফিগারেশন (একদম সঠিক তথ্য বসানো হয়েছে) ---
SUPABASE_URL = "https://scsjaefaoyjivdxovuqz.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SERVICE_ROLE_KEY = st.secrets["SERVICE_ROLE_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# কানেকশন সেটআপ
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
admin_supabase: Client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Stock Metadata AI - Pro", layout="wide")

# সেশন স্টেট (লগইন মনে রাখার জন্য)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ২. অ্যাডমিন কন্ট্রোল প্যানেল ---
if st.query_params.get("admin") == "true":
    st.title("👨‍✈️ Admin Approval Dashboard")
    users = admin_supabase.table("users_list").select("*").execute()
    if users.data:
        for user in users.data:
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.write(user['email'])
            col2.write(f"Status: {user['status']}")
            if user['status'] == 'pending':
                if col3.button("Approve", key=user['email']):
                    admin_supabase.table("users_list").update({"status": "approved"}).eq("email", user['email']).execute()
                    st.rerun()
    st.stop()

# --- ৩. লগইন ও সাইন-আপ সিস্টেম ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab2:
        st.subheader("নতুন অ্যাকাউন্ট খুলুন")
        reg_email = st.text_input("Email", key="r_email").strip()
        reg_pass = st.text_input("Password", type="password", key="r_pass")
        if st.button("Register"):
            try:
                admin_supabase.table("users_list").insert({"email": reg_email, "password": str(reg_pass), "status": "pending"}).execute()
                st.success("রেজিস্ট্রেশন হয়েছে! এবার ?admin=true দিয়ে নিজেকে Approve করুন।")
            except: st.error("এই ইমেইল দিয়ে আগেই অ্যাকাউন্ট খোলা হয়েছে।")

    with tab1:
        st.subheader("লগইন করুন")
        login_email = st.text_input("Email", key="l_email").strip()
        login_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Login"):
            res = admin_supabase.table("users_list").select("*").eq("email", login_email).execute()
            if res.data and str(res.data[0]['password']) == str(login_pass):
                if res.data[0]['status'] == 'approved':
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.warning("আপনার অ্যাকাউন্ট এখনও Pending!")
            else: st.error("ভুল ইমেইল বা পাসওয়ার্ড!")

# --- ৪. আসল অ্যাপ (লগইন করার পর যা দেখা যাবে) ---
else:
    # সাইডবারে লগআউট বাটন
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🚀 AI Metadata Generator")
    
    # ইনপুট অপশন
    platform = st.radio("Select Platform:", ["Adobe Stock", "Freepik", "Shutterstock"], horizontal=True)
    files = st.file_uploader("Upload Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    if files:
        if st.button("Generate Now"):
            for f in files:
                img = Image.open(f)
                st.image(img, width=300, caption=f.name)
                
                with st.spinner(f"Generating for {f.name}..."):
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content([f"As a {platform} expert, give me a professional SEO Title and 40 relevant Keywords for this stock photo.", img])
                    
                    st.subheader(f"Results for {f.name}")
                    st.code(response.text)
                    st.divider()
