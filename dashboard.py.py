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
    # القائمة الجانبية
    st.sidebar.title("🧭 القائمة الرئيسية")
    st.sidebar.write(f"👤 **المستخدم:** {st.session_state.utilisateur}")
    st.sidebar.write(f"👷 **الرتبة:** {st.session_state.role}")
    
    menu = st.sidebar.radio("اختر القسم:", [
        "🏠 الرئيسية", 
        "📅 جدول الأعمال (Calendrier)", 
        "👷 إدارة الخدامة وخلاصهم", 
        "📊 تقدم الأشغال (Avancement des Articles)"
    ])
    
    if st.button("تسجيل الخروج", key="logout_btn"):
        st.session_state.authentifie = False
        st.rerun()

    if menu == "🏠 الرئيسية":
        st.title("🏗️ لوحة تحكم H.O Bâtiment")
        st.success(f"مرحباً بك يا {st.session_state.utilisateur}! النظام جاهز والبيانات مرتبة.")
        st.info("استعمل القائمة الجانبية لتتبع الـ Calendrier، الخدامة، ونسب الإنجاز.")

    elif menu == "📅 جدول الأعمال (Calendrier)":
        st.title("📅 جدول الأعمال والتخطيط الزمني للشانطي")
        date_jour = st.date_input("تاريخ اليوم:", datetime.now())
        tache = st.text_area("الأعمال المبرمجة:")
        if st.button("حفظ في الـ Calendrier"):
            st.success(f"تم تسجيل البرنامج ليوم {date_jour} بنجاح!")

    elif menu == "👷 إدارة الخدامة وخلاصهم":
        st.title("👷 إدارة الخدامة وخلاصهم")
        
        # مصدر معلومات الخدامة (قائمة واضحة)
        liste_ouvriers = ["محمد العياري", "علي بن صالح", "صابر الشارني", "مقاول الهيكل الأساسي"]
        ouvrier_choisi = st.selectbox("اختر العامل أو المقاول:", liste_ouvriers)
        
        jours = st.number_input("عدد الأيام المنجزة:", min_value=0.0, step=0.5)
        salaire_jour = st.number_input("الأجرة اليومية (بالدينار):", min_value=0.0, value=50.0)
        
        total_a_payer = jours * salaire_jour
        st.write(f"💵 **المبلغ الجملي للخلاص لـ {ouvrier_choisi}:** {total_a_payer} د.ت")
        
        if st.button("حفظ الخلاص"):
            st.success(f"تم تسجيل خلاص {ouvrier_choisi} بقيمة {total_a_payer} د.ت بنجاح!")

    elif menu == "📊 تقدم الأشغال (Avancement des Articles)":
        st.title("📊 متابعة تقدم الأشغال (Avancement)")
        
        # مصدر معلومات الـ Articles (بنود الأشغال في الشانطي)
        liste_articles = ["حفر الأساسات (Fouilles)", "صب البتون تنظيف (Béton de propreté)", "تركيـز الحديد (Frappe ferraillage)", "صب البتون المسلح (Coulage béton armé)"]
        article_choisi = st.selectbox("اختر بند الأشغال (Article):", liste_articles)
        
        col1, col2 = st.columns(2)
        with col1:
            av_jour = st.number_input("التقدم اليومي (Par Jour %):", min_value=0.0, max_value=100.0)
        with col2:
            av_semaine = st.number_input("التقدم الأسبوعي (Par Semaine %):", min_value=0.0, max_value=100.0)
        
        av_totale = min(av_semaine, 100.0) # مثال حساب إجمالي تجميعي
        
        st.write("---")
        st.subheader(f"📈 ملخص إنجاز بند: {article_choisi}")
        m1, m2, m3 = st.columns(3)
        m1.metric("اليومي (Par Jour)", f"{av_jour}%")
        m2.metric("الأسبوعي (Par Semaine)", f"{av_semaine}%")
        m3.metric("الإجمالي (Totale)", f"{av_totale}%")
        
        if st.button("حفظ نسب الإنجاز"):
            st.success(f"تم تحديث نسب الإنجاز للـ Article '{article_choisi}' بنجاح!")
