import streamlit as st
import calendar
from datetime import date, datetime
import os
import csv

st.set_page_config(page_title="H.O Construction - Tableau de Bord", page_icon="🏗️", layout="wide")

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

os.makedirs("uploads", exist_ok=True)

# جلب لوجو الشركة
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
st.sidebar.markdown("<p class='brand-subtitle'>Construction & Travaux Publics</p>", unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# اختيار المشروع
projet_choisi = st.sidebar.selectbox("📂 اختر المشروع:", [
    "LOT 2 - KHALIJ CHAARA",
    "LOT 1 - BOUKHROUF"
])

# ==========================================
# الأهداف التعاقدية ومعطيات المشاريع
# ==========================================
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
            "Double Cloison 0.35m": {"nom_csv": "double cloison 0,35 m", "objectif": 1450.0, "unite": "م²"},
            "Double Cloison 0.30m": {"nom_csv": "double cloison 0,30 m", "objectif": 110.0, "unite": "م²"},
            "Cloison 0.25m": {"nom_csv": "cloison 0,25 m", "objectif": 1150.0, "unite": "م²"},
            "Enduit extérieur": {"nom_csv": "enduit exterieur", "objectif": 4700.0, "unite": "م²"},
            "Enduit intérieur": {"nom_csv": "enduit interieur", "objectif": 2050.0, "unite": "م²"},
            "Carrelage marbre 25x25": {"nom_csv": "carrelage marbre 25x25", "objectif": 1150.0, "unite": "م²"},
        }
    }
}

p_conf = objectifs_projets[projet_choisi]
date_debut = p_conf["date_debut"]

