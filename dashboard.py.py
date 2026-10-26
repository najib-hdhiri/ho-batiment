import streamlit as st
import calendar
from datetime import date
import os

st.set_page_config(
    page_title="H.O Bâtiment",
    page_icon="🏗️",
    layout="wide"
)

st.markdown("""
<style>
.brand-container {
    text-align: center;
    background: #fff;
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
    margin: 2px 0 0 0;
}
</style>
""", unsafe_allow_html=True)

os.makedirs("uploads", exist_ok=True)

logo_path = None
for p in ["uploads/logo_saved.jpg", "logo.jpg", "logo.png"]:
    if os.path.exists(p):
        logo_path = p
        break

st.sidebar.markdown('<div class="brand-container">', unsafe_allow_html=True)
if logo_path:
    st.sidebar.image(logo_path, width=110)
else:
    st.sidebar.markdown("<h1 style='text-align:center;margin:0;'>🏗️</h1>", unsafe_allow_html=True)

st.sidebar.markdown("<p class='brand-title'>H.O Bâtiment</p>", unsafe_allow_html=True)
st.sidebar.markdown("<p class='brand-subtitle'>Construction & Travaux Publics</p>", unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

noms_p = [
    "خليج الشعرة (Khalij Chaara)",
    "بوخروف (Boukharouf)"
]
projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", noms_p)

def ouv(spec, tel, tx, jt, js, pt, av):
    return {
        "specialite": spec, "tel": tel,
        "taux_jour": tx, "jours_total": jt,
        "jours_semaine": js, "paye_total": pt,
        "avances": av
    }

def art(obj, ft, fs, un):
    return {
        "objectif": obj, "fait_total": ft,
        "fait_semaine": fs, "unite": un
    }

db = {}

# المشروع 1
db[noms_p[0]] = {
    "date_debut": date(2026, 5, 18),
    "stats": {"vert": 65, "jaune": 44, "meteo": 8, "conge": 5},
    "jours": {
        "2026-05-18": ("vert", "انطلاق الشانطي ووضع البوردور T2"),
        "2026-05-19": ("jaune", "أرضية غير مهيئة"),
        "2026-05-26": ("meteo", "طقس خايب (أمطار وعواصف)"),
        "2026-05-29": ("conge", "يوم راحة عادي"),
        "2026-06-11": ("visite", "زيارة السيد المدير العام")
    },
    "ouvriers": {
        "بشير بن حميد": ouv("رئيس مجموعة / بناي", "99 888 777", 65, 50, 6, 2500, 400),
        "صالح بن عمار": ouv("بناي محترف", "98 123 456", 60, 65, 5, 3000, 500),
        "الهادي العياري": ouv("مانوفري", "22 345 678", 40, 40, 3, 1500, 300)
    },
    "articles": {
        "Bordure T2": art(1000, 650, 120, "ml"),
        "Bordure Mince P2": art(800, 400, 80, "ml"),
        "Caniveau CS2": art(500, 250, 40, "ml"),
        "Caniveau CC2": art(300, 150, 30, "ml"),
        "Pavé autobloquant": art(600, 200, 50, "م²")
    }
}

# المشروع 2
db[noms_p[1]] = {
    "date_debut": date(2026, 6, 1),
    "stats": {"vert": 30, "jaune": 10, "meteo": 4, "conge": 3},
    "jours": {
        "2026-06-01": ("vert", "دخول الآلات وبداية التهيئة"),
        "2026-06-02": ("meteo", "رياح قوية وأمطار")
    },
    "ouvriers": {
        "بشير بن حميد": ouv("رئيس الفريق", "99 888 777", 70, 30, 6, 1500, 200),
        "جمعة المجبري": ouv("رئيس الفريق", "55 789 012", 70, 30, 6, 1500, 200),
        "علي الطرابلسي": ouv("بناي", "24 567 890", 60, 25, 4, 1000, 100)
    },
    "articles": {
        "Double Cloison 0.35m": art(500, 250, 50, "م²"),
        "Cloison 0.25m": art(400, 200, 40, "م²"),
        "Enduit extérieur": art(1
