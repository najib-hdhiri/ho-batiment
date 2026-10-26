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
    
    menu = st.sidebar.radio("اختر القسم:", ["🏠 الرئيسية", "📖 دفتر الورشة (Journal)", "💰 المصاريف والمالية"])
    
    if st.button("تسجيل الخروج", key="logout_btn"):
        st.session_state.authentifie = False
        st.rerun()

    if menu == "🏠 الرئيسية":
        st.title("🏗️ لوحة تحكم H.O Bâtiment")
        st.success(f"مرحباً بك يا {st.session_state.utilisateur}! المشروع يخدم بانتظام.")
        st.info("استعمل القائمة الجانبية للتنقل بين دفتر الورشة وإدارة المصاريف.")

    elif menu == "📖 دفتر الورشة (Journal)":
        st.title("📖 تسجيل تقرير الورشة اليومي")
        
        date_jour = st.date_input("تاريخ اليوم:", datetime.now())
        tache_realise = st.text_area("الأعمال المنجزة اليوم:")
        remarques = st.text_area("ملاحظات أو صعوبات في الشانطي:")
        
        if st.button("حفظ التقرير"):
            st.success("تم حفظ تقرير الورشة بنجاح!")

    elif menu == "💰 المصاريف والمالية":
        st.title("💰 تتبع المصاريف")
        
        item = st.text_input("نوع المصروف (مثال: مواد بناء، نقل...):")
        montant = st.number_input("المبلغ (بالدينار):", min_value=0.0, format="%.2f")
        
        if st.button("إضافة المصروف"):
            st.success(f"تم تسجيل مصروف بقيمة {montant} د.ت بنجاح!")