# ==========================================
# دالة القراءة المباشرة من ملفات الـ CSV
# ==========================================
def charger_donnees(lot_cible):
    jours_data = {}
    ouvriers_total_jours = 0.0
    ouvriers_par_nom = {}
    quantites_realisees = {k: 0.0 for k in p_conf["articles"].keys()}
    stats = {"vert": 0, "jaune": 0, "meteo": 0, "conge": 0}

    # 1. قراءة الأشغال واليد العاملة من journal_chantier.csv
    if os.path.exists(FICHIER_CHANTIER):
        with open(FICHIER_CHANTIER, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for ligne in reader:
                if (ligne.get("Lot") or "").strip() != lot_cible:
                    continue
                
                date_raw = (ligne.get("Date") or "")[:10].strip()
                try:
                    d_obj = datetime.strptime(date_raw, "%d/%m/%Y")
                    date_iso = d_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

                op = (ligne.get("Operation") or "").strip().lower()
                desc = (ligne.get("Description") or "").strip().lower()
                try:
                    qte = float((ligne.get("Quantite") or "0").replace(",", "."))
                except ValueError:
                    qte = 0.0

                if date_iso not in jours_data:
                    jours_data[date_iso] = {"etat": "vert", "details": {"travail": []}}
                
                if op == "travaux":
                    jours_data[date_iso]["details"]["travail"].append(f"{ligne.get('Description')}: {qte} {ligne.get('Unite')}")
                    # تجميع كميات الفصول
                    for art_nom, art_info in p_conf["articles"].items():
                        if art_info["nom_csv"] in desc:
                            quantites_realisees[art_nom] += qte

                elif op == "personnel":
                    ouvriers_total_jours += qte

    # 2. قراءة التعطيلات والتوقفات من journal_perturbations.csv
    if os.path.exists(FICHIER_INCIDENTS):
        with open(FICHIER_INCIDENTS, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for ligne in reader:
                if (ligne.get("Lot") or "").strip() != lot_cible:
                    continue

                date_raw = (ligne.get("Date") or "")[:10].strip()
                try:
                    if "/" in date_raw:
                        d_obj = datetime.strptime(date_raw, "%d/%m/%Y")
                    else:
                        d_obj = datetime.strptime(date_raw, "%Y-%m-%d")
                    date_iso = d_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

                type_inc = (ligne.get("Type") or "").strip()
                cause = (ligne.get("Cause") or "").strip()
                obs = (ligne.get("Observations") or "").strip()
                details_txt = cause + (f" ({obs})" if obs else "")

                if "meteo" in cause.lower() or "مطر" in cause.lower() or "ريح" in cause.lower():
                    jours_data[date_iso] = {"etat": "meteo", "details": {"probleme": details_txt}}
                else:
                    jours_data[date_iso] = {"etat": "jaune", "details": {"probleme": details_txt}}

    # حساب الإحصائيات
    for j, data in jours_data.items():
        etat = data["etat"]
        if etat in stats:
            stats[etat] += 1

    return jours_data, quantites_realisees, ouvriers_total_jours, stats

donnees_chantier, quantites_realisees, ouvriers_total_jours, stats = charger_donnees(projet_choisi)

if 'jour_clique' not in st.session_state:
    st.session_state.jour_clique = None

def set_jour(jour):
    st.session_state.jour_clique = jour

# ==========================================
# متابعة الأشغال في القائمة الجانبية (Sidebar)
# ==========================================
st.sidebar.markdown("### 🚧 تقدم الأشغال التعاقدية (حي من الـ CSV)")

for art_nom, art_info in p_conf["articles"].items():
    fait = quantites_realisees.get(art_nom, 0.0)
    obj = art_info["objectif"]
    pct = min(int((fait / obj) * 100), 100) if obj > 0 else 0
    
    st.sidebar.write(f"**{art_nom}** : {pct}% ({fait:.1f} / {obj:.0f} {art_info['unite']})")
    st.sidebar.progress(pct)

# ==========================================
# الصفحة الرئيسية (Main View)
# ==========================================
st.title(f"🏗️ H.O Bâtiment — {projet_choisi}")
st.markdown("**متابعة حية متصلة مباشرة مع قاعدة بيانات الـ Agent IA**")

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
col_stat1.metric("🟢 أيام العمل الفعلية", f"{stats['vert']} يوم")
col_stat2.metric("🟡 أيام توقف الأشغال", f"{stats['jaune']} يوم")
col_stat3.metric("🌧️ توقف بسبب الطقس", f"{stats['meteo']} يوم")
col_stat4.metric("👷 مجموع أيام اليد العاملة", f"{ouvriers_total_jours:.1f} شخص-يوم")
st.markdown("---")

# تفاصيل اليوم عند النقر
jour = st.session_state.jour_clique
if jour:
    st.info(f"📅 **تفاصيل اليوم المحدد: {jour}**")
    if jour in donnees_chantier:
        etat = donnees_chantier[jour]["etat"]
        details = donnees_chantier[jour]["details"]
        if etat == "vert":
            travaux_str = " | ".join(details.get("travail", [])) if details.get("travail") else "يوم عمل مسجل"
            st.success(f"🟢 **أشغال منجزة:** {travaux_str}")
        elif etat == "jaune":
            st.warning(f"🟡 **إيقاف أشغال:** {details.get('probleme', 'بدون تفاصيل')}")
        elif etat == "meteo":
            st.error(f"🌧️ **توقف بسبب الطقس:** {details.get('probleme', 'أمطار أو رياح')}")
    else:
        st.write("📝 لا توجد عمليات مسجلة في هذا اليوم.")
else:
    st.markdown("👉 **انقر على أي يوم مسجل في الرزنامة أسفله للاطلاع على تفاصيله:**")

st.markdown("---")

# رسم الرزنامة التفاعلية
mois_arabes = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
annee = date_debut.year
mois_a_afficher = list(range(date_debut.month, 13))

def get_couleur_jour(date_str):
    if date_str in donnees_chantier:
        etat = donnees_chantier[date_str]["etat"]
        if etat == "vert": return "🟢"
        if etat == "jaune": return "🟡"
        if etat == "meteo": return "🌧️"
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
            for k, j_num in enumerate(semaine):
                if j_num == 0: 
                    cols[k].write("")
                else:
                    date_str = f"{annee}-{m1:02d}-{j_num:02d}"
                    if date(annee, m1, j_num) < date_debut: 
                        cols[k].markdown(f"<div style='text-align:center; color:grey; font-size: 12px;'>🚫</div>", unsafe_allow_html=True)
                    else: 
                        cols[k].button(f"{get_couleur_jour(date_str)} {j_num}", key=f"btn_{projet_choisi}_{date_str}", on_click=set_jour, args=(date_str,), use_container_width=True)
                        
    if i + 1 < len(mois_a_afficher):
        m2 = mois_a_afficher[i+1]
        with col2:
            st.markdown(f"<h5 style='text-align: center; background-color: #f0f2f6; padding: 5px; border-radius: 5px;'>شهر {mois_arabes[m2-1]} {annee}</h5>", unsafe_allow_html=True)
            cols_j2 = st.columns(7)
            for k, j in enumerate(jours_semaine): cols_j2[k].markdown(f"<div style='text-align: center; font-size: 11px; font-weight: bold;'>{j[:4]}</div>", unsafe_allow_html=True)
            
            for semaine in calendar.monthcalendar(annee, m2):
                cols = st.columns(7)
                for k, j_num in enumerate(semaine):
                    if j_num == 0: 
                        cols[k].write("")
                    else:
                        date_str = f"{annee}-{m2:02d}-{j_num:02d}"
                        if date(annee, m2, j_num) < date_debut: 
                            cols[k].markdown(f"<div style='text-align:center; color:grey; font-size: 12px;'>🚫</div>", unsafe_allow_html=True)
                        else: 
                            cols[k].button(f"{get_couleur_jour(date_str)} {j_num}", key=f"btn_{projet_choisi}_{date_str}_2", on_click=set_jour, args=(date_str,), use_container_width=True)
