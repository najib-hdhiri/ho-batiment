import streamlit as st
import calendar
from datetime import date, datetime
import os
import csv

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

# ==========================================
# بيانات المشاريع
# ==========================================
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
# القائمة الرئيسية ومحتوى الأقسام
# ==========================================
menu = st.sidebar.radio("اختر القسم:", [
    "🏠 الرئيسية والمشاريع", 
    "📅 الكالندري (12 شهراً)", 
    "👷 إدارة الخدامة (الصور والڤستات)", 
    "📊 تقدم الأشغال (Avancement)"
])

if menu == "🏠 الرئيسية والمشاريع":
    st.title("🏗️ لوحة تحكم H.O Bâtiment")
    st.success(f"تم اختيار المشروع بنجاح: **{projet_choisi}**")
    st.markdown("### 📋 ملخص بنود الأشغال للمشروع:")
    for art, info in p_conf["articles"].items():
        st.write(f"- **{art}**: الهدف الجملي = {info['objectif']} {info['unite']}")

elif menu == "📅 الكالندري (12 شهراً)":
    st.title("📅 التخطيط السنوي ودفتر الورشة")
    mois_liste = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    mois_choisi = st.selectbox("اختر الشهر:", mois_liste)
    
    col1, col2 = st.columns(2)
    with col1:
        jour_num = st.number_input("اليوم:", min_value=1, max_value=31, value=1)
    with col2:
        statut_jour = st.selectbox("حالة اليوم:", ["خدمة عادية", "🟡 يوم أصفر (توقف/مشكلة)"])
    
    note_jour = st.text_area("ملاحظات الأعمال أو أسباب التوقف:")
    
    if statut_jour == "🟡 يوم أصفر (توقف/مشكلة)":
        st.warning("⚠️ تم تسجيل هذا اليوم كـ 'يوم أصفر' بسبب توقف الأشغال.")
        
    if st.button("حفظ اليوم"):
        st.success(f"تم حفظ بيانات يوم {jour_num} {mois_choisi} بنجاح.")

elif menu == "👷 إدارة الخدامة (الصور والڤستات)":
    st.title("👷 إدارة فريق العمل")
    
    ouvriers = [
        {"nom": "محمد العياري", "gilet": "أصفر (رئيس فريق)", "img": "https://img.icons8.com/color/96/worker-male.png"},
        {"nom": "علي بن صالح", "gilet": "برتقالي (عامل)", "img": "https://img.icons8.com/color/96/worker-male.png"},
        {"nom": "صابر الشارني", "gilet": "أخضر (مراقب)", "img": "https://img.icons8.com/color/96/worker-male.png"}
    ]
    
    for ouv in ouvriers:
        c1, c2, c3 = st.columns([1, 2, 2])
        with c1:
            st.image(ouv["img"], width=60)
        with c2:
            st.markdown(f"**{ouv['nom']}**")
        with c3:
            st.write(f"🦺 {ouv['gilet']}")
        st.markdown("---")
        
    st.subheader("💰 تسجيل الخلاص")
    ouv_sel = st.selectbox("العامل:", [o["nom"] for o in ouvriers])
    jours = st.number_input("أيام العمل:", min_value=0.0, step=0.5)
    salaire = st.number_input("الأجرة اليومية (د.ت):", min_value=0.0, value=50.0)
    
    if st.button("تأكيد الخلاص"):
        st.success(f"تم تسجيل خلاص {ouv_sel}: {jours * salaire} د.ت")

elif menu == "📊 تقدم الأشغال (Avancement)":
    st.title("📊 متابعة تقدم الأشغال")
    
    # جلب الـ Articles الخاصة بالمشروع المختار فقط
    articles_dispos = list(p_conf["articles"].keys())
    art_sel = st.selectbox("اختر الـ Article:", articles_dispos)
    unite_art = p_conf["articles"][art_sel]["unite"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        av_j = st.number_input(f"تقدم يومي ({unite_art}):", min_value=0.0)
    with col2:
        av_s = st.number_input(f"تقدم أسبوعي ({unite_art}):", min_value=0.0)
    with col3:
        av_t = st.number_input(f"تقدم إجمالي ({unite_art}):", min_value=0.0)
        
    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("اليومي", f"{av_j} {unite_art}")
    m2.metric("الأسبوعي", f"{av_s} {unite_art}")
    m3.metric("الإجمالي", f"{av_t} {unite_art}")
    
    if st.button("تسجيل التقدم"):
        st.success(f"تم حفظ نسب التقدم للـ Article: {art_sel}")
