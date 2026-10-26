import streamlit as st
import calendar
from datetime import date
import os

st.set_page_config(page_title="H.O Construction", page_icon="🏗️", layout="wide")

css_style = """
<style>
.brand-container { text-align: center; background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 20px; }
.brand-title { color: #ff4b4b; font-size: 20px; font-weight: bold; margin: 5px 0 0 0; }
.brand-subtitle { color: gray; font-size: 12px; margin-top: 2px; margin-bottom: 0; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

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
    st.sidebar.markdown("<h1 style='text-align: center; margin:0;'>🏗️</h1>", unsafe_allow_html=True)

st.sidebar.markdown("<p class='brand-title'>H.O Bâtiment</p>", unsafe_allow_html=True)
st.sidebar.markdown("<p class='brand-subtitle'>Construction & Travaux Publics</p>", unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

projets_noms = ["خليج الشعرة (Khalij Chaara)", "بوخروف (Boukharouf)"]
projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", projets_noms)

# بناء قاعدة البيانات بطريقة محمية ضد أخطاء النسخ في الهاتف
base_donnees_projets = {}

# --- المشروع الأول ---
p1_jours = {
    "2026-05-18": dict(etat="vert", travail="انطلاق الشانطي ووضع البوردور T2", probleme=""),
    "2026-05-19": dict(etat="jaune", travail="", probleme="أرضية غير مهيئة"),
    "2026-05-26": dict(etat="meteo", travail="", probleme="طقس خايب (أمطار وعواصف)"),
    "2026-05-29": dict(etat="conge", travail="يوم راحة عادي", probleme=""),
    "2026-06-11": dict(etat="visite", travail="زيارة السيد المدير العام", probleme="")
}

p1_ouvriers = {}
p1_ouvriers["بشير بن حميد"] = dict(specialite="رئيس مجموعة / بناي", tel="99 888 777", taux_jour=65, jours_total=50, jours_semaine=6, paye_total=2500, avances=400)
p1_ouvriers["صالح بن عمار"] = dict(specialite="بناي محترف", tel="98 123 456", taux_jour=60, jours_total=65, jours_semaine=5, paye_total=3000, avances=500)
p1_ouvriers["الهادي العياري"] = dict(specialite="مانوفري", tel="22 345 678", taux_jour=40, jours_total=40, jours_semaine=3, paye_total=1500, avances=300)

p1_articles = {}
p1_articles["Bordure T2"] = dict(objectif=1000, fait_total=650, fait_semaine=120, unite="ml")
p1_articles["Bordure Mince P2"] = dict(objectif=800, fait_total=400, fait_semaine=80, unite="ml")
p1_articles["Caniveau CS2"] = dict(objectif=5
