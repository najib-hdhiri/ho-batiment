import streamlit as st
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="H.O Bâtiment", page_icon="🏗️", layout="wide")

# معطيات المستخدمين
utilisateurs = {
    "admin": {"mot_de_passe": "1234", "role": "مدير المشروع"},
    "najib": {"mot_de_passe": "2026", "role": "رئيس الشانطي"},
    "mra9eb": {"mot_de_passe": "0000", "role": "مراقب الأشغال"}
}

# حالة المصادقة
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

# واجهة تسجيل الدخول
if not st.session_state.authentifie:
    st.title("🏗️ H.O Bâtiment - تسجيل الدخول")
    
    nom_utilisateur = st.text_input("اسم المستخدم:")
    mot_de_passe = st.text_input("كلمة السر:", type="password")
    
    if st.button("دخول"):
        user_clean = nom_utilisateur.strip()
        pass_clean = mot_de_passe.strip()
        
        if user_clean in utilisateurs and utilisateurs[user_clean]["mot_de_passe"] == pass_clean:
            st.session_state.authentifie = True
            st.session_state.utilisateur = user_clean
            st.session_state.role = utilisateurs[user_clean]["role"]
            st.rerun()
        else:
            st.error("اسم المستخدم أو كلمة السر خطأ!")

else:
    # محتوى لوحة التحكم بعد الدخول بنجاح
    st.sidebar.title("🧭 القائمة الرئيسية")
    st.sidebar.write(f"👤 **المستخدم:** {st.session_state.utilisateur}")
    st.sidebar.write(f"👷 **الرتبة:** {st.session_state.role}")
    
    menu = st.sidebar.radio("اختر القسم:", [
        "🏠 الرئيسية", 
        "📅 جدول الأعمال (Calendrier)", 
        "👷 إدارة الخدامة والخلاص", 
        "📊 تقدم الأشغال (Avancement des Articles)"
    ])
    
    if st.button("تسجيل الخروج", key="logout_btn"):
        st.session_state.authentifie = False
        st.rerun()

    if menu == "🏠 الرئيسية":
        st.title("🏗️ لوحة تحكم H.O Bâtiment")
        st.success(f"مرحباً بك يا {st.session_state.utilisateur}! النظام جاهز لمتابعة الشانطي.")
        st.info("استعمل القائمة الجانبية لتتبع الـ Calendrier، الخدامة، ونسب الإنجاز.")

    elif menu == "📅 جدول الأعمال (Calendrier)":
        st.title("📅 جدول الأعمال والتخطيط الزمني")
        date_selectionnee = st.date_input("اختر تاريخ اليوم في الشانطي:", datetime.now())
        evenement = st.text_area("أهم الأعمال المبرمجة لهذا اليوم:")
        if st.button("حفظ الموعد في الـ Calendrier"):
            st.success(f"تم تسجيل موعد ليوم {date_selectionnee} بنجاح!")

    elif menu == "👷 إدارة الخدامة والخلاص":
        st.title("👷 إدارة الخدامة وخلاصهم")
        nom_ouvrier = st.text_input("اسم العامل أو المقاول:")
        jours_travailles = st.number_input("عدد الأيام المنجزة:", min_value=0.0, step=0.5)
        salaire_journalier = st.number_input("الأجرة اليومية (بالدينار):", min_value=0.0)
        
        total_a_payer = jours_travailles * salaire_journalier
        st.write(f"💵 **المبلغ الجملي للخلاص:** {total_a_payer} د.ت")
        
        if st.button("حفظ معطيات الخلاص"):
            st.success(f"تم تسجيل خلاص العامل {nom_ouvrier} بنجاح بقيمة {total_a_payer} د.ت!")

    elif menu == "📊 تقدم الأشغال (Avancement des Articles)":
        st.title("📊 متابعة تقدم الأشغال (Avancement)")
        
        article = st.text_input("اسم البند / الـ Article (مثال: حفر، صب béton...):")
        avancement_jour = st.number_input("نسبة الإنجاز اليومي (%):", min_value=0.0, max_value=100.0)
        
        st.write("---")
        st.subheader("📈 ملخص الإنجاز")
        st.metric(label="التقدم اليومي (Par Jour)", value=f"{avancement_jour}%")
        st.info("سيتم تجميع نسب الإنجاز أسبوعياً (Par Semaine) وإجمالياً (Totale) تلقائياً مع إدخال التقارير القادمة.")
        
        if st.button("حفظ تقدم الـ Article"):
            st.success(f"تم تسجيل تقدم الـ Article '{article}' بنجاح!")
