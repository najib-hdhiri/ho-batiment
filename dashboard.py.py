import streamlit as st
import calendar
from datetime import date, datetime
import os
import csv
import pandas as pd

st.set_page_config(page_title="H.O Bâtiment - Tableau de Bord", page_icon="🏗️", layout="wide")

# ==========================================
# نظام تسجيل الدخول بكلمة السر
# ==========================================
utilisateurs = {
    "admin": {"mot_de_passe": "1234", "role": "مدير المشروع"},
    "najib": {"mot_de_passe": "2026", "role": "رئيس الشانطي"},
    "mra9eb": {"mot_de_passe": "0000", "role": "مراقب الأشغال"}
}

if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
    st.session_state.utilisateur = ""

if not st.session_state.authentifie:
    st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>H.O Bâtiment - تسجيل الدخول</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        nom_utilisateur = st.text_input("اسم المستخدم:")
        mot_de_passe = st.text_input("كلمة السر:", type="password")
        if st.button("دخول"):
            if nom_utilisateur in utilisateurs and utilisateurs[nom_utilisateur]["mot_de_passe"] == mot_de_passe:
                st.session_state.authentifie = True
                st.session_state.utilisateur = nom_utilisateur
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة السر خطأ!")
    st.stop()

# ==========================================
# تصميم CSS فخم ومنظم للواجهة
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

DOSSIER = os.path.dirname(os.path.abspath(__file__))
FICHIER_CHANTIER = os.path.join(DOSSIER, "journal_chantier.csv")
FICHIER_INCIDENTS = os.path.join(DOSSIER, "journal_perturbations.csv")
FICHIER_AVANCEMENT = os.path.join(DOSSIER, "avancement.csv")

os.makedirs("uploads", exist_ok=True)

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

st.sidebar.markdown("<p class='brand-title'>H.O Bâtiment</p>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p class='brand-subtitle'>مرحباً: {st.session_state.utilisateur}</p>", unsafe_allow_html=True)
if st.sidebar.button("خروج (Déconnexion)"):
    st.session_state.authentifie = False
    st.rerun()

st.sidebar.markdown('</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", [
    "LOT 2 - KHALIJ CHAARA",
    "LOT 1 - BOUKHROUF"
])

objectifs_projets = {
    "LOT 2 - KHALIJ CHAARA": {
        "date_debut": date(2026, 5, 18),
        "articles": {
            "Bordure T2": {"nom_csv": "bordure t2", "objectif": 7700.0, "unite": "ml"},
            "Bordure Mince P2": {"nom_csv": "bordure mince", "objectif": 7250.0, "unite": "ml"},
            "Caniveau CS2": {"nom_csv": "caniveau central cs2", "objectif": 7700.0, "unite": "ml"},
            "Caniveau CC2": {"nom_csv": "caniveau central cc2", "objectif": 500.0, "unite": "ml"},
            "Pavé autobloquant": {"nom_csv": "pave autobloquant", "objectif": 15500.0, "unite": "م²"},
        }
    },
    "LOT 1 - BOUKHROUF": {
        "date_debut": date(2026, 6, 1),
        "articles": {
            "A.01 Double cloison 0.35m": {"nom_csv": "double cloison 0,35 m", "objectif": 1450.0, "unite": "م²"},
            "A.02 Double cloison 0.30m": {"nom_csv": "double cloison 0,30 m", "objectif": 110.0, "unite": "م²"},
        }
    }
}

p_conf = objectifs_projets[projet_choisi]

# ==========================================
# الأقسام (Tabs) الاحترافية للشانطي
# ==========================================
tab1, tab2, tab3 = st.tabs(["📖 دفتر الورشة (Journal)", "👷 إدارة الموارد البشرية", "📊 متابعة الإنجاز (Avancement)"])

