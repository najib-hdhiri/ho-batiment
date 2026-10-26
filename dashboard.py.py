import streamlit as st

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
    st.title("H.O Bâtiment - تسجيل الدخول")
    
    nom_utilisateur = st.text_input("اسم المستخدم:")
    mot_de_passe = st.text_input("كلمة السر:", type="password")
    
    if st.button("دخول"):
        # تنظيف المدخلات من الفراغات تلقائياً
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
    # محتوى اللوحة بعد تسجيل الدخول بنجاح
    st.title("مرحباً بك في لوحة تحكم H.O Bâtiment")
    st.write(f"المستخدم الحالي: {st.session_state.utilisateur} ({st.session_state.role})")
    
    if st.button("تسجيل الخروج"):
        st.session_state.authentifie = False
        st.rerun()
