import streamlit as st
import calendar
from datetime import date
import os

st.set_page_config(page_title="H.O Construction - Tableau de Bord", page_icon="🏗️", layout="wide")

# ==========================================
# تصميم CSS فخم ومنظم للملفات واللوغو
# ==========================================
st.markdown("""
    <style>
    .brand-container {
        text-align: center;
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    .brand-title {
        color: #ff4b4b;
        font-size: 20px;
        font-weight: bold;
        margin: 5px 0 0 0;
    }
    .brand-subtitle {
        color: gray;
        font-size: 12px;
        margin-top: 2px;
        margin-bottom: 0;
    }
    .img-box {
        border-radius: 10px;
        border: 2px solid #ddd;
        padding: 5px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# التأكد من وجود مجلد uploads لحفظ الصور
os.makedirs("uploads", exist_ok=True)

# جلب اللوغو من المجلد مباشرة
logo_path = None
if os.path.exists("uploads/logo_saved.jpg"):
    logo_path = "uploads/logo_saved.jpg"
elif os.path.exists("logo.jpg"):
    logo_path = "logo.jpg"
elif os.path.exists("logo.png"):
    logo_path = "logo.png"

st.sidebar.markdown('<div class="brand-container">', unsafe_allow