with tab1:
    st.header("📖 دفتر الورشة اليومي (Journal de Chantier)")
    date_jour = st.date_input("تاريخ التقرير:", datetime.now())
    
    col_meteo, col_eff = st.columns(2)
    with col_meteo:
        meteo = st.selectbox("حالة الطقس:", ["☀️ مشمس", "☁️ غائم", "🌧️ ممطر", "💨 رياح قوية"])
    with col_eff:
        effectif = st.number_input("عدد العمال الحاضرين اليوم:", min_value=0, value=5)
        
    travaux = st.text_area("وصف الأشغال المنجزة اليوم:")
    
    jour_jaune = st.checkbox("🟡 تسجيل يوم أصفر (توقف عن العمل / مشكلة)")
    if jour_jaune:
        cause = st.text_input("سبب التوقف (عطب، طقس، نقص مواد...):")
        if st.button("💾 حفظ تقرير التوقف (Jour Jaune)"):
            if cause:
                with open(FICHIER_INCIDENTS, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([projet_choisi, date_jour, cause])
                st.error(f"تم تسجيل توقف العمل ليوم {date_jour} بنجاح!")
            else:
                st.warning("الرجاء كتابة سبب التوقف.")
    else:
        if st.button("💾 حفظ تقرير الورشة"):
            with open(FICHIER_CHANTIER, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([projet_choisi, date_jour, meteo, effectif, travaux])
            st.success(f"تم حفظ تقرير يوم {date_jour} بنجاح!")

with tab2:
    st.header("👷 إدارة الفريق والعمال")
    st.info("تتبع الحضور، صور العمال، والڤستات الخاصة بالسلامة.")
    
    ouvriers_data = [
        {"nom": "محمد العياري", "role": "رئيس فريق", "gilet": "🟡 أصفر", "photo": "https://img.icons8.com/color/96/worker-male.png"},
        {"nom": "علي بن صالح", "role": "عامل بناء", "gilet": "🟠 برتقالي", "photo": "https://img.icons8.com/color/96/worker-male.png"},
        {"nom": "صابر الشارني", "role": "مراقب", "gilet": "🟢 أخضر", "photo": "https://img.icons8.com/color/96/worker-male.png"}
    ]
    
    for ouv in ouvriers_data:
        c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
        with c1:
            st.image(ouv["photo"], width=50)
        with c2:
            st.write(f"**{ouv['nom']}**")
        with c3:
            st.write(f"الخطة: {ouv['role']}")
        with c4:
            st.write(f"🦺 الڤست: {ouv['gilet']}")
        st.markdown("---")
        
    st.subheader("💰 حساب الخلاص")
    ouv_sel = st.selectbox("اختر العامل:", [o["nom"] for o in ouvriers_data])
    jours_trav = st.number_input("أيام العمل المنجزة:", min_value=0.0, step=0.5)
    salaire_jour = st.number_input("الأجرة اليومية (د.ت):", min_value=0.0, value=50.0)
    
    if st.button("تأكيد خلاص العامل"):
        st.success(f"تم اعتماد خلاص {ouv_sel} بمبلغ قدره {jours_trav * salaire_jour} د.ت")

with tab3:
    st.header("📊 متابعة تقدم الأشغال (Avancement)")
    
    articles_dispos = list(p_conf["articles"].keys())
    art_sel = st.selectbox("اختر بند الأشغال (Article):", articles_dispos)
    
    info_art = p_conf["articles"][art_sel]
    objectif_total = info_art["objectif"]
    unite = info_art["unite"]
    
    st.write(f"🎯 **الهدف الجملي للـ Article:** {objectif_total} {unite}")
    
    col_j, col_s = st.columns(2)
    with col_j:
        av_jour = st.number_input(f"التقدم اليومي ({unite}):", min_value=0.0, step=1.0)
    with col_s:
        av_semaine = st.number_input(f"التقدم الأسبوعي ({unite}):", min_value=0.0, step=1.0)
        
    if st.button("💾 تسجيل التقدم"):
        with open(FICHIER_AVANCEMENT, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([projet_choisi, datetime.now().date(), art_sel, av_jour, av_semaine])
        st.success(f"تم تسجيل تقدم قدره {av_jour} {unite} لـ {art_sel} اليوم.")
        
    st.markdown("---")
    st.subheader("📋 تاريخ الإنجازات المسجلة")
    if os.path.exists(FICHIER_AVANCEMENT):
        df_av = pd.read_csv(FICHIER_AVANCEMENT, names=["Projet", "Date", "Article", "Av_Jour", "Av_Semaine"])
        df_filtre = df_av[(df_av["Projet"] == projet_choisi) & (df_av["Article"] == art_sel)]
        if not df_filtre.empty:
            st.dataframe(df_filtre, use_container_width=True)
            total_realise = df_filtre["Av_Jour"].sum()
            restant = objectif_total - total_realise
            
            c_tot, c_rest = st.columns(2)
            c_tot.metric("الإجمالي المنجز", f"{total_realise} {unite}")
            c_rest.metric("المتبقي", f"{restant} {unite}")
        else:
            st.info("لا توجد تسجيلات سابقة لهذا البند.")
    else:
        st.info("ملف الإنجازات فارغ حالياً.")
