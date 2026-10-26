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
    .img-box {
        border-radius: 10px;
        border: 2px solid #ddd;
        padding: 5px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

os.makedirs("uploads", exist_ok=True)

logo_path = None
if os.path.exists("uploads/logo_saved.jpg"):
    logo_path = "uploads/logo_saved.jpg"
elif os.path.exists("logo.jpg"):
    logo_path = "logo.jpg"
elif os.path.exists("logo.png"):
    logo_path = "logo.png"

st.sidebar.markdown('<div class="brand-container">', unsafe_allow_html=True)
if logo_path:
    st.sidebar.image(logo_path, width=110)
else:
    st.sidebar.markdown("<h1 style='text-align: center; margin:0;'>🏗️</h1>", unsafe_allow_html=True)

st.sidebar.markdown("<p class='brand-title'>H.O Bâtiment</p>", unsafe_allow_html=True)
st.sidebar.markdown("<p class='brand-subtitle'>Construction & Travaux Publics</p>", unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", [
    "خليج الشعرة (Khalij Chaara)", 
    "بوخروف (Boukharouf)"
])

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
            "بشير بن حميد": {
                "specialite": "رئيس مجموعة / بناي",
                "tel": "99 888 777",
                "taux_jour": 65,
                "jours_total": 50,
                "jours_semaine": 6,
                "paye_total": 2500,
                "avances": 400,
            },
            "صالح بن عمار": {
                "specialite": "بناي محترف",
                "tel": "98 123 456",
                "taux_jour": 60,
                "jours_total": 65,
                "jours_semaine": 5,
                "paye_total": 3000,
                "avances": 500,
            },
            "الهادي العياري": {
                "specialite": "مانوفري",
                "tel": "22 345 678",
                "taux_jour": 40,
                "jours_total": 40,
                "jours_semaine": 3,
                "paye_total": 1500,
                "avances": 300,
            },
        },
        "articles": {
            "Bordure T2": {"objectif": 1000, "fait_total": 650, "fait_semaine": 120, "unite": "ml"},
            "Bordure Mince P2": {"objectif": 800, "fait_total": 400, "fait_semaine": 80, "unite": "ml"},
            "Caniveau CS2": {"objectif": 500, "fait_total": 250, "fait_semaine": 40, "unite": "ml"},
            "Caniveau CC2": {"objectif": 300, "fait_total": 150, "fait_semaine": 30, "unite": "ml"},
            "Pavé autobloquant": {"objectif": 600, "fait_total": 200, "fait_semaine": 50, "unite": "م²"},
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
            "بشير بن حميد": {
                "specialite": "رئيس الفريق",
                "tel": "99 888 777",
                "taux_jour": 70,
                "jours_total": 30,
                "jours_semaine": 6,
                "paye_total": 1500,
                "avances": 200,
            },
            "جمعة المجبري": {
                "specialite": "رئيس الفريق",
                "tel": "55 789 012",
                "taux_jour": 70,
                "jours_total": 30,
                "jours_semaine": 6,
                "paye_total": 1500,
                "avances": 200,
            },
            "علي الطرابلسي": {
                "specialite": "بناي",
                "tel": "24 567 890",
                "taux_jour": 60,
                "jours_total": 25,
                "jours_semaine": 4,
                "paye_total": 1000,
                "avances": 100,
            },
        },
        "articles": {
            "Double Cloison 0.35m": {"objectif": 500, "fait_total": 250, "fait_semaine": 50, "unite": "م²"},
            "Cloison 0.25m": {"objectif": 400, "fait_total": 200, "fait_semaine": 40, "unite": "م²"},
            "Enduit extérieur": {"objectif": 1000, "fait_total": 500, "fait_semaine": 80, "unite": "م²"},
            "Enduit intérieur": {"objectif": 900, "fait_total": 450, "fait_semaine": 70, "unite": "م²"},
            "Carrelage marbré 25x25": {"objectif": 600, "fait_total": 300, "fait_semaine": 60, "unite": "م²"},
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
# إدارة ملفات الخدامة (بدون CIN وزر الرفع يختفي بعد وضع الصورة)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 👷 ملفات الخدامة")
ouvrier_choisi = st.sidebar.selectbox("اختر الخدام:", [""] + list(p_data["ouvriers"].keys()))

if ouvrier_choisi and ouvrier_choisi != "":
    o = p_data["ouvriers"][ouvrier_choisi]
    salaire_merite = o["jours_total"] * o["taux_jour"]
    solde = salaire_merite - (o["paye_total"] + o["avances"])
    
    st.sidebar.markdown(f"<h3 style='text-align: center;'>👷‍♂️ {ouvrier_choisi}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align: center; color: gray; margin-top: -10px;'>{o['specialite']}</p>", unsafe_allow_html=True)
    
    safe_name = ouvrier_choisi.replace(" ", "_")
    img_path = f"uploads/{safe_name}_photo.jpg"
    
    # إذا الصورة موجودة: نظهرها فقط ويختفي مربع الرفع (Upload) تماماً
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
    st.sidebar.write(f"📅 **خدم جملة:** {o['jours_total']} يوم")
    st.sidebar.write(f"💰 **خالص جملة:** {o['paye_total']} د | **آفونس:** {o['avances']} د")
    
    if solde > 0:
        st.sidebar.error(f"🔴 مستحقاته الباقية: {solde} دينار")
    elif solde < 0:
        st.sidebar.warning(f"⚠️ في الروج بـ: {abs(solde)} دينار")
    else:
        st.sidebar.success("✅ الحساب خالص ومريقل")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚧 متابعة الأشغال والـ Articles")

articles_disponibles = list(p_data["articles"].keys())
article_selectionne = st.sidebar.selectbox("🔍 اختر العنصر:", [""] + articles_disponibles)

if article_selectionne and article_selectionne != "":
    tache_trouvee = p_data["articles"][article_selectionne]
    pourcentage = min(int((tache_trouvee['fait_total'] / tache_trouvee['objectif']) * 100), 100)
    
    st.sidebar.write(f"📊 **التقدم في ({article_selectionne}):** {pourcentage}%")
    st.sidebar.progress(pourcentage)
    st.sidebar.write(f"✅ **خدمنا جملة:** {tache_trouvee['fait_total']} / {tache_trouvee['objectif']} {tache_trouvee['unite']}")
    st.sidebar.write(f"⚡ **خدمنا الجمعة هذه:** {tache_trouvee['fait_semaine']} {tache_trouvee['unite']}")
    
    reste = tache_trouvee['objectif'] - tache_trouvee['fait_total']
    if reste > 0:
        st.sidebar.write(f"⏳ **مازال ناقص:** {reste} {tache_trouvee['unite']}")
    else:
        st.sidebar.write("✅ **كملت 100%**")

# ==========================================
# الواجهة الرئيسية (Main Page)
# ==========================================
st.title(f"📅 H.O Bâtiment - {projet_choisi}")
st.markdown("**Entreprise H.O Construction & Travaux Publics** - Suivi des Chantiers & Avancement")

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
col_stat1.metric("🟢 أيام العمل", f"{p_data['stats']['vert']} يوم")
col_stat2.metric("🟡 إيقاف الأشغال", f"{p_data['stats']['jaune']} يوم")
col_stat3.metric("🌧️ طقس خايب", f"{p_data['stats']['meteo']} يوم")
col_stat4.metric("🔵 راحة عادية", f"{p_data['stats']['conge']} يوم")
st.markdown("---")

jour = st.session_state.jour_clique
if jour:
    st.info(f"📅 **تفاصيل يوم الرزنامة: {jour}**")
    if jour in donnees_chantier:
        etat = donnees_chantier[jour]["etat"]
        if etat == "vert":
            st.success(f"🟢 يوم عمل فعلي — **التفاصيل:** {donnees_chantier[jour]['details'].get('travail', '')}")
        elif etat == "visite":
            st.info(f"📋 زيارة رسمية — **البيان:** {donnees_chantier[jour]['details'].get('travail', '')}")
        elif etat == "jaune":
            st.warning(f"🟡 إيقاف الأشغال — **السبب:** {donnees_chantier[jour]['details']['probleme']}")
        elif etat == "meteo":
            st.error(f"🌧️ توقف بسبب الطقس — **التفاصيل:** {donnees_chantier[jour]['details']['probleme']}")
        elif etat == "conge":
            st.info(f"🔵 يوم راحة عادي — **البيان:** {donnees_chantier[jour]['details'].get('travail', '')}")
    else:
        st.write("📝 لا يوجد تسجيل خاص في هذا اليوم.")
else:
    st.markdown("👉 **انقر على أي يوم في الرزنامة أسفله لمتابعة تفاصيله هنا:**")

st.markdown("---")

mois_arabes = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
annee = date_debut.year
mois_a_afficher = list(range(date_debut.month, 13))

def get_couleur_jour(date_str):
    if date_str in donnees_chantier:
        etat = donnees_chantier[date_str]["etat"]
        if etat == "vert": return "🟢"
        if etat == "visite": return "📋"
        if etat == "jaune": return "🟡"
        if etat == "meteo": return "🌧️"
        if etat == "conge": return "🔵"
    return "⬜"

for i in range(0, len(mois_a_afficher), 2):
    col1, col2 = st.columns(2)
    
    m1 = mois_a_afficher[i]
    with col1:
        st.markdown(f"<h5 style='text-align: center; background-color: #f0f2f6; padding: 5px; border-radius: 5px;'>شهر {mois_arabes[m1-1]} {annee}</h5>", unsafe_allow_html=True)
        jours_semaine = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
        cols_j1 = st.columns(7)
        for k, j in enumerate(jours_semaine): cols_j1[k].markdown(f"<div style='text-align: center; font-size: 11px; font-weight: bold;'>{j[:4]}</div>", unsafe_allow_html=True)
        
        for semaine in calendar.monthcalendar(annee, m1):
            cols = st.columns(7)
            for k, jour in enumerate(semaine):
                if jour == 0: cols[k].write("")
                else:
                    date_str = f"{annee}-{m1:02d}-{jour:02d}"
                    if date(annee, m1, jour) < date_debut: cols[k].markdown(f"<div style='text-align:center; color:grey; font-size: 12px;'>🚫</div>", unsafe_allow_html=True)
                    else: cols[k].button(f"{get_couleur_jour(date_str)} {jour}", key=f"btn_{projet_choisi}_{date_str}", on_click=set_jour, args=(date_str,), use_container_width=True)
                        
    if i + 1 < len(mois_a_afficher):
        m2 = mois_a_afficher[i+1]
        with col2:
            st.markdown(f"<h5 style='text-align: center; background-color: #f0f2f6; padding: 5px; border-radius: 5px;'>شهر {mois_arabes[m2-1]} {annee}</h5>", unsafe_allow_html=True)
            cols_j2 = st.columns(7)
            for k, j in enumerate(jours_semaine): cols_j2[k].markdown(f"<div style='text-align: center; font-size: 11px; font-weight: bold;'>{j[:4]}</div>", unsafe_allow_html=True)
            
            for semaine in calendar.monthcalendar(annee, m2):
                cols = st.columns(7)
                for k, jour in enumerate(semaine):
                    if jour == 0: cols[k].write("")
                    else:
                        date_str = f"{annee}-{m2:02d}-{jour:02d}"
                        if date(annee, m2, jour) < date_debut: cols[k].markdown(f"<div style='text-align:center; color:grey; font-size: 12px;'>🚫</div>", unsafe_allow_html=True)
                        else: cols[k].button(f"{get_couleur_jour(date_str)} {jour}", key=f"2_btn_{projet_choisi}_{date_str}", on_click=set_jour, args=(date_str,), use_container_width=True)
