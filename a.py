import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- ১. কনফিগারেশন ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- ২. সাইজ ছোট করার জন্য কাস্টম CSS ---
st.set_page_config(page_title="SIGRAPHICEONE AI", layout="wide")

st.markdown("""
    <style>
    /* পেজের উপরের গ্যাপ একদম জিরো করা */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        max-width: 98% !important;
    }
    
    .stApp { background-color: #050A0F; }

    /* মেইন টাইটেল আরও ছোট করা হয়েছে */
    .main-title {
        color: white;
        text-align: center;
        font-size: 20px !important;
        font-weight: 700;
        margin: 0px !important;
        padding: 5px 0px !important;
    }

    /* সাইডবার উইডথ কমানো হয়েছে */
    [data-testid="stSidebar"] {
        min-width: 260px !important;
        max-width: 260px !important;
        background-color: #121F2B;
    }

    /* বাটনগুলো স্লিম করা হয়েছে */
    .stButton>button {
        background-color: #1E2D3D !important;
        color: white !important;
        height: 32px !important;
        font-size: 12px !important;
        padding: 0px !important;
    }

    /* আপলোড বক্স ছোট করা */
    .stFileUploader section {
        padding: 0px !important;
    }
    
    /* রেজাল্ট কার্ড কমপ্যাক্ট করা */
    .result-card {
        background-color: #121F2B;
        border: 1px solid #3E4C59;
        border-radius: 5px;
        padding: 10px;
        font-size: 13px !important;
    }
    
    /* কন্টাক্ট বাটন ছোট করা */
    div.stButton > button:first-child[kind="primary"] {
        background-color: #FF4B4B !important;
        height: 30px !important;
        width: 100px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ৩. সাইডবার ---
with st.sidebar:
    st.markdown("<h4 style='color:#00D1FF; text-align:center; margin:0;'>SIGRAPHICEONE</h4>", unsafe_allow_html=True)
    app_mode = st.radio("Mode Selection", ["Metadata", "Image to Prompt"])
    st.write("---")
    title_words = st.slider("Title limit", 10, 100, 40)
    keyword_count = st.slider("Tag limit", 10, 50, 40)

# --- ৪. টাইটেল ও কন্টাক্ট রো ---
t_col, c_col = st.columns([6, 1])
with t_col:
    st.markdown('<p class="main-title">SIGRAPHICEONE METADATA GENERATOR</p>', unsafe_allow_html=True)
with c_col:
    if st.button("CONTACT", type="primary"):
        st.toast("📞 +8801XXXXXXXXX")

# প্ল্যাটফর্ম বাটন (টাইট স্পেস)
p_col1, p_col2, p_col3 = st.columns(3)
with p_col1: st.button("ADOBE STOCK")
with p_col2: st.button("FREEPIK")
with p_col3: st.button("SHUTTERSTOCK")

st.markdown("<hr style='margin: 5px 0; border: 0.1px solid #1E2D3D;'>", unsafe_allow_html=True)

# --- ৫. ওয়ার্কিং এরিয়া (স্লিম লুক) ---
l_col, r_col = st.columns([1, 1.2], gap="small")

with l_col:
    st.write("**📤 Upload**")
    uploaded_file = st.file_uploader("", type=['jpg','png','jpeg'], label_visibility="collapsed")
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)

with r_col:
    if uploaded_file:
        with st.spinner("Wait..."):
            try:
                if app_mode == "Metadata":
                    p = f"SEO Title (max {title_words} words) and {keyword_count} keywords. Comma separated."
                    res = model.generate_content([p, img])
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.write("**Title:**")
                    st.code(res.text.split('\n')[0], language="text")
                    st.write("**Tags:**")
                    st.code(res.text, language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    res = model.generate_content(["Detailed AI prompt for this image.", img])
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.write("**AI Prompt:**")
                    st.code(res.text.strip(), language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error("Limit exceeded or error.")
    else:
        st.info("Upload image to see results.")
