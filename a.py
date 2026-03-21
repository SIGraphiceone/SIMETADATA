import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- ১. কনফিগারেশন ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- ২. মেইন কন্টেইনার বাদ দেওয়া এবং লেআউট ফিক্স করার CSS ---
st.set_page_config(page_title="SIGRAPHICEONE AI", layout="wide")

st.markdown("""
    <style>
    /* ১. মেইন সাদা কন্টেইনার/বক্স বাদ দেওয়া */
    .stAppViewMain {
        background-color: #050A0F !important; /* পুরো ব্যাকগ্রাউন্ড ডার্ক */
    }
    
    .block-container {
        max-width: 98% !important;
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        background: transparent !important; /* মেইন বক্স ইনভিজিবল করা হলো */
    }

    /* ২. হেডার ও টাইটেল পজিশন ফিক্স */
    .main-title {
        color: white;
        text-align: center;
        font-size: 28px !important;
        font-weight: 800;
        letter-spacing: 2px;
        margin: 10px 0px !important;
    }

    /* ৩. কন্টাক্ট বাটন ডিজাইন */
    div.stButton > button:first-child[kind="primary"] {
        background-color: #FF4B4B !important;
        border: none !important;
        color: white !important;
        border-radius: 5px;
        height: 40px !important;
    }

    /* ৪. আউটপুট বক্স (টাইটেল, ট্যাগ ও প্রম্পট) আনহাইড করা */
    .result-box {
        background-color: #121F2B;
        border: 1px solid #3E4C59;
        border-radius: 10px;
        padding: 20px;
        margin-top: 10px;
    }

    /* সাইডবার সেটিংস */
    [data-testid="stSidebar"] {
        background-color: #121F2B;
        border-right: 1px solid #00D1FF;
    }
    
    .stCodeBlock { border: 1px solid #3E4C59 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ৩. সাইডবার (মোড সিলেকশন) ---
with st.sidebar:
    st.markdown("<h3 style='color:#00D1FF; text-align:center;'>SIGRAPHICEONE</h3>", unsafe_allow_html=True)
    st.write("---")
    # মোড সিলেকশন
    app_mode = st.radio("Mode Selection", ["Metadata", "Image to Prompt"])
    st.write("---")
    title_words = st.slider("Title limit", 10, 100, 40)
    keyword_count = st.slider("Tag limit", 10, 50, 40)

# --- ৪. হেডার ও কন্টাক্ট (সাদা বক্স ছাড়াই দেখা যাবে) ---
col_t, col_c = st.columns([5, 1])
with col_t:
    st.markdown('<p class="main-title">SIGRAPHICEONE METADATA GENERATOR</p>', unsafe_allow_html=True)
with col_c:
    if st.button("CONTACT", type="primary", use_container_width=True):
        st.toast("📞 Contact: +8801XXXXXXXXX")

# প্ল্যাটফর্ম বাটন
p1, p2, p3 = st.columns(3)
with p1: st.button("ADOBE STOCK")
with p2: st.button("FREEPIK")
with p3: st.button("SHUTTERSTOCK")

st.markdown("<hr style='border: 0.1px solid #1E2D3D; margin: 15px 0;'>", unsafe_allow_html=True)

# --- ৫. মেইন ওয়ার্ক এরিয়া ---
left, right = st.columns([1, 1.2], gap="medium")

with left:
    st.markdown("##### 📤 Upload Image")
    uploaded_file = st.file_uploader("", type=['jpg','png','jpeg'], label_visibility="collapsed")
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)

with right:
    if uploaded_file:
        with st.spinner("AI Generating..."):
            try:
                if app_mode == "Metadata":
                    # মেটাডেটা বক্স (টাইটেল ও কি-ওয়ার্ড আলাদা)
                    prompt = f"Professional SEO Title (max {title_words} words) and {keyword_count} keywords. Separated by commas."
                    res = model.generate_content([prompt, img])
                    
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.write("**📝 SEO Title:**")
                    st.code(res.text.split('\n')[0], language="text") # কপি বাটনসহ
                    
                    st.write("**🏷️ Tag Keywords:**")
                    st.code(res.text, language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                else:
                    # প্রম্পট জেনারেশন বক্স
                    res = model.generate_content(["Describe this image for AI prompt generation.", img])
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.write("**🎨 AI Image Prompt:**")
                    st.code(res.text.strip(), language="text") # আলাদা বক্স ফিরে এসেছে
                    st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                # ১ নম্বর সমস্যার সমাধান: কোটা এরর হ্যান্ডলিং
                st.warning("⚠️ Quota full or API Busy. Please wait 30 seconds and try again.")
    else:
        st.info("Please upload an image to see the generated boxes.")
