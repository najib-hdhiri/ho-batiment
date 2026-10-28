import streamlit as st
import calendar
from datetime import date, datetime, timedelta
import os
import json
import urllib.parse

st.set_page_config(page_title="H.O Bâtiment - Système Central IA", page_icon="🏗️", layout="wide")

# ==========================================
# تصميم CSS متجاوب مع الهاتف والحاسوب
# ==========================================
st.markdown("""
    <style>
    .brand-container { text-align: center; background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 15px; }
    .brand-title { color: #ff4b4b; font-size: 20px; font-weight: bold; margin: 5px 0 0 0; }
    .brand-subtitle { color: gray; font-size: 12px; margin-top: 2px; margin-bottom: 0; }
    input[type="checkbox"] { transform: scale(1.3); accent-color: #28a745 !important; cursor: pointer; }
    .worker-row { background-color: #f8f9fa; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-right: 4px solid #28a745; }
    .time-machine-box { background-color: #fff8e1; border: 2px solid #ffc107; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    .visite-badge { background-color: #e3f2fd; color: #0d47a1; padding: 6px 12px; border-radius: 6px; font-weight: bold; border-right: 4px solid #1976d2; margin-top: 5px; }
    .share-btn { display: inline-block; padding: 10px 16px; border-radius: 8px; color: white !important; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 5px; }
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
# قاعدة البيانات الابتدائية
# ==========================================
default_db = {
    "خليج الشعرة (Khalij Chaara)": {
        "date_debut": "2026-05-18",
        "stats": {"vert": 65, "jaune": 44, "gris": 12, "meteo": 8, "conge": 5},
        "jours": {
            "2026-05-18": {"etat": "vert", "visite_note": "", "details": {"travail": "انطلاق الشانطي ووضع البوردور T2"}, "photo": "", "presences": {"بشير بن حميد": 1.0, "صالح بن عمار": 1.0}, "avancement": {"Bordure T2": 45.0}},
            "2026-05-19": {"etat": "jaune", "visite_note": "", "details": {"probleme": "أرضية غير مهيئة"}, "photo": "", "presences": {}, "avancement": {}},
            "2026-05-26": {"etat": "meteo", "visite_note": "", "details": {"probleme": "أمطار غزيرة ورياح قوية"}, "photo": "", "presences": {}, "avancement": {}},
            "2026-06-11": {"etat": "vert", "visite_note": "زيارة ميدانية للسيد المدير العام ومكتب الدراسات", "details": {"travail": "تقدم أشغال البوردور والكنفو"}, "photo": "", "presences": {"بشير بن حميد": 1.0, "صالح بن عمار": 1.0, "الهادي العياري": 1.0}, "avancement": {"Bordure T2": 60.0}},
        },
        "photos_chantier": [], "models_3d": [], "plans_ia": [],
        "ouvriers": {
            "بشير بن حميد": {"specialite": "رئيس مجموعة / بناي", "tel": "99 888 777", "taux_jour": 65.0, "statut": "نشط", "jours_base": 48.0, "paye_total": 2500.0, "avances": 400.0, "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 1.0, "الأحد": 0.0}},
            "صالح بن عمار": {"specialite": "بناي محترف", "tel": "98 123 456", "taux_jour": 60.0, "statut": "نشط", "jours_base": 63.0, "paye_total": 3000.0, "avances": 500.0, "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 0.0, "الأحد": 0.0}},
            "الهادي العياري": {"specialite": "مانوفري", "tel": "22 345 678", "taux_jour": 40.0, "statut": "نشط", "jours_base": 39.0, "paye_total": 1500.0, "avances": 300.0, "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 0.0, "الجمعة": 0.0, "السبت": 0.0, "الأحد": 0.0}},
        },
        "articles": {
            "Bordure T2": {"objectif": 7700.0, "fait_base": 1435.0, "unite": "ml"},
            "Bordure Mince P2": {"objectif": 7250.0, "fait_base": 1450.0, "unite": "ml"},
            "Caniveau CS2": {"objectif": 7700.0, "fait_base": 1155.0, "unite": "ml"},
            "Caniveau CC2": {"objectif": 500.0, "fait_base": 150.0, "unite": "ml"},
            "Pavé autobloquant": {"objectif": 15500.0, "fait_base": 3100.0, "unite": "م²"},
        }
    },
    "بوخروف (Boukharouf)": {
        "date_debut": "2026-06-01",
        "stats": {"vert": 30, "jaune": 10, "gris": 5, "meteo": 4, "conge": 3},
        "jours": {
            "2026-06-01": {"etat": "vert", "visite_note": "حضور المهندس المعماري لانطلاق الأشغال", "details": {"travail": "دخول الآلات وبداية التهيئة"}, "photo": "", "presences": {"بشير بن حميد": 1.0, "جمعة المجبري": 1.0}, "avancement": {"A.01 Double Cloison 0.35m": 35.0}},
            "2026-06-02": {"etat": "meteo", "visite_note": "", "details": {"probleme": "توقف بسبب سوء الأحوال الجوية (رياح وأمطار)"}, "photo": "", "presences": {}, "avancement": {}},
        },
        "photos_chantier": [], "models_3d": [], "plans_ia": [],
        "ouvriers": {
            "بشير بن حميد": {"specialite": "رئيس الفريق", "tel": "99 888 777", "taux_jour": 70.0, "statut": "نشط", "jours_base": 29.0, "paye_total": 1500.0, "avances": 200.0, "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 1.0, "الأحد": 0.0}},
            "جمعة المجبري": {"specialite": "رئيس الفريق", "tel": "55 789 012", "taux_jour": 70.0, "statut": "نشط", "jours_base": 29.0, "paye_total": 1500.0, "avances": 200.0, "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 1.0, "السبت": 1.0, "الأحد": 0.0}},
            "علي الطرابلسي": {"specialite": "بناي", "tel": "24 567 890", "taux_jour": 60.0, "statut": "نشط", "jours_base": 25.0, "paye_total": 1000.0, "avances": 100.0, "semaine": {"الإثنين": 1.0, "الثلاثاء": 1.0, "الأربعاء": 1.0, "الخميس": 1.0, "الجمعة": 0.0, "السبت": 0.0, "الأحد": 0.0}},
        },
        "articles": {
            "A.01 Double Cloison 0.35m": {"objectif": 1450.0, "fait_base": 400.0, "unite": "م²"},
            "A.02 Double Cloison 0.30m": {"objectif": 110.0, "fait_base": 33.0, "unite": "م²"},
            "A.03 Cloison 0.25m": {"objectif": 1150.0, "fait_base": 345.0, "unite": "م²"},
            "A.04 Cloison 0.20m": {"objectif": 5.0, "fait_base": 1.5, "unite": "م²"},
            "A.05 Cloison 0.15m": {"objectif": 180.0, "fait_base": 54.0, "unite": "م²"},
            "A.06 Cloison 0.10m": {"objectif": 400.0, "fait_base": 120.0, "unite": "م²"},
            "B-1 Enduit extérieur": {"objectif": 4700.0, "fait_base": 1410.0, "unite": "م²"},
            "B-2 Enduit intérieur": {"objectif": 2050.0, "fait_base": 615.0, "unite": "م²"},
            "B-3 Enduit sous plafond": {"objectif": 1900.0, "fait_base": 570.0, "unite": "م²"},
            "B-4 Enduit grillagé": {"objectif": 350.0, "fait_base": 105.0, "unite": "م²"},
            "B-5 Enduit de ravoirage": {"objectif": 850.0, "fait_base": 255.0, "unite": "م²"},
            "C-1 Carrelage marbré 25x25": {"objectif": 1150.0, "fait_base": 345.0, "unite": "م²"},
            "C-2 Carrelage carreaux": {"objectif": 2400.0, "fait_base": 720.0, "unite": "م²"},
            "C-3 Revêtement carreaux": {"objectif": 190.0, "fait_base": 57.0, "unite": "م²"},
            "C-4 Plinthe": {"objectif": 1000.0, "fait_base": 300.0, "unite": "ml"},
            "C-5 Revêtement extérieur": {"objectif": 15.0, "fait_base": 4.5, "unite": "م²"},
            "C-6 Seuils en marbre Thala": {"objectif": 15.0, "fait_base": 4.5, "unite": "م²"},
            "C-7 Siffle en marbre Thala": {"objectif": 50.0, "fait_base": 15.0, "unite": "ml"},
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
                    for d_key, d_val in data[proj]["jours"].items():
                        d_val.setdefault("presences", {})
                        d_val.setdefault("avancement", {})
                        d_val.setdefault("visite_note", "")
                        if d_val.get("etat") == "visite":
                            d_val["etat"] = "vert"
                            if not d_val["visite_note"]:
                                d_val["visite_note"] = d_val.get("details", {}).get("travail", "زيارة رسمية")
                    for o_key, o_val in data[proj]["ouvriers"].items():
                        o_val.setdefault("statut", "نشط")
                        if "jours_base" not in o_val:
                            o_val["jours_base"] = o_val.get("jours_total", 30.0)
                        o_val.setdefault("semaine", {j: 0.0 for j in jours_semaine_noms})
                    for a_key, a_val in data[proj]["articles"].items():
                        if "fait_base" not in a_val:
                            a_val["fait_base"] = a_val.get("fait_total", 0.0)
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

# دوال حساب المجاميع الديناميكية من الرزنامة والقاعدة
def calc_worker_days(p_data, nom_ouv, start_d=None, end_d=None):
    jours_cal = 0.0
    for d_str, j_info in p_data["jours"].items():
        try:
            d_obj = date.fromisoformat(d_str)
            if start_d and d_obj < start_d:
                continue
            if end_d and d_obj > end_d:
                continue
            jours_cal += float(j_info.get("presences", {}).get(nom_ouv, 0.0))
        except Exception:
            pass
    return jours_cal

def calc_article_qty(p_data, nom_art, start_d=None, end_d=None):
    qty_cal = 0.0
    for d_str, j_info in p_data["jours"].items():
        try:
            d_obj = date.fromisoformat(d_str)
            if start_d and d_obj < start_d:
                continue
            if end_d and d_obj > end_d:
                continue
            qty_cal += float(j_info.get("avancement", {}).get(nom_art, 0.0))
        except Exception:
            pass
    return qty_cal

# ==========================================
# القائمة الجانبية: الشعار + محرك البحث الشامل + إدارة العمال
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
        st.sidebar.image(logo_path, width=100)
else:
    st.sidebar.markdown("<h1 style='text-align: center; margin:0;'>🏗️</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p class='brand-title'>H.O Bâtiment</p><p class='brand-subtitle'>Agent IA — Central Hub</p></div>", unsafe_allow_html=True)

projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", list(base_donnees_projets.keys()))
p_data = base_donnees_projets[projet_choisi]
donnees_chantier = p_data["jours"]
date_debut = date.fromisoformat(p_data["date_debut"])

if 'jour_clique' not in st.session_state or st.session_state.jour_clique is None:
    st.session_state.jour_clique = date.today().isoformat()

def set_jour(jour):
    st.session_state.jour_clique = jour

# ------------------------------------------
# محرك البحث الشامل في القائمة الجانبية (Recherche IA)
# ------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 محرك البحث والتصفية (Recherche IA)")

search_query = st.sidebar.text_input("🔎 اكتب اسم عامل أو بند (Article):", placeholder="مثال: بشير، Bordure، Cloison...")
type_recherche = st.sidebar.radio("تصنيف البحث:", ["👷 بحث عن خدام", "🧱 بحث عن بند (Article)"], horizontal=True)

periode_filtre = st.sidebar.selectbox("📅 الفترة الزمنية للبحث:", [
    "الكل (منذ بداية المشروع)",
    "الأسبوع الحالي (الجمعة الحالية)",
    "حسب الشهر",
    "بين تاريخين (فترة مخصصة)"
])

d_start, d_end = None, None
if periode_filtre == "الأسبوع الحالي (الجمعة الحالية)":
    today_d = date.today()
    d_start = today_d - timedelta(days=today_d.weekday())
    d_end = d_start + timedelta(days=6)
elif periode_filtre == "حسب الشهر":
    mois_choisi_nom = st.sidebar.selectbox("اختر الشهر:", mois_arabes, index=date.today().month - 1)
    m_idx = mois_arabes.index(mois_choisi_nom) + 1
    annee_rech = date_debut.year
    _, last_day = calendar.monthrange(annee_rech, m_idx)
    d_start = date(annee_rech, m_idx, 1)
    d_end = date(annee_rech, m_idx, last_day)
elif periode_filtre == "بين تاريخين (فترة مخصصة)":
    c_d1, c_d2 = st.sidebar.columns(2)
    d_start = c_d1.date_input("من:", value=date_debut, key="rech_d1")
    d_end = c_d2.date_input("إلى:", value=date.today(), key="rech_d2")

# 1. نتائج البحث عن خدام
if type_recherche == "👷 بحث عن خدام":
    tous_ouvriers = list(p_data["ouvriers"].keys())
    ouvriers_filtres = [n for n in tous_ouvriers if search_query.strip().lower() in n.lower()] if search_query.strip() else tous_ouvriers
    
    ouvrier_choisi = st.sidebar.selectbox("👤 اختر الخدام من النتائج:",ouvriers_filtres if ouvriers_filtres else ["لا توجد نتائج"])
    
    if ouvrier_choisi in p_data["ouvriers"]:
        o = p_data["ouvriers"][ouvrier_choisi]
        statut_actuel = o.get("statut", "نشط")
        badge_color = "🟢 نشط" if statut_actuel == "نشط" else ("🟠 معلق مؤقتاً" if statut_actuel == "معلق" else "🔴 حساب مقفول")
        
        st.sidebar.markdown(f"#### 👷‍♂️ {ouvrier_choisi} ({badge_color})")
        st.sidebar.write(f"🛠️ **الاختصاص:** {o['specialite']} | 📞 {o['tel']}")
        st.sidebar.write(f"💵 **الأجر اليومي:** {o['taux_jour']} د")
        
        # حساب الأيام
        jours_sem_courante = sum(float(v) for v in o.get("semaine", {}).values())
        jours_hist_total = calc_worker_days(p_data, ouvrier_choisi)
        jours_cumul_global = o.get("jours_base", 0.0) + jours_hist_total + jours_sem_courante
        
        if periode_filtre == "الكل (منذ بداية المشروع)":
            jours_periode = jours_cumul_global
        elif periode_filtre == "الأسبوع الحالي (الجمعة الحالية)":
            jours_periode = jours_sem_courante + calc_worker_days(p_data, ouvrier_choisi, d_start, d_end)
        else:
            jours_periode = calc_worker_days(p_data, ouvrier_choisi, d_start, d_end)
            
        st.sidebar.info(
            f"📊 **نتيجة الفترة ({periode_filtre}):**\n"
            f"- أيام العمل: **{jours_periode} يوم**\n"
            f"- استحقاق الفترة: **{jours_periode * o['taux_jour']} دينار**"
        )
        
        salaire_global_merite = jours_cumul_global * o['taux_jour']
        solde_restant = salaire_global_merite - (o['paye_total'] + o['avances'])
        
        st.sidebar.write(f"📈 **المجموع الجملي بالمشروع:** {jours_cumul_global} يوم ({salaire_global_merite} د)")
        st.sidebar.write(f"💰 **خالص:** {o['paye_total']} د | **آفونس:** {o['avances']} د")
        if solde_restant > 0:
            st.sidebar.error(f"🔴 الباقي للخلاص: {solde_restant} دينار")
        else:
            st.sidebar.success("✅ الحساب خالص ومريقل (0 د)")
            
        # تغيير حالة العامل أو قفل الحساب
        with st.sidebar.expander("⚙️ إدارة حالة الحساب (تعليق / قفل الحساب)"):
            nouveau_statut = st.selectbox("تغيير وضعية العامل:", ["نشط", "معلق", "مقفول"], index=["نشط", "معلق", "مقفول"].index(statut_actuel), key=f"st_{ouvrier_choisi}")
            if st.button("💾 تحديث وضعية العامل", use_container_width=True):
                o["statut"] = nouveau_statut
                save_db(base_donnees_projets)
                st.rerun()
            if solde_restant > 0 and st.button("🔒 تصفية المستحقات وقفل الحساب نهائياً", use_container_width=True):
                o["paye_total"] += solde_restant
                o["statut"] = "مقفول"
                save_db(base_donnees_projets)
                st.sidebar.success("تم خلاص الباقي وقفل الحساب!")
                st.rerun()

# 2. نتائج البحث عن بند (Article)
else:
    tous_articles = list(p_data["articles"].keys())
    articles_filtres = [a for a in tous_articles if search_query.strip().lower() in a.lower()] if search_query.strip() else tous_articles
    
    article_selectionne = st.sidebar.selectbox("🧱 اختر البند من النتائج:", articles_filtres if articles_filtres else ["لا توجد نتائج"])
    
    if article_selectionne in p_data["articles"]:
        art_info = p_data["articles"][article_selectionne]
        unite_a = art_info["unite"]
        
        # حساب الكميات (الأسبوعية، الشهرية، المخصصة، والجملي)
        today_d = date.today()
        start_week = today_d - timedelta(days=today_d.weekday())
        start_month = date(today_d.year, today_d.month, 1)
        
        qty_semaine = calc_article_qty(p_data, article_selectionne, start_week, today_d)
        qty_mois = calc_article_qty(p_data, article_selectionne, start_month, today_d)
        qty_hist_all = calc_article_qty(p_data, article_selectionne)
        qty_total_global = art_info.get("fait_base", 0.0) + qty_hist_all
        
        if periode_filtre == "الكل (منذ بداية المشروع)":
            qty_periode = qty_total_global
        else:
            qty_periode = calc_article_qty(p_data, article_selectionne, d_start, d_end)
            
        pourcentage = min(int((qty_total_global / art_info['objectif']) * 100), 100) if art_info['objectif'] > 0 else 0
        reste_contrat = max(art_info['objectif'] - qty_total_global, 0.0)
        
        st.sidebar.markdown(f"#### 🧱 {article_selectionne}")
        st.sidebar.write(f"📊 **نسبة الإنجاز الجملية:** {pourcentage}%")
        st.sidebar.progress(pourcentage)
        
        st.sidebar.info(
            f"📌 **تفاصيل الإنجاز ({unite_a}):**\n"
            f"- 🔎 خلال الفترة المختارة: **{qty_periode} {unite_a}**\n"
            f"- ⚡ هذا الأسبوع: **{qty_semaine} {unite_a}**\n"
            f"- 📅 هذا الشهر: **{qty_mois} {unite_a}**\n"
            f"- ✅ المنجز الجملي: **{qty_total_global} / {art_info['objectif']} {unite_a}**\n"
            f"- ⏳ المتبقي بالعقد: **{reste_contrat} {unite_a}**"
        )

# ------------------------------------------
# إضافة عامل جديد للمشروع
# ------------------------------------------
st.sidebar.markdown("---")
with st.sidebar.expander("➕ إضافة عامل جديد للمشروع"):
    new_nom = st.text_input("الاسم واللقب:", key="new_ouv_nom")
    new_spec = st.text_input("الاختصاص (بناي، مانوفري...):", key="new_ouv_spec")
    new_tel = st.text_input("رقم الهاتف:", key="new_ouv_tel")
    new_taux = st.number_input("الأجر اليومي (دينار):", min_value=10.0, value=50.0, step=5.0, key="new_ouv_taux")
    if st.button("✅ تسجيل العامل الجديد", use_container_width=True):
        if new_nom.strip():
            p_data["ouvriers"][new_nom.strip()] = {
                "specialite": new_spec or "عامل",
                "tel": new_tel or "-",
                "taux_jour": new_taux,
                "statut": "نشط",
                "jours_base": 0.0,
                "paye_total": 0.0,
                "avances": 0.0,
                "semaine": {j: 0.0 for j in jours_semaine_noms}
            }
            save_db(base_donnees_projets)
            st.sidebar.success(f"تمت إضافة {new_nom} بنجاح!")
            st.rerun()
        else:
            st.sidebar.warning("يرجى كتابة اسم العامل.")

# ==========================================
# الواجهة الرئيسية: الإحصائيات + مركز التحكم + آلة الزمن
# ==========================================
st.title(f"🤖 H.O Bâtiment — {projet_choisi}")

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
col_stat1.metric("🟢 أيام العمل الفعلية", f"{p_data['stats'].get('vert', 0)} يوم")
col_stat2.metric("🟡 إيقاف الأشغال", f"{p_data['stats'].get('jaune', 0)} يوم")
col_stat3.metric("🌧️ سوء الأحوال الجوية", f"{p_data['stats'].get('meteo', 0)} يوم")
col_stat4.metric("🔵 راحة عادية", f"{p_data['stats'].get('conge', 0)} يوم")

# ==========================================
# 1. آلة الزمن: تعديل أي يوم يتم النقر عليه في الرزنامة + إرسال التقرير
# ==========================================
jour = st.session_state.jour_clique
st.markdown(f"<div class='time-machine-box'><h4>⏳ المتابعة اليومية وآلة الزمن — تاريخ اليوم المختار: {jour}</h4><small>انقر على أي يوم في الرزنامة أسفله للرجوع بالزمن ومراجعة أو تعديل كل معطياته (حضور، كميات، صور، زيارات رسمية).</small></div>", unsafe_allow_html=True)

if jour not in donnees_chantier:
    donnees_chantier[jour] = {"etat": "vert", "visite_note": "", "details": {"travail": "أشغال اعتيادية بالشانطي"}, "photo": "", "presences": {}, "avancement": {}}

j_data = donnees_chantier[jour]
j_data.setdefault("visite_note", "")
j_data.setdefault("presences", {})
j_data.setdefault("avancement", {})

tab_j_etat, tab_j_ouv, tab_j_art, tab_j_ph, tab_j_rep = st.tabs([
    f"📅 1. يوميات ({jour}) والزيارات",
    f"👷 2. حضور الخدامة ({jour})",
    f"🧱 3. كميات الأشغال ({jour})",
    f"📸 4. صور الشانطي ({jour})",
    f"📲 5. تقرير اليوم (WhatsApp / Email)"
])

# تبويب 1: حالة اليوم + ملاحظة الزيارة الرسمية المستقلة
with tab_j_etat:
    c_et1, c_et2 = st.columns(2)
    etats_options = [
        ("vert", "🟢 يوم عمل فعلي"),
        ("jaune", "🟡 إيقاف أشغال"),
        ("meteo", "🌧️ توقف بسبب سوء الأحوال الجوية"),
        ("conge", "🔵 يوم راحة عادي")
    ]
    etat_codes = [x[0] for x in etats_options]
    idx_etat = etat_codes.index(j_data.get("etat", "vert")) if j_data.get("etat") in etat_codes else 0
    
    with c_et1:
        nouvel_etat = st.selectbox("حالة الشانطي في هذا اليوم:", etats_options, index=idx_etat, format_func=lambda x: x[1], key=f"et_{jour}")
        detail_cle = "probleme" if nouvel_etat[0] in ["jaune", "meteo"] else "travail"
        val_note_actuelle = j_data.get("details", {}).get("travail") or j_data.get("details", {}).get("probleme", "")
        nouvelle_note = st.text_input("تقرير الأشغال أو سبب التوقف:", value=val_note_actuelle, key=f"nt_{jour}")
        
    with c_et2:
        has_visite = st.checkbox("📋 تسجيل زيارة رسمية / ملاحظة رقابة في هذا اليوم", value=bool(j_data.get("visite_note", "")), key=f"chk_vis_{jour}")
        visite_texte = ""
        if has_visite:
            visite_texte = st.text_input("تفاصيل وملاحظات الزيارة الرسمية:", value=j_data.get("visite_note", ""), placeholder="مثال: زيارة المهندس، مكتب المراقبة، ملاحظات فنية...", key=f"txt_vis_{jour}")
            
    if st.button("💾 حفظ يوميات الشانطي والزيارات", key=f"save_et_{jour}", use_container_width=True):
        j_data["etat"] = nouvel_etat[0]
        j_data["details"] = {detail_cle: nouvelle_note}
        j_data["visite_note"] = visite_texte if has_visite else ""
        save_db(base_donnees_projets)
        st.success(f"✅ تم حفظ حالة يوم {jour} وملاحظات الزيارة بنجاح!")

    if j_data.get("visite_note"):
        st.markdown(f"<div class='visite-badge'>📋 ملاحظة زيارة رسمية موثقة: {j_data['visite_note']}</div>", unsafe_allow_html=True)

# تبويب 2: حضور الخدامة في اليوم المختار (مع مراعاة حالة العامل)
with tab_j_ouv:
    st.markdown(f"**✅ كوشي العمال الحاضرين في يوم ({jour}) — يتحدث الحساب المالي والجملي أوتوماتيكياً:**")
    cols_h_ouv = st.columns(3)
    idx_col = 0
    modif_hist_ouv = False
    for nom_ouv, info_ouv in p_data["ouvriers"].items():
        statut_o = info_ouv.get("statut", "نشط")
        if statut_o == "مقفول":
            continue
        with cols_h_ouv[idx_col % 3]:
            est_pres_jour = float(j_data["presences"].get(nom_ouv, 0.0)) >= 0.5
            label_ouv = f"👷‍♂️ {nom_ouv} ({info_ouv['specialite']})" + (" [معلق]" if statut_o == "معلق" else "")
            coche_j = st.checkbox(label_ouv, value=est_pres_jour, key=f"chk_hist_{projet_choisi}_{jour}_{nom_ouv}")
            val_pres_j = 1.0 if coche_j else 0.0
            if float(j_data["presences"].get(nom_ouv, 0.0)) != val_pres_j:
                j_data["presences"][nom_ouv] = val_pres_j
                modif_hist_ouv = True
        idx_col += 1
    if modif_hist_ouv:
        save_db(base_donnees_projets)
        st.toast(f"✅ تم تحديث حضور يوم {jour} في قاعدة البيانات!")

# تبويب 3: كميات الأشغال المنجزة في اليوم المختار
with tab_j_art:
    if j_data["avancement"]:
        st.markdown(f"**📊 الأشغال المسجلة في يوم {jour}:**")
        for a_nom, a_qty in list(j_data["avancement"].items()):
            u_str = p_data["articles"].get(a_nom, {}).get("unite", "")
            st.info(f"🧱 **{a_nom}:** {a_qty} {u_str}")
    else:
        st.write("لم يتم تسجيل كميات منجزة في هذا التاريخ بعد.")
        
    c_ar1, c_ar2, c_ar3 = st.columns([2, 2, 1])
    with c_ar1:
        art_j_sel = st.selectbox("اختر البند لتسجيل أو تعديل كمية هذا اليوم:", list(p_data["articles"].keys()), key=f"art_s_{jour}")
    with c_ar2:
        val_act_art = float(j_data["avancement"].get(art_j_sel, 0.0))
        u_art_sel = p_data["articles"][art_j_sel]["unite"]
        qty_j_val = st.number_input(f"الكمية المنجزة ليوم {jour} ({u_art_sel}):", min_value=0.0, value=val_act_art, step=5.0, key=f"qty_s_{jour}_{art_j_sel}")
    with c_ar3:
        st.write("")
        if st.button("✅ حفظ الكمية", key=f"btn_art_{jour}", use_container_width=True):
            if qty_j_val > 0:
                j_data["avancement"][art_j_sel] = qty_j_val
            elif art_j_sel in j_data["avancement"]:
                del j_data["avancement"][art_j_sel]
            save_db(base_donnees_projets)
            st.success(f"تم تحديث كمية ({art_j_sel}) ليوم {jour}!")
            st.rerun()

# تبويب 4: صور الشانطي الخاصة باليوم المختار
with tab_j_ph:
    cp_j1, cp_j2 = st.columns(2)
    with cp_j1:
        mode_cap_j = st.radio("إضافة صورة لتوثيق هذا اليوم:", ["📂 رفع صورة من الجهاز/الهاتف", "📷 التقاط بالكاميرا"], horizontal=True, key=f"rad_ph_{jour}")
        if mode_cap_j == "📷 التقاط بالكاميرا":
            img_j_up = st.camera_input("التقط صورة:", key=f"cam_{jour}")
        else:
            img_j_up = st.file_uploader("اختر صورة:", type=["jpg", "png", "jpeg"], key=f"up_ph_{jour}")
        desc_ph_j = st.text_input("وصف الصورة:", placeholder="مثال: أشغال البوردور / تقدم البناء...", key=f"dsc_ph_{jour}")
        if st.button("💾 حفظ الصورة ليوم " + jour, key=f"btn_save_ph_{jour}", use_container_width=True):
            if img_j_up is not None:
                path_ph_j = f"uploads/chantier_photos/{jour}_{len(p_data['photos_chantier'])+1}.jpg"
                with open(path_ph_j, "wb") as f:
                    f.write(img_j_up.getbuffer())
                j_data["photo"] = path_ph_j
                p_data["photos_chantier"].append({"date": jour, "article": "توثيق يومي", "desc": desc_ph_j or f"صورة يوم {jour}", "path": path_ph_j})
                save_db(base_donnees_projets)
                st.success("تم حفظ الصورة وربطها باليوم!")
                st.rerun()
    with cp_j2:
        if j_data.get("photo") and os.path.exists(j_data["photo"]):
            st.image(j_data["photo"], caption=f"📸 الصورة الموثقة ليوم {jour}", use_container_width=True)
        else:
            st.info("لا توجد صورة مرفوعة لهذا اليوم بعد.")

# تبويب 5: تحرير وإرسال التقرير اليومي عبر WhatsApp أو Email
with tab_j_rep:
    ouv_presents_list = [k for k, v in j_data.get("presences", {}).items() if float(v) >= 0.5]
    art_faits_list = [f"- {k}: {v} {p_data['articles'][k]['unite']}" for k, v in j_data.get("avancement", {}).items()]
    etat_label_dict = {"vert": "يوم عمل فعلي 🟢", "jaune": "إيقاف أشغال 🟡", "meteo": "توقف بسبب سوء الأحوال الجوية 🌧️", "conge": "يوم راحة 🔵"}
    note_jour_txt = j_data.get("details", {}).get("travail") or j_data.get("details", {}).get("probleme", "لا توجد ملاحظات")
    
    rapport_texte = (
        f"🏗️ *تقرير شانطي H.O Bâtiment*\n"
        f"📂 *المشروع:* {projet_choisi}\n"
        f"📅 *التاريخ:* {jour}\n"
        f"📌 *حالة الشانطي:* {etat_label_dict.get(j_data.get('etat', 'vert'), 'عمل فعلي')}\n"
        f"📝 *الملاحظات اليومية:* {note_jour_txt}\n"
    )
    if j_data.get("visite_note"):
        rapport_texte += f"📋 *ملاحظة زيارة رسمية:* {j_data['visite_note']}\n"
    rapport_texte += f"\n👷 *العمال الحاضرون ({len(ouv_presents_list)}):*\n"
    rapport_texte += (", ".join(ouv_presents_list) if ouv_presents_list else "لم يسجل حضور") + "\n"
    rapport_texte += f"\n🧱 *الكميات المنجزة اليوم:*\n"
    rapport_texte += ("\n".join(art_faits_list) if art_faits_list else "لم تسجل كميات") + "\n"
    
    st.text_area("📄 نص التقرير اليومي الجاهز للإرسال:", value=rapport_texte, height=210, key=f"rep_area_{jour}")
    
    encoded_rep = urllib.parse.quote(rapport_texte)
    encoded_subj = urllib.parse.quote(f"تقرير شانطي {projet_choisi} - {jour}")
    
    col_sh1, col_sh2 = st.columns(2)
    with col_sh1:
        st.markdown(f'<a href="https://wa.me/?text={encoded_rep}" target="_blank" class="share-btn wa-btn">🟢 إرسال التقرير عبر WhatsApp</a>', unsafe_allow_html=True)
    with col_sh2:
        st.markdown(f'<a href="mailto:?subject={encoded_subj}&body={encoded_rep}" target="_blank" class="share-btn mail-btn">📧 إرسال التقرير عبر Email</a>', unsafe_allow_html=True)

# ==========================================
# 2. مركز التحكم السريع (الجمعة الحالية + الآفونس + 3D + البلانات)
# ==========================================
st.markdown("---")
with st.expander("📱 **مركز التحكم السريع (ورقة حضور الأسبوع، الآفونس، تصاور 3D، وقراءة البلانات IA)**", expanded=False):
    tab_sem, tab_av, tab_3d, tab_plans = st.tabs([
        "👷 1. ورقة حضور الجمعة الحالية (كوشاج ✅)",
        "💰 2. تسجيل آفونس أو خلاص",
        "🏢 3. تصاور 3D",
        "📐 4. قراءة البلانات (IA)"
    ])
    
    with tab_sem:
        st.markdown("##### ✅ **ورقة الحضور السريعة للأسبوع الحالي (للعمال النشطين):**")
        changement_presence = False
        for nom_ouv, info_ouv in p_data["ouvriers"].items():
            if info_ouv.get("statut", "نشط") != "نشط":
                continue
            st.markdown(f"<div class='worker-row'><b>👷‍♂️ {nom_ouv}</b> <span style='color:gray; font-size:13px;'>({info_ouv['specialite']} — {info_ouv['taux_jour']} د/يوم)</span></div>", unsafe_allow_html=True)
            cols_check = st.columns(8)
            total_sem = 0.0
            for idx_j, js in enumerate(jours_semaine_noms):
                est_present = float(info_ouv.get("semaine", {}).get(js, 0.0)) >= 0.5
                nouvelle_val = cols_check[idx_j].checkbox(f"{js}", value=est_present, key=f"chk_mob_{projet_choisi}_{nom_ouv}_{js}")
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
            st.toast("✅ تم حفظ حضور الأسبوع تلقائياً!")

    with tab_av:
        c_av1, c_av2, c_av3, c_av4 = st.columns([2, 2, 2, 2])
        with c_av1:
            ouv_mob = st.selectbox("اختر الخدام:", list(p_data["ouvriers"].keys()), key="mob_ouv")
        with c_av2:
            avance_plus = st.number_input("المبلغ (دينار):", min_value=0.0, value=0.0, step=10.0, key="mob_av")
        with c_av3:
            type_paiement = st.radio("نوع الدفع:", ["آفونس (Avance)", "خلاص صافي (Payé)"], horizontal=True)
        with c_av4:
            st.write("")
            if st.button("💵 تسجيل المبلغ", use_container_width=True):
                if avance_plus > 0:
                    if type_paiement == "آفونس (Avance)":
                        p_data["ouvriers"][ouv_mob]["avances"] += avance_plus
                    else:
                        p_data["ouvriers"][ouv_mob]["paye_total"] += avance_plus
                    save_db(base_donnees_projets)
                    st.success(f"تم تسجيل {avance_plus} د لـ ({ouv_mob}) بنجاح!")

    with tab_3d:
        c3d1, c3d2 = st.columns(2)
        with c3d1:
            titre_3d = st.text_input("عنوان التصميم 3D:", key="t_3d")
            zone_3d = st.text_input("المنطقة أو البند الموافق:", key="z_3d")
        with c3d2:
            img_3d = st.file_uploader("ارفع صورة 3D (Render):", type=["jpg", "png", "jpeg"], key="up_3d")
        if st.button("✅ إضافة التصميم 3D للمعرض", use_container_width=True) and img_3d is not None:
            path_3d = f"uploads/3d_models/3d_{len(p_data['models_3d'])+1}.jpg"
            with open(path_3d, "wb") as f:
                f.write(img_3d.getbuffer())
            p_data["models_3d"].append({"titre": titre_3d or "تصميم 3D", "zone": zone_3d, "path": path_3d})
            save_db(base_donnees_projets)
            st.success("تمت إضافة التصميم 3D بنجاح!")
        if p_data["models_3d"]:
            cols_3d = st.columns(2)
            for idx, m3d in enumerate(p_data["models_3d"]):
                if os.path.exists(m3d["path"]):
                    with cols_3d[idx % 2]:
                        st.image(m3d["path"], caption=f"🏢 {m3d['titre']} ({m3d['zone']})", use_container_width=True)

    with tab_plans:
        cpl1, cpl2 = st.columns(2)
        with cpl1:
            nom_plan = st.text_input("اسم البلان أو الطابق:", key="nom_pl")
            article_lie = st.selectbox("البند المرتبط بالبلان:", list(p_data["articles"].keys()), key="art_pl")
            notes_plan = st.text_area("ملاحظات الأبعاد والكوتاسيون:", key="note_pl")
        with cpl2:
            img_plan = st.file_uploader("ارفع صورة البلان:", type=["jpg", "png", "jpeg"], key="up_pl")
        if st.button("🤖 حفظ البلان وتحليل المعطيات", use_container_width=True) and img_plan is not None:
            path_pl = f"uploads/plans/plan_{len(p_data['plans_ia'])+1}.jpg"
            with open(path_pl, "wb") as f:
                f.write(img_plan.getbuffer())
            obj_art = p_data["articles"][article_lie]["objectif"]
            fait_art = p_data["articles"][article_lie].get("fait_base", 0.0) + calc_article_qty(p_data, article_lie)
            unite_a = p_data["articles"][article_lie]["unite"]
            synthese_ia = f"📐 تحليل البلان ({nom_plan or 'بلان هندسي'}): مرتبط ببند [{article_lie}] — الهدف التعاقدي: {obj_art} {unite_a} | المنجز الجملي: {fait_art} {unite_a}. الملاحظات: {notes_plan or 'مطابق للمواصفات.'}"
            p_data["plans_ia"].append({"nom": nom_plan or "بلان هندسي", "article": article_lie, "synthese": synthese_ia, "path": path_pl})
            save_db(base_donnees_projets)
            st.success("تم حفظ البلان وإصدار التحليل الفني!")
        for pl in reversed(p_data["plans_ia"]):
            col_p_img, col_p_txt = st.columns([1, 2])
            with col_p_img:
                if os.path.exists(pl["path"]):
                    st.image(pl["path"], use_container_width=True)
            with col_p_txt:
                st.markdown(f"#### 📐 {pl['nom']} — ({pl['article']})")
                st.info(pl["synthese"])

# ==========================================
# 3. الرزنامة التفاعلية للرجوع بالزمن
# ==========================================
st.markdown("---")
st.markdown("### 📅 رزنامة المتابعة اليومية (انقر على أي يوم لمراجعته أو تعديله الفوق)")
st.caption("🟢 عمل فعلي | 🟡 إيقاف أشغال | 🌧️ توقف بسبب سوء الأحوال الجوية | 🔵 راحة | 📋 يوم به ملاحظة زيارة رسمية")

annee = date_debut.year
mois_a_afficher = list(range(date_debut.month, 13))

def get_icone_jour(date_str):
    if date_str in donnees_chantier:
        j_obj
