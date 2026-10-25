import streamlit as st
import calendar
from datetime import date, datetime
import os
import csv

st.set_page_config(page_title="H.O Bâtiment - Tableau de Bord", page_icon="🏗️", layout="wide")

# ==========================================
# نظام تسجيل الدخول بكلمة السر
# ==========================================
utilisateurs = {
    "admin": {"mot_de_passe": "1234", "role": "مدير المشروع"},
    "najib": {"mot_de_passe": "2026", "role": "رئيس الشانطي"},
    "mra9eb": {"mot_de_passe": "0000", "role": "مراقب الأشغال"}
}

if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
    st.session_state.utilisateur = ""

if not st.session_state.authentifie:
    st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>H.O Bâtiment - تسجيل الدخول</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        nom_utilisateur = st.text_input("اسم المستخدم:")
        mot_de_passe = st.text_input("كلمة السر:", type="password")
        if st.button("دخول"):
            if nom_utilisateur in utilisateurs and utilisateurs[nom_utilisateur]["mot_de_passe"] == mot_de_passe:
                st.session_state.authentifie = True
                st.session_state.utilisateur = nom_utilisateur
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة السر خطأ!")
    st.stop()

# ==========================================
# تصميم CSS فخم ومنظم للواجهة
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
    </style>
""", unsafe_allow_html=True)

DOSSIER = os.path.dirname(os.path.abspath(__file__))
FICHIER_CHANTIER = os.path.join(DOSSIER, "journal_chantier.csv")
FICHIER_INCIDENTS = os.path.join(DOSSIER, "journal_perturbations.csv")

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
st.sidebar.markdown(f"<p class='brand-subtitle'>مرحباً: {st.session_state.utilisateur}</p>", unsafe_allow_html=True)
if st.sidebar.button("خروج (Déconnexion)"):
    st.session_state.authentifie = False
    st.rerun()

st.sidebar.markdown('</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", [
    "LOT 2 - KHALIJ CHAARA",
    "LOT 1 - BOUKHROUF"
])

objectifs_projets = {
    "LOT 2 - KHALIJ CHAARA": {
        "date_debut": date(2026, 5, 18),
        "articles": {
            "Bordure T2": {"nom_csv": "bordure t2", "objectif": 7700.0, "unite": "ml"},
            "Bordure Mince P2": {"nom_csv": "bordure mince", "objectif": 7250.0, "unite": "ml"},
            "Caniveau CS2": {"nom_csv": "caniveau central cs2", "objectif": 7700.0, "unite": "ml"},
            "Caniveau CC2": {"nom_csv": "caniveau central cc2", "objectif": 500.0, "unite": "ml"},
            "Pavé autobloquant": {"nom_csv": "pave autobloquant", "objectif": 15500.0, "unite": "م²"},
        }
    },
    "LOT 1 - BOUKHROUF": {
        "date_debut": date(2026, 6, 1),
        "articles": {
            "A.01 Double cloison 0.35m": {"nom_csv": "double cloison 0,35 m", "objectif": 1450.0, "unite": "م²"},
            "A.02 Double cloison 0.30m": {"nom_csv": "double cloison 0,30 m", "objectif": 110.0, "unite": "م²"},
        }
    }
}

p_conf = objectifs_projets[projet_choisi]

st.success(f"تم اختيار المشروع بنجاح: {projet_choisi}")
st.write("لوحة المتابعة تعمل بانتظام مع نظام الحماية وكلمة السر.")