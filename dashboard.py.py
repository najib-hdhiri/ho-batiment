import streamlit as st
import calendar
from datetime import date
import os

st.set_page_config(page_title="H.O Construction - Tableau de Bord", page_icon="🏗️", layout="wide")

# ==========================================
# تصميم CSS فخم ومنظم للملفات واللوغو
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

os.makedirs("uploads", exist_ok=True)

# ==========================================
# إدارة اللوغو
# ==========================================
logo_path = None
for p in ["uploads/logo_saved.jpg", "logo.jpg", "logo.png"]:
    if os.path.exists(p):
        logo_path = p
        break

st.sidebar.markdown('<div class="brand-container">', unsafe_allow_html=True)
if logo_path:
    col_l1, col_l2, col_l3 = st.sidebar.columns([1, 2, 1])
    with col_l2:
        st.sidebar.image(logo_path, width=110)
else:
    st.sidebar.markdown("<h1 style='text-align: center; margin:0;'>🏗️</h1>", unsafe_allow_html=True)

st.sidebar.markdown("<p class='brand-title'>H.O Bâtiment</p>", unsafe_allow_html=True)
st.sidebar.markdown("<p class='brand-subtitle'>Construction & Travaux Publics</p>", unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

if not logo_path:
    up_logo = st.sidebar.file_uploader("🖼️ أضف شعار الشركة (Logo):", type=["jpg", "png", "jpeg"], key="up_logo_ho")
    if up_logo is not None:
        with open("uploads/logo_saved.jpg", "wb") as f:
            f.write(up_logo.getbuffer())
        st.rerun()

st.sidebar.markdown("---")

projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", [
    "خليج الشعرة (Khalij Chaara)", 
    "بوخروف (Boukharouf)"
])

# ==========================================
# قاعدة البيانات المستخرجة من جدول الأسعار
# ==========================================
base_donnees_projets = {
    "خليج الشعرة (Khalij Chaara)": {
        "date_debut": date(2026, 5, 18),
        "stats": {"vert": 65, "jaune": 44, "gris": 12, "meteo": 8, "conge": 5},
        "jours": {
            "2026-05-18": {"etat": "vert", "details": {"travail": "انطلاق الشانطي ووضع البوردور T2"}},
            "2026-05-19": {"etat": "jaune", "details": {"probleme": "أرضية غير مهيئة"}},
            "2026-05-26": {"etat": "meteo", "details": {"probleme": "طقس خايب (أمطار وعواصف)"}},
            "2026-05-29": {"etat": "conge", "details": {"travail": "يوم راحة عادي"}},
            "2026-06-11": {"etat": "visite", "details": {"travail": "زيارة السيد المدير العام"}},
        },
        "ouvriers": {
            "بشير بن حميد": {"specialite": "رئيس مجموعة / بناي", "tel": "99 888 777", "taux_jour": 65, "jours_total": 50, "jours_semaine": 6, "paye_total": 2500, "avances": 400},
            "صالح بن عمار": {"specialite": "بناي محترف", "tel": "98 123 456", "taux_jour": 60, "jours_total": 65, "jours_semaine": 5, "paye_total": 3000, "avances": 500},
            "الهادي العياري": {"specialite": "مانوفري", "tel": "22 345 678", "taux_jour": 40, "jours_total": 40, "jours_semaine": 3, "paye_total": 1500, "avances": 300},
        },
        "articles": {
            "Bordure T2": {"objectif": 7700.0, "fait_total": 650, "fait_semaine": 120, "unite": "ml"},
            "Bordure Mince P2": {"objectif": 7250.0, "fait_total": 400, "fait_semaine": 80, "unite": "ml"},
            "Caniveau CS2": {"objectif": 7700.0, "fait_total": 250, "fait_semaine": 40, "unite": "ml"},
            "Caniveau CC2": {"objectif": 500.0, "fait_total": 150, "fait_semaine": 30, "unite": "ml"},
            "Pavé autobloquant": {"objectif": 15500.0, "fait_total": 200, "fait_semaine": 50, "unite": "م²"},
        }
    },
    "بوخروف (Boukharouf)": {
        "date_debut": date(2026, 6, 1),
        "stats": {"vert": 30, "jaune": 10, "gris": 5, "meteo": 4, "conge": 3},
        "jours": {
            "2026-06-01": {"etat": "vert", "details": {"travail": "دخول الآلات وبداية التهيئة"}},
            "2026-06-02": {"etat": "meteo", "details": {"probleme": "رياح قوية وأمطار"}},
        },
        "ouvriers": {
            "بشير بن حميد": {"specialite": "رئيس الفريق", "tel": "99 888 777", "taux_jour": 70, "jours_total": 30, "jours_semaine": 6, "paye_total": 1500, "avances": 200},
            "جمعة المجبري": {"specialite": "رئيس الفريق", "tel": "55 789 012", "taux_jour": 70, "jours_total": 30, "jours_semaine": 6, "paye_total": 1500, "avances": 200},
            "علي الطرابلسي": {"specialite": "بناي", "tel": "24 567 890", "taux_jour": 60, "jours_total": 25, "jours_semaine": 4, "paye_total": 1000, "avances": 100},
        },
        "articles": {
            "A.01 Double Cloison 0.35m": {"objectif": 1450.0, "fait_total": 250, "fait_semaine": 50, "unite": "م²"},
            "A.02 Double Cloison 0.30m": {"objectif": 110.0, "fait_total": 40, "fait_semaine": 15, "unite": "م²"},
            "A.03 Cloison 0.25m": {"objectif": 1150.0, "fait_total": 200, "fait_semaine": 40, "unite": "م²"},
            "A.04 Cloison 0.20m": {"objectif": 5.0, "fait_total": 2, "fait_semaine": 1, "unite": "م²"},
            "A.05 Cloison 0.15m": {"objectif": 180.0, "fait_total": 50, "fait_semaine": 10, "unite": "م²"},
            "A.06 Cloison 0.10m": {"objectif": 400.0, "fait_total": 100, "fait_semaine": 20, "unite": "م²"},
            "B-1 Enduit extérieur": {"objectif": 4700.0, "fait_total": 500, "fait_semaine": 80, "unite": "م²"},
            "B-2 Enduit intérieur": {"objectif": 2050.0, "fait_total": 450, "fait_semaine": 70, "unite": "م²"},
            "B-3 Enduit sous plafond": {"objectif": 1900.0, "fait_total": 300, "fait_semaine": 50, "unite": "م²"},
            "B-4 Enduit grillagé": {"objectif": 350.0, "fait_total": 50, "fait_semaine": 10, "unite": "م²"},
            "B-5 Enduit de ravoirage": {"objectif": 850.0, "fait_total": 150, "fait_semaine": 30, "unite": "م²"},
            "C-1 Carrelage marbré 25x25": {"objectif": 1150.0, "fait_total": 300, "fait_semaine": 60, "unite": "م²"},
            "C-2 Carrelage carreaux": {"objectif": 2400.0, "fait_total": 600, "fait_semaine": 100, "unite": "م²"},
            "C-3 Revêtement carreaux": {"objectif": 190.0, "fait_total": 40, "fait_semaine": 10, "unite": "م²"},
            "C-4 Plinthe": {"objectif": 1000.0, "fait_total": 200, "fait_semaine": 40, "unite": "ml"},
            "C-5 Revêtement extérieur": {"objectif": 15.0, "fait_total": 5, "fait_semaine": 2, "unite": "م²"},
            "C-6 Seuils en marbre Thala": {"objectif": 15.0, "fait_total": 4, "fait_semaine": 1, "unite": "م²"},
            "C-7 Siffle en marbre Thala": {"objectif": 50.0, "fait_total": 10, "fait_semaine": 5, "unite": "ml"},
        }
    }
}

