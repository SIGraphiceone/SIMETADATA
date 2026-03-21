import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- ১. কনফিগারেশন ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- ২. মেইন কন্টেইনার বাদ দেওয়া এবং ডিজাইন ফিক্স (CSS) ---
st.set_page_config(page_title="SIGRAPHICEONE AI", layout="wide")

st.markdown("""
    <style>
    /* মেইন সাদা বক্স/কন্টেইনার বাদ দেওয়া */
    .stAppViewMain { background-color: #050A0F !important; }
    .block-container {
        max-width: 70% !important;
        padding-top: 1rem !important;
        background: transparent !important;
    }

    /* টাইটেল এবং কন্টাক্ট বাটন পজিশন */
    .main-title {
        color: white;
        text-align: center;
        font-size: 26px !important;
        font-weight: 800;
        margin-bottom: 15px !important;
    }

    /* বাটন ডিজাইন (জেনারেট ও কন্টাক্ট) */
    div.stButton > button {
        border-radius: 5px;
        font-weight: bold;
    }
    
    /* জেনারেট বাটনকে হাইলাইট করা */
    .gen-btn > div > button {
        background-color: #00D1FF !important;
        color: black !important;
        width: 100% !important;
        height: 50px !important;
    }

    /* রেজাল্ট বক্স আনহাইড করা */
    .result-card {
        background-color: #121F2B;
        border: 1px solid #3E4C59;
        border-radius: 10px;
        padding: 20px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ৩. সাইডবার ---
with st.sidebar:
    st.markdown("<h3 style='color:#00D1FF; text-align:center;'>SIGRAPHICEONE</h3>", unsafe_allow_html=True)
    app_mode = st.radio("Mode Selection", ["Metadata", "Image to Prompt"])
    st.write("---")
    title_words = st.slider("Title limit", 10, 100, 40)
    keyword_count = st.slider("Tag limit", 10, 50, 40)

# --- ৪. হেডার ---
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
    with p_cols[i]: st.button(p, use_container_width=True)

st.write("---")

# --- ৫. মেইন ওয়ার্ক এরিয়া ---
left, right = st.columns([1, 1.2], gap="medium")

with left:
    st.markdown("##### 📤 Upload Image")
    uploaded_file = st.file_uploader("", type=['jpg','png','jpeg'], label_visibility="collapsed")
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)
        
        # জেনারেট বাটন (যা আপনি চেয়েছিলেন)
        st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
        generate_clicked = st.button("🚀 GENERATE NOW")
        st.markdown('</div>', unsafe_allow_html=True)

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
                # কোটা এরর মেসেজ
                st.warning("⚠️ API Quota Full. Please wait 30 seconds.")
    elif uploaded_file:
        st.info("Click the 'GENERATE NOW' button to see results.")
    else:
        st.info("Upload an image to get started.")
