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
            "2026-06-01": {"etat": "vert", "visite_note": "", "details": {"travail": "دخول الآلات وبداية التهيئة", "photo": ""}, "presences": {}, "avancement": {}},
            "2026-06-02": {"etat": "meteo", "visite_note": "", "details": {"probleme": "توقف بسبب سوء الأحوال الجوية (رياح وأمطار)", "photo": ""}, "presences": {}, "avancement": {}},
        },
        "photos_chantier": [],
        "models_3d": [],
        "plans_ia": [],
        "ouvriers": {
            "بشير بن حميد": {
                "specialite": "رئيس الفريق", "tel": "99 888 777", "taux_jour": 70, "statut": "نشط",
                "jours_total": 30.0, "paye_total": 1500.0, "avances": 200.0,
                "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 1.0, "الأحد": 0.0}
            },
            "جمعة المجبري": {
                "specialite": "رئيس الفريق", "tel": "55 789 012", "taux_jour": 70, "statut": "نشط",
                "jours_total": 30.0, "paye_total": 1500.0, "avances": 200.0,
                "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 1.0, "الأحد": 0.0}
            },
            "علي الطرابلسي": {
                "specialite": "بناي", "tel": "24 567 890", "taux_jour": 60, "statut": "نشط",
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
            "C-7 Siffle en marbre Thala": {"objectif": 50.0, "fait_total": 15.0, "fait_semaine": 5.0, "unite": "ml"},
        }
    }
}

def load_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for proj in data:
                    data[proj].setdefault("photos_chantier", [])
                    data[proj].setdefault("models_3d", [])
                    data[proj].setdefault("plans_ia", [])
                    for d_k, d_v in data[proj]["jours"].items():
                        d_v.setdefault("presences", {})
                        d_v.setdefault("avancement", {})
                        d_v.setdefault("visite_note", "")
                        d_v.setdefault("details", {})
                        if d_v.get("etat") == "visite":
                            d_v["etat"] = "vert"
                            d_v["visite_note"] = d_v["details"].get("travail", "زيارة رسمية")
                    for o_k, o_v in data[proj]["ouvriers"].items():
                        o_v.setdefault("statut", "نشط")
                        o_v.setdefault("semaine", {j: 0.0 for j in jours_semaine_noms})
                return data
        except Exception:
            pass
    return default_db

def save_db(db_data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

if "db" not in st.session_state:
    st.session_state.db = load_db()

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
# إدارة اللوغو والقائمة الجانبية
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

projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", list(base_donnees_projets.keys()))
p_data = base_donnees_projets[projet_choisi]
donnees_chantier = p_data["jours"]
date_debut = date.fromisoformat(p_data["date_debut"])

if 'jour_clique' not in st.session_state:
    st.session_state.jour_clique = None

def set_jour(jour):
    st.session_state.jour_clique = jour

# ----------------------------------------------------
# 1. خانة البحث والفلترة الزمنية في الجهة اليسرى
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 بحث متقدم (Recherche IA)")
mot_cle_recherche = st.sidebar.text_input("🔎 ابحث عن اسم خدام أو بند (Article):", placeholder="اكتب اسم الخدام أو البند...")

filtre_temps = st.sidebar.selectbox("📅 اختر فترة المتابعة:", [
    "الكل (الجملي والأسبوعي)",
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
# 2. ملفات الخدامة وحسابات Agent IA في الجهة اليسرى
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 👷 ملفات الخدامة وحسابات Agent IA")

liste_ouv_filtree = [k for k in p_data["ouvriers"].keys() if mot_cle_recherche.strip().lower() in k.lower()] if mot_cle_recherche.strip() else list(p_data["ouvriers"].keys())
ouvrier_choisi = st.sidebar.selectbox("اختر الخدام للمعاينة:", [""] + liste_ouv_filtree)

if ouvrier_choisi and ouvrier_choisi != "":
    o = p_data["ouvriers"][ouvrier_choisi]
    statut_ouv = o.get("statut", "نشط")
    etat_badge = "🟢 نشط" if statut_ouv == "نشط" else ("🟠 عمل معلق" if statut_ouv == "معلق" else "🔴 حساب مقفول")
    
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

    if filtre_temps != "الكل (الجملي والأسبوعي)":
        j_periode = calc_worker_days_period(p_data, ouvrier_choisi, d_debut_f, d_fin_f)
        if filtre_temps == "بالجمعة (الأسبوع الحالي)":
            j_periode += jours_travailles_semaine
        st.sidebar.warning(f"📆 **أيام العمل ({filtre_temps}):** {j_periode} يوم ({j_periode * o['taux_jour']} د)")
    
    jours_hist_supp = calc_worker_days_period(p_data, ouvrier_choisi)
    salaire_merite = (o['jours_total'] + jours_travailles_semaine + jours_hist_supp) * o['taux_jour']
    solde = salaire_merite - (o['paye_total'] + o['avances'])
    
    st.sidebar.write(f"📊 **إجمالي الأيام (الجملي):** {o['jours_total'] + jours_travailles_semaine + jours_hist_supp} يوم")
    st.sidebar.write(f"💰 **خالص جملة:** {o['paye_total']} د | **آفونس:** {o['avances']} د")
    if solde > 0:
        st.sidebar.error(f"🔴 المستحقات الباقية: {solde} دينار")
    else:
        st.sidebar.success("✅ الحساب خالص ومريقل")

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
        if statut_ouv != "مقفول":
            if st.button("🔒 قفل الحساب", key=f"close_{ouvrier_choisi}", use_container_width=True):
                if solde > 0:
                    o["paye_total"] += solde
                o["statut"] = "مقفول"
                save_db(base_donnees_projets)
                st.rerun()
        else:
            if st.button("🔓 فتح الحساب", key=f"open_{ouvrier_choisi}", use_container_width=True):
                o["statut"] = "نشط"
                save_db(base_donnees_projets)
                st.rerun()

# إضافة عامل جديد مع إمكانية تحديد وضعيته منذ البداية
with st.sidebar.expander("➕ إضافة عامل جديد"):
    nom_nv = st.text
