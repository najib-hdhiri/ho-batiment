import streamlit as st
import calendar
from datetime import date
import os
import json

st.set_page_config(page_title="H.O Construction - Tableau de Bord IA", page_icon="🏗️", layout="wide")

# ==========================================
# تصميم CSS
# ==========================================
st.markdown("""
    <style>
    .brand-container { text-align: center; background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .brand-title { color: #ff4b4b; font-size: 20px; font-weight: bold; margin: 5px 0 0 0; }
    .brand-subtitle { color: gray; font-size: 12px; margin-top: 2px; margin-bottom: 0; }
    input[type="checkbox"] { transform: scale(1.3); accent-color: #28a745 !important; cursor: pointer; }
    .worker-row { background-color: #f8f9fa; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-right: 4px solid #28a745; }
    .time-machine-box { background-color: #fff3cd; border: 2px solid #ffc107; padding: 15px; border-radius: 10px; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

for folder in ["uploads", "uploads/chantier_photos", "uploads/3d_models", "uploads/plans"]:
    os.makedirs(folder, exist_ok=True)

DATA_FILE = "uploads/chantier_data.json"

# ==========================================
# قاعدة البيانات
# ==========================================
default_db = {
    "خليج الشعرة (Khalij Chaara)": {
        "date_debut": "2026-05-18",
        "stats": {"vert": 65, "jaune": 44, "gris": 12, "meteo": 8, "conge": 5},
        "jours": {},
        "photos_chantier": [], "models_3d": [], "plans_ia": [],
        "ouvriers": {
            "بشير بن حميد": {"specialite": "رئيس مجموعة / بناي", "tel": "99 888 777", "taux_jour": 65, "jours_total": 50.0, "paye_total": 2500.0, "avances": 400.0, "semaine": {}},
            "صالح بن عمار": {"specialite": "بناي محترف", "tel": "98 123 456", "taux_jour": 60, "jours_total": 65.0, "paye_total": 3000.0, "avances": 500.0, "semaine": {}},
        },
        "articles": {
            "Bordure T2": {"objectif": 7700.0, "fait_total": 1540.0, "fait_semaine": 120.0, "unite": "ml"},
            "Pavé autobloquant": {"objectif": 15500.0, "fait_total": 3100.0, "fait_semaine": 50.0, "unite": "م²"},
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
                    # ضمان وجود هيكل الحضور والأشغال لكل يوم للرجوع بالزمن
                    for d_key in data[proj]["jours"]:
                        data[proj]["jours"][d_key].setdefault("presences", {})
                        data[proj]["jours"][d_key].setdefault("avancement", {})
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
jours_semaine_noms = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]

# ==========================================
# القائمة الجانبية
# ==========================================
st.sidebar.markdown('<div class="brand-container">', unsafe_allow_html=True)
st.sidebar.markdown("<h1 style='text-align: center; margin:0;'>🏗️</h1><p class='brand-title'>H.O Bâtiment</p><p class='brand-subtitle'>Agent IA</p></div>", unsafe_allow_html=True)

projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", list(base_donnees_projets.keys()))
p_data = base_donnees_projets[projet_choisi]
donnees_chantier = p_data["jours"]
date_debut = date.fromisoformat(p_data["date_debut"])

if 'jour_clique' not in st.session_state:
    st.session_state.jour_clique = None

def set_jour(jour):
    st.session_state.jour_clique = jour

# ==========================================
# إحصائيات ورزنامة الشانطي
# ==========================================
st.title(f"🤖 H.O Bâtiment — {projet_choisi}")
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
col_stat1.metric("🟢 أيام العمل الفعلية", f"{p_data['stats'].get('vert', 0)} يوم")
col_stat2.metric("🟡 إيقاف الأشغال", f"{p_data['stats'].get('jaune', 0)} يوم")
col_stat3.metric("🌧️ توقف طقس", f"{p_data['stats'].get('meteo', 0)} يوم")
col_stat4.metric("🔵 راحة عادية", f"{p_data['stats'].get('conge', 0)} يوم")
st.markdown("---")

# ==========================================
# آلة الزمن: عرض وتعديل اليوم المختار (Historical Tracking)
# ==========================================
jour = st.session_state.jour_clique
if jour:
    st.markdown(f"<div class='time-machine-box'><h3>⏳ آلة الزمن: مراجعة وتعديل يوم {jour}</h3></div>", unsafe_allow_html=True)
    
    # تهيئة اليوم إذا لم يكن مسجلاً
    if jour not in donnees_chantier:
        donnees_chantier[jour] = {"etat": "vert", "details": {"travail": "لم يتم تسجيل تفاصيل"}, "photo": "", "presences": {}, "avancement": {}}
    
    j_data = donnees_chantier[jour]
    
    tab_j_etat, tab_j_ouv, tab_j_art, tab_j_ph = st.tabs(["📅 حالة اليوم", "👷 حضور الخدامة", "🧱 كميات الأشغال", "📸 صورة اليوم"])
    
    # 1. تعديل حالة اليوم والملاحظات
    with tab_j_etat:
        c_et1, c_et2 = st.columns(2)
        with c_et1:
            nouvel_etat = st.selectbox("حالة الشانطي في هذا اليوم:", [
                ("vert", "🟢 يوم عمل عادي"), ("jaune", "🟡 إيقاف أشغال"), 
                ("meteo", "🌧️ طقس خايب"), ("conge", "🔵 يوم راحة"), ("visite", "📋 زيارة رسمية")
            ], index=["vert", "jaune", "meteo", "conge", "visite"].index(j_data.get("etat", "vert")), format_func=lambda x: x[1], key=f"et_{jour}")
        with c_et2:
            detail_cle = "probleme" if j_data.get("etat") in ["jaune", "meteo"] else "travail"
            nouvelle_note = st.text_input("ملاحظات / تقرير:", value=j_data["details"].get(detail_cle, ""), key=f"nt_{jour}")
        
        if st.button("💾 حفظ حالة اليوم"):
            j_data["etat"] = nouvel_etat[0]
            cle_n = "probleme" if nouvel_etat[0] in ["jaune", "meteo"] else "travail"
            j_data["details"] = {cle_n: nouvelle_note}
            save_db(base_donnees_projets)
            st.success("تم تحديث حالة اليوم بنجاح!")

    # 2. تعديل حضور الخدامة في هذا اليوم القديم
    with tab_j_ouv:
        st.write("ضع علامة على العمال الذين حضروا في هذا التاريخ بالتحديد:")
        for nom_ouv, info_ouv in p_data["ouvriers"].items():
            est_present = j_data["presences"].get(nom_ouv, 0.0) >= 0.5
            cocher = st.checkbox(f"👷‍♂️ {nom_ouv} ({info_ouv['specialite']})", value=est_present, key=f"chk_hist_{jour}_{nom_ouv}")
            nouvelle_val_hist = 1.0 if cocher else 0.0
            
            if j_data["presences"].get(nom_ouv, 0.0) != nouvelle_val_hist:
                # إذا قام بتغيير الحضور، نعدل مجموع أيام العامل أوتوماتيكياً
                diff = nouvelle_val_hist - j_data["presences"].get(nom_ouv, 0.0)
                info_ouv["jours_total"] += diff
                j_data["presences"][nom_ouv] = nouvelle_val_hist
                save_db(base_donnees_projets)
                st.toast(f"✅ تم تصحيح حضور {nom_ouv} وتحديث مجموع أيامه!")

    # 3. تعديل أو إضافة أشغال في هذا اليوم
    with tab_j_art:
        st.write("الكميات المنجزة المسجلة في هذا اليوم:")
        for art_nom, qty in list(j_data["avancement"].items()):
            st.info(f"🧱 **{art_nom}:** {qty} {p_data['articles'][art_nom]['unite']}")
            
        st.write("---")
        c_art1, c_art2, c_art3 = st.columns([2, 2, 1])
        with c_art1:
            art_hist = st.selectbox("إضافة/تعديل بند:", list(p_data["articles"].keys()), key=f"art_h_{jour}")
        with c_art2:
            qty_hist = st.number_input(f"الكمية ({p_data['articles'][art_hist]['unite']}):", min_value=0.0, step=1.0, key=f"qty_h_{jour}")
        with c_art3:
            st.write("")
            if st.button("➕ حفظ الكمية", key=f"btn_h_{jour}"):
                ancienne_qty = j_data["avancement"].get(art_hist, 0.0)
                diff_qty = qty_hist - ancienne_qty
                p_data["articles"][art_hist]["fait_total"] += diff_qty
                j_data["avancement"][art_hist] = qty_hist
                save_db(base_donnees_projets)
                st.success(f"تم تسجيل {qty_hist} لـ {art_hist} وتحديث المجموع!")

    # 4. صورة الشانطي لذلك اليوم
    with tab_j_ph:
        photo_existante = j_data.get("photo", "")
        if photo_existante and os.path.exists(photo_existante):
            st.image(photo_existante, caption=f"📸 صورة الشانطي ليوم {jour}", width=350)
        else:
            img_hist = st.file_uploader("📂 إضافة صورة لهذا اليوم بأثر رجعي:", type=["jpg", "png", "jpeg"], key=f"ph_h_{jour}")
            if img_hist and st.button("💾 حفظ الصورة", key=f"btn_ph_{jour}"):
                path_h_ph = f"uploads/chantier_photos/{jour}_retro.jpg"
                with open(path_h_ph, "wb") as f:
                    f.write(img_hist.getbuffer())
                j_data["photo"] = path_h_ph
                save_db(base_donnees_projets)
                st.success("تم ربط الصورة باليوم!")
else:
    st.markdown("👉 **انقر على أي يوم في الرزنامة أسفله لاستعراض وتعديل يوميات الشانطي القديمة (آلة الزمن):**")

st.markdown("---")

# ==========================================
# رسم الرزنامة
# ==========================================
mois_arabes = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
annee = date_debut.year
mois_a_afficher = list(range(date_debut.month, 13))

def get_couleur_jour(date_str):
    if date_str in donnees_chantier:
        etat = donnees_chantier[date_str].get("etat", "vert")
        if etat == "vert": return "🟢"
        if etat == "visite": return "📋"
        if etat == "jaune": return "🟡"
        if etat == "meteo": return "🌧️"
        if etat == "conge": return "🔵"
    return "⬜"

for i in range(0, len(mois_a_afficher), 2):
    col1, col2 = st.columns(2)
    m1 = mois_a_afficher[i]
    with col1:
        st.markdown(f"<h5 style='text-align: center; background-color: #f0f2f6; padding: 5px; border-radius: 5px;'>شهر {mois_arabes[m1-1]} {annee}</h5>", unsafe_allow_html=True)
        jours_semaine = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
        cols_j1 = st.columns(7)
        for k, j in enumerate(jours_semaine): cols_j1[k].markdown(f"<div style='text-align: center; font-size: 11px; font-weight: bold;'>{j[:4]}</div>", unsafe_allow_html=True)
        
        for semaine in calendar.monthcalendar(annee, m1):
            cols = st.columns(7)
            for k, num_jour in enumerate(semaine):
                if num_jour == 0: cols[k].write("")
                else:
                    date_str = f"{annee}-{m1:02d}-{num_jour:02d}"
                    if date(annee, m1, num_jour) < date_debut: cols[k].markdown(f"<div style='text-align:center; color:grey; font-size: 12px;'>🚫</div>", unsafe_allow_html=True)
                    else: cols[k].button(f"{get_couleur_jour(date_str)} {num_jour}", key=f"btn_{projet_choisi}_{date_str}", on_click=set_jour, args=(date_str,), use_container_width=True)
                        
    if i + 1 < len(mois_a_afficher):
        m2 = mois_a_afficher[i+1]
        with col2:
            st.markdown(f"<h5 style='text-align: center; background-color: #f0f2f6; padding: 5px; border-radius: 5px;'>شهر {mois_arabes[m2-1]} {annee}</h5>", unsafe_allow_html=True)
            cols_j2 = st
