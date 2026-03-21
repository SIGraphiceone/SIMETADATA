import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- ১. কনফিগারেশন ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- ২. লেআউট ফিক্স করার জন্য হার্ডকোর CSS ---
st.set_page_config(page_title="SIGRAPHICEONE AI", layout="wide")

st.markdown("""
    <style>
    /* মেইন উইন্ডোর গ্যাপ জিরো করা */
    .block-container {
        padding-top: 1rem !important;
        max-width: 98% !important;
    }
    .stApp { background-color: #050A0F; }

    /* টাইটেল স্টাইল */
    .main-title {
        color: white;
        text-align: center;
        font-size: 30px !important;
        font-weight: 800;
        margin-bottom: 0px;
    }

    /* সাইডবার লক করা */
    [data-testid="stSidebar"] {
        background-color: #121F2B;
        border-right: 2px solid #00D1FF;
        min-width: 300px !important;
    }

    /* প্ল্যাটফর্ম বাটনগুলোকে কাছাকাছি আনা */
    div.stButton > button {
        background-color: #1E2D3D !important;
        color: white !important;
        border: 1px solid #3E4C59 !important;
        border-radius: 5px;
        height: 45px;
    }

    /* কন্টাক্ট বাটন ফিক্স */
    .contact-container {
        display: flex;
        justify-content: flex-end;
    }
    
    /* আউটপুট বক্স ডিজাইন */
    .result-card {
        background-color: #121F2B;
        border: 1px solid #3E4C59;
        border-radius: 10px;
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ৩. সাইডবার ---
with st.sidebar:
    st.markdown("<h2 style='color:#00D1FF; text-align:center;'>SIGRAPHICEONE</h2>", unsafe_allow_html=True)
    st.write("---")
    app_mode = st.radio("Mode Selection", ["Metadata", "Image to Prompt"])
    st.write("---")
    title_words = st.slider("Title word count", 10, 100, 41)
    keyword_count = st.slider("Tag keyword count", 10, 50, 40)

# --- ৪. হেডার ---
h_col1, h_col2 = st.columns([5, 1])
with h_col1:
    st.markdown('<p class="main-title">SIGRAPHICEONE METADATA GENERATOR</p>', unsafe_allow_html=True)
with h_col2:
    if st.button("CONTACT", type="primary", use_container_width=True):
        st.info("📞 Contact: +8801XXXXXXXXX")

# প্ল্যাটফর্ম বাটন (টাইট রো)
st.write("")
b1, b2, b3 = st.columns(3)
with b1: st.button("ADOBE STOCK")
with b2: st.button("FREEPIK")
with b3: st.button("SHUTTERSTOCK")

st.markdown("<hr style='border: 0.5px solid #1E2D3D; margin: 10px 0;'>", unsafe_allow_html=True)

# --- ৫. ওয়ার্কিং এরিয়া (গ্যাপ ফিক্সড) ---
left, right = st.columns([1, 1], gap="medium")

with left:
    st.markdown("### 📷 Upload Image")
    uploaded_file = st.file_uploader("", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)

with right:
    if uploaded_file:
        with st.spinner("Processing..."):
            try:
                if app_mode == "Metadata":
                    prompt = f"Professional SEO Title (max {title_words} words) and {keyword_count} keywords for this stock photo. No serial numbers."
                    response = model.generate_content([prompt, img])
                    
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.write("**📝 SEO Title:**")
                    st.code(response.text.split('\n')[0], language="text")
                    st.write("**🏷️ Keywords:**")
                    st.code(response.text, language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    prompt_gen = "Write a high-quality AI image generation prompt for this image."
                    response = model.generate_content([prompt_gen, img])
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.write("**🎨 AI Image Prompt:**")
                    st.code(response.text.strip(), language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("👈 Please upload an image to start.")
