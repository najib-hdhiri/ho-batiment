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

# القائمة الرئيسية المدمجة لكل تفاصيل الشانطي
menu = st.sidebar.radio("اختر القسم:", [
    "🏠 الرئيسية والمشاريع", 
    "📅 الكالندري (12 شهراً ونهار أصفر)", 
    "👷 إدارة الخدامة والڤستات والصور", 
    "📊 تقدم الأشغال (Avancement)"
])

projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", [
    "LOT 2 - KHALIJ CHAARA",
    "LOT 1 - BOUKHROUF"
])

objectifs_projets = {
    "LOT 2 - KHALIJ CHAARA": {
        "date_debut": date(2026, 5, 18),
        "articles": {
            "Bordure T2": {"objectif": 7700.0, "unite": "ml"},
            "Bordure Mince P2": {"objectif": 7250.0, "unite": "ml"},
            "Caniveau CS2": {"objectif": 7700.0, "unite": "ml"},
            "Caniveau CC2": {"objectif": 500.0, "unite": "ml"},
            "Pavé autobloquant": {"objectif": 15500.0, "unite": "م²"},
        }
    },
    "LOT 1 - BOUKHROUF": {
        "date_debut": date(2026, 6, 1),
        "articles": {
            "A.01 Double cloison 0.35m": {"objectif": 1450.0, "unite": "م²"},
            "A.02 Double cloison 0.30m": {"objectif": 110.0, "unite": "م²"},
        }
    }
}

p_conf = objectifs_projets[projet_choisi]

# ==========================================
# محتوى الأقسام
# ==========================================
if menu == "🏠 الرئيسية والمشاريع":
    st.title("🏗️ لوحة تحكم H.O Bâtiment")
    st.success(f"تم اختيار المشروع بنجاح: **{projet_choisi}**")
    st.info("النظام جاهز لمتابعة الشانطي، الكالندري السنوية، والخدامة.")
    
    st.markdown("### 📋 ملخص بنود الأشغال للمشروع:")
    for art, info in p_conf["articles"].items():
        st.write(f"- **{art}**: الهدف الجملي = {info['objectif']} {info['unite']}")

elif menu == "📅 الكالندري (12 شهراً ونهار أصفر)":
    st.title("📅 جدول الأعمال والتخطيط السنوي (12 شهراً)")
    
    mois_liste = [
        "يناير (01)", "فبراير (02)", "مارس (03)", "أبريل (04)",
        "ماي (05)", "جوان (06)", "جولية (07)", "أوت (08)",
        "سبتمبر (09)", "أكتوبر (10)", "نوفمبر (11)", "ديسمبر (12)"
    ]
    
    mois_choisi = st.selectbox("اختر الشهر:", mois_liste)
    
    col1, col2 = st.columns(2)
    with col1:
        jour_num = st.number_input("اليوم:", min_value=1, max_value=31, value=1)
    with col2:
        statut_jour = st.selectbox("حالة اليوم في الشانطي:", ["خدمة عادية (Normal)", "🟡 يوم أصفر (توقف عن العمل / مشكلة)"])
    
    note_jour = st.text_area(f"تسجيل ملاحظات أو أعمال ليوم {jour_num} في شهر {mois_choisi}:")
    
    if statut_jour == "🟡 يوم أصفر (توقف عن العمل / مشكلة)":
        st.error("⚠️ تنبيه: تم تسجيل يوم توقف (Jour Jaune) لهذا اليوم في الشانطي!")
        
    if st.button("حفظ حالة اليوم"):
        st.success(f"تم تسجيل بيانات شهر {mois_choisi} (اليوم {jour_num}) بنجاح للمشروع {projet_choisi}!")

elif menu == "👷 إدارة الخدامة والڤستات والصور":
    st.title("👷 إدارة الخدامة، الصور، والڤستات (Gilets)")
    
    # قائمة الخدامة مع الڤستات الافتراضية
    ouvriers_data = [
        {"nom": "محمد العياري", "gilet": "أصفر (رئيس فريق)", "photo": "https://img.icons8.com/color/96/user-male-circle--v1.png"},
        {"nom": "علي بن صالح", "gilet": "برتقالي (عامل)", "photo": "https://img.icons8.com/color/96/user-male-circle--v1.png"},
        {"nom": "صابر الشارني", "gilet": "أخضر (مراقب)", "photo": "https://img.icons8.com/color/96/user-male-circle--v1.png"}
    ]
    
    for ouv in ouvriers_data:
        c1, c2, c3 = st.columns([1, 2, 2])
        with c1:
            st.image(ouv["photo"], width=50)
        with c2:
            st.write(f"**{ouv['nom']}**")
        with c3:
            st.write(f"🦺 الڤست: {ouv['gilet']}")
        st.markdown("---")
        
    st.subheader("💰 حساب الخلاص والأيام")
    ouv_sel = st.selectbox("اختر العامل للخلاص:", [o["nom"] for o in ouvriers_data])
    jours = st.number_input("عدد الأيام المنجزة:", min_value=0.0, step=0.5)
    salaire = st.number_input("الأجرة اليومية (د.ت):", min_value=0.0, value=50.0)
    
    total = jours * salaire
    st.write(f"💵 **المبلغ الجملي للخلاص:** {total} د.ت")
    if st.button("حفظ الخلاص"):
        st.success(f"تم تسجيل خلاص العامل {ouv_sel} بقيمة {total} د.ت بنجاح!")

elif menu == "📊 تقدم الأشغال (Avancement)":
    st.title("📊 متابعة تقدم الأشغال (Par Jour / Semaine / Totale)")
    
    articles_dispos = list(p_conf["articles"].keys())
    art_sel = st.selectbox("اختر بند الأشغال (Article):", articles_dispos)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        av_j = st.number_input("التقدم اليومي (%):", 0.0, 100.0)
    with col2:
        av_s = st.number_input("التقدم الأسبوعي (%):", 0.0, 100.0)
    with col3:
        av_t = st.number_input("التقدم الإجمالي (%):", 0.0, 100.0)
        
    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("يومي (Par Jour)", f"{av_j}%")
    m2.metric("أسبوعي (Par Semaine)", f"{av_s}%")
    m3.metric("إجمالي (Totale)", f"{av_t}%")
    
    if st.button("حفظ نسب الإنجاز"):
        st.success(f"تم حفظ نسب التقدم للـ Article '{art_sel}' بنجاح!")
