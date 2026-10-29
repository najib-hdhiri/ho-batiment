import streamlit as st
import calendar
from datetime import date, timedelta
import os
import json
import urllib.parse
import pandas as pd

# ضبط الرزنامة لتبدأ دائماً بيوم الإثنين لتتطابق 100% مع ورقة الحضور السريعة
calendar.setfirstweekday(calendar.MONDAY)

st.set_page_config(page_title="H.O Construction - Tableau de Bord IA", page_icon="🏗️", layout="wide")

# ==========================================
# تصميم CSS الأصلي المتجاوب مع التلفون والبيسي + الجداول المزينة
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
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 14px;
        text-align: right;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .styled-table thead tr {
        background-color: #ff4b4b;
        color: #ffffff;
        text-align: right;
        font-weight: bold;
    }
    .styled-table th, .styled-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #dddddd;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f8f9fa;
    }
    .styled-table tbody tr.total-row {
        background-color: #e8f5e9;
        font-weight: bold;
        color: #1b5e20;
        border-top: 2px solid #28a745;
    }
    </style>
""", unsafe_allow_html=True)

for folder in ["uploads", "uploads/chantier_photos", "uploads/3d_models", "uploads/plans", "uploads/exports"]:
    os.makedirs(folder, exist_ok=True)

DATA_FILE = "uploads/chantier_data.json"
jours_semaine_noms = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
mois_arabes = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

# ==========================================
# قاموس البحث الذكي بالفرنسية والعربية (Smart Search)
# ==========================================
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
    if not query or not query.strip():
        return True
    q = query.strip().lower()
    texte_complet = (nom_item + " " + ALIASES_RECHERCHE.get(nom_item, "")).lower()
    return q in texte_complet

# ==========================================
# قاعدة البيانات الموحدة: مشروع خليج الشعرة (شامل خليج الشعرة وبوخروف وكل الـ 23 بند)
# ==========================================
ALL_ARTICLES_DEFAULT = {
    "Bordure T2": {"objectif": 7700.0, "fait_total": 1540.0, "fait_semaine": 120.0, "unite": "ml"},
    "Bordure Mince P2": {"objectif": 7250.0, "fait_total": 1450.0, "fait_semaine": 80.0, "unite": "ml"},
    "Caniveau CS2": {"objectif": 7700.0, "fait_total": 1155.0, "fait_semaine": 40.0, "unite": "ml"},
    "Caniveau CC2": {"objectif": 500.0, "fait_total": 150.0, "fait_semaine": 30.0, "unite": "ml"},
    "Pavé autobloquant": {"objectif": 15500.0, "fait_total": 3100.0, "fait_semaine": 50.0, "unite": "م²"},
    "A.01 Double Cloison 0.35m": {"objectif": 1450.0, "fait_total": 435.0, "fait_semaine": 50.0, "unite": "م²"},
    "A.02 Double Cloison 0.30m": {"objectif": 110.0, "fait_total": 33.0, "fait_semaine": 15.0, "unite": "م²"},
    "A.03 Cloison 0.25m": {"objectif": 1150.0, "fait_total": 345.0, "fait_semaine": 40.0, "unite": "م²"},
    "A.04 Cloison 0.20m": {"objectif": 5.0, "fait_total": 1.5, "fait_semaine": 1.0, "unite": "م²"},
    "A.05 Cloison 0.15m": {"objectif": 180.0, "fait_total": 54.0, "fait_semaine": 10.0, "unite": "م²"},
    "A.06 Cloison 0.10m": {"objectif": 400.0, "fait_total": 120.0, "fait_semaine": 20.0, "unite": "م²"},
    "B-1 Enduit extérieur": {"objectif": 4700.0, "fait_total": 1410.0, "fait_semaine": 80.0, "unite": "م²"},
    "B-2 Enduit intérieur": {"objectif": 2050.0, "fait_total": 615.0, "fait_semaine": 70.0, "unite": "م²"},
    "B-3 Enduit sous plafond": {"objectif": 1900.0, "fait_total": 570.0, "fait_semaine": 50.0, "unite": "م²"},
    "B-4 Enduit grillagé": {"objectif": 350.0, "fait_total": 105.0, "fait_semaine": 10.0, "unite": "م²"},
    "B-5 Enduit de ravoirage": {"objectif": 850.0, "fait_total": 255.0, "fait_semaine": 30.0, "unite": "م²"},
    "C-1 Carrelage marbré 25x25": {"objectif": 1150.0, "fait_total": 345.0, "fait_semaine": 60.0, "unite": "م²"},
    "C-2 Carrelage carreaux": {"objectif": 2400.0, "fait_total": 720.0, "fait_semaine": 100.0, "unite": "م²"},
    "C-3 Revêtement carreaux": {"objectif": 190.0, "fait_total": 57.0, "fait_semaine": 10.0, "unite": "م²"},
    "C-4 Plinthe": {"objectif": 1000.0, "fait_total": 300.0, "fait_semaine": 40.0, "unite": "ml"},
    "C-5 Revêtement extérieur": {"objectif": 15.0, "fait_total": 4.5, "fait_semaine": 2.0, "unite": "م²"},
    "C-6 Seuils en marbre Thala": {"objectif": 15.0, "fait_total": 4.5, "fait_semaine": 1.0, "unite": "م²"},
    "C-7 Siffle en marbre Thala": {"objectif": 50.0, "fait_total": 15.0, "fait_semaine": 5.0, "unite": "ml"}
}

ALL_OUVRIERS_DEFAULT = {
    "بشير بن حميد": {
        "specialite": "رئيس مجموعة / بناي", "tel": "99 888 777", "taux_jour": 65.0, "statut": "نشط",
        "date_cloture": "2026-05-18", "jours_depuis_cloture": 6.0, "jours_archives": 44.0, "paye_depuis_cloture": 0.0, "avances": 400.0, "paye_total": 2500.0,
        "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 1.0, "الأحد": 0.0}
    },
    "صالح بن عمار": {
        "specialite": "بناي محترف", "tel": "98 123 456", "taux_jour": 60.0, "statut": "نشط",
        "date_cloture": "2026-05-18", "jours_depuis_cloture": 10.0, "jours_archives": 55.0, "paye_depuis_cloture": 0.0, "avances": 500.0, "paye_total": 3000.0,
        "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 0.0, "الأحد": 0.0}
    },
    "الهادي العياري": {
        "specialite": "مانوفري", "tel": "22 345 678", "taux_jour": 40.0, "statut": "نشط",
        "date_cloture": "2026-05-18", "jours_depuis_cloture": 8.0, "jours_archives": 32.0, "paye_depuis_cloture": 0.0, "avances": 300.0, "paye_total": 1500.0,
        "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 0.0, "الجمعة": 0.0, "السبت": 0.0, "الأحد": 0.0}
    },
    "جمعة المجبري": {
        "specialite": "رئيس فريق", "tel": "55 789 012", "taux_jour": 70.0, "statut": "نشط",
        "date_cloture": "2026-05-18", "jours_depuis_cloture": 5.0, "jours_archives": 25.0, "paye_depuis_cloture": 0.0, "avances": 200.0, "paye_total": 1500.0,
        "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 1.0, "الأحد": 0.0}
    },
    "علي الطرابلسي": {
        "specialite": "بناي", "tel": "24 567 890", "taux_jour": 60.0, "statut": "نشط",
        "date_cloture": "2026-05-18", "jours_depuis_cloture": 4.0, "jours_archives": 21.0, "paye_depuis_cloture": 0.0, "avances": 100.0, "paye_total": 1000.0,
        "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 0.0, "السبت": 0.0, "الأحد": 0.0}
    }
}

default_db = {
    "خليج الشعرة (Khalij Chaara)": {
        "date_debut": "2026-05-18",
        "stats": {"vert": 65, "jaune": 44, "gris": 12, "meteo": 8, "conge": 5},
        "jours": {
            "2026-05-18": {"etat": "vert", "visite_note": "", "details": {"travail": "انطلاق الشانطي ووضع البوردور T2", "photo": ""}, "presences": {}, "avancement": {}},
            "2026-05-19": {"etat": "jaune", "visite_note": "", "details": {"probleme": "أرضية غير مهيئة", "photo": ""}, "presences": {}, "avancement": {}},
            "2026-05-26": {"etat": "meteo", "visite_note": "", "details": {"probleme": "توقف بسبب سوء الأحوال الجوية (أمطار وعواصف)", "photo": ""}, "presences": {}, "avancement": {}},
            "2026-05-29": {"etat": "conge", "visite_note": "", "details": {"travail": "يوم راحة عادي", "photo": ""}, "presences": {}, "avancement": {}},
            "2026-06-11": {"etat": "vert", "visite_note": "زيارة السيد المدير العام", "details": {"travail": "تقدم أشغال البوردور والدبل كلوازون", "photo": ""}, "presences": {}, "avancement": {}},
        },
        "photos_chantier": [],
        "models_3d": [],
        "plans_ia": [],
        "ouvriers": ALL_OUVRIERS_DEFAULT,
        "articles": ALL_ARTICLES_DEFAULT
    }
}

def load_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # توحيد المشروع في "خليج الشعرة (Khalij Chaara)" مع دمج كافة البنود والعمال دون نقص
                proj_key = "خليج الشعرة (Khalij Chaara)"
                if proj_key not in data:
                    data = default_db
                else:
                    data = {proj_key: data[proj_key]}
                
                p = data[proj_key]
                p.setdefault("photos_chantier", [])
                p.setdefault("models_3d", [])
                p.setdefault("plans_ia", [])
                p.setdefault("articles", {})
                p.setdefault("ouvriers", {})
                
                # ضمان وجود كل الـ 23 بند كاملة
                for k_art, v_art in ALL_ARTICLES_DEFAULT.items():
                    if k_art not in p["articles"]:
                        p["articles"][k_art] = v_art
                    else:
                        p["articles"][k_art].setdefault("fait_semaine", v_art["fait_semaine"])
                        
                # ضمان وجود كافة العمال وحقول تاريخ وقف الحساب (الخلاص)
                for k_ouv, v_ouv in ALL_OUVRIERS_DEFAULT.items():
                    if k_ouv not in p["ouvriers"]:
                        p["ouvriers"][k_ouv] = v_ouv
                for o_k, o_v in p["ouvriers"].items():
                    o_v.setdefault("statut", "نشط")
                    o_v.setdefault("date_cloture", p["date_debut"])
                    o_v.setdefault("jours_depuis_cloture", 5.0)
                    o_v.setdefault("jours_archives", o_v.get("jours_total", 30.0))
                    o_v.setdefault("paye_depuis_cloture", 0.0)
                    o_v.setdefault("semaine", {j: 0.0 for j in jours_semaine_noms})
                    
                for d_k, d_v in p["jours"].items():
                    d_v.setdefault("presences", {})
                    d_v.setdefault("avancement", {})
                    d_v.setdefault("visite_note", "")
                    d_v.setdefault("details", {})
                return data
        except Exception:
            pass
    return default_db

def save_db(db_data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

if "db" not in st.session_state:
    st.session_state.db = load_db()
    save_db(st.session_state.db)

base_donnees_projets = st.session_state.db

def calc_worker_days_period(p_data, nom_ouv, start_d=None, end_d=None):
    total_d = 0.0
    for d_str, j_info in p_data["jours"].items():
        try:
            d_obj = date.fromisoformat(d_str)
            if start_d and d_obj < start_d: continue
            if end_d and d_obj > end_d: continue
            total_d += float(j_info.get("presences", {}).get(nom_ouv, 0.0))
        except Exception:
            pass
    return total_d

def calc_article_qty_period(p_data, nom_art, start_d=None, end_d=None):
    total_q = 0.0
    for d_str, j_info in p_data["jours"].items():
        try:
            d_obj = date.fromisoformat(d_str)
            if start_d and d_obj < start_d: continue
            if end_d and d_obj > end_d: continue
            total_q += float(j_info.get("avancement", {}).get(nom_art, 0.0))
        except Exception:
            pass
    return total_q

# ==========================================
# إدارة اللوغو والقائمة الجانبية (الجهة اليسرى)
# ==========================================
logo_path = None
for p in ["uploads/logo_saved.jpg", "logo.jpg", "logo.png"]:
    if os.path.exists(p):
        logo_path = p
        break

st.sidebar.markdown('<div class="brand-container">', unsafe_allow_html=True)
if logo_path:
    col_l1, col_l2, col_l3 = st.sidebar.columns([1, 2, 1])
    with col_l2:
        st.sidebar.image(logo_path, width=110)
else:
    st.sidebar.markdown("<h1 style='text-align: center; margin:0;'>🏗️</h1>", unsafe_allow_html=True)

st.sidebar.markdown("<p class='brand-title'>H.O Bâtiment</p>", unsafe_allow_html=True)
st.sidebar.markdown("<p class='brand-subtitle'>Agent IA — Central Hub</p>", unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

if not logo_path:
    up_logo = st.sidebar.file_uploader("🖼️ أضف شعار الشركة (Logo):", type=["jpg", "png", "jpeg"], key="up_logo_ho")
    if up_logo is not None:
        with open("uploads/logo_saved.jpg", "wb") as f:
            f.write(up_logo.getbuffer())
        st.rerun()

st.sidebar.markdown("---")

projet_choisi = "خليج الشعرة (Khalij Chaara)"
st.sidebar.info(f"📂 **المشروع:** {projet_choisi}")
p_data = base_donnees_projets[projet_choisi]
donnees_chantier = p_data["jours"]
date_debut = date.fromisoformat(p_data["date_debut"])

if 'jour_clique' not in st.session_state:
    st.session_state.jour_clique = None

def set_jour(jour):
    st.session_state.jour_clique = jour

# ----------------------------------------------------
# 1. خانة البحث الفوري الذكي بالعربية والفرنسية (Recherche IA)
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 بحث متقدم (Recherche IA)")
mot_cle_recherche = st.sidebar.text_input(
    "🔎 ابحث عن اسم خدام أو بند (Article):",
    placeholder="مثال: bechir, bachir, بشير, bordure, cloison..."
)

filtre_temps = st.sidebar.selectbox("📅 اختر فترة المتابعة:", [
    "من تاريخ وقف الحساب (الخلاص)",
    "بالجمعة (الأسبوع الحالي)",
    "بالشهر (اختيار شهر محدد)",
    "من تاريخ معين (فترة مخصصة)"
])

d_debut_f, d_fin_f = None, None
if filtre_temps == "بالجمعة (الأسبوع الحالي)":
    auj = date.today()
    d_debut_f = auj - timedelta(days=auj.weekday())
    d_fin_f = d_debut_f + timedelta(days=6)
elif filtre_temps == "بالشهر (اختيار شهر محدد)":
    mois_sel = st.sidebar.selectbox("اختر الشهر:", mois_arabes, index=date.today().month - 1)
    m_num = mois_arabes.index(mois_sel) + 1
    _, fin_m = calendar.monthrange(date_debut.year, m_num)
    d_debut_f = date(date_debut.year, m_num, 1)
    d_fin_f = date(date_debut.year, m_num, fin_m)
elif filtre_temps == "من تاريخ معين (فترة مخصصة)":
    cf1, cf2 = st.sidebar.columns(2)
    d_debut_f = cf1.date_input("من تاريخ:", value=date_debut, key="f_d1")
    d_fin_f = cf2.date_input("إلى تاريخ:", value=date.today(), key="f_d2")

# ----------------------------------------------------
# 2. ملفات الخدامة وحسابات Agent IA (مع اختيار تلقائي عند البحث)
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 👷 ملفات الخدامة وحسابات Agent IA")

liste_ouv_filtree = [k for k in p_data["ouvriers"].keys() if match_smart(k, mot_cle_recherche)]
options_ouv = [""] + liste_ouv_filtree
# إذا كتب المستخدم بحثاً وطابق عاملاً، يتم اختياره وإظهاره أوتوماتيكياً!
index_auto_ouv = 1 if (mot_cle_recherche.strip() and len(liste_ouv_filtree) >= 1) else 0
ouvrier_choisi = st.sidebar.selectbox("اختر الخدام للمعاينة:", options_ouv, index=index_auto_ouv)

if ouvrier_choisi and ouvrier_choisi != "":
    o = p_data["ouvriers"][ouvrier_choisi]
    statut_ouv = o.get("statut", "نشط")
    etat_badge = "🟢 نشط" if statut_ouv == "نشط" else ("🟠 عمل معلق وقتياً" if statut_ouv == "معلق" else "🔴 حساب مقفول")
    
    st.sidebar.markdown(f"<h3 style='text-align: center;'>👷‍♂️ {ouvrier_choisi}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align: center; color: #ff4b4b; font-weight: bold;'>🤖 {o['specialite']} | {etat_badge}</p>", unsafe_allow_html=True)
    
    safe_name = ouvrier_choisi.replace(" ", "_")
    img_path = f"uploads/{safe_name}_photo.jpg"
    
    if os.path.exists(img_path):
        st.sidebar.image(img_path, width=140)
    else:
        img_ouvrier = st.sidebar.file_uploader(f"🖼️ صورة {ouvrier_choisi}:", type=["jpg", "png", "jpeg"], key=f"img_{ouvrier_choisi}")
        if img_ouvrier is not None:
            with open(img_path, "wb") as f:
                f.write(img_ouvrier.getbuffer())
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.write(f"📞 **الهاتف:** {o['tel']}")
    st.sidebar.write(f"💵 **خلاص نهاره:** {o['taux_jour']} دينار")
    
    st.sidebar.markdown("📅 **أيام الحضور (كوشاج سريع ✅):**")
    
    jours_travailles_semaine = 0.0
    for js in jours_semaine_noms:
        present_side = float(o.get("semaine", {}).get(js, 1.0)) >= 0.5
        coche_side = st.sidebar.checkbox(f"{js}", value=present_side, key=f"side_chk_{projet_choisi}_{ouvrier_choisi}_{js}", disabled=(statut_ouv != "نشط"))
        val_j = 1.0 if coche_side else 0.0
        o["semaine"][js] = val_j
        jours_travailles_semaine += val_j
    save_db(base_donnees_projets)
        
    st.sidebar.info(f"⚡ مجموع أيام هذه الجمعة: **{int(jours_travailles_semaine)} أيام**")
    
    salaire_semaine = jours_travailles_semaine * o['taux_jour']
    st.sidebar.success(f"💰 **أجرة هذه الجمعة:** {salaire_semaine} دينار")

    # حساب إجمالي الأيام من تاريخ وقف الحساب (الخلاص)
    date_cloture_str = o.get("date_cloture", p_data["date_debut"])
    date_cloture_obj = date.fromisoformat(date_cloture_str)
    jours_cal_depuis_cloture = calc_worker_days_period(p_data, ouvrier_choisi, date_cloture_obj, date.today())
    total_jours_depuis_cloture = o.get("jours_depuis_cloture", 0.0) + jours_travailles_semaine + jours_cal_depuis_cloture
    
    if filtre_temps != "من تاريخ وقف الحساب (الخلاص)":
        j_periode = calc_worker_days_period(p_data, ouvrier_choisi, d_debut_f, d_fin_f)
        if filtre_temps == "بالجمعة (الأسبوع الحالي)":
            j_periode += jours_travailles_semaine
        st.sidebar.warning(f"📆 **أيام العمل ({filtre_temps}):** {j_periode} يوم ({j_periode * o['taux_jour']} د)")
    
    salaire_merite_periode = total_jours_depuis_cloture * o['taux_jour']
    solde = salaire_merite_periode - (o.get('paye_depuis_cloture', 0.0) + o.get('avances', 0.0))
    
    st.sidebar.write(f"🗓️ **تاريخ آخر خلاص (وقف الحساب):** {date_cloture_str}")
    st.sidebar.write(f"📊 **إجمالي الأيام (من تاريخ الخلاص):** {total_jours_depuis_cloture} يوم")
    st.sidebar.write(f"💰 **المستحق منذ الخلاص:** {salaire_merite_periode} د | **آفونس:** {o['avances']} د")
    if solde > 0:
        st.sidebar.error(f"🔴 المستحقات الباقية للخلاص: {solde} دينار")
    else:
        st.sidebar.success("✅ الحساب خالص ومريقل (0 د)")

    st.sidebar.markdown("⚙️ **إدارة حساب وعمل الخدام:**")
    col_act1, col_act2 = st.sidebar.columns(2)
    with col_act1:
        if statut_ouv != "معلق":
            if st.button("⏸️ تعليق العمل", key=f"susp_{ouvrier_choisi}", use_container_width=True):
                o["statut"] = "معلق"
                save_db(base_donnees_projets)
                st.rerun()
        else:
            if st.button("▶️ إعادة تفعيل", key=f"act_{ouvrier_choisi}", use_container_width=True):
                o["statut"] = "نشط"
                save_db(base_donnees_projets)
                st.rerun()
    with col_act2:
        if st.button("🔒 خلاص ووقف الحساب", key=f"close_{ouvrier_choisi}", use_container_width=True):
            if solde > 0:
                o["paye_total"] = o.get("paye_total", 0.0) + solde + o.get("avances", 0.0)
            o["jours_archives"] = o.get("jours_archives", 0.0) + total_jours_depuis_cloture
            o["jours_depuis_cloture"] = 0.0
            o["paye_depuis_cloture"] = 0.0
            o["avances"] = 0.0
            o["semaine"] = {j: 0.0 for j in jours_semaine_noms}
            o["date_cloture"] = date.today().isoformat()
            save_db(base_donnees_projets)
            st.sidebar.success("✅ تم خلاص العامل وتصفير العداد من تاريخ اليوم!")
            st.rerun()

with st.sidebar.expander("➕ إضافة عامل جديد"):
    nom_nv = st.text_input("اسم ولقب الخدام:", key="nv_nom")
    spec_nv = st.text_input("الاختصاص:", placeholder="بناي / مانوفري...", key="nv_spec")
    tel_nv = st.text_input("رقم الهاتف:", key="nv_tel")
    taux_nv = st.number_input("خلاص النهار (د):", min_value=10.0, value=50.0, step=5.0, key="nv_taux")
    statut_nv = st.selectbox("الوضعية الابتدائية:", ["نشط", "معلق"], key="nv_statut")
    if st.button("✅ حفظ العامل الجديد", use_container_width=True):
        if nom_nv.strip():
            p_data["ouvriers"][nom_nv.strip()] = {
                "specialite": spec_nv or "عامل",
                "tel": tel_nv or "-",
                "taux_jour": taux_nv,
                "statut": statut_nv,
                "date_cloture": date.today().isoformat(),
                "jours_depuis_cloture": 0.0,
                "jours_archives": 0.0,
                "paye_depuis_cloture": 0.0,
                "paye_total": 0.0,
                "avances": 0.0,
                "semaine": {j: 0.0 for j in jours_semaine_noms}
            }
            save_db(base_donnees_projets)
            st.sidebar.success(f"تمت إضافة {nom_nv} بوضعية ({statut_nv})!")
            st.rerun()

# ----------------------------------------------------
# 3. تحليل Agent IA للأشغال والبنود (مع اختيار تلقائي عند البحث)
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 تحليل Agent IA للأشغال والبنود")

articles_disponibles = [a for a in p_data["articles"].keys() if match_smart(a, mot_cle_recherche)]
options_art = [""] + articles_disponibles
index_auto_art = 1 if (mot_cle_recherche.strip() and len(articles_disponibles) >= 1 and len(liste_ouv_filtree) == 0) else 0
article_selectionne = st.sidebar.selectbox("🔍 اختر البند (Article):", options_art, index=index_auto_art)

if article_selectionne and article_selectionne != "":
    tache_trouvee = p_data["articles"][article_selectionne]
    unite_a = tache_trouvee['unite']
    pourcentage = min(int((tache_trouvee['fait_total'] / tache_trouvee['objectif']) * 100), 100)
    
    auj_d = date.today()
    debut_mois_courant = date(auj_d.year, auj_d.month, 1)
    fait_mois_courant = calc_article_qty_period(p_data, article_selectionne, debut_mois_courant, auj_d) + tache_trouvee['fait_semaine']
    fait_passe = max(tache_trouvee['fait_total'] - tache_trouvee['fait_semaine'], 0.0)
    
    st.sidebar.write(f"📊 **نسبة الإنجاز في ({article_selectionne}):** {pourcentage}%")
    st.sidebar.progress(pourcentage)
    st.sidebar.write(f"⏮️ **المنجز السابق:** {fait_passe} {unite_a}")
    st.sidebar.write(f"⚡ **إنجاز الجمعة (الأسبوعي):** +{tache_trouvee['fait_semaine']} {unite_a}")
    st.sidebar.write(f"📅 **الإنجاز الشهري:** {fait_mois_courant} {unite_a}")
    st.sidebar.write(f"✅ **المنجز الجملي الحالي:** {tache_trouvee['fait_total']} / {tache_trouvee['objectif']} {unite_a}")
    
    if filtre_temps != "من تاريخ وقف الحساب (الخلاص)" and d_debut_f and d_fin_f:
        q_periode = calc_article_qty_period(p_data, article_selectionne, d_debut_f, d_fin_f)
        st.sidebar.info(f"🔎 **المنجز خلال ({filtre_temps}):** {q_periode} {unite_a}")
    
    reste = max(tache_trouvee['objectif'] - tache_trouvee['fait_total'], 0.0)
    if reste > 0:
        st.sidebar.write(f"⏳ **المتبقي حسب العقد:** {reste} {unite_a}")
    else:
        st.sidebar.write("✅ **اكتمل البند بنجاح 100%**")

# ----------------------------------------------------
# 4. التقارير الموحدة والمزينة + حفظ Google Drive + WhatsApp / Email
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 التقارير الموحدة و Google Drive")
afficher_grand_rapport = st.sidebar.checkbox("📊 إظهار الجدول الموحد المزين (المالية والأشغال والمقارنة)", value=False)

date_rap = st.sidebar.date_input("تاريخ التقرير:", value=date.fromisoformat(st.session_state.jour_clique) if st.session_state.jour_clique else date.today(), key="side_rep_d")
d_rap_str = date_rap.isoformat()
j_rap_info = donnees_chantier.get(d_rap_str, {})
etat_rap_map = {"vert": "يوم عمل عادي 🟢", "jaune": "إيقاف أشغال 🟡", "meteo": "توقف بسبب سوء الأحوال الجوية 🌧️", "conge": "يوم راحة 🔵"}
etat_rap_txt = etat_rap_map.get(j_rap_info.get("etat", "vert"), "يوم عمل 🟢")
note_rap_txt = j_rap_info.get("details", {}).get("travail") or j_rap_info.get("details", {}).get("probleme", "أشغال اعتيادية")
visite_rap_txt = j_rap_info.get("visite_note", "")
ouv_actifs_sem = [k for k, v in p_data["ouvriers"].items() if v.get("statut", "نشط") == "نشط"]

texte_rapport_auto = (
    f"🏗️ *تقرير شانطي H.O Bâtiment*\n"
    f"📂 المشروع: {projet_choisi}\n"
    f"📅 التاريخ: {d_rap_str}\n"
    f"📌 الحالة: {etat_rap_txt}\n"
    f"📝 التفاصيل: {note_rap_txt}\n"
)
if visite_rap_txt:
    texte_rapport_auto += f"📋 ملاحظة زيارة رسمية: {visite_rap_txt}\n"
texte_rapport_auto += f"👷 عدد العمال النشطين: {len(ouv_actifs_sem)}\n"

enc_msg = urllib.parse.quote(texte_rapport_auto)
enc_sub = urllib.parse.quote(f"تقرير شانطي {projet_choisi} - {d_rap_str}")
st.sidebar.markdown(f'<a href="https://wa.me/?text={enc_msg}" target="_blank" class="share-btn wa-btn">🟢 إرسال عبر WhatsApp</a>', unsafe_allow_html=True)
st.sidebar.markdown(f'<a href="mailto:?subject={enc_sub}&body={enc_msg}" target="_blank" class="share-btn mail-btn">📧 إرسال عبر Email</a>', unsafe_allow_html=True)


# ==========================================
# الواجهة الرئيسية الأصلية: المركز الذكي للتلفون والبيسي
# ==========================================
st.title(f"🤖 H.O Bâtiment — {projet_choisi}")

# عرض الجدول الموحد المزين عند تفعيله من القائمة اليسرى
if afficher_grand_rapport:
    with st.container():
        st.markdown("### 📊 التقرير التنفيذي الموحد (المالية + تقدم الأشغال والمقارنة مع الماضي)")
        
        # بناء الجدول الموحد للمالية والعمال
        lignes_fin = []
        tot_jours_all = 0.0
        tot_merite_all = 0.0
        tot_av_all = 0.0
        tot_reste_all = 0.0
        for k_o, v_o in p_data["ouvriers"].items():
            j_sem = sum(float(x) for x in v_o.get("semaine", {}).values())
            d_cl = date.fromisoformat(v_o.get("date_cloture", p_data["date_debut"]))
            j_cal = calc_worker_days_period(p_data, k_o, d_cl, date.today())
            j_actifs = v_o.get("jours_depuis_cloture", 0.0) + j_sem + j_cal
            merite_o = j_actifs * v_o["taux_jour"]
            av_o = v_o.get("avances", 0.0)
            reste_o = merite_o - av_o
            tot_jours_all += j_actifs
            tot_merite_all += merite_o
            tot_av_all += av_o
            tot_reste_all += reste_o
            lignes_fin.append({
                "الخدام": k_o, "الاختصاص": v_o["specialite"], "الوضعية": v_o.get("statut", "نشط"),
                "تاريخ وقف الحساب": v_o.get("date_cloture", "-"), "أيام العمل (منذ الخلاص)": j_actifs,
                "أيام الأرشيف السابقة": v_o.get("jours_archives", 0.0), "الأجر اليومي (د)": v_o["taux_jour"],
                "المستحق الحالي (د)": merite_o, "الآفونس (د)": av_o, "الصافي للخلاص (د)": reste_o
            })
            
        html_fin = "<table class='styled-table'><thead><tr><th>الخدام</th><th>الاختصاص</th><th>الوضعية</th><th>تاريخ آخر خلاص</th><th>الأيام السابقة (أرشيف)</th><th>أيام الفترة الحالية</th><th>اليومية</th><th>المستحق</th><th>الآفونس</th><th>الباقي للخلاص</th></tr></thead><tbody>"
        for r in lignes_fin:
            html_fin += f"<tr><td><b>{r['الخدام']}</b></td><td>{r['الاختصاص']}</td><td>{r['الوضعية']}</td><td>{r['تاريخ وقف الحساب']}</td><td>{r['أيام الأرشيف السابقة']}</td><td><b>{r['أيام العمل (منذ الخلاص)']} يوم</b></td><td>{r['الأجر اليومي (د)']} د</td><td>{r['المستحق الحالي (د)']} د</td><td>{r['الآفونس (د)']} د</td><td style='color:#d32f2f; font-weight:bold;'>{r['الصافي للخلاص (د)']} د</td></tr>"
        html_fin += f"<tr class='total-row'><td colspan='5'>المجموع المالي الموحد للشانطي</td><td>{tot_jours_all} يوم</td><td>-</td><td>{tot_merite_all} د</td><td>{tot_av_all} د</td><td>{tot_reste_all} دينار</td></tr></tbody></table>"
        st.markdown("#### 💰 1. جدول المالية وأجور العمال (منذ تاريخ وقف الحساب)")
        st.markdown(html_fin, unsafe_allow_html=True)

        # بناء جدول الأشغال والمقارنة بين الماضي والحاضر والنسب المئوية
        lignes_art = []
        html_art = "<table class='styled-table'><thead><tr><th>البند (Article)</th><th>الهدف التعاقدي</th><th>المنجز السابق (الماضي)</th><th>إنجاز هذه الجمعة (+)</th><th>المنجز الجملي الحالي</th><th>المتبقي</th><th>نسبة الإنجاز والتقدم</th></tr></thead><tbody>"
        for k_a, v_a in p_data["articles"].items():
            obj_a = v_a["objectif"]
            act_a = v_a["fait_total"]
            sem_a = v_a.get("fait_semaine", 0.0)
            passe_a = max(act_a - sem_a, 0.0)
            rem_a = max(obj_a - act_a, 0.0)
            pct_a = round((act_a / obj_a) * 100, 1) if obj_a > 0 else 0
            pct_passe = round((passe_a / obj_a) * 100, 1) if obj_a > 0 else 0
            evol = round(pct_a - pct_passe, 1)
            u_a = v_a["unite"]
            bar_html = f"<div style='background:#e0e0e0; border-radius:6px; width:100%; height:18px;'><div style='background:#28a745; width:{min(pct_a, 100)}%; height:18px; border-radius:6px; text-align:center; color:white; font-size:11px; line-height:18px;'>{pct_a}% (+{evol}%)</div></div>"
            html_art += f"<tr><td><b>{k_a}</b></td><td>{obj_a} {u_a}</td><td>{passe_a} {u_a} ({pct_passe}%)</td><td style='color:#28a745; font-weight:bold;'>+{sem_a} {u_a}</td><td><b>{act_a} {u_a}</b></td><td>{rem_a} {u_a}</td><td style='width:220px;'>{bar_html}</td></tr>"
            lignes_art.append({
                "البند": k_a, "الوحدة": u_a, "الهدف التعاقدي": obj_a, "المنجز السابق": passe_a,
                "إنجاز الأسبوع": sem_a, "المنجز الجملي": act_a, "المتبقي": rem_a, "النسبة المئوية (%)": pct_a
            })
        html_art += "</tbody></table>"
        st.markdown("#### 🧱 2. جدول تقدم الأشغال والمقارنة بين الماضي والحاضر")
        st.markdown(html_art, unsafe_allow_html=True)

        # زر تحميل الملف الموحد لـ Google Drive
        df_unifie_fin = pd.DataFrame(lignes_fin)
        df_unifie_art = pd.DataFrame(lignes_art)
        csv_unifie = "--- الجدول المالي الموحد للعمال ---\n" + df_unifie_fin.to_csv(index=False) + "\n--- جدول تقدم الأشغال والمقارنة ---\n" + df_unifie_art.to_csv(index=False)
        st.download_button(
            "☁️ تحميل الجدول الموحد الكامل (المالية + الأشغال) لحفظه في Google Drive (Excel/CSV)",
            data=csv_unifie.encode("utf-8-sig"),
            file_name=f"Rapport_Unifie_HO_Batiment_{date.today().isoformat()}.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.markdown("---")

with st.expander("📱 **مركز التحكم السريع والـ Agent IA (خدامة، أشغال، صور، 3D، وبلانات)**", expanded=True):
    tab_ouv, tab_art, tab_jour, tab_photos, tab_3d, tab_plans = st.tabs([
        "👷 1. حضور الخدامة (كوشاج سريع ✅)", 
        "🧱 2. الأشغال", 
        "📅 3. يوميات الشانطي",
        "📸 4. صور الشانطي",
        "🏢 5. تصاور 3D",
        "📐 6. قراءة البلانات (IA)"
    ])
    
    # 1. حضور الخدامة (يسحب اسم العامل المعلق وقتياً من ورقة الحضور السريعة)
    with tab_ouv:
        st.markdown("##### ✅ **ورقة الحضور السريعة (من الإثنين إلى الأحد — العمال المعلقون وقتياً يُسحب اسمهم تلقائياً):**")
        
        changement_presence = False
        for nom_ouv, info_ouv in p_data["ouvriers"].items():
            statut_o = info_ouv.get("statut", "نشط")
            if statut_o != "نشط":
                continue
            st.markdown(f"<div class='worker-row'><b>👷‍♂️ {nom_ouv}</b> <span style='color:gray; font-size:13px;'>({info_ouv['specialite']} — {info_ouv['taux_jour']} د/يوم)</span></div>", unsafe_allow_html=True)
            cols_check = st.columns(8)
            total_sem = 0.0
            for idx_j, js in enumerate(jours_semaine_noms):
                est_present = float(info_ouv.get("semaine", {}).get(js, 0.0)) >= 0.5
                nouvelle_val = cols_check[idx_j].checkbox(
                    f"{js}", 
                    value=est_present, 
                    key=f"chk_mob_{projet_choisi}_{nom_ouv}_{js}"
                )
                val_num = 1.0 if nouvelle_val else 0.0
                if info_ouv["semaine"].get(js, 0.0) != val_num:
                    info_ouv["semaine"][js] = val_num
                    changement_presence = True
                total_sem += val_num
            
            salaire_sem_ouv = total_sem * info_ouv['taux_jour']
            cols_check[7].markdown(f"**{int(total_sem)} أيام**<br><span style='color:#28a745; font-weight:bold;'>{int(salaire_sem_ouv)} د</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 5px 0 12px 0;'>", unsafe_allow_html=True)

        if changement_presence:
            save_db(base_donnees_projets)
            st.toast("✅ تم حفظ الحضور وتحديث الحساب تلقائياً!")

        st.markdown("##### 💰 **تسجيل آفونس (Avance) أو خلاص جديد:**")
        c_av1, c_av2, c_av3, c_av4 = st.columns([2, 2, 2, 2])
        with c_av1:
            ouv_mob = st.selectbox("اختر الخدام:", list(p_data["ouvriers"].keys()), key="mob_ouv")
        with c_av2:
            avance_plus = st.number_input("المبلغ (دينار):", min_value=0.0, value=0.0, step=10.0, key="mob_av")
        with c_av3:
            type_paiement = st.radio("نوع الدفع:", ["آفونس (Avance)", "دفعة خلاص (Payé)"], horizontal=True)
        with c_av4:
            st.write("")
            if st.button("💵 تسجيل المبلغ", use_container_width=True):
                if avance_plus > 0:
                    if type_paiement == "آفونس (Avance)":
                        p_data["ouvriers"][ouv_mob]["avances"] += avance_plus
                    else:
                        p_data["ouvriers"][ouv_mob]["paye_depuis_cloture"] = p_data["ouvriers"][ouv_mob].get("paye_depuis_cloture", 0.0) + avance_plus
                        p_data["ouvriers"][ouv_mob]["paye_total"] += avance_plus
                    save_db(base_donnees_projets)
                    st.success(f"🤖 Agent IA: تم تسجيل {avance_plus} د لـ ({ouv_mob}) بنجاح!")

    # 2. تقدم البنود
    with tab_art:
        ca1, ca2 = st.columns(2)
        with ca1:
            art_mob = st.selectbox("اختر البند (Article):", list(p_data["articles"].keys()), key="mob_art")
            unite_art = p_data["articles"][art_mob]["unite"]
        with ca2:
            qty_ajout = st.number_input(f"الكمية المنجزة اليوم ({unite_art}):", min_value=0.0, value=0.0, step=5.0, key="mob_qty")
            
        if st.button("✅ إضافة الكمية المنجزة فوراً", use_container_width=True):
            if qty_ajout > 0:
                p_data["articles"][art_mob]["fait_total"] += qty_ajout
                p_data["articles"][art_mob]["fait_semaine"] += qty_ajout
                d_auj_str = date.today().isoformat()
                if d_auj_str not in p_data["jours"]:
                    p_data["jours"][d_auj_str] = {"etat": "vert", "visite_note": "", "details": {"travail": f"إنجاز {art_mob}", "photo": ""}, "presences": {}, "avancement": {}}
                p_data["jours"][d_auj_str]["avancement"][art_mob] = p_data["jours"][d_auj_str]["avancement"].get(art_mob, 0.0) + qty_ajout
                save_db(base_donnees_projets)
                st.success(f"🤖 Agent IA: تمت إضافة {qty_ajout} {unite_art} لبند ({art_mob}). المجموع الحالي: {p_data['articles'][art_mob]['fait_total']} {unite_art}!")

    # 3. يوميات الشانطي
    with tab_jour:
        cj1, cj2, cj3 = st.columns(3)
        with cj1:
            date_mob = st.date_input("تاريخ اليوم:", value=date.today(), key="mob_date")
        with cj2:
            etat_mob = st.selectbox("حالة الشانطي:", [
                ("vert", "🟢 يوم عمل عادي"),
                ("jaune", "🟡 إيقاف أشغال"),
                ("meteo", "🌧️ توقف بسبب سوء الأحوال الجوية"),
                ("conge", "🔵 يوم راحة")
            ], format_func=lambda x: x[1], key="mob_etat")
        with cj3:
            note_mob = st.text_input("ملاحظة أو تفاصيل اليوم:", placeholder="مثال: صبينا البيتون / أمطار غزيرة...", key="mob_note")
            
        visite_mob = st.text_input("📋 ملاحظة زيارة رسمية (اختياري):", placeholder="اتركه فارغاً أو اكتب تفاصيل الزيارة الرسمية إن وجدت...", key="mob_visite_note")
            
        if st.button("✅ تسجيل اليوم في الرزنامة", use_container_width=True):
            d_str = date_mob.isoformat()
            code_etat = etat_mob[0]
            cle_detail = "probleme" if code_etat in ["jaune", "meteo"] else "travail"
            old_ph = p_data["jours"].get(d_str, {}).get("details", {}).get("photo", "")
            old_pres = p_data["jours"].get(d_str, {}).get("presences", {})
            old_av = p_data["jours"].get(d_str, {}).get("avancement", {})
            p_data["jours"][d_str] = {
                "etat": code_etat,
                "visite_note": visite_mob.strip(),
                "details": {cle_detail: note_mob or etat_mob[1], "photo": old_ph},
                "presences": old_pres,
                "avancement": old_av
            }
            if code_etat in p_data["stats"]:
                p_data["stats"][code_etat] += 1
            save_db(base_donnees_projets)
            st.success(f"🤖 Agent IA: تم تسجيل يوم {d_str} في الرزنامة بنجاح!")

    # 4. صور الشانطي الحية (رفع مجموعة من الصور في نفس الوقت أو بالكاميرا)
    with tab_photos:
        st.markdown("📸 **صور الشانطي مباشرة بالتلفون أو ارفع مجموعة صور دفعة واحدة لربطها بالمشروع والرزنامة:**")
        cp1, cp2 = st.columns(2)
        with cp1:
            date_photo = st.date_input("تاريخ الصور:", value=date.today(), key="date_ph")
            art_photo = st.selectbox("البند المرتبط بالصور:", ["عام (شانطي كامل)"] + list(p_data["articles"].keys()), key="art_ph")
            desc_photo = st.text_input("وصف الصور:", placeholder="مثال: تقدم أشغال البوردور في الجهة الشمالية", key="desc_ph")
        with cp2:
            mode_capture = st.radio("طريقة الإدخال:", ["📂 رفع صورة أو مجموعة صور معاً", "📷 تصوير مباشر بالكاميرا"], horizontal=True)
            imgs_chantier_list = []
            if mode_capture == "📷 تصوير مباشر بالكاميرا":
                cam_img = st.camera_input("التقط صورة للشانطي:")
                if cam_img is not None:
                    imgs_chantier_list = [cam_img]
            else:
                up_imgs = st.file_uploader("اختر صورة أو عدة صور معاً:", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="up_ch_ph")
                if up_imgs:
                    imgs_chantier_list = up_imgs

        if st.button("✅ حفظ صور الشانطي وتوثيقها", use_container_width=True):
            if imgs_chantier_list:
                d_str = date_photo.isoformat()
                last_saved_path = ""
                for idx_img, img_obj in enumerate(imgs_chantier_list):
                    filename = f"uploads/chantier_photos/{d_str}_{len(p_data['photos_chantier'])+1}_{idx_img}.jpg"
                    with open(filename, "wb") as f:
                        f.write(img_obj.getbuffer())
                    last_saved_path = filename
                    entry = {"date": d_str, "article": art_photo, "desc": desc_photo or "صورة ميدانية", "path": filename}
                    p_data["photos_chantier"].append(entry)
                
                if d_str not in p_data["jours"]:
                    p_data["jours"][d_str] = {"etat": "vert", "visite_note": "", "details": {"travail": desc_photo or "توثيق بالصور", "photo": last_saved_path}, "presences": {}, "avancement": {}}
                else:
                    p_data["jours"][d_str]["details"]["photo"] = last_saved_path
                    
                save_db(base_donnees_projets)
                st.success(f"🤖 Agent IA: تم حفظ {len(imgs_chantier_list)} صورة للشانطي وربطها بالرزنامة بنجاح!")
            else:
                st.warning("⚠️ الرجاء اختيار أو التقاط صورة أولاً.")

        if p_data["photos_chantier"]:
            st.markdown("---")
            st.markdown("🖼️ **أرشيف صور الشانطي المسجلة:**")
            cols_ph = st.columns(3)
            for idx, ph in enumerate(reversed(p_data["photos_chantier"])):
                if os.path.exists(ph["path"]):
                    with cols_ph[idx % 3]:
                        st.image(ph["path"], caption=f"📅 {ph['date']} | 🧱 {ph['article']} — {ph['desc']}", use_container_width=True)

    # 5. تصاور 3D والتصاميم النهائية
    with tab_3d:
        st.markdown("🏢 **معرض التصاميم ثلاثية الأبعاد (3D Renders & Maquettes) للمقارنة الميدانية:**")
        c3d1, c3d2 = st.columns(2)
        with c3d1:
            titre_3d = st.text_input("عنوان التصميم 3D:", placeholder="مثال: الواجهة الرئيسية / الرصيف المبلط", key="t_3d")
            zone_3d = st.text_input("المنطقة أو البند الموافق:", placeholder="مثال: Pavé autobloquant + Bordure T2", key="z_3d")
        with c3d2:
            img_3d = st.file_uploader("ارفع صورة 3D (Render):", type=["jpg", "png", "jpeg"], key="up_3d")

        if st.button("✅ إضافة التصميم 3D للمعرض", use_container_width=True):
            if img_3d is not None:
                path_3d = f"uploads/3d_models/3d_{len(p_data['models_3d'])+1}.jpg"
                with open(path_3d, "wb") as f:
                    f.write(img_3d.getbuffer())
                p_data["models_3d"].append({"titre": titre_3d or "تصميم 3D", "zone": zone_3d, "path": path_3d})
                save_db(base_donnees_projets)
                st.success("🤖 Agent IA: تمت إضافة التصميم 3D بنجاح!")

        if p_data["models_3d"]:
            st.markdown("---")
            cols_3d = st.columns(2)
            for idx, m3d in enumerate(p_data["models_3d"]):
                if os.path.exists(m3d["path"]):
                    with cols_3d[idx % 2]:
                        st.image(m3d["path"], caption=f"🏢 {m3d['titre']} ({m3d['zone']})", use_container_width=True)

    # 6. قراءة وتحليل البلانات بالـ Agent IA
    with tab_plans:
        st.markdown("📐 **قارئ ومحلل البلانات الهندسية الذكي (Agent IA - Lecture des Plans):**")
        cpl1, cpl2 = st.columns(2)
        with cpl1:
            nom_plan = st.text_input("اسم البلان أو الطابق:", placeholder="مثال: Plan de Coffrage RDC / Plan d'aménagement", key="nom_pl")
            article_lie = st.selectbox("البند المرتبط بالبلان:", list(p_data["articles"].keys()), key="art_pl")
            notes_plan = st.text_area("قراءة البلان / ملاحظات الأبعاد والكوتاسيون (أو سؤال للـ Agent IA):", placeholder="مثال: طول البوردور في هذا المقطع 250 متر، سمك الحائط 35 صم...", key="note_pl")
        with cpl2:
            img_plan = st.file_uploader("ارفع صورة البلان (أو صوره من الشانطي):", type=["jpg", "png", "jpeg"], key="up_pl")

        if st.button("🤖 حفظ البلان وتحليل المعطيات مع البند", use_container_width=True):
            if img_plan is not None:
                path_pl = f"uploads/plans/plan_{len(p_data['plans_ia'])+1}.jpg"
                with open(path_pl, "wb") as f:
                    f.write(img_plan.getbuffer())
                
                obj_art = p_data["articles"][article_lie]["objectif"]
                fait_art = p_data["articles"][article_lie]["fait_total"]
                unite_a = p_data["articles"][article_lie]["unite"]
                synthese_ia = (
                    f"📐 تحليل Agent IA للبلان ({nom_plan or 'بلان هندسي'}): "
                    f"مرتبط ببند [{article_lie}] — الهدف التعاقدي الجملي في الكراس: {obj_art} {unite_a} | "
                    f"المنجز حالياً في الشانطي: {fait_art} {unite_a} (المتبقي: {obj_art - fait_art} {unite_a}). "
                    f"الملاحظات الفنية المعتمدة: {notes_plan or 'مطابق للمواصفات التعاقدية.'}"
                )
                
                p_data["plans_ia"].append({
                    "nom": nom_plan or "بلان هندسي",
                    "article": article_lie,
                    "synthese": synthese_ia,
                    "path": path_pl
                })
                save_db(base_donnees_projets)
                st.success("✅ تم حفظ البلان وإصدار التحليل الفني بواسطة Agent IA!")
            else:
                st.warning("⚠️ الرجاء رفع صورة البلان أولاً.")

        if p_data["plans_ia"]:
            st.markdown("---")
            st.markdown("📋 **سجل البلانات المحللة عبر Agent IA:**")
            for pl in reversed(p_data["plans_ia"]):
                with st.container():
                    col_p_img, col_p_txt = st.columns([1, 2])
                    with col_p_img:
                        if os.path.exists(pl["path"]):
                            st.image(pl["path"], use_container_width=True)
                    with col_p_txt:
                        st.markdown(f"#### 📐 {pl['nom']} — ({pl['article']})")
                        st.info(pl["synthese"])
                    st.markdown("---")

# ==========================================
# إحصائيات ورزنامة الشانطي + الرجوع بالزمن (مطابقة لأيام الإثنين - الأحد)
# ==========================================
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
col_stat1.metric("🟢 أيام العمل الفعلية", f"{p_data['stats']['vert']} يوم")
col_stat2.metric("🟡 إيقاف الأشغال", f"{p_data['stats']['jaune']} يوم")
col_stat3.metric("🌧️ سوء الأحوال الجوية", f"{p_data['stats']['meteo']} يوم")
col_stat4.metric("🔵 راحة عادية", f"{p_data['stats']['conge']} يوم")
st.markdown("---")

jour = st.session_state.jour_clique
if jour:
    st.info(f"📅 **تفاصيل اليوم المختار عبر تقرير Agent IA: {jour}**")
    if jour not in donnees_chantier:
        donnees_chantier[jour] = {"etat": "vert", "visite_note": "", "details": {"travail": "يوم عمل اعتيادي", "photo": ""}, "presences": {}, "avancement": {}}
        
    etat = donnees_chantier[jour]["etat"]
    details_j = donnees_chantier[jour]["details"]
    visite_j = donnees_chantier[jour].get("visite_note", "")
    
    if etat == "vert":
        st.success(f"🟢 يوم عمل فعلي — **تقرير IA:** {details_j.get('travail', '')}")
    elif etat == "jaune":
        st.warning(f"🟡 إيقاف الأشغال — **السبب:** {details_j.get('probleme', '')}")
    elif etat == "meteo":
        st.error(f"🌧️ توقف بسبب سوء الأحوال الجوية — **رصد IA:** {details_j.get('probleme', '')}")
    elif etat == "conge":
        st.info(f"🔵 يوم راحة — **ملاحظة IA:** {details_j.get('travail', '')}")
        
    if visite_j:
        st.info(f"📋 **ملاحظة زيارة رسمية:** {visite_j}")
        
    photo_j = details_j.get("photo", "")
    if photo_j and os.path.exists(photo_j):
        st.image(photo_j, caption=f"📸 صورة الشانطي الموثقة ليوم {jour}", width=400)

    with st.expander(f"✏️ تعديل معطيات يوم ({jour}) — (حالة اليوم، الزيارة الرسمية، الحضور، الكميات، والصور)", expanded=False):
        c_ed1, c_ed2 = st.columns(2)
        with c_ed1:
            etats_list = [("vert", "🟢 يوم عمل عادي"), ("jaune", "🟡 إيقاف أشغال"), ("meteo", "🌧️ توقف بسبب سوء الأحوال الجوية"), ("conge", "🔵 يوم راحة")]
            idx_e = [x[0] for x in etats_list].index(etat) if etat in [x[0] for x in etats_list] else 0
            nv_etat_j = st.selectbox("تغيير حالة اليوم:", etats_list, index=idx_e, format_func=lambda x: x[1], key=f"ed_et_{jour}")
            nv_note_j = st.text_input("تعديل الملاحظة اليومية:", value=details_j.get("travail") or details_j.get("probleme", ""), key=f"ed_nt_{jour}")
            nv_vis_j = st.text_input("📋 ملاحظة زيارة رسمية:", value=visite_j, key=f"ed_vis_{jour}")
            if st.button("💾 حفظ تعديل اليوميات", key=f"btn_ed_j_{jour}"):
                donnees_chantier[jour]["etat"] = nv_etat_j[0]
                cle_d = "probleme" if nv_etat_j[0] in ["jaune", "meteo"] else "travail"
                donnees_chantier[jour]["details"][cle_d] = nv_note_j
                donnees_chantier[jour]["visite_note"] = nv_vis_j
                save_db(base_donnees_projets)
                st.rerun()
        with c_ed2:
            st.markdown("**👷 تعديل حضور الخدامة في هذا اليوم:**")
            for n_o, inf_o in p_data["ouvriers"].items():
                if inf_o.get("statut") == "مقفول": continue
                pres_old = float(donnees_chantier[jour].get("presences", {}).get(n_o, 0.0)) >= 0.5
                chk_p = st.checkbox(f"{n_o}", value=pres_old, key=f"ed_p_{jour}_{n_o}")
                val_p = 1.0 if chk_p else 0.0
                if float(donnees_chantier[jour].get("presences", {}).get(n_o, 0.0)) != val_p:
                    donnees_chantier[jour].setdefault("presences", {})[n_o] = val_p
                    save_db(base_donnees_projets)
            
            st.markdown("**🧱 تسجيل/تعديل كمية منجزة في هذا اليوم:**")
            art_ed = st.selectbox("البند:", list(p_data["articles"].keys()), key=f"ed_ar_{jour}")
            q_old = float(donnees_chantier[jour].get("avancement", {}).get(art_ed, 0.0))
            q_new = st.number_input("الكمية:", min_value=0.0, value=q_old, step=5.0, key=f"ed_q_{jour}")
            if st.button("💾 حفظ كمية اليوم", key=f"btn_ed_q_{jour}"):
                diff_q = q_new - q_old
                p_data["articles"][art_ed]["fait_total"] += diff_q
                donnees_chantier[jour].setdefault("avancement", {})[art_ed] = q_new
                save_db(base_donnees_projets)
                st.success("تم تحديث الكمية!")
                st.rerun()
else:
    st.markdown("👉 **انقر على أي يوم في الرزنامة أسفله لاستعراض تحليل Agent IA وصور الشانطي الموثقة أو تعديل الأيام السابقة:**")

st.markdown("---")

annee = date_debut.year
mois_a_afficher = list(range(date_debut.month, 13))

def get_couleur_jour(date_str):
    if date_str in donnees_chantier:
        etat = donnees_chantier[date_str]["etat"]
        vis_icon = "📋" if donnees_chantier[date_str].get("visite_note") else ""
        if etat == "vert": return f"🟢{vis_icon}"
        if etat == "jaune": return f"🟡{vis_icon}"
        if etat == "meteo": return f"🌧️{vis_icon}"
        if etat == "conge": return f"🔵{vis_icon}"
    return "⬜"

for i in range(0, len(mois_a_afficher), 2):
    col1, col2 = st.columns(2)
    
    m1 = mois_a_afficher[i]
    with col1:
        st.markdown(f"<h5 style='text-align: center; background-color: #f0f2f6; padding: 5px; border-radius: 5px;'>شهر {mois_arabes[m1-1]} {annee}</h5>", unsafe_allow_html=True)
        cols_j1 = st.columns(7)
        for k, j in enumerate(jours_semaine_noms):
            cols_j1[k].markdown("<div style='text-align: center; font-size: 11px; font-weight: bold;'>" + j[:4] + "</div>", unsafe_allow_html=True)
        
        for semaine in calendar.monthcalendar(annee, m1):
            cols = st.columns(7)
            for k, jour_num in enumerate(semaine):
                if jour_num == 0: cols[k].write("")
                else:
                    date_str = f"{annee}-{m1:02d}-{jour_num:02d}"
                    if date(annee, m1, jour_num) < date_debut:
                        cols[k].markdown("<div style='text-align:center; color:grey; font-size: 12px;'>🚫</div>", unsafe_allow_html=True)
                    else:
                        cols[k].button(f"{get_couleur_jour(date_str)} {jour_num}", key=f"btn_{projet_choisi}_{date_str}", on_click=set_jour, args=(date_str,), use_container_width=True)
                        
    if i + 1 < len(mois_a_afficher):
        m2 = mois_a_afficher[i+1]
        with col2:
            st.markdown(f"<h5 style='text-align: center; background-color: #f0f2f6; padding: 5px; border-radius: 5px;'>شهر {mois_arabes[m2-1]} {annee}</h5>", unsafe_allow_html=True)
            cols_j2 = st.columns(7)
            for k, j in enumerate(jours_semaine_noms):
                cols_j2[k].markdown("<div style='text-align: center; font-size: 11px; font-weight: bold;'>" + j[:4] + "</div>", unsafe_allow_html=True)
            
            for semaine in calendar.monthcalendar(annee, m2):
                cols = st.columns(7)
                for k, jour_num in enumerate(semaine):
                    if jour_num == 0: cols[k].write("")
                    else:
                        date_str = f"{annee}-{m2:02d}-{jour_num:02d}"
                        if date(annee, m2, jour_num) < date_debut:
                            cols[k].markdown("<div style='text-align:center; color:grey; font-size: 12px;'>🚫</div>", unsafe_allow_html=True)
                        else:
                            cols[k].button(f"{get_couleur_jour(date_str)} {jour_num}", key=f"2_btn_{projet_choisi}_{date_str}", on_click=set_jour, args=(date_str,), use_container_width=True)