p_data = base_donnees_projets[projet_choisi]
donnees_chantier = p_data["jours"]
date_debut = p_data["date_debut"]

if 'jour_clique' not in st.session_state:
    st.session_state.jour_clique = None

def set_jour(jour):
    st.session_state.jour_clique = jour

# ==========================================
# إدارة ملفات الخدامة (مع متابعة أيام الأسبوع من لثنين للأحد)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 👷 ملفات الخدامة ومتابعة الأسبوع")
ouvrier_choisi = st.sidebar.selectbox("اختر الخدام:", [""] + list(p_data["ouvriers"].keys()))

if ouvrier_choisi and ouvrier_choisi != "":
    o = p_data["ouvriers"][ouvrier_choisi]
    
    st.sidebar.markdown(f"<h3 style='text-align: center;'>👷‍♂️ {ouvrier_choisi}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align: center; color: gray; margin-top: -10px;'>{o['specialite']}</p>", unsafe_allow_html=True)
    
    safe_name = ouvrier_choisi.replace(" ", "_")
    img_path = f"uploads/{safe_name}_photo.jpg"
    
    if os.path.exists(img_path):
        st.sidebar.image(img_path, width=140)
    else:
        img_ouvrier = st.sidebar.file_uploader(f"🖼️ صورة {ouvrier_choisi}:", type=["jpg", "png", "jpeg"], key=f"img_{ouvrier_choisi}")
        if img_ouvrier is not None:
            with open(img_path, "wb") as f:
                f.write(img_ouvrier.getbuffer())
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.write(f"📞 **الهاتف:** {o['tel']}")
    st.sidebar.write(f"💵 **خلاص نهاره:** {o['taux_jour']} دينار")
    
    # تتبع أيام العمل الأسبوعية (من الإثنين للأحد) مربوط بالذكاء الاصطناعي والحسابات
    st.sidebar.markdown("📅 **متابعة أيام العمل (من الإثنين للأحد):**")
    jours_semaine_noms = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    
    jours_travailles_semaine = 0.0
    for js in jours_semaine_noms:
        val_j = st.sidebar.number_input(f"{js}:", min_value=0.0, max_value=1.0, value=1.0, step=0.5, key=f"{ouvrier_choisi}_{js}")
        jours_travailles_semaine += val_j
        
    st.sidebar.info(defaut_semaine := f"⚡ مجموع أيام هذه اللحمة (الإثنين-الأحد): **{jours_trava
