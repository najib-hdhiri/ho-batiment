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
    "Pavé autobloquant": "pave autobloquant بافي رصيف"
}

def match_smart(nom_item, query):
    if not query or not query.strip(): return True
    q = query.strip().lower()
    return q in (nom_item + " " + ALIASES_RECHERCHE.get(nom_item, "")).lower()

ALL_ARTICLES_DEFAULT = {
    "Bordure T2": {"objectif": 7700.0, "fait_total": 1540.0, "fait_semaine": 120.0, "unite": "ml"},
    "Pavé autobloquant": {"objectif": 15500.0, "fait_total": 3100.0, "fait_semaine": 50.0, "unite": "م²"}
}

ALL_OUVRIERS_DEFAULT = {
    "بشير بن حميد": {"specialite": "رئيس مجموعة / بناي", "tel": "99 888 777", "taux_jour": 65.0, "statut": "نشط", "date_cloture": "2026-05-18", "avances": 400.0, "paye_total": 2500.0, "semaine": {}},
    "صالح بن عمار": {"specialite": "بناي محترف", "tel": "98 123 456", "taux_jour": 60.0, "statut": "نشط", "date_cloture": "2026-05-18", "avances": 500.0, "paye_total": 3000.0, "semaine": {}},
    "الهادي العياري": {"specialite": "مانوفري", "tel": "22 345 678", "taux_jour": 40.0, "statut": "نشط", "date_cloture": "2026-05-18", "avances": 300.0, "paye_total": 1500.0, "semaine": {}},
    "جمعة المجبري": {"specialite": "رئيس فريق", "tel": "55 789 012", "taux_jour": 70.0, "statut": "نشط", "date_cloture": "2026-05-18", "avances": 200.0, "paye_total": 1500.0, "semaine": {}},
    "علي الطرابلسي": {"specialite": "بناي", "tel": "24 567 890", "taux_jour": 60.0, "statut": "نشط", "date_cloture": "2026-05-18", "avances": 100.0, "paye_total": 1000.0, "semaine": {}}
}

default_db = {
    "خليج الشعرة (Khalij Chaara)": {
        "date_debut": "2026-05-18",
        "stats": {"vert": 65, "jaune": 44, "gris": 12, "meteo": 8, "conge": 5},
        "jours": {}, "photos_chantier": [], "models_3d": [], "plans_ia": [],
        "ouvriers": ALL_OUVRIERS_DEFAULT, "articles": ALL_ARTICLES_DEFAULT
    }
}

def load_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                proj_key = "خليج الشعرة (Khalij Chaara)"
                if proj_key not in data: data = default_db
                else: data = {proj_key: data[proj_key]}
                p = data[proj_key]
                p.setdefault("ouvriers", {})
                for k_ouv, v_ouv in ALL_OUVRIERS_DEFAULT.items():
                    if k_ouv not in p["ouvriers"]: p["ouvriers"][k_ouv] = v_ouv
                for o_k, o_v in p["ouvriers"].items():
                    o_v.setdefault("statut", "نشط")
                    o_v.setdefault("date_cloture", p["date_debut"])
                    o_v.setdefault("tel", "99 000 000")
                    o_v.setdefault("semaine", {j: 0.0 for j in jours_semaine_noms})
                return data
        except Exception: pass
    return default_db

