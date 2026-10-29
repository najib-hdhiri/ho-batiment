import streamlit as st
import calendar
from datetime import date, timedelta
import os
import json
import pandas as pd

calendar.setfirstweekday(calendar.MONDAY)

st.set_page_config(page_title="H.O Bâtiment - Système Central IA", page_icon="🏗️", layout="wide")

st.markdown("""
    <style>
    .brand-container { text-align: center; background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .brand-title { color: #ff4b4b; font-size: 20px; font-weight: bold; margin: 5px 0 0 0; }
    .brand-subtitle { color: gray; font-size: 12px; margin-top: 2px; margin-bottom: 0; }
    input[type="checkbox"] { transform: scale(1.3); accent-color: #28a745 !important; cursor: pointer; }
    .worker-row { background-color: #f8f9fa; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-right: 4px solid #28a745; }
    </style>
""", unsafe_allow_html=True)

for folder in ["uploads", "uploads/chantier_photos", "uploads/3d_models", "uploads/plans", "uploads/exports"]:
    os.makedirs(folder, exist_ok=True)

DATA_FILE = "uploads/chantier_data.json"
jours_semaine_noms = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
mois_arabes = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

ALIASES_RECHERCHE = {
    "بشير بن حميد": "bechir bachir bchir ben hmid بشير بن حميد",
    "صالح بن عمار": "saleh salah salh ben ammar صالح بن عمار",
    "الهادي العياري": "hedi hadi elhedi ayari الهادي العياري",
    "جمعة المجبري": "jomaa jemaa jom3a mejbri جمعة المجبري",
    "علي الطرابلسي": "ali trabelsi علي الطرابلسي",
    "Bordure T2": "bordure t2 بوردور",
    "Bordure Mince P2": "bordure mince p2 بوردور جويد",
    "Caniveau CS2": "caniveau cs2 كنفو كانيفو",
    "Caniveau CC2": "caniveau cc2 كنفو كانيفو",
    "Pavé autobloquant": "pave autobloquant بافي رصيف",
    "A.01 Double Cloison 0.35m": "double cloison 0.35 35 دبل كلوازون حائط",
    "A.02 Double Cloison 0.30m": "double cloison 0.30 30 دبل كلوازون",
    "A.03 Cloison 0.25m": "cloison 0.25 25 كلوازون",
    "A.04 Cloison 0.20m": "cloison 0.20 20 كلوازون",
    "A.05 Cloison 0.15m": "cloison 0.15 15 كلوازون",
    "A.06 Cloison 0.10m": "cloison 0.10 10 كلوازون",
    "B-1 Enduit extérieur": "enduit exterieur ب1 لياسة خارجية دريساج",
    "B-2 Enduit intérieur": "enduit interieur ب2 لياسة داخلية",
    "B-3 Enduit sous plafond": "enduit sous plafond ب3 سقف",
    "B-4 Enduit grillagé": "enduit grillage ب4 قرياج",
    "B-5 Enduit de ravoirage": "enduit ravoirage ب5 رافواراج",
    "C-1 Carrelage marbré 25x25": "carrelage marbre 25 جليز كرلاج",
    "C-2 Carrelage carreaux": "carrelage carreaux جليز",
    "C-3 Revêtement carreaux": "revetement carreaux فايونس",
    "C-4 Plinthe": "plinthe بلينت",
    "C-5 Revêtement extérieur": "revetement exterieur تغليف خارجي",
    "C-6 Seuils en marbre Thala": "seuils marbre thala رخام تالة عتبة",
    "C-7 Siffle en marbre Thala": "siffle marbre thala سيفل رخام تالة"
}

def match_smart(nom_item, query):
    if not query or not query.strip(): return True
    q = query.strip().lower()
