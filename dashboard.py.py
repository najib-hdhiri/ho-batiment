import streamlit as st
import calendar
from datetime import date
import os

st.set_page_config(
    page_title="H.O Construction - Tableau de Bord",
    page_icon="🏗️",
    layout="wide"
)

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

st.sidebar.markdown(
    '<div class="brand-container">',
    unsafe_allow_html=True
)

if logo_path:
    st.sidebar.image(logo_path, width=110)
else:
    st.sidebar.markdown(
        "<h1 style='text-align: center; margin:0;'>🏗️</h1>",
        unsafe_allow_html=True
    )

st.sidebar.markdown(
    "<p class='brand-title'>H.O Bâtiment</p>",
    unsafe_allow_html=True
)
st.sidebar.markdown(
    "<p class='brand-subtitle'>Construction & Travaux Publics</p>",
    unsafe_allow_html=True
)
st.sidebar.markdown('</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", [
    "خليج الشعرة (Khalij Chaara)", 
    "بوخروف (Boukharouf)"
])

base_donnees_projets = {
    "خليج الشعرة (Khalij Chaara)": {
        "date_debut": date(2026, 5, 18),
        "stats": {"vert": 65, "jaune": 44, "gris": 12, "meteo": 8, "conge": 5},
        "jours": {
            "2026-05-18": {"etat": "vert", "details": {"travail": "انطلاق الشانطي ووضع البوردور T2"}},
            "2026-05-19": {"etat": "jaune", "details": {"probleme": "أرضية غير مهيئة"}},
            "2026-05-26": {"etat": "meteo", "details": {"probleme": "طقس خايب (أمطار وعواصف)"}},
            "2026-05-29": {"etat": "conge", "details": {"travail": "يوم راحة عادي"}},
            "2026-06-11": {"etat": "visite", "details": {"travail": "زيارة السيد المدير العام"}},
        },
        "ouvriers": {
            "بشير بن حميد": {
                "specialite": "رئيس مجموعة / بناي",
                "tel": "99 888 777",
                "taux_jour": 65,
                "jours_total": 50,
                "jours_semaine": 6,
                "paye_total": 2500,
                "avances": 400,
            },
            "صالح بن عمار": {
