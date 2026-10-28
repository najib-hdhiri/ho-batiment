import streamlit as st
import calendar
from datetime import date, timedelta
import os
import json
import urllib.parse

st.set_page_config(page_title="H.O Construction - Tableau de Bord IA", page_icon="🏗️", layout="wide")

# ==========================================
# تصميم CSS الأصلي المتجاوب مع التلفون والبيسي + مربعات خضراء
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
    input[type="checkbox"] {
        transform: scale(1.3);
        accent-color: #28a745 !important;
        cursor: pointer;
    }
    .worker-row {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-right: 4px solid #28a745;
    }
    .share-btn {
        display: inline-block;
        padding: 10px 15px;
        border-radius: 8px;
        color: white !important;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        width: 100%;
        margin-top: 8px;
    }
    .wa-btn { background-color: #25D366; }
    .mail-btn { background-color: #1976D2; }
    </style>
""", unsafe_allow_html=True)

for folder in ["uploads", "uploads/chantier_photos", "uploads/3d_models", "uploads/plans"]:
    os.makedirs(folder, exist_ok=True)

DATA_FILE = "uploads/chantier_data.json"
jours_semaine_noms = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
mois_arabes = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

# ==========================================
# قاعدة البيانات الأصلية المستخرجة من جدول الأسعار
# ==========================================
default_db = {
    "خليج الشعرة (Khalij Chaara)": {
        "date_debut": "2026-05-18",
        "stats": {"vert": 65, "jaune": 44, "gris": 12, "meteo": 8, "conge": 5},
        "jours": {
            "2026-05-18": {"etat": "vert", "visite_note": "", "details": {"travail": "انطلاق الشانطي ووضع البوردور T2", "photo": ""}, "presences": {}, "avancement": {}},
            "2026-05-19": {"etat": "jaune", "visite_note": "", "details": {"probleme": "أرضية غير مهيئة", "photo": ""}, "presences": {}, "avancement": {}},
            "2026-05-26": {"etat": "meteo", "visite_note": "", "details": {"probleme": "توقف بسبب سوء الأحوال الجوية (أمطار وعواصف)", "photo": ""}, "presences": {}, "avancement": {}},
            "2026-05-29": {"etat": "conge", "visite_note": "", "details": {"travail": "يوم راحة عادي", "photo": ""}, "presences": {}, "avancement": {}},
            "2026-06-11": {"etat": "vert", "visite_note": "زيارة السيد المدير العام", "details": {"travail": "تقدم أشغال البوردور", "photo": ""}, "presences": {}, "avancement": {}},
        },
        "photos_chantier": [],
        "models_3d": [],
        "plans_ia": [],
        "ouvriers": {
            "بشير بن حميد": {
                "specialite": "رئيس مجموعة / بناي", "tel": "99 888 777", "taux_jour": 65, "statut": "نشط",
                "jours_total": 50.0, "paye_total": 2500.0, "avances": 400.0,
                "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 1.0, "الأحد": 0.0}
            },
            "صالح بن عمار": {
                "specialite": "بناي محترف", "tel": "98 123 456", "taux_jour": 60, "statut": "نشط",
                "jours_total": 65.0, "paye_total": 3000.0, "avances": 500.0,
                "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 0.0, "الأحد": 0.0}
            },
            "الهادي العياري": {
                "specialite": "مانوفري", "tel": "22 345 678", "taux_jour": 40, "statut": "نشط",
                "jours_total": 40.0, "paye_total": 1500.0, "avances": 300.0,
                "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 0.0, "الجمعة": 0.0, "السبت": 0.0, "الأحد": 0.0}
            },
        },
        "articles": {
            "Bordure T2": {"objectif": 7700.0, "fait_total": 1540.0, "fait_semaine": 120.0
