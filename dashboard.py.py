import streamlit as st
import calendar
from datetime import date
import os
import json

st.set_page_config(page_title="H.O Construction - Tableau de Bord IA", page_icon="🏗️", layout="wide")

# ==========================================
# تصميم CSS متجاوب مع التلفون والبيسي
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

# إنشاء المجلدات الخاصة بالصور والبلانات والـ 3D
for folder in ["uploads", "uploads/chantier_photos", "uploads/3d_models", "uploads/plans"]:
    os.makedirs(folder, exist_ok=True)

DATA_FILE = "uploads/chantier_data.json"

# ==========================================
# قاعدة البيانات الأصلية المستخرجة من جدول الأسعار
# ==========================================
default_db = {
    "خليج الشعرة (Khalij Chaara)": {
        "date_debut": "2026-05-18",
        "stats": {"vert": 65, "jaune": 44, "gris": 12, "meteo": 8, "conge": 5},
        "jours": {
            "2026-05-18": {"etat": "vert", "details": {"travail": "انطلاق الشانطي ووضع البوردور T2", "photo": ""}},
            "2026-05-19": {"etat": "jaune", "details": {"probleme": "أرضية غير مهيئة", "photo": ""}},
            "2026-05-26": {"etat": "meteo", "details": {"probleme": "طقس خايب (أمطار وعواصف)", "photo": ""}},
            "2026-05-29": {"etat": "conge", "details": {"travail": "يوم راحة عادي", "photo": ""}},
            "2026-06-11": {"etat": "visite", "details": {"travail": "زيارة السيد المدير العام", "photo": ""}},
        },
        "photos_chantier": [],
        "models_3d": [],
        "plans_ia": [],
        "ouvriers": {
            "بشير بن حميد": {
                "specialite": "رئيس مجموعة / بناي", "tel": "99 888 777", "taux_jour": 65,
                "jours_total": 50.0, "paye_total": 2500.0, "avances": 400.0,
                "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 1.0, "الأحد": 0.0}
            },
            "صالح بن عمار": {
                "specialite": "بناي محترف", "tel": "98 123 456", "taux_jour": 60,
                "jours_total": 65.0, "paye_total": 3000.0, "avances": 500.0,
                "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 0.0, "الأحد": 0.0}
            },
            "الهادي العياري": {
                "specialite": "مانوفري", "tel": "22 345 678", "taux_jour": 40,
                "jours_total": 40.0, "paye_total": 1500.0, "avances": 300.0,
                "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 0.0, "الجمعة": 0.0, "السبت": 0.0, "الأحد": 0.0}
            },
        },
        "articles": {
            "Bordure T2": {"objectif": 7700.0, "fait_total": 1540.0, "fait_semaine": 120.0, "unite": "ml"},
            "Bordure Mince P2": {"objectif": 7250.0, "fait_total": 1450.0, "fait_semaine": 80.0, "unite": "ml"},
            "Caniveau CS2": {"objectif": 7700.0, "fait_total": 1155.0, "fait_semaine": 40.0, "unite": "ml"},
            "Caniveau CC2": {"objectif": 500.0, "fait_total": 150.0, "fait_semaine": 30.0, "unite": "ml"},
            "Pavé autobloquant": {"objectif": 15500.0, "fait_total": 3100.0, "fait_semaine": 50.0, "unite": "م²"},
        }
    },
    "بوخروف (Boukharouf)": {
        "date_debut": "2026-06-01",
        "stats": {"vert": 30, "jaune": 10, "gris": 5, "meteo": 4, "conge": 3},
        "jours": {
            "2026-06-01": {"etat": "vert", "details": {"travail": "دخول الآلات وبداية التهيئة", "photo": ""}},
            "2026-06-02": {"etat": "meteo", "details": {"probleme": "رياح قوية وأمطار", "photo": ""}},
        },
        "photos_chantier": [],
        "models_3d": [],
        "plans_ia": [],
        "ouvriers": {
            "بشير بن حميد": {
                "specialite": "رئيس الفريق", "tel": "99 888 777", "taux_jour": 70,
                "jours_total": 30.0, "paye_total": 1500.0, "avances": 200.0,
                "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 1.0, "الأحد": 0.0}
            },
            "جمعة المجبري": {
                "specialite": "رئيس الفريق", "tel": "55 789 012", "taux_jour": 70,
                "jours_total": 30.0, "paye_total": 1500.0, "avances": 200.0,
                "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 1.0, "الأحد": 0.0}
            },
            "علي الطرابلسي": {
                "specialite": "بناي", "tel": "24 567 890", "taux_jour": 60,
                "jours_total": 25.0, "paye_total": 1000.0, "avances": 100.0,
                "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 0.0, "السبت": 0.0, "الأحد": 0.0}
            },
        },
        "articles": {
            "A.01 Double Cloison 0.35m": {"objectif": 1450.0, "fait_total": 435.0, "fait_semaine": 50.0, "unite": "م²"},
            "A.02 Double Cloison 0.30m": {"objectif": 110.0, "fait_total": 33.0, "fait_semaine": 15.0, "unite": "م²"},
            "A.03 Cloison 0.25m": {"objectif": 1150.0, "fait_total": 345.0, "fait_semaine": 40.0, "unite": "م²"},
            "A.04 Cloison 0.20m": {"objectif": 5.0, "fait_total": 1.5, "fait_semaine": 1.0, "unite": "م²"},
            "A.05 Cloison 0.15m": {"objectif": 180.0, "fait_total": 54.0, "fait_semaine": 10.0, "unite": "م²"},
            "A.06 Cloison 0.10m": {"objectif": 400.0, "fait_total": 120.0, "fait_semaine": 20.0, "unite": "م²"},
            "B-1 Enduit extérieur": {"objectif": 4700.0, "fait_total": 1410.0, "fait_sem
