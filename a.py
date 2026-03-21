import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- ১. কনফিগারেশন ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- ২. পারফেক্ট ডিজাইন (CSS) - যা আপনার গ্যাপ কমাবে ---
st.set_page_config(page_title="SIGRAPHICEONE AI", layout="wide")

st.markdown("""
    <style>
    /* পুরো পেজের গ্যাপ কমানো */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 98% !important;
    }
    
    .stApp { background-color: #050A0F; }

    /* টাইটেল এবং হেডার স্টাইল */
    .main-title {
        color: white;
        text-align: center;
        font-size: 32px !important;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }

    /* সাইডবার ডিজাইন */
    [data-testid="stSidebar"] {
        background-color: #121F2B;
        border-right: 2px solid #00D1FF;
        min-width: 300px !important;
    }

    /* বাটন এবং ইনপুট বক্স বড় করা */
    .stButton>button {
        width: 100%;
        background-color: #1E2D3D;
        color: white;
        border: 1px solid #3E4C59;
        height: 50px;
    }

    /* কন্টাক্ট বাটন লাল করা */
    div.stButton > button:first-child {
        background-color: #FF4B4B !important;
        border: none !important;
    }

    /* রেজাল্ট কার্ড - যা প্রিভিউয়ের মতো দেখাবে */
    .output-card {
        background-color: #121F2B;
        border: 1px solid #3E4C59;
        border-radius: 10px;
        padding: 20px;
        margin-top: 10px;
    }
    
    /* গ্যাপ কমানোর জন্য কলাম অ্যাডজাস্টমেন্ট */
    [data-testid="column"] {
        padding: 0px 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ৩. সাইডবার ---
with st.sidebar:
    st.markdown("<h2 style='color:#00D1FF; text-align:center;'>SIGRAPHICEONE</h2>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("### Mode Selection")
    app_mode = st.radio("", ["Metadata", "Image to Prompt"], label_visibility="collapsed")
    st.write("---")
    title_words = st.slider("Title word count", 10, 100, 41)
    keyword_count = st.slider("Tag keyword count", 10, 50, 40)

# --- ৪. মেইন বডি (Header & Buttons) ---
col_head, col_contact = st.columns([5, 1])
with col_head:
    st.markdown('<p class="main-title">SIGRAPHICEONE METADATA GENERATOR</p>', unsafe_allow_html=True)
with col_contact:
    if st.button("CONTACT"):
        st.toast("📞 Contact: +8801793410783")

# প্ল্যাটফর্ম বাটন
st.write("") 
c1, c2, c3 = st.columns(3)
with c1: st.button("ADOBE STOCK")
with c2: st.button("FREEPIK")
with c3: st.button("SHUTTERSTOCK")

st.markdown("<hr style='border: 0.5px solid #1E2D3D; margin: 10px 0;'>", unsafe_allow_html=True)

# --- ৫. মেইন কন্টেন্ট (গ্যাপ কমিয়ে সাজানো) ---
# কলামের রেশিও [1, 1] রাখলে গ্যাপ কমে আসবে
left_col, right_col = st.columns([1, 1], gap="small")

with left_col:
    st.markdown("### 📷 Upload Image")
    uploaded_file = st.file_uploader("", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)

with right_col:
    if uploaded_file:
        st.markdown('<div class="output-card">', unsafe_allow_html=True)
        if app_mode == "Metadata":
            st.markdown("### 📝 Generated Results")
            # টাইটেল ও কপি বাটন
            st.write("**SEO Title:**")
            st.code("Your Generated Title Will Appear Here", language="text")
            st.write("**Keywords:**")
            st.code("Key1, Key2, Key3, Key4...", language="text")
        else:
            st.markdown("### 🎨 AI Image Prompt")
            st.code("Your AI Image Prompt Will Appear Here", language="text")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("👈 Please upload an image to see the results.")
