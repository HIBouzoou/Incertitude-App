import streamlit as st
import numpy as np
import pandas as pd
from math import sqrt

st.set_page_config(page_title="Calculateur d'Incertitude Élargie", layout="wide")

st.title("📊 Calculateur d'Incertitude Élargie")
st.markdown("### Calcul de U = √(U_A² + U_B²)")

# Dictionnaire des coefficients d2 pour n < 20
d2_values = {
    2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326,
    6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970,
    10: 3.078, 11: 3.173, 12: 3.258, 13: 3.336,
    14: 3.407, 15: 3.472, 16: 3.532, 17: 3.588,
    18: 3.640, 19: 3.689
}

# ==================== CALCUL DE UA ====================
st.header("1️⃣ Calcul de U_A (Incertitude de Type A)")

with st.expander("📝 Saisie des mesures", expanded=True):
    n_mesures = st.number_input("Nombre de mesures", min_value=2, max_value=100, value=10, step=1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        mesures_input = st.text_area(
            "Saisissez les mesures (une par ligne)",
            height=200,
            help="Entrez chaque mesure sur une nouvelle ligne"
        )
    
    with col2:
        st.info("""
        **Instructions:**
        - Entrez vos mesures, une par ligne
        - Si n < 20 : σ = étendue/d2
        - Si n ≥ 20 : σ calculé normalement
        - Mesures dépendantes : U_A = σ
        - Mesures indépendantes : U_A = σ/√n
        """)

mesures = []
if mesures_input:
    try:
        mesures = [float(x.strip()) for x in mesures_input.split('\n') if x.strip()]
        n = len(mesures)
        
        if n >= 2:
            st.success(f"✅ {n} mesures saisies")
            
            # Afficher les statistiques
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Nombre de mesures", n)
            with col2:
                st.metric("Moyenne", f"{np.mean(mesures):.4f}")
            with col3:
                etendue = max(mesures) - min(mesures)
                st.metric("Étendue", f"{etendue:.4f}")
            
            # Calcul de l'écart-type
            if n < 20:
                d2 = d2_values.get(n, 1.0)
                ecart_type = etendue / d2
                st.info(f"📌 n < 20 → σ = étendue/d2 = {etendue:.4f}/{d2:.3f} = **{ecart_type:.4f}**")
            else:
                ecart_type = np.std(mesures, ddof=1)
                st.info(f"📌 n ≥ 20 → σ = **{ecart_type:.4f}** (écart-type calculé)")
            
            # Choix du type de mesures
            mesures_dependantes = st.radio(
                "Type de mesures",
                ["Indépendantes", "Dépendantes"],
                horizontal=True
            )
            
            if mesures_dependantes == "Dépendantes":
                UA = ecart_type
                st.success(f"### U_A = σ = **{UA:.4f}**")
            else:
                UA = ecart_type / sqrt(n)
                st.success(f"### U_A = σ/√n = {ecart_type:.4f}/√{n} = **{UA:.4f}**")
        else:
            st.warning("⚠️ Veuillez saisir au moins 2 mesures")
            UA = 0
    except ValueError:
        st.error("❌ Erreur de format. Assurez-vous d'entrer des nombres valides.")
        UA = 0
else:
    UA = 0

# ==================== CALCUL DE UB ====================
st.header("2️⃣ Calcul de U_B (Incertitude de Type B)")

with st.expander("📝 Configuration des paramètres", expanded=True):
    st.markdown("**Formule du mesurande : EI = f(X₁, X₂, X₃, ...)**")
    
    n_parametres = st.number_input(
        "Nombre de paramètres",
        min_value=1,
        max_value=10,
        value=3,
        step=1
    )
    
    st.markdown("---")
    
    # Dictionnaire des lois de probabilité et leurs coefficients
    lois_prob = {
        "Normale": 2.0,
        "Rectangulaire": sqrt(3),
        "Triangulaire": sqrt(6),
        "U (uniforme)": sqrt(3),
        "Arcsinus": sqrt(2)
    }
    
    parametres_data = []
    
    for i in range(n_parametres):
        st.markdown(f"### Paramètre X{i+1}")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            nom = st.text_input(f"Nom", value=f"X{i+1}", key=f"nom_{i}")
        
        with col2:
            max_val = st.number_input(f"Max", value=1.0, format="%.4f", key=f"max_{i}")
        
        with col3:
            min_val = st.number_input(f"Min", value=0.0, format="%.4f", key=f"min_{i}")
        
        with col4:
            loi = st.selectbox(f"Loi", list(lois_prob.keys()), key=f"loi_{i}")
        
        sensibilite = st.number_input(
            f"Sensibilité (∂EI/∂{nom})",
            value=1.0,
            format="%.4f",
            key=f"sens_{i}",
            help="Dérivée partielle de EI par rapport à ce paramètre"
        )
        
        etendue = max_val - min_val
        coeff_loi = lois_prob[loi]
        uxi = sensibilite * coeff_loi * (etendue / 2)
        
        parametres_data.append({
            "Paramètre": nom,
            "Min": min_val,
            "Max": max_val,
            "Étendue": etendue,
            "Loi": loi,
            "Coeff. loi": coeff_loi,
            "Sensibilité": sensibilite,
            "U(xi)": uxi,
            "U(xi)²": uxi**2
        })
        
        st.info(f"U({nom}) = {sensibilite:.4f} × {coeff_loi:.4f} × {etendue/2:.4f} = **{uxi:.4f}**")
        st.markdown("---")

# Affichage du tableau récapitulatif
if parametres_data:
    st.subheader("📋 Tableau récapitulatif")
    df = pd.DataFrame(parametres_data)
    st.dataframe(df, use_container_width=True)
    
    # Calcul de UB
    somme_carres = sum([p["U(xi)²"] for p in parametres_data])
    UB = sqrt(somme_carres)
    
    st.success(f"### U_B = √(Σ U(xi)²) = √{somme_carres:.6f} = **{UB:.4f}**")

else:
    UB = 0

# ==================== CALCUL DE U ====================
st.header("3️⃣ Incertitude Élargie U")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("U_A", f"{UA:.4f}")

with col2:
    st.metric("U_B", f"{UB:.4f}")

with col3:
    U = sqrt(UA**2 + UB**2)
    st.metric("U (Incertitude Élargie)", f"{U:.4f}", delta=None)

st.success(f"## 🎯 U = √(U_A² + U_B²) = √({UA:.4f}² + {UB:.4f}²) = **{U:.4f}**")

# Résumé détaillé
with st.expander("📊 Détails du calcul", expanded=False):
    st.markdown(f"""
    **Calcul détaillé:**
    
    - U_A² = {UA**2:.6f}
    - U_B² = {UB**2:.6f}
    - U_A² + U_B² = {UA**2 + UB**2:.6f}
    - U = √({UA**2 + UB**2:.6f}) = **{U:.4f}**
    """)

# Bouton de réinitialisation
if st.button("🔄 Réinitialiser tous les calculs"):
    st.rerun()
