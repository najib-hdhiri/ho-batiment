import streamlit as st
import calendar
from datetime import date, timedelta
import os
import json
import urllib.parse
import pandas as pd

st.set_page_config(page_title="H.O Bâtiment - Système Central IA", page_icon="🏗️", layout="wide")

# ==========================================
# تصميم CSS الجداول المزينة والمنظمة
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
    .report-card { background: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; border-top: 5px solid #ff4b4b; }
    </style>
""", unsafe_allow_html=True)

for folder in ["uploads", "uploads/chantier_photos", "uploads/3d_models", "uploads/plans", "uploads/exports"]:
    os.makedirs(folder, exist_ok=True)

DATA_FILE = "uploads/chantier_data.json"
jours_semaine_noms = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
mois_arabes = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

# ==========================================
# قاعدة البيانات (التركيز الأساسي على خليج الشعرة والبنود الكاملة)
# ==========================================
default_db = {
    "خليج الشعرة (Khalij Chaara)": {
        "date_debut": "2026-05-18",
        "stats": {"vert": 65, "jaune": 44, "gris": 12, "meteo": 8, "conge": 5},
        "jours": {},
        "photos_chantier": [], "models_3d": [], "plans_ia": [],
        "ouvriers": {
            "بشير بن حميد (Bechir)": {"specialite": "رئيس مجموعة / بناي", "tel": "99 888 777", "taux_jour": 65, "statut": "نشط", "dernier_cloture": "2026-05-18", "paye_total": 0.0, "avances": 0.0, "semaine": {}},
            "صالح بن عمار (Saleh)": {"specialite": "بناي محترف", "tel": "98 123 456", "taux_jour": 60, "statut": "نشط", "dernier_cloture": "2026-05-18", "paye_total": 0.0, "avances": 0.0, "semaine": {}},
            "الهادي العياري (Hedi)": {"specialite": "مانوفري", "tel": "22 345 678", "taux_jour": 40, "statut": "نشط", "dernier_cloture": "2026-05-18", "paye_total": 0.0, "avances": 0.0, "semaine": {}},
        },
        "articles": {
            "Bordure T2": {"objectif": 7700.0, "fait_total": 1540.0, "unite": "ml"},
            "Bordure Mince P2": {"objectif": 7250.0, "fait_total": 1450.0, "unite": "ml"},
            "Caniveau CS2": {"objectif": 7700.0, "fait_total": 1155.0, "unite": "ml"},
            "Caniveau CC2": {"objectif": 500.0, "fait_total": 150.0, "unite": "ml"},
            "Pavé autobloquant": {"objectif": 15500.0, "fait_total": 3100.0, "unite": "م²"},
            "A.01 Double Cloison 0.35m": {"objectif": 1450.0, "fait_total": 435.0, "unite": "م²"},
            "A.02 Double Cloison 0.30m": {"objectif": 110.0, "fait_total": 33.0, "unite": "م²"},
            "A.03 Cloison 0.25m": {"objectif": 1150.0, "fait_total": 345.0, "unite": "م²"},
            "B-1 Enduit extérieur": {"objectif": 4700.0, "fait_total": 1410.0, "unite": "م²"},
            "C-1 Carrelage marbré 25x25": {"objectif": 1150.0, "fait_total": 345.0, "unite": "م²"},
            "C-4 Plinthe": {"objectif": 1000.0, "fait_total": 300.0, "unite": "ml"}
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
                    for o_k, o_v in data[proj]["ouvriers"].items():
                        o_v.setdefault("statut", "نشط")
                        o_v.setdefault("dernier_cloture", data[proj]["date_debut"])
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

def calc_worker_days_since_cloture(p_data, nom_ouv):
    o_info = p_data["ouvriers"][nom_ouv]
    d_cloture_str = o_info.get("dernier_cloture", p_data["date_debut"])
    d_cloture = date.fromisoformat(d_cloture_str)
    
    total_d = 0.0
    for d_str, j_info in p_data["jours"].items():
        try:
            d_obj = date.fromisoformat(d_str)
            if d_obj > d_cloture:
                total_d += float(j_info.get("presences", {}).get(nom_ouv, 0.0))
        except Exception:
            pass
    return total_d

# ==========================================
# القائمة الجانبية: بحث ذكي باللغتين
# ==========================================
st.sidebar.markdown('<div class="brand-container">', unsafe_allow_html=True)
st.sidebar.markdown("<h1 style='text-align: center; margin:0;'>🏗️</h1><p class='brand-title'>H.O Bâtiment</p><p class='brand-subtitle'>Agent IA — Central Hub</p></div>", unsafe_allow_html=True)

projet_choisi = st.sidebar.selectbox("📂 المشروع:", list(base_donnees_projets.keys()))
p_data = base_donnees_projets[projet_choisi]
donnees_chantier = p_data["jours"]
date_debut = date.fromisoformat(p_data["date_debut"])

if 'jour_clique' not in st.session_state:
    st.session_state.jour_clique = None

def set_jour(jour):
    st.session_state.jour_clique = jour

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 بحث ذكي (Smart Search)")
mot_cle = st.sidebar.text_input("🔎 ابحث باسم عامل أو بند (Bechir, بشير, Bordure):", placeholder="اكتب بالعربي أو الفرنسية...")

def match_search(text, query):
    if not query.strip(): return True
    q = query.strip().lower()
    return q in text.lower()

ouvriers_filtres = [k for k in p_data["ouvriers"].keys() if match_search(k, mot_cle)]
articles_filtres = [k for k in p_data["articles"].keys() if match_search(k, mot_cle)]

st.sidebar.markdown("---")
st.sidebar.markdown("### 👷 إدارة العمال والمالية")
ouvrier_choisi = st.sidebar.selectbox("اختر الخدام للمعاینة:", [""] + ouvriers_filtres)

if ouvrier_choisi and ouvrier_choisi != "":
    o = p_data["ouvriers"][ouvrier_choisi]
    statut_ouv = o.get("statut", "نشط")
    
    st.sidebar.markdown(f"#### 👷‍♂️ {ouvrier_choisi}")
    st.sidebar.write(f"💵 الأجر اليومي: **{o['taux_jour']} د** | الحالة: **{statut_ouv}**")
    
    jours_semaine_courante = sum(float(v) for v in o.get("semaine", {}).values())
    jours_depuis_cloture = calc_worker_days_since_cloture(p_data, ouvrier_choisi)
    total_jours_actifs = jours_depuis_cloture + jours_semaine_courante
    
    salaire_du = total_jours_actifs * o['taux_jour']
    solde_restant = salaire_du - o['avances']
    
    st.sidebar.info(
        f"📊 **الملخص المالي (منذ آخر خلاص في {o.get('dernier_cloture')}):**\n"
        f"- أيام العمل: **{total_jours_actifs} يوم**\n"
        f"- المستحق: **{salaire_du} دينار**\n"
        f"- الآفونس: **{o['avances']} د**\n"
        f"- **الباقي للخلاص: {solde_restant} د**"
    )

    col_a1, col_a2 = st.sidebar.columns(2)
    with col_a1:
        if statut_ouv == "نشط" and st.button("⏸️ تعليق", use_container_width=True):
            o["statut"] = "معلق"
            save_db(base_donnees_projets)
            st.rerun()
        elif statut_ouv == "معلق" and st.button("▶️ تفعيل", use_container_width=True):
            o["statut"] = "نشط"
            save_db(base_donnees_projets)
            st.rerun()
    with col_a2:
        if st.button("🔒 خلاص وقفل الحساب", use_container_width=True):
            o["paye_total"] += solde_restant
            o["avances"] = 0.0
            o["dernier_cloture"] = date.today().isoformat()
            save_db(base_donnees_projets)
            st.sidebar.success("تم غلق الحساب وتصفير الفترة بنجاح!")
            st.rerun()

with st.sidebar.expander("➕ إضافة عامل جديد"):
    nom_nv = st.text_input("الاسم (عربي / فرنسي):", key="nv_n")
    spec_nv = st.text_input("الاختصاص:", key="nv_s")
    taux_nv = st.number_input("خلاص النهار (د):", min_value=10.0, value=50.0, key="nv_t")
    if st.button("✅ حفظ العامل", use_container_width=True) and nom_nv.strip():
        p_data["ouvriers"][nom_nv.strip()] = {"specialite": spec_nv or "عامل", "tel": "-", "taux_jour": taux_nv, "statut": "نشط", "dernier_cloture": date.today().isoformat(), "paye_total": 0.0, "avances": 0.0, "semaine": {j: 0.0 for j in jours_semaine_noms}}
        save_db(base_donnees_projets)
        st.rerun()

# ==========================================
# الواجهة الرئيسية
# ==========================================
st.title(f"🤖 H.O Bâtiment — {projet_choisi}")

tab_dash, tab_ouv_w, tab_art_w, tab_rep, tab_tools = st.tabs([
    "📊 لوحة القيادة (Dashboard)", 
    "👷 ورقة الحضور السريعة", 
    "🧱 متابعة الأشغال والبنود", 
    "📋 التقارير المزينة والموحدة", 
    "⚙️ أدوات الشانطي والصور"
])

with tab_dash:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🟢 أيام العمل", f"{p_data['stats']['vert']} يوم")
    c2.metric("🟡 إيقاف الأشغال", f"{p_data['stats']['jaune']} يوم")
    c3.metric("🌧️ سوء أحوال", f"{p_data['stats']['meteo']} يوم")
    c4.metric("🔵 راحة", f"{p_data['stats']['conge']} يوم")
    st.markdown("---")
    st.markdown("### 📈 نظرة عامة على نسب إنجاز البنود الأساسية")
    for a_n, a_v in p_data["articles"].items():
        pct = min(int((a_v["fait_total"] / a_v["objectif"]) * 100), 100)
        st.write(f"**{a_n}** — ({a_v['fait_total']} / {a_v['objectif']} {a_v['unite']}) — **{pct}%**")
        st.progress(pct)

with tab_ouv_w:
    st.markdown("##### ✅ **ورقة الحضور السريعة (من الإثنين إلى الأحد):**")
    changement_presence = False
    for nom_ouv, info_ouv in p_data["ouvriers"].items():
        if info_ouv.get("statut") != "نشط": continue
        st.markdown(f"<div class='worker-row'><b>👷‍♂️ {nom_ouv}</b> <span style='color:gray; font-size:13px;'>({info_ouv['specialite']} — {info_ouv['taux_jour']} د/يوم)</span></div>", unsafe_allow_html=True)
        cols_check = st.columns(8)
        total_sem = 0.0
        for idx_j, js in enumerate(jours_semaine_noms):
            est_present = float(info_ouv.get("semaine", {}).get(js, 0.0)) >= 0.5
            nouvelle_val = cols_check[idx_j].checkbox(f"{js}", value=est_present, key=f"chk_w_{nom_ouv}_{js}")
            val_num = 1.0 if nouvelle_val else 0.0
            if info_ouv["semaine"].get(js, 0.0) != val_num:
                info_ouv["semaine"][js] = val_num
                changement_presence = True
            total_sem += val_num
        cols_check[7].markdown(f"**{int(total_sem)} أيام**<br><span style='color:#28a745; font-weight:bold;'>{int(total_sem * info_ouv['taux_jour'])} د</span>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 5px 0 10px 0;'>", unsafe_allow_html=True)
    if changement_presence:
        save_db(base_donnees_projets)
        st.toast("✅ تم تحديث الحضور!")

with tab_art_w:
    st.markdown("##### 🧱 **تسجيل وإدارة كميات البنود:**")
    art_sel = st.selectbox("اختر البند:", articles_filtres if articles_filtres else list(p_data["articles"].keys()))
    q_val = st.number_input(f"الكمية المنجزة ({p_data['articles'][art_sel]['unite']}):", min_value=0.0, step=5.0)
    if st.button("✅ تسجيل الكمية في الشانطي", use_container_width=True) and q_val > 0:
        p_data["articles"][art_sel]["fait_total"] += q_val
        save_db(base_donnees_projets)
        st.success("تمت إضافة الكمية بنجاح!")

with tab_rep:
    st.markdown("<div class='report-card'><h3>📋 التقارير التنفيذية والجدول الموحد للمالية والأشغال</h3><p>مقارنة شاملة بين الأهداف، المنجز، والنسب المئوية مع الوضع المالي للعمال.</p></div>", unsafe_allow_html=True)
    
    st.markdown("#### 🧱 جدول متابعة الأشغال والنسب المئوية")
    data_table_art = []
    for a_k, a_v in p_data["articles"].items():
        p_val = round((a_v["fait_total"] / a_v["objectif"]) * 100, 1) if a_v["objectif"] > 0 else 0
        data_table_art.append({
            "البند (Article)": a_k,
            "الهدف التعاقدي": f"{a_v['objectif']} {a_v['unite']}",
            "المنجز الجملي": f"{a_v['fait_total']} {a_v['unite']}",
            "المتبقي": f"{max(a_v['objectif'] - a_v['fait_total'], 0)} {a_v['unite']}",
            "نسبة الإنجاز (%)": f"{p_val}%"
        })
    st.dataframe(pd.DataFrame(data_table_art), use_container_width=True)
    
    st.markdown("#### 💰 الجدول المالي الموحد للعمال")
    data_table_ouv = []
    for o_k, o_v in p_data["ouvriers"].items():
        j_pers = calc_worker_days_since_cloture(p_data, o_k)
        tot_d = j_pers + sum(float(v) for v in o_v.get("semaine", {}).values())
        tot_s = tot_d * o_v['taux_jour']
        data_table_ouv.append({
            "العامل": o_k,
            "الاختصاص": o_v['specialite'],
            "الأجر اليومي": f"{o_v['taux_jour']} د",
            "أيام العمل النشطة": f"{tot_d} يوم",
            "المستحق المالي": f"{tot_s} د",
            "الوضع": o_v['statut']
        })
    st.dataframe(pd.DataFrame(data_table_ouv), use_container_width=True)
    
    txt_rep_gen = f"🏗️ *تقرير H.O Bâtiment - مشروع خليج الشعرة*\n📊 تم تحديث نسب الإنجاز والمالية بنجاح."
    enc_m = urllib.parse.quote(txt_rep_gen)
    st.markdown(f'<a href="https://wa.me/?text={enc_m}" target="_blank" class="share-btn wa-btn">🟢 إرسال التقرير عبر WhatsApp</a>', unsafe_allow_html=True)

with tab_tools:
    st.markdown("##### 📸 صور الشانطي والرزنامة للتاريخ:")
    d_ch = st.date_input("تاريخ اليوم:", value=date.today())
    n_ch = st.text_input("ملاحظة اليوم:")
    if st.button("✅ تسجيل حالة اليوم"):
        donnees_chantier[d_ch.isoformat()] = {"etat": "vert", "visite_note": "", "details": {"travail": n_ch or "يوم عمل"}}
        save_db(base_donnees_projets)
        st.success("تم التسجيل!")

st.markdown("---")
st.markdown("### 📅 الرزنامة التاريخية (انقر على أي يوم للمراجعة والتعديل)")
annee = date_debut.year
for m_num in range(date_debut.month, 13):
    st.markdown(f"**شهر {mois_arabes[m_num-1]} {annee}**")
    cols_sem = st.columns(7)
    for k, j_n in enumerate(jours_semaine_noms): 
        cols_sem[k].markdown("<div style='text-align:center; font-size:12px; font-weight:bold;'>" + j_n[:4] + "</div>", unsafe_allow_html=True)
    for semaine in calendar.monthcalendar(annee, m_num):
        cols = st.columns(7)
        for k, j_num in enumerate(semaine):
            if j_num == 0: cols[k].write("")
            else:
                d_str = f"{annee}-{m_num:02d}-{j_num:02d}"
                cols[k].button(f"🟢 {j_num}" if d_str in donnees_chantier else f"⬜ {j_num}", key=f"b_{d_str}", on_click=set_jour, args=(d_str,), use_container_width=True)
