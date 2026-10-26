import streamlit as st
import pandas as pd
from datetime import datetime

# إعداد الصفحة بعرض كامل
st.set_page_config(page_title="H.O Bâtiment", page_icon="🏗️", layout="wide")

# معطيات المستخدمين
utilisateurs = {
    "admin": {"mot_de_passe": "1234", "role": "مدير المشروع"},
    "najib": {"mot_de_passe": "2026", "role": "رئيس الشانطي"},
    "mra9eb": {"mot_de_passe": "0000", "role": "مراقب الأشغال"}
}

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
    # ---------------------------------------------------------
    # القائمة الجانبية (الشعار على اليسار + الڤستات + الخدامة)
    # ---------------------------------------------------------
    with st.sidebar:
        # مكان الشعار (Logo)
        st.markdown("### 🏗️ H.O Bâtiment")
        st.markdown("---")
        st.write(f"👤 **المستخدم:** {st.session_state.utilisateur}")
        st.write(f"👷 **الرتبة:** {st.session_state.role}")
        st.markdown("---")
        
        menu = st.radio("اختر القسم:", [
            "🏠 الرئيسية", 
            "📅 الكالندري (12 شهراً)", 
            "👷 إدارة الخدامة والڤستات والصور", 
            "📊 تقدم الأشغال (Par Jour / Semaine / Totale)"
        ])
        
        st.markdown("---")
        if st.button("تسجيل الخروج", key="logout_btn"):
            st.session_state.authentifie = False
            st.rerun()

    # ---------------------------------------------------------
    # المحتوى الرئيسي حسب الأقسام
    # ---------------------------------------------------------
    if menu == "🏠 الرئيسية":
        st.title("🏗️ لوحة تحكم H.O Bâtiment")
        st.success(f"مرحباً بك يا {st.session_state.utilisateur}! النظام جاهز بجميع تفاصيل الشانطي.")
        
        # تنبيه النهار الأصفر (حالة توقف العمل)
        st.warning("⚠️ **تنبيه الشانطي:** إذا صارت مشكلة وما خدمتوناش اليوم، استعمل خاصية 'النهار الأصفر' لتسجيل التوقف.")

    elif menu == "📅 الكالندري (12 شهراً)":
        st.title("📅 جدول الأعمال والـ Calendrier السنوي (12 شهراً)")
        
        mois_liste = [
            "يناير (Janvier)", "فبراير (Février)", "مارس (Mars)", "أبريل (Avril)",
            "ماي (Mai)", "جوان (Juin)", "جولية (Juillet)", "أوت (Août)",
            "سبتمبر (Septembre)", "أكتوبر (Octobre)", "نوفمبر (Novembre)", "ديسمبر (Décembre)"
        ]
        
        mois_choisi = st.selectbox("اختر الشهر للتحكم في الأيام والتخطيط:", mois_liste)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            jour_num = st.number_input("اليوم من الشهر:", min_value=1, max_value=31, value=1)
        with col_c2:
            statut_jour = st.selectbox("حالة اليوم:", ["خدمة عادية (Normal)", "🟡 يوم أصفر (مشكلة / توقف عن العمل)"])
        
        note_jour = st.text_area(f"ملاحظات أو أعمال يوم {jour_num} في شهر {mois_choisi}:")
        
        if statut_jour == "🟡 يوم أصفر (مشكلة / توقف عن العمل)":
            st.error("🟡 تم رصد يوم توقف (Jour Jaune) بسبب مشكلة في الشانطي!")
            
        if st.button("حفظ حالة اليوم في الكالندري"):
            st.success(f"تم حفظ بيانات يوم {jour_num} من {mois_choisi} بنجاح!")

    elif menu == "👷 إدارة الخدامة والڤستات والصور":
        st.title("👷 إدارة الخدامة، الصور، والـيستات (Gilets)")
        
        # قائمة الخدامة مع تصاورهم الافتراضية والڤستات
        ouvriers_data = [
            {"nom": "محمد العياري", "gilet": "أصفر (رئيس فريق)", "photo": "https://img.icons8.com/color/96/user-male-circle--v1.png"},
            {"nom": "علي بن صالح", "gilet": "برتقالي (عامل)", "photo": "https://img.icons8.com/color/96/user-male-circle--v1.png"},
            {"nom": "صابر الشارني", "gilet": "أخضر (مراقب)", "photo": "https://img.icons8.com/color/96/user-male-circle--v1.png"}
        ]
        
        for ouv in ouvriers_data:
            c1, c2, c3 = st.columns([1, 2, 2])
            with c1:
                st.image(ouv["photo"], width=60)
            with c2:
                st.subheader(ouv["nom"])
            with c3:
                st.write(f"🦺 **الڤست:** {ouv['gilet']}")
            st.markdown("---")
            
        st.subheader("💰 حساب الخلاص والأيام")
        ouvrier_selectionne = st.selectbox("اختر العامل للخلاص:", [o["nom"] for o in ouvriers_data])
        jours_travailles = st.number_input("عدد الأيام المنجزة:", min_value=0.0, step=0.5)
        salaire_jour = st.number_input("الأجرة اليومية (د.ت):", min_value=0.0, value=50.0)
        
        total_pay = jours_travailles * salaire_jour
        st.write(f"💵 **المبلغ الجملي للخلاص:** {total_pay} د.ت")
        if st.button("حفظ الخلاص"):
            st.success(f"تم تسجيل خلاص العامل {ouvrier_selectionne} بقيمة {total_pay} د.ت بنجاح!")

    elif menu == "📊 تقدم الأشغال (Par Jour / Semaine / Totale)":
        st.title("📊 متابعة تقدم الأشغال (Avancement)")
        
        liste_articles = ["حفر الأساسات (Fouilles)", "صب البتون تنظيف (Béton de propreté)", "تركيـز الحديد (Ferraillage)", "صب البتون المسلح (Coulage)"]
        article_choisi = st.selectbox("اختر بند الأشغال (Article):", liste_articles)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            av_jour = st.number_input("التقدم اليومي (%):", 0.0, 100.0)
        with col2:
            av_semaine = st.number_input("التقدم الأسبوعي (%):", 0.0, 100.0)
        with col3:
            av_totale = st.number_input("التقدم الإجمالي (%):", 0.0, 100.0)
            
        st.markdown("---")
        st.subheader(f"📈 تقرير إنجاز: {article_choisi}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("يومي (Par Jour)", f"{av_jour}%")
        m2.metric("أسبوعي (Par Semaine)", f"{av_semaine}%")
        m3.metric("إجمالي (Totale)", f"{av_totale}%")
        
        if st.button("حفظ نسب الإنجاز"):
            st.success(f"تم تسجيل تقدم الـ Article '{article_choisi}' بنجاح!")
