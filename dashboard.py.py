import streamlit as st
import calendar
from datetime import date, timedelta
import os
import json
import urllib.parse
import pandas as pd

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
    .share-btn { display: inline-block; padding: 10px 15px; border-radius: 8px; color: white !important; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 8px; }
    .wa-btn { background-color: #25D366; }
    .mail-btn { background-color: #1976D2; }
    .drive-box { background-color: #e8f5e9; border: 2px solid #4caf50; padding: 15px; border-radius: 10px; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

for folder in ["uploads", "uploads/chantier_photos", "uploads/3d_models", "uploads/plans", "uploads/exports"]:
    os.makedirs(folder, exist_ok=True)

DATA_FILE = "uploads/chantier_data.json"
jours_semaine_noms = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
mois_arabes = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

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
            "بشير بن حميد": {"specialite": "رئيس مجموعة / بناي", "tel": "99 888 777", "taux_jour": 65, "statut": "نشط", "jours_total": 50.0, "paye_total": 2500.0, "avances": 400.0, "semaine": {}},
            "صالح بن عمار": {"specialite": "بناي محترف", "tel": "98 123 456", "taux_jour": 60, "statut": "نشط", "jours_total": 65.0, "paye_total": 3000.0, "avances": 500.0, "semaine": {}},
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
                    for d_k, d_v in data[proj]["jours"].items():
                        d_v.setdefault("presences", {})
                        d_v.setdefault("avancement", {})
                        d_v.setdefault("visite_note", "")
                        d_v.setdefault("details", {})
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
# القائمة الجانبية (بحث + عمال + تصدير لـ Google Drive)
# ==========================================
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
st.sidebar.markdown("<p class='brand-title'>H.O Bâtiment</p><p class='brand-subtitle'>Agent IA — Central Hub</p></div>", unsafe_allow_html=True)

projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", list(base_donnees_projets.keys()))
p_data = base_donnees_projets[projet_choisi]
donnees_chantier = p_data["jours"]
date_debut = date.fromisoformat(p_data["date_debut"])

if 'jour_clique' not in st.session_state:
    st.session_state.jour_clique = None

def set_jour(jour):
    st.session_state.jour_clique = jour

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 بحث متقدم (Recherche IA)")
mot_cle_recherche = st.sidebar.text_input("🔎 ابحث عن اسم خدام أو بند:", placeholder="اكتب اسم الخدام أو البند...")

filtre_temps = st.sidebar.selectbox("📅 اختر فترة المتابعة:", [
    "الكل (الجملي والأسبوعي)", "بالجمعة (الأسبوع الحالي)", "بالشهر (اختيار شهر محدد)", "من تاريخ معين (فترة مخصصة)"
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
    d_debut_f = cf1.date_input("من:", value=date_debut, key="f_d1")
    d_fin_f = cf2.date_input("إلى:", value=date.today(), key="f_d2")

st.sidebar.markdown("---")
st.sidebar.markdown("### 👷 ملفات الخدامة وحسابات Agent IA")
liste_ouv_filtree = [k for k in p_data["ouvriers"].keys() if mot_cle_recherche.strip().lower() in k.lower()] if mot_cle_recherche.strip() else list(p_data["ouvriers"].keys())
ouvrier_choisi = st.sidebar.selectbox("اختر الخدام للمعاينة:", [""] + liste_ouv_filtree)

if ouvrier_choisi and ouvrier_choisi != "":
    o = p_data["ouvriers"][ouvrier_choisi]
    statut_ouv = o.get("statut", "نشط")
    etat_badge = "🟢 نشط" if statut_ouv == "نشط" else ("🟠 معلق مؤقتاً" if statut_ouv == "معلق" else "🔴 حساب مقفول")
    
    st.sidebar.markdown(f"<h3 style='text-align: center;'>👷‍♂️ {ouvrier_choisi}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align: center; color: #ff4b4b; font-weight: bold;'>🤖 {o['specialite']} | {etat_badge}</p>", unsafe_allow_html=True)
    
    st.sidebar.write(f"📞 **الهاتف:** {o['tel']} | 💵 **النهار:** {o['taux_jour']} د")
    
    jours_travailles_semaine = 0.0
    for js in jours_semaine_noms:
        present_side = float(o.get("semaine", {}).get(js, 1.0)) >= 0.5
        coche_side = st.sidebar.checkbox(f"{js}", value=present_side, key=f"side_chk_{projet_choisi}_{ouvrier_choisi}_{js}", disabled=(statut_ouv != "نشط"))
        val_j = 1.0 if coche_side else 0.0
        o["semaine"][js] = val_j
        jours_travailles_semaine += val_j
    save_db(base_donnees_projets)
        
    jours_hist_supp = calc_worker_days_period(p_data, ouvrier_choisi)
    salaire_merite = (o['jours_total'] + jours_travailles_semaine + jours_hist_supp) * o['taux_jour']
    solde = salaire_merite - (o['paye_total'] + o['avances'])
    
    st.sidebar.write(f"💰 **خالص:** {o['paye_total']} د | **آفونس:** {o['avances']} د")
    if solde > 0:
        st.sidebar.error(f"🔴 المستحقات الباقية: {solde} دينار")
    else:
        st.sidebar.success("✅ الحساب خالص ومريقل")

    st.sidebar.markdown("⚙️ **إدارة وضعية الخدام:**")
    col_act1, col_act2 = st.sidebar.columns(2)
    with col_act1:
        if statut_ouv != "معلق":
            if st.button("⏸️ تعليق وقتي", key=f"susp_{ouvrier_choisi}", use_container_width=True):
                o["statut"] = "معلق"
                save_db(base_donnees_projets)
                st.rerun()
        else:
            if st.button("▶️ تفعيل", key=f"act_{ouvrier_choisi}", use_container_width=True):
                o["statut"] = "نشط"
                save_db(base_donnees_projets)
                st.rerun()
    with col_act2:
        if statut_ouv != "مقفول":
            if st.button("🔒 قفل الحساب", key=f"close_{ouvrier_choisi}", use_container_width=True):
                if solde > 0: o["paye_total"] += solde
                o["statut"] = "مقفول"
                save_db(base_donnees_projets)
                st.rerun()
        else:
            if st.button("🔓 فتح", key=f"open_{ouvrier_choisi}", use_container_width=True):
                o["statut"] = "نشط"
                save_db(base_donnees_projets)
                st.rerun()

with st.sidebar.expander("➕ إضافة عامل جديد"):
    nom_nv = st.text_input("الاسم واللقب:", key="nv_nom")
    spec_nv = st.text_input("الاختصاص:", key="nv_spec")
    tel_nv = st.text_input("الهاتف:", key="nv_tel")
    taux_nv = st.number_input("خلاص النهار (د):", min_value=10.0, value=50.0, step=5.0, key="nv_taux")
    statut_nv = st.selectbox("الوضعية الابتدائية:", ["نشط", "معلق"], key="nv_statut")
    if st.button("✅ حفظ العامل", use_container_width=True) and nom_nv.strip():
        p_data["ouvriers"][nom_nv.strip()] = {"specialite": spec_nv or "عامل", "tel": tel_nv or "-", "taux_jour": taux_nv, "statut": statut_nv, "jours_total": 0.0, "paye_total": 0.0, "avances": 0.0, "semaine": {j: 0.0 for j in jours_semaine_noms}}
        save_db(base_donnees_projets)
        st.rerun()

# ----------------------------------------------------
# تصدير وربط البيانات بـ Google Drive
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### ☁️ ربط وحفظ الملفات في Google Drive")
st.sidebar.caption("حفظ جداول الأجور، تقارير الأشغال، واليوميات كملفات Excel/CSV لتخزينها أوتوماتيكياً في Google Drive.")

if st.sidebar.button("📦 توليد ملفات Excel للجداول والتقارير", use_container_width=True):
    # تحضير ملف Excel للعمال
    df_ouv = pd.DataFrame([{"العامل": k, "الاختصاص": v["specialite"], "الهاتف": v["tel"], "الأجر اليومي": v["taux_jour"], "الوضع": v["statut"], "الخالص": v["paye_total"], "الآفونس": v["avances"]} for k, v in p_data["ouvriers"].items()])
    path_excel_ouv = "uploads/exports/Rapport_Ouvriers.csv"
    df_ouv.to_csv(path_excel_ouv, index=False, encoding="utf-8-sig")
    
    # تحضير ملف Excel للبنود
    df_art = pd.DataFrame([{"البند": k, "الهدف": v["objectif"], "المنجز الجملي": v["fait_total"], "الوحدة": v["unite"]} for k, v in p_data["articles"].items()])
    path_excel_art = "uploads/exports/Rapport_Articles.csv"
    df_art.to_csv(path_excel_art, index=False, encoding="utf-8-sig")
    
    st.sidebar.success("✅ تم توليد ملفات التصدير بنجاح! حملها وضعها في Google Drive:")
    with open(path_excel_ouv, "rb") as f1:
        st.sidebar.download_button("📥 تحميل ملف العمال (CSV)", f1, file_name="Ouvriers_HO.csv")
    with open(path_excel_art, "rb") as f2:
        st.sidebar.download_button("📥 تحميل ملف الأشغال (CSV)", f2, file_name="Articles_HO.csv")

# ==========================================
# الواجهة الرئيسية
# ==========================================
st.title(f"🤖 H.O Bâtiment — {projet_choisi}")

with st.expander("📱 **مركز التحكم السريع والـ Agent IA (خدامة، أشغال، صور متعددة، 3D، وبلانات)**", expanded=True):
    tab_ouv, tab_art, tab_jour, tab_photos, tab_3d, tab_plans = st.tabs([
        "👷 1. حضور الخدامة (كوشاج سريع ✅)", 
        "🧱 2. الأشغال", 
        "📅 3. يوميات الشانطي",
        "📸 4. صور الشانطي (متعددة)",
        "🏢 5. تصاور 3D",
        "📐 6. قراءة البلانات (IA)"
    ])
    
    # 1. حضور الخدامة (العامل المعلق يختفي وقتياً من ورقة الحضور)
    with tab_ouv:
        st.markdown("##### ✅ **ورقة الحضور السريعة (العمال المعلقون لا يظهرون هنا):**")
        changement_presence = False
        for nom_ouv, info_ouv in p_data["ouvriers"].items():
            if info_ouv.get("statut") != "نشط":
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
            st.toast("✅ تم حفظ الحضور!")

        st.markdown("##### 💰 **تسجيل آفونس (Avance) أو خلاص جديد:**")
        c_av1, c_av2, c_av3, c_av4 = st.columns([2, 2, 2, 2])
        with c_av1: ouv_mob = st.selectbox("اختر الخدام:", list(p_data["ouvriers"].keys()), key="mob_ouv")
        with c_av2: avance_plus = st.number_input("المبلغ (د):", min_value=0.0, value=0.0, step=10.0, key="mob_av")
        with c_av3: type_paiement = st.radio("النوع:", ["آفونس (Avance)", "خلاص صافي (Payé)"], horizontal=True)
        with c_av4:
            st.write("")
            if st.button("💵 تسجيـل", use_container_width=True) and avance_plus > 0:
                if type_paiement == "آفونس (Avance)": p_data["ouvriers"][ouv_mob]["avances"] += avance_plus
                else: p_data["ouvriers"][ouv_mob]["paye_total"] += avance_plus
                save_db(base_donnees_projets)
                st.success("تم التسجيل بنجاح!")

    with tab_art:
        ca1, ca2 = st.columns(2)
        with ca1:
            art_mob = st.selectbox("اختر البند:", list(p_data["articles"].keys()), key="mob_art")
            unite_art = p_data["articles"][art_mob]["unite"]
        with ca2:
            qty_ajout = st.number_input(f"الكمية المنجزة اليوم ({unite_art}):", min_value=0.0, value=0.0, step=5.0, key="mob_qty")
        if st.button("✅ إضافة الكمية المنجزة", use_container_width=True) and qty_ajout > 0:
            p_data["articles"][art_mob]["fait_total"] += qty_ajout
            p_data["articles"][art_mob]["fait_semaine"] += qty_ajout
            d_auj_str = date.today().isoformat()
            p_data["jours"].setdefault(d_auj_str, {"etat": "vert", "visite_note": "", "details": {}, "presences": {}, "avancement": {}})
            p_data["jours"][d_auj_str]["avancement"][art_mob] = p_data["jours"][d_auj_str]["avancement"].get(art_mob, 0.0) + qty_ajout
            save_db(base_donnees_projets)
            st.success("تمت إضافة الكمية!")

    with tab_jour:
        cj1, cj2, cj3 = st.columns(3)
        with cj1: date_mob = st.date_input("التاريخ:", value=date.today(), key="mob_date")
        with cj2: etat_mob = st.selectbox("الحالة:", [("vert", "🟢 عمل عادي"), ("jaune", "🟡 إيقاف أشغال"), ("meteo", "🌧️ سوء أحوال جوية"), ("conge", "🔵 راحة")], format_func=lambda x: x[1], key="mob_etat")
        with cj3: note_mob = st.text_input("ملاحظة اليوم:", key="mob_note")
        visite_mob = st.text_input("📋 ملاحظة زيارة رسمية:", key="mob_visite_note")
        if st.button("✅ تسجيل اليوم", use_container_width=True):
            d_str = date_mob.isoformat()
            code_etat = etat_mob[0]
            cle_detail = "probleme" if code_etat in ["jaune", "meteo"] else "travail"
            old_j = p_data["jours"].get(d_str, {"presences": {}, "avancement": {}, "details": {}})
            p_data["jours"][d_str] = {"etat": code_etat, "visite_note": visite_mob.strip(), "details": {cle_detail: note_mob or etat_mob[1], "photo": old_j["details"].get("photo", "")}, "presences": old_j["presences"], "avancement": old_j["avancement"]}
            save_db(base_donnees_projets)
            st.success("تم تسجيل اليوم!")

    # 4. رفع مجموعة من الصور في نفس الوقت (Multiple Photos)
    with tab_photos:
        st.markdown("📸 **رفع مجموعة من صور الشانطي في نفس الوقت (Multiple Photos):**")
        cp1, cp2 = st.columns(2)
        with cp1:
            date_photo = st.date_input("التاريخ:", value=date.today(), key="date_ph")
            art_photo = st.selectbox("البند المرتبط:", ["عام (شانطي كامل)"] + list(p_data["articles"].keys()), key="art_ph")
            desc_photo = st.text_input("وصف الصور:", key="desc_ph")
        with cp2:
            imgs_multiples = st.file_uploader("اختر عدة صور (يمكنك تحديد مجموعة معاً):", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="up_multi_ph")

        if st.button("✅ حفظ جميع الصور وربطها بالشانطي", use_container_width=True) and imgs_multiples:
            d_str = date_photo.isoformat()
            for idx, img_file in enumerate(imgs_multiples):
                filename = f"uploads/chantier_photos/{d_str}_multi_{len(p_data['photos_chantier'])+1}_{idx}.jpg"
                with open(filename, "wb") as f:
                    f.write(img_file.getbuffer())
                p_data["photos_chantier"].append({"date": d_str, "article": art_photo, "desc": desc_photo or "صورة ميدانية", "path": filename})
            save_db(base_donnees_projets)
            st.success(f"تم حفظ {len(imgs_multiples)} صور بنجاح!")

        if p_data["photos_chantier"]:
            st.markdown("---")
            cols_ph = st.columns(3)
            for idx, ph in enumerate(reversed(p_data["photos_chantier"])):
                if os.path.exists(ph["path"]):
                    with cols_ph[idx % 3]:
                        st.image(ph["path"], caption=f"📅 {ph['date']} | {ph['desc']}", use_container_width=True)

    with tab_3d:
        c3d1, c3d2 = st.columns(2)
        with c3d1:
            t_3d = st.text_input("عنوان 3D:", key="t_3d")
            z_3d = st.text_input("المنطقة:", key="z_3d")
        with c3d2:
            img_3d = st.file_uploader("صورة 3D:", type=["jpg", "png", "jpeg"], key="up_3d")
        if st.button("✅ إضافة 3D", use_container_width=True) and img_3d is not None:
            path_3d = f"uploads/3d_models/3d_{len(p_data['models_3d'])+1}.jpg"
            with open(path_3d, "wb") as f: f.write(img_3d.getbuffer())
            p_data["models_3d"].append({"titre": t_3d or "3D", "zone": z_3d, "path": path_3d})
            save_db(base_donnees_projets)
            st.success("تمت الإضافة!")
        if p_data["models_3d"]:
            cols_3d = st.columns(2)
            for idx, m3d in enumerate(p_data["models_3d"]):
                if os.path.exists(m3d["path"]):
                    with cols_3d[idx % 2]: st.image(m3d["path"], caption=m3d["titre"], use_container_width=True)

    with tab_plans:
        cpl1, cpl2 = st.columns(2)
        with cpl1:
            nom_pl = st.text_input("اسم البلان:", key="nom_pl")
            art_pl = st.selectbox("البند المرتبط:", list(p_data["articles"].keys()), key="art_pl")
            note_pl = st.text_area("ملاحظات الكوتاسيون:", key="note_pl")
        with cpl2:
            img_pl = st.file_uploader("صورة البلان:", type=["jpg", "png", "jpeg"], key="up_pl")
        if st.button("🤖 تحليل وحفظ البلان", use_container_width=True) and img_pl is not None:
            path_pl = f"uploads/plans/plan_{len(p_data['plans_ia'])+1}.jpg"
            with open(path_pl, "wb") as f: f.write(img_pl.getbuffer())
            p_data["plans_ia"].append({"nom": nom_pl or "بلان", "article": art_pl, "synthese": f"تحليل البلان [{art_pl}]: {note_pl}", "path": path_pl})
            save_db(base_donnees_projets)
            st.success("تم الحفظ!")

# ==========================================
# الرزنامة واليوميات
# ==========================================
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
col_stat1.metric("🟢 عمل فعلي", f"{p_data['stats']['vert']} يوم")
col_stat2.metric("🟡 إيقاف أشغال", f"{p_data['stats']['jaune']} يوم")
col_stat3.metric("🌧️ سوء أحوال جوية", f"{p_data['stats']['meteo']} يوم")
col_stat4.metric("🔵 راحة", f"{p_data['stats']['conge']} يوم")
st.markdown("---")

jour = st.session_state.jour_clique
if jour:
    st.info(f"📅 **يوم مختار: {jour}**")
    if jour not in donnees_chantier: donnees_chantier[jour] = {"etat": "vert", "visite_note": "", "details": {"travail": "عمل اعتيادي"}, "presences": {}, "avancement": {}}
    j_info = donnees_chantier[jour]
    st.write(f"الحالة: {j_info['etat']} | ملاحظة: {j_info['details'].get('travail','')}")

annee = date_debut.year
mois_a_afficher = list(range(date_debut.month, 13))
def get_couleur_jour(date_str):
    if date_str in donnees_chantier:
        etat = donnees_chantier[date_str]["etat"]
        vis = "📋" if donnees_chantier[date_str].get("visite_note") else ""
        return f"{'🟢' if etat=='vert' else ('🟡' if etat=='jaune' else ('🌧️' if etat=='meteo' else '🔵'))}{vis}"
    return "⬜"

for i in range(0, len(mois_a_afficher), 2):
    col1, col2 = st.columns(2)
    for idx_m, m_num in enumerate([mois_a_afficher[i], mois_a_afficher[i+1] if i+1 < len(mois_a_afficher) else None]):
        if m_num is None: continue
        with (col1 if idx_m==0 else col2):
            st.markdown(f"<h5 style='text-align: center; background-color: #f0f2f6; padding: 5px;'>شهر {mois_arabes[m_num-1]} {annee}</h5>", unsafe_allow_html=True)
            cols_j = st.columns(7)
            for k, j in enumerate(jours_semaine_noms): cols_j[k].markdown(f"<div style='text-align: center; font-size: 11px; font-weight: bold;'>{j[:4]}</div>", unsafe_allow_html=True)
            for semaine in calendar.monthcalendar(annee, m_num):
                cols = st.columns(7)
                for k, jour_num in enumerate(semaine):
                    if jour_num == 0: cols[k].write("")
                    else:
                        date_str = f"{annee}-{m_num:02d}-{jour_num:02d}"
                        if date(annee, m_num, jour_num) < date_debut: cols[k].markdown("<div style='text-align:center; color:grey;'>🚫</div>", unsafe_allow_html=True)
                        else: cols[k].button(f"{get_couleur_jour(date_str)} {jour_num}", key=f"btn_{projet_choisi}_{date_str}", on_click=set_jour, args=(date_str,), use_container_width=True)