def save_db(db_data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(db_data, f, ensure_ascii=False, indent=2)

if "db" not in st.session_state:
    st.session_state.db = load_db()
    save_db(st.session_state.db)

base_donnees_projets = st.session_state.db
projet_choisi = "خليج الشعرة (Khalij Chaara)"
p_data = base_donnees_projets[projet_choisi]
donnees_chantier = p_data["jours"]
date_debut = date.fromisoformat(p_data["date_debut"])

if 'jour_clique' not in st.session_state: st.session_state.jour_clique = None
if 'mode_edition_presence' not in st.session_state: st.session_state.mode_edition_presence = False
if 'query_recherche_active' not in st.session_state: st.session_state.query_recherche_active = ""

def set_jour(jour): st.session_state.jour_clique = jour

def calc_worker_days_period(p_data, nom_ouv, start_d=None, end_d=None):
    total_d = 0.0
    for d_str, j_info in p_data["jours"].items():
        try:
            d_obj = date.fromisoformat(d_str)
            if start_d and d_obj < start_d: continue
            if end_d and d_obj > end_d: continue
            total_d += float(j_info.get("presences", {}).get(nom_ouv, 0.0))
        except Exception: pass
    return total_d

# ==========================================
# إدارة اللوغو والقائمة الجانبية (Sidebar)
# ==========================================
logo_path = None
for p in ["uploads/logo_saved.jpg", "logo.jpg", "logo.png"]:
    if os.path.exists(p): logo_path = p; break

st.sidebar.markdown('<div class="brand-container">', unsafe_allow_html=True)
if logo_path:
    col_l1, col_l2, col_l3 = st.sidebar.columns([1, 2, 1])
    with col_l2: st.sidebar.image(logo_path, width=110)
else:
    st.sidebar.markdown("<h1 style='text-align: center; margin:0;'>🏗️</h1>", unsafe_allow_html=True)

st.sidebar.markdown("<p class='brand-title'>H.O Bâtiment</p>", unsafe_allow_html=True)
st.sidebar.markdown("<p class='brand-subtitle'>Agent IA — Central Hub</p>", unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

if not logo_path:
    up_logo = st.sidebar.file_uploader("🖼️ أضف شعار الشركة (Logo):", type=["jpg", "png", "jpeg"], key="up_logo_ho")
    if up_logo is not None:
        with open("uploads/logo_saved.jpg", "wb") as f: f.write(up_logo.getbuffer())
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(f"📂 **المشروع:** {projet_choisi}")

# 1. البحث المتقدم
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 بحث متقدم (Recherche IA)")
txt_input_rech = st.sidebar.text_input("🔎 ابحث عن اسم خدام أو بند:", value=st.session_state.query_recherche_active, placeholder="bechir, بشير, bordure...")
if st.sidebar.button("🔍 تنفيذ البحث", use_container_width=True):
    st.session_state.query_recherche_active = txt_input_rech
    st.rerun()

query_actuelle = st.session_state.query_recherche_active

filtre_temps = st.sidebar.selectbox("📅 فترة المتابعة:", ["من تاريخ وقف الحساب (الخلاص)", "بالجمعة (الأسبوع الحالي)", "بالشهر", "بين تاريخين"])
d_debut_f, d_fin_f = None, None
if filtre_temps == "بالجمعة (الأسبوع الحالي)":
    auj = date.today()
    d_debut_f = auj - timedelta(days=auj.weekday())
    d_fin_f = d_debut_f + timedelta(days=6)
elif filtre_temps == "بالشهر":
    m_sel = st.sidebar.selectbox("الشهر:", mois_arabes, index=date.today().month - 1)
    m_num = mois_arabes.index(m_sel) + 1
    _, fin_m = calendar.monthrange(date_debut.year, m_num)
    d_debut_f = date(date_debut.year, m_num, 1); d_fin_f = date(date_debut.year, m_num, fin_m)
elif filtre_temps == "بين تاريخين":
    c1, c2 = st.sidebar.columns(2)
    d_debut_f = c1.date_input("من:", value=date_debut)
    d_fin_f = c2.date_input("إلى:", value=date.today())

# 2. ملفات الخدامة وحسابات Agent IA في اليسار
st.sidebar.markdown("---")
st.sidebar.markdown("### 👷 ملفات الخدامة وحسابات Agent IA")
liste_ouv_filtree = [k for k in p_data["ouvriers"].keys() if match_smart(k, query_actuelle)]
options_ouv = [""] + liste_ouv_filtree
index_auto_ouv = 1 if (query_actuelle.strip() and len(liste_ouv_filtree) >= 1) else 0
ouvrier_choisi = st.sidebar.selectbox("اختر الخدام للمعاينة:", options_ouv, index=index_auto_ouv)

if ouvrier_choisi and ouvrier_choisi != "":
    o = p_data["ouvriers"][ouvrier_choisi]
    statut_ouv = o.get("statut", "نشط")
    etat_badge = "🟢 نشط" if statut_ouv == "نشط" else ("🟠 معلق وقتياً" if statut_ouv == "معلق" else "🔴 مقفول")
    
    st.sidebar.markdown(f"<h3 style='text-align: center;'>👷‍♂️ {ouvrier_choisi}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align: center; color: #ff4b4b; font-weight: bold;'>🤖 {o['specialite']} | {etat_badge}</p>", unsafe_allow_html=True)
    
    safe_name = ouvrier_choisi.replace(" ", "_")
    img_path = f"uploads/{safe_name}_photo.jpg"
    if os.path.exists(img_path):
        st.sidebar.image(img_path, width=140)
    else:
        img_ouvrier = st.sidebar.file_uploader(f"🖼️ صورة {ouvrier_choisi}:", type=["jpg", "png", "jpeg"], key=f"img_{ouvrier_choisi}")
        if img_ouvrier is not None:
            with open(img_path, "wb") as f: f.write(img_ouvrier.getbuffer())
            st.rerun()

    st.sidebar.markdown("---")
    
    with st.sidebar.expander("✏️ تعديل الهاتف وخلاص النهار"):
        nouveau_tel = st.text_input("رقم الهاتف:", value=o.get("tel", "-"), key=f"tel_ed_{ouvrier_choisi}")
        nouveau_taux = st.number_input("خلاص النهار (د):", min_value=10.0, value=float(o['taux_jour']), step=5.0, key=f"taux_ed_{ouvrier_choisi}")
        if st.button("💾 حفظ التعديلات", key=f"btn_save_edit_{ouvrier_choisi}", use_container_width=True):
            o["tel"] = nouveau_tel
            o["taux_jour"] = nouveau_taux
            save_db(base_donnees_projets)
            st.sidebar.success("تم التعديل بنجاح!")
            st.rerun()

    st.sidebar.write(f"📞 **الهاتف:** {o.get('tel', '-')}")
    st.sidebar.write(f"💵 **خلاص نهاره:** {o['taux_jour']} دينار")
    
    jours_semaine_compte = sum(float(v) for v in o.get("semaine", {}).values() if float(v) >= 0.5)
    date_cloture_str = o.get("date_cloture", p_data["date_debut"])
    date_cloture_obj = date.fromisoformat(date_cloture_str)
    jours_cal_depuis_cloture = calc_worker_days_period(p_data, ouvrier_choisi, date_cloture_obj, date.today())
    total_jours_depuis_cloture = jours_semaine_compte + jours_cal_depuis_cloture
    
    st.sidebar.info(f"📊 **عدد أيام الحضور (منذ آخر خلاص):** {int(total_jours_depuis_cloture)} يوم")
    
    salaire_merite_periode = total_jours_depuis_cloture * o['taux_jour']
    solde = salaire_merite_periode - o['avances']
    
    st.sidebar.write(f"🗓️ **آخر خلاص:** {date_cloture_str}")
    st.sidebar.write(f"💰 **المستحق:** {salaire_merite_periode} د | **آفونس:** {o['avances']} د")
    if solde >= 0:
        st.sidebar.success(f"✅ الحساب خالص / الباقي: **{solde} د**")
    else:
        st.sidebar.error(f"🔵 الخدام خالص، وتسالو تسبقة زايدة: **{solde} د** (بالسالب)")

    st.sidebar.markdown("⚙️ **إدارة عمل الخدام:**")
    col_act1, col_act2 = st.sidebar.columns(2)
    with col_act1:
        if statut_ouv != "معلق":
            if st.button("⏸️ تعليق العمل", key=f"susp_{ouvrier_choisi}", use_container_width=True):
                o["statut"] = "معلق"; save_db(base_donnees_projets); st.rerun()
        else:
            if st.button("▶️ تفعيل", key=f"act_{ouvrier_choisi}", use_container_width=True):
                o["statut"] = "نشط"; save_db(base_donnees_projets); st.rerun()
    with col_act2:
        if st.button("🔒 خلاص ووقف الحساب", key=f"close_{ouvrier_choisi}", use_container_width=True):
            if solde > 0: o["paye_total"] = o.get("paye_total", 0.0) + solde + o["avances"]
            o["avances"] = 0.0; o["semaine"] = {j: 0.0 for j in jours_semaine_noms}; o["date_cloture"] = date.today().isoformat()
            save_db(base_donnees_projets); st.sidebar.success("تم غلق الحساب وتصفير الفترة!"); st.rerun()

with st.sidebar.expander("➕ إضافة عامل جديد"):
    nom_nv = st.text_input("اسم ولقب الخدام:", key="nv_nom")
    spec_nv = st.text_input("الاختصاص:", key="nv_spec")
    tel_nv = st.text_input("رقم الهاتف:", key="nv_tel")
    taux_nv = st.number_input("خلاص النهار (د):", min_value=10.0, value=50.0, step=5.0, key="nv_taux")
    statut_nv = st.selectbox("الوضعية الابتدائية:", ["نشط", "معلق"], key="nv_statut")
    if st.button("✅ حفظ العامل الجديد", use_container_width=True) and nom_nv.strip():
        p_data["ouvriers"][nom_nv.strip()] = {
            "specialite": spec_nv or "عامل", "tel": tel_nv or "-", "taux_jour": taux_nv, "statut": statut_nv,
            "date_cloture": date.today().isoformat(), "paye_total": 0.0, "avances": 0.0, "semaine": {j: 0.0 for j in jours_semaine_noms}
        }
        save_db(base_donnees_projets); st.rerun()

# 3. تحليل Agent IA للأشغال والبنود في اليسار
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 تحليل Agent IA للأشغال والبنود")
articles_disponibles = [a for a in p_data["articles"].keys() if match_smart(a, query_actuelle)]
options_art = [""] + articles_disponibles
index_auto_art = 1 if (query_actuelle.strip() and len(articles_disponibles) >= 1 and len(liste_ouv_filtree) == 0) else 0
article_selectionne = st.sidebar.selectbox("🔍 اختر البند (Article):", options_art, index=index_auto_art)

if article_selectionne and article_selectionne != "":
    tache_trouvee = p_data["articles"][article_selectionne]
    unite_a = tache_trouvee['unite']
    pourcentage = min(int((tache_trouvee['fait_total'] / tache_trouvee['objectif']) * 100), 100)
    st.sidebar.write(f"📊 **نسبة الإنجاز ({article_selectionne}):** {pourcentage}%")
    st.sidebar.progress(pourcentage)
    st.sidebar.write(f"✅ **المنجز الجملي:** {tache_trouvee['fait_total']} / {tache_trouvee['objectif']} {unite_a}")
    st.sidebar.write(f"⚡ **إنجاز الجمعة:** {tache_trouvee['fait_semaine']} {unite_a}")
    reste = max(tache_trouvee['objectif'] - tache_trouvee['fait_total'], 0.0)
    st.sidebar.write(f"⏳ **المتبقي بالعقد:** {reste} {unite_a}")

# 4. التنزيل بصيغة Excel (مع ترميز صحيح utf-8-sig للعربية والفرنسية)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 التنزيل بصيغة Excel (Google Drive)")

data_ouv_export = []
for k_o, v_o in p_data["ouvriers"].items():
    js = sum(float(x) for x in v_o.get("semaine", {}).values())
    dc = date.fromisoformat(v_o.get("date_cloture", p_data["date_debut"]))
    jd = calc_worker_days_period(p_data, k_o, dc, date.today())
    ja = js + jd
    mo = ja * v_o["taux_jour"]
    av = v_o.get("avances", 0.0)
    re = mo - av
    data_ouv_export.append({
        "الخدام": k_o, "الاختصاص": v_o["specialite"], "الهاتف": v_o.get("tel", "-"),
        "الوضعية": v_o.get("statut", "نشط"), "تاريخ آخر خلاص": v_o.get("date_cloture", "-"),
        "أيام العمل": ja, "اليومية (د)": v_o["taux_jour"], "المستحق (د)": mo, "الآفونس (د)": av, "الصافي الباقي (د)": re
    })
df_export_ouv = pd.DataFrame(data_ouv_export)
csv_ouv_data = df_export_ouv.to_csv(index=False, encoding="utf-8-sig")

st.sidebar.download_button(
    label="📥 تنزيل تقرير أجور العمال (Excel)",
    data=csv_ouv_data,
    file_name=f"Rapport_Ouvriers_{date.today().isoformat()}.csv",
    mime="text/csv",
    use_container_width=True
)

data_art_export = []
for k_a, v_a in p_data["articles"].items():
    obj = v_a["objectif"]
    fait = v_a["fait_total"]
    sem = v_a.get("fait_semaine", 0.0)
    rem = max(obj - fait, 0.0)
    pct = round((fait / obj) * 100, 1) if obj > 0 else 0
    data_art_export.append({
        "البند": k_a, "الوحدة": v_a["unite"], "الهدف التعاقدي": obj,
        "المنجز الجملي": fait, "إنجاز الأسبوع": sem, "المتبقي": rem, "نسبة الإنجاز (%)": pct
    })
df_export_art = pd.DataFrame(data_art_export)
csv_art_data = df_export_art.to_csv(index=False, encoding="utf-8-sig")

st.sidebar.download_button(
    label="📥 تنزيل تقرير الأشغال والتقدم (Excel)",
    data=csv_art_data,
    file_name=f"Rapport_Articles_{date.today().isoformat()}.csv",
    mime="text/csv",
    use_container_width=True
)


# ==========================================
# الواجهة الرئيسية
# ==========================================
st.title(f"🤖 H.O Bâtiment — {projet_choisi}")

with st.expander("📱 **مركز التحكم السريع (حضور الخدامة، الأشغال، يوميات، صور متعددة، 3D، وبلانات)**", expanded=True):
    tab_ouv, tab_art, tab_jour, tab_photos, tab_3d, tab_plans = st.tabs([
        "👷 1. حضور الخدامة", "🧱 2. الأشغال", "📅 3. يوميات الشانطي", "📸 4. صور متعددة", "🏢 5. تصاور 3D", "📐 6. البلانات"
    ])
    
    with tab_ouv:
        st.markdown("##### ✅ **ورقة الحضور السريعة للأسبوع (زر الفتح والتأكيد لمنع الخطأ):**")
        
        col_v1, col_v2 = st.columns([2, 2])
        with col_v1:
            if not st.session_state.mode_edition_presence:
                if st.button("🔓 فتح ورقة الحضور للتعديل", use_container_width=True):
                    st.session_state.mode_edition_presence = True
                    st.rerun()
            else:
                if st.button("💾 تأكيد وحفظ الحضور (Valider)", use_container_width=True):
                    st.session_state.mode_edition_presence = False
                    save_db(base_donnees_projets)
                    st.success("✅ C'est bon Validé! تم الحفظ وقفل الورقة أماناً.")
                    st.rerun()
                    
        with col_v2:
            if st.session_state.mode_edition_presence:
                st.markdown("<p style='color: orange; font-weight: bold;'>⚠️ الورقة مفتوحة للتعديل حالياً</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: green; font-weight: bold;'>🔒 الورقة مقفلة ومؤمنة (آمنة من الأخطاء)</p>", unsafe_allow_html=True)

        chg = False
        for nom_ouv, info_ouv in p_data["ouvriers"].items():
            if info_ouv.get("statut") != "نشط": continue
            st.markdown(f"<div class='worker-row'><b>👷‍♂️ {nom_ouv}</b> ({info_ouv['specialite']} — {info_ouv['taux_jour']} د)</div>", unsafe_allow_html=True)
            cols_c = st.columns(8)
            tot_s = 0.0
            for idx_j, js in enumerate(jours_semaine_noms):
                pres = float(info_ouv.get("semaine", {}).get(js, 0.0)) >= 0.5
                val = cols_c[idx_j].checkbox(f"{js}", value=pres, key=f"chk_mob_{nom_ouv}_{js}", disabled=(not st.session_state.mode_edition_presence))
                v_num = 1.0 if val else 0.0
                if info_ouv["semaine"].get(js, 0.0) != v_num:
                    info_ouv["semaine"][js] = v_num; chg = True
                tot_s += v_num
            cols_c[7].markdown(f"**{int(tot_s)} أيام**<br><span style='color:#28a745; font-weight:bold;'>{int(tot_s * info_ouv['taux_jour'])} د</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
        if chg and st.session_state.mode_edition_presence:
            save_db(base_donnees_projets)

        st.markdown("##### 💰 **تسجيل آفونس (Avance) أو خلاص جديد:**")
        c_av1, c_av2, c_av3 = st.columns(3)
        with c_av1: ouv_m = st.selectbox("الخدام:", list(p_data["ouvriers"].keys()), key="mob_ouv")
        with c_av2: av_p = st.number_input("المبلغ (د):", min_value=0.0, step=10.0, key="mob_av")
        with c_av3:
            st.write("")
            if st.button("💵 تسجيل آفونس", use_container_width=True) and av_p > 0:
                p_data["ouvriers"][ouv_m]["avances"] += av_p; save_db(base_donnees_projets); st.success("تم تسجيل الآفونس!")

    with tab_art:
        ca1, ca2 = st.columns(2)
        with ca1: art_m = st.selectbox("البند:", list(p_data["articles"].keys()), key="mob_art")
        with ca2: qty_a = st.number_input(f"الكمية ({p_data['articles'][art_m]['unite']}):", min_value=0.0, step=5.0, key="mob_qty")
        if st.button("✅ إضافة الكمية المنجزة", use_container_width=True) and qty_a > 0:
            p_data["articles"][art_m]["fait_total"] += qty_a
            p_data["articles"][art_m]["fait_semaine"] += qty_a
            save_db(base_donnees_projets); st.success("تمت الإضافة!")

    with tab_jour:
        cj1, cj2, cj3 = st.columns(3)
        with cj1: d_mob = st.date_input("التاريخ:", value=date.today())
        with cj2: et_mob = st.selectbox("الحالة:", [("vert", "🟢 عمل عادي"), ("jaune", "🟡 إيقاف أشغال"), ("meteo", "🌧️ سوء أحوال جوية"), ("conge", "🔵 راحة")], format_func=lambda x: x[1])
        with cj3: nt_mob = st.text_input("ملاحظات / سبب الإيقاف:")
        vis_mob = st.text_input("📋 ملاحظة زيارة رسمية:")
        if st.button("✅ تسجيل اليوم", use_container_width=True):
            donnees_chantier[d_mob.isoformat()] = {"etat": et_mob[0], "visite_note": vis_mob.strip(), "details": {"travail": nt_mob or et_mob[1]}, "presences": {}, "avancement": {}}
            save_db(base_donnees_projets); st.success("تم التسجيل!")

    with tab_photos:
        st.markdown("📸 **رفع عدة صور في نفس الوقت:**")
        up_imgs = st.file_uploader("اختر الصور:", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
        if st.button("✅ حفظ الصور", use_container_width=True) and up_imgs:
            for img in up_imgs:
                fn = f"uploads/chantier_photos/{date.today().isoformat()}_{len(p_data['photos_chantier'])+1}.jpg"
                with open(fn, "wb") as f: f.write(img.getbuffer())
                p_data["photos_chantier"].append({"date": date.today().isoformat(), "article": "شانطي", "desc": "صورة", "path": fn})
            save_db(base_donnees_projets); st.success("تم حفظ الصور بنجاح!")

    with tab_3d:
        st.markdown("🏢 **معرض 3D**")
        img_3d = st.file_uploader("صورة 3D:", type=["jpg", "png", "jpeg"])
        if st.button("حفظ 3D", use_container_width=True) and img_3d:
            fn = f"uploads/3d_models/3d_{len(p_data['models_3d'])+1}.jpg"
            with open(fn, "wb") as f: f.write(img_3d.getbuffer())
            p_data["models_3d"].append({"titre": "تصميم", "zone": "-", "path": fn}); save_db(base_donnees_projets); st.success("تمت الإضافة!")

    with tab_plans:
        st.markdown("📐 **البلانات**")
        img_pl = st.file_uploader("صورة البلان:", type=["jpg", "png", "jpeg"])
        if st.button("حفظ البلان", use_container_width=True) and img_pl:
            fn = f"uploads/plans/plan_{len(p_data['plans_ia'])+1}.jpg"
            with open(fn, "wb") as f: f.write(img_pl.getbuffer())
            p_data["plans_ia"].append({"nom": "بلان", "article": "عام", "synthese": "تحليل", "path": fn}); save_db(base_donnees_projets); st.success("تم الحفظ!")

# ==========================================
# الرزنامة التفاعلية (قلم التلوين السريع)
# ==========================================
st.markdown("---")
st.markdown("### 📅 رزنامة المتابعة والتلوين السريع (اختر الحالة وانقر على اليوم مباشرة)")

col_p1, col_p2 = st.columns([2, 2])
with col_p1:
    mode_pinceau = st.selectbox("🎨 اختر حالة التلوين السريع للرزنامة:", [
        ("vert", "🟢 يوم عمل عادي"),
        ("jaune", "🟡 إيقاف أشغال"),
        ("meteo", "🌧️ سوء أحوال جوية"),
        ("conge", "🔵 راحة عادية"),
        ("delete", "🗑️ مسح لون اليوم")
    ], format_func=lambda x: x[1])

annee = date_debut.year
for m_num in range(date_debut.month, 13):
    st.markdown(f"<h5 style='text-align: center; background-color: #f0f2f6; padding: 5px;'>شهر {mois_arabes[m_num-1]} {annee}</h5>", unsafe_allow_html=True)
    cols_sem = st.columns(7)
    for k, j_n in enumerate(jours_semaine_noms): cols_sem[k].markdown(f"<div style='text-align:center; font-size:12px; font-weight:bold;'>{j_n[:4]}</div>", unsafe_allow_html=True)
    
    for semaine in calendar.monthcalendar(annee, m_num):
        cols = st.columns(7)
        for k, j_num in enumerate(semaine):
            if j_num == 0: cols[k].write("")
            else:
                d_str = f"{annee}-{m_num:02d}-{j_num:02d}"
                if date(annee, m_num, j_num) < date_debut:
                    cols[k].markdown("<div style='text-align:center; color:grey; font-size:12px;'>🚫</div>", unsafe_allow_html=True)
                else:
                    j_info = donnees_chantier.get(d_str, {})
                    etat_j = j_info.get("etat", "")
                    vis_j = "📋" if j_info.get("visite_note") else ""
                    icon = "⬜"
                    if etat_j == "vert": icon = f"🟢{vis_j}"
                    elif etat_j == "jaune": icon = f"🟡{vis_j}"
                    elif etat_j == "meteo": icon = f"🌧️{vis_j}"
                    elif etat_j == "conge": icon = f"🔵{vis_j}"
                    
                    if cols[k].button(f"{icon} {j_num}", key=f"pinc_{d_str}", use_container_width=True):
                        if mode_pinceau[0] == "delete":
                            if d_str in donnees_chantier: del donnees_chantier[d_str]
                        else:
                            donnees_chantier.setdefault(d_str, {"visite_note": "", "details": {}, "presences": {}, "avancement": {}})
                            donnees_chantier[d_str]["etat"] = mode_pinceau[0]
                        save_db(base_donnees_projets)
                        st.rerun()
