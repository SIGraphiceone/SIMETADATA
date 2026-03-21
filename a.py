import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- ১. কনফিগারেশন (Gemini 2.5 Flash) ---
# নিশ্চিত করুন যে আপনার Streamlit Cloud Secrets-এ GEMINI_API_KEY সেভ করা আছে
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# আপনার রিকোয়েস্ট অনুযায়ী gemini-2.5-flash মডেল সেট করা হয়েছে
model = genai.GenerativeModel('gemini-2.5-flash')

# --- ২. পেজ সেটআপ এবং ডিজাইন (CSS) ---
st.set_page_config(page_title="SIGRAPHICEONE METADATA AI", layout="wide")

st.markdown("""
    <style>
    /* মেইন কন্টেইনার এবং ব্যাকগ্রাউন্ড */
    .block-container { padding-top: 1.5rem; max-width: 95% !important; }
    .stApp { background-color: #050A0F; color: white; }
    
    /* সাইডবার স্টাইল */
    [data-testid="stSidebar"] {
        background-color: #121F2B;
        border-right: 2px solid #00D1FF;
        width: 320px !important;
    }

    /* টাইটেল এবং বাটন */
    .main-title {
        color: white;
        text-align: center;
        font-size: 38px !important;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 0px;
    }
    
    .stButton>button {
        width: 100%;
        background-color: #1E2D3D;
        color: white;
        border: 1px solid #3E4C59;
        border-radius: 8px;
        padding: 12px;
        font-weight: bold;
    }
    
    /* কন্টাক্ট বাটন */
    div.stButton > button:first-child[kind="primary"] {
        background-color: #FF4B4B;
        border: none;
        width: 140px;
    }

    /* আউটপুট কার্ড ডিজাইন */
    .output-card {
        background-color: #121F2B;
        border: 1px solid #3E4C59;
        border-radius: 15px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ৩. সাইডবার লজিক (Mode Selection) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00D1FF; text-align:center;'>SIGRAPHICEONE</h2>", unsafe_allow_html=True)
    st.write("---")
    
    st.markdown("### 🛠️ Mode Selection")
    # ইউজার Metadata অথবা Image to Prompt সিলেক্ট করতে পারবেন
    app_mode = st.radio("", ["Metadata", "Image to Prompt"], label_visibility="collapsed")
    
    st.write("---")
    # স্লাইডার কন্ট্রোল
    title_words = st.slider("Title word count", 10, 100, 20)
    keyword_count = st.slider("Tag keyword count", 10, 50, 40)

# --- ৪. হেডার এবং কন্টাক্ট ---
col_title, col_contact = st.columns([5, 1])
with col_title:
    st.markdown('<p class="main-title">SIGRAPHICEONE METADATA GENERATOR</p>', unsafe_allow_html=True)
with col_contact:
    if st.button("CONTACT", type="primary"):
        st.toast("📞 Contact me at: +8801XXXXXXXXX") # আপনার ফোন নম্বর এখানে দিন

# --- ৫. প্ল্যাটফর্ম সিলেকশন বাটন ---
st.write("")
p1, p2, p3 = st.columns(3)
platform = "Adobe Stock"
with p1: 
    if st.button("ADOBE STOCK"): platform = "Adobe Stock"
with p2: 
    if st.button("FREEPIK"): platform = "Freepik"
with p3: 
    if st.button("SHUTTERSTOCK"): platform = "Shutterstock"

st.markdown("<hr style='border: 0.5px solid #1E2D3D; margin: 20px 0;'>", unsafe_allow_html=True)

# --- ৬. মেইন ওয়ার্ক এরিয়া (Upload & Results) ---
left_col, right_col = st.columns([1.3, 1], gap="large")

with left_col:
    st.markdown("### 📤 Upload Image")
    uploaded_file = st.file_uploader("Choose Files (JPG, PNG, JPEG)", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Preview", use_container_width=True)

with right_col:
    if uploaded_file:
        st.markdown('<div class="output-card">', unsafe_allow_html=True)
        st.markdown(f"### ✨ {app_mode} Result")
        
        with st.spinner("AI is thinking..."):
            try:
                if app_mode == "Metadata":
                    # মেটাডেটা প্রম্পট
                    meta_prompt = f"As a {platform} expert, give me a professional SEO Title (max {title_words} words) and exactly {keyword_count} relevant Keywords for this photo. Format: Just the Title, then the Keywords separated by commas. No serial numbers."
                    response = model.generate_content([meta_prompt, img])
                    
                    # রেজাল্ট আলাদা করা (টাইটেল এবং ট্যাগ)
                    full_text = response.text
                    st.write("**📝 Generated Title:**")
                    st.code(full_text.split("\n")[0].replace("Title:", "").strip(), language="text")
                    
                    st.write("**🏷️ Keywords (Comma Separated):**")
                    # ট্যাগগুলো এক লাইনে কমা দিয়ে দেখানো
                    keywords = full_text.replace(full_text.split("\n")[0], "").replace("Keywords:", "").strip()
                    st.code(keywords, language="text")
                
                else:
                    # Image to Prompt মোড
                    prompt_gen = "Analyze this image and write a detailed AI generation prompt to recreate this image with midjourney or dall-e style. Include lighting and mood."
                    response = model.generate_content([prompt_gen, img])
                    
                    st.write("**🎨 AI Image Prompt:**")
                    st.code(response.text.strip(), language="text")
            
            except Exception as e:
                st.error(f"Something went wrong: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👈 Please upload an image to generate metadata or prompt.")
