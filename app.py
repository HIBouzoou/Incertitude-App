import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import StringIO

# Configuration de la page
st.set_page_config(page_title="Laboratoire de Métrologie", page_icon="🔬", layout="wide")

# Base de données des classes d'instruments
CLASSES_DB = {
    "Classe 0.5": {"EMT": 0.5, "Resolution": 0.01, "Plage": "0-100"},
    "Classe 1.0": {"EMT": 1.0, "Resolution": 0.1, "Plage": "0-200"},
    "Classe 1.5": {"EMT": 1.5, "Resolution": 0.1, "Plage": "0-500"},
    "Classe 2.5": {"EMT": 2.5, "Resolution": 0.5, "Plage": "0-1000"},
}

# Initialisation de la session state
if 'mesures' not in st.session_state:
    st.session_state.mesures = None
if 'validated' not in st.session_state:
    st.session_state.validated = False

# Titre principal
st.title("🔬 Bienvenue au Laboratoire de Métrologie")
st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Informations sur le mesurande
    st.subheader("1. Informations Mesurande")
    mesurande = st.text_input("Nom du mesurande", "Température", key="mesurande")
    unite = st.selectbox("Unité", ["°C", "°F", "K", "Pa", "Bar", "mm", "m"])
    
    st.subheader("2. Caractéristiques Instrument")
    classe = st.selectbox("Classe de l'instrument", list(CLASSES_DB.keys()))
    temperature = st.slider("Température ambiante (°C)", 15, 30, 20)
    homogeneite = st.selectbox("Homogénéité", ["Excellente", "Bonne", "Acceptable"])
    
    # Affichage des infos de la classe sélectionnée
    st.info(f"""
    **Classe sélectionnée: {classe}**
    - EMT: ±{CLASSES_DB[classe]['EMT']} {unite}
    - Résolution: {CLASSES_DB[classe]['Resolution']} {unite}
    - Plage: {CLASSES_DB[classe]['Plage']} {unite}
    """)
    
    st.subheader("3. Plan de mesure")
    nb_echantillons = st.number_input("Nombre d'échantillons", 1, 20, 5)
    nb_operateurs = st.number_input("Nombre d'opérateurs", 1, 10, 3)
    
    total_mesures = nb_echantillons * nb_operateurs
    st.success(f"**Total: {total_mesures} mesures à effectuer**")
    
    # Bouton de réinitialisation
    st.markdown("---")
    st.subheader("🔄 Réinitialisation")
    if st.button("🗑️ Effacer et Réinitialiser Tout", type="secondary", key="reset_btn"):
        st.session_state.mesures = None
        st.session_state.validated = False
        st.success("✅ Application réinitialisée !")
        st.rerun()

# Corps principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Saisie des Mesures")
    
    # Options d'import/export
    tab_input1, tab_input2, tab_input3 = st.tabs(["✏️ Saisie Manuelle", "📤 Import", "🎲 Données Test"])
    
    with tab_input1:
        if st.button("🔄 Initialiser le tableau", type="primary"):
            st.session_state.mesures = pd.DataFrame(
                np.nan,
                index=[f"Échantillon {i+1}" for i in range(int(nb_echantillons))],
                columns=[f"Opérateur {i+1}" for i in range(int(nb_operateurs))]
            )
            st.session_state.validated = False
            st.rerun()
    
    with tab_input2:
        st.subheader("📥 Importer vos données")
        
        # Import fichier
        uploaded_file = st.file_uploader("Charger un fichier CSV", type=['csv', 'txt'])
        
        if uploaded_file is not None:
            try:
                # Déterminer le type de fichier
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                if file_extension == 'csv':
                    df_import = pd.read_csv(uploaded_file, index_col=0)
                elif file_extension == 'txt':
                    df_import = pd.read_csv(uploaded_file, sep='\t', index_col=0)
                else:
                    st.error("Format non supporté")
                    df_import = None
                
                if df_import is not None:
                    st.success(f"✅ Fichier chargé: {df_import.shape[0]} échantillons × {df_import.shape[1]} opérateurs")
                    st.dataframe(df_import, width=700)
                    
                    if st.button("✅ Confirmer l'import", key="confirm_import"):
                        st.session_state.mesures = df_import
                        st.session_state.validated = False
                        st.success("Données importées!")
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
        
        # Import texte
        st.markdown("---")
        st.subheader("📝 Coller des données")
        text_data = st.text_area("Données (séparées par tabulation ou virgule)", height=150, 
                                 placeholder="Échantillon1\t12.5\t12.6\t12.4\nÉchantillon2\t12.7\t12.5\t12.6")
        
        if text_data:
            col_sep1, col_sep2 = st.columns(2)
            with col_sep1:
                separateur = st.radio("Séparateur", ["Tabulation", "Virgule", "Point-virgule"], horizontal=True)
            with col_sep2:
                has_header = st.checkbox("Première ligne = en-têtes", value=True)
            
            sep_map = {"Tabulation": "\t", "Virgule": ",", "Point-virgule": ";"}
            
            if st.button("✅ Charger texte", key="load_text"):
                try:
                    if has_header:
                        df_import = pd.read_csv(StringIO(text_data), sep=sep_map[separateur], index_col=0)
                    else:
                        df_import = pd.read_csv(StringIO(text_data), sep=sep_map[separateur], index_col=0, header=None)
                        df_import.columns = [f"Opérateur {i+1}" for i in range(df_import.shape[1])]
                    
                    st.session_state.mesures = df_import
                    st.session_state.validated = False
                    st.success("Données importées!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
        
        # Template CSV
        st.markdown("---")
        st.subheader("📋 Télécharger un modèle CSV")
        template_df = pd.DataFrame(
            np.nan,
            index=[f"Échantillon {i+1}" for i in range(int(nb_echantillons))],
            columns=[f"Opérateur {i+1}" for i in range(int(nb_operateurs))]
        )
        
        st.download_button(
            "📥 Télécharger Template CSV", 
            template_df.to_csv(), 
            "template_mesures.csv", 
            "text/csv",
            help="Fichier CSV vide à remplir avec vos mesures"
        )
    
    with tab_input3:
        st.subheader("🎲 Données de Test")
        
        type_test = st.selectbox(
            "Scénario",
            ["Excellentes", "Acceptables", "Avec Biais", "Non Conformes", "Personnalisées", "Grandes Séries"]
        )
        
        if type_test == "Excellentes":
            test_data = pd.DataFrame({
                'Opérateur 1': [20.15, 25.32, 30.48, 35.62, 40.78],
                'Opérateur 2': [20.18, 25.35, 30.52, 35.68, 40.82],
                'Opérateur 3': [20.12, 25.30, 30.45, 35.60, 40.75]
            }, index=[f"Échantillon {i+1}" for i in range(5)])
            st.info("✅ Écart-type ~0.05°C")
        
        elif type_test == "Acceptables":
            test_data = pd.DataFrame({
                'Opérateur 1': [20.1, 25.3, 30.5, 35.6, 40.8],
                'Opérateur 2': [20.3, 25.4, 30.7, 35.8, 41.0],
                'Opérateur 3': [19.9, 25.2, 30.4, 35.5, 40.6]
            }, index=[f"Échantillon {i+1}" for i in range(5)])
            st.info("ℹ️ Écart-type ~0.15°C")
        
        elif type_test == "Avec Biais":
            test_data = pd.DataFrame({
                'Opérateur 1': [20.15, 25.32, 30.48, 35.62, 40.78],
                'Opérateur 2': [20.45, 25.80, 31.05, 36.20, 41.35],
                'Opérateur 3': [19.95, 25.10, 30.20, 35.35, 40.50]
            }, index=[f"Échantillon {i+1}" for i in range(5)])
            st.warning("⚠️ Opérateur 2 : +0.5°C")
        
        elif type_test == "Non Conformes":
            test_data = pd.DataFrame({
                'Opérateur 1': [20.2, 25.5, 30.8, 35.9, 41.2],
                'Opérateur 2': [20.8, 26.2, 31.5, 36.8, 42.0],
                'Opérateur 3': [19.5, 24.8, 29.9, 35.0, 40.1]
            }, index=[f"Échantillon {i+1}" for i in range(5)])
            st.error("❌ Écart-type ~0.60°C")
        
        elif type_test == "Personnalisées":
            test_data = pd.DataFrame({
                'Opérateur 1': [12.45, 15.67, 18.23, 21.89, 24.12],
                'Opérateur 2': [12.50, 15.70, 18.28, 21.95, 24.18],
                'Opérateur 3': [12.42, 15.65, 18.20, 21.85, 24.08]
            }, index=[f"Échantillon {i+1}" for i in range(5)])
            st.info("📊 Données mixtes")
        
        else:
            np.random.seed(42)
            base_values = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65]
            test_data = pd.DataFrame({
                f'Opérateur {i+1}': [val + np.random.normal(0, 0.1) for val in base_values]
                for i in range(5)
            }, index=[f"Échantillon {i+1}" for i in range(10)])
            st.info("📈 10 × 5 mesures")
        
        st.dataframe(test_data.round(3), width=700)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Moyenne", f"{test_data.values.mean():.3f}")
        with col_s2:
            st.metric("Écart-type", f"{test_data.values.std():.3f}")
        with col_s3:
            st.metric("Étendue", f"{(test_data.values.max() - test_data.values.min()):.3f}")
        
        if st.button("✅ Charger", type="primary", key="load_test"):
            st.session_state.mesures = test_data
            st.session_state.validated = False
            st.success(f"✅ Données chargées: {test_data.shape[0]}×{test_data.shape[1]}")
            st.rerun()
    
    if st.session_state.mesures is not None:
        st.markdown("---")
        st.write(f"**{mesurande}** ({unite}) • {st.session_state.mesures.shape[0]}×{st.session_state.mesures.shape[1]}")
        
        edited_df = st.data_editor(
            st.session_state.mesures,
            width=700,
            num_rows="fixed",
            key="data_editor"
        )
        
        if st.button("✅ Valider", type="primary"):
            if edited_df.isna().any().any():
                st.warning("⚠️ Certaines cellules sont vides")
            else:
                st.session_state.mesures = edited_df
                st.session_state.validated = True
                st.success("✅ Validé!")
                st.rerun()

with col2:
    st.header("📊 Classes")
    df_classes = pd.DataFrame(CLASSES_DB).T
    st.dataframe(df_classes, width=400)
    st.info("💡 EMT = Erreur Maximale Tolérée")

# Section Résultats
if st.session_state.validated and st.session_state.mesures is not None:
    st.markdown("---")
    st.header("📈 Résultats et Analyses")
    
    df = st.session_state.mesures
    
    # Calculs statistiques
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Moyenne générale", f"{df.values.mean():.3f} {unite}")
        st.metric("Écart-type général", f"{df.values.std():.3f} {unite}")
    
    with col2:
        st.metric("Minimum", f"{df.values.min():.3f} {unite}")
        st.metric("Maximum", f"{df.values.max():.3f} {unite}")
    
    with col3:
        etendue = df.values.max() - df.values.min()
        st.metric("Étendue", f"{etendue:.3f} {unite}")
        cv = (df.values.std() / df.values.mean() * 100) if df.values.mean() != 0 else 0
        st.metric("Coefficient Variation", f"{cv:.2f} %")
    
    # Analyses détaillées
    tab1, tab2, tab3 = st.tabs(["📊 Par Échantillon", "👥 Par Opérateur", "📋 Tableau Complet"])
    
    with tab1:
        st.subheader("Statistiques par échantillon")
        stats_echantillons = pd.DataFrame({
            'Moyenne': df.mean(axis=1),
            'Écart-type': df.std(axis=1),
            'Min': df.min(axis=1),
            'Max': df.max(axis=1),
            'Étendue': df.max(axis=1) - df.min(axis=1)
        })
        st.dataframe(stats_echantillons.round(3), width=700)
    
    with tab2:
        st.subheader("Statistiques par opérateur")
        stats_operateurs = pd.DataFrame({
            'Moyenne': df.mean(axis=0),
            'Écart-type': df.std(axis=0),
            'Min': df.min(axis=0),
            'Max': df.max(axis=0),
            'Étendue': df.max(axis=0) - df.min(axis=0)
        })
        st.dataframe(stats_operateurs.round(3), width=700)
    
    with tab3:
        st.subheader("Tableau complet des mesures")
        st.dataframe(df.round(3), width=700)
    
    # Analyse de conformité
    st.markdown("---")
    st.subheader("🎯 Analyse de Conformité")
    
    emt = CLASSES_DB[classe]['EMT']
    ecart_type = df.values.std()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if ecart_type <= emt / 3:
            st.success(f"✅ **Excellent:** Écart-type ({ecart_type:.3f}) << EMT/3 ({emt/3:.3f})")
        elif ecart_type <= emt / 2:
            st.info(f"ℹ️ **Acceptable:** Écart-type ({ecart_type:.3f}) < EMT/2 ({emt/2:.3f})")
        else:
            st.error(f"❌ **Non conforme:** Écart-type ({ecart_type:.3f}) > EMT/2 ({emt/2:.3f})")
    
    with col2:
        st.write(f"**Paramètres de référence:**")
        st.write(f"• EMT: ±{emt} {unite}")
        st.write(f"• Résolution: {CLASSES_DB[classe]['Resolution']} {unite}")
        st.write(f"• Température: {temperature}°C")
        st.write(f"• Homogénéité: {homogeneite}")
    
    # Exports
    st.markdown("---")
    st.subheader("📥 Exporter les Résultats")
    
    col_e1, col_e2, col_e3 = st.columns(3)
    
    with col_e1:
        # Export rapport texte
        rapport = f"""RAPPORT DE MÉTROLOGIE
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
=====================================

CONFIGURATION
- Mesurande: {mesurande} ({unite})
- Classe: {classe}
- EMT: ±{emt} {unite}
- Température: {temperature}°C
- Homogénéité: {homogeneite}

PLAN DE MESURE
- Échantillons: {df.shape[0]}
- Opérateurs: {df.shape[1]}
- Total mesures: {df.shape[0] * df.shape[1]}

RÉSULTATS GÉNÉRAUX
- Moyenne: {df.values.mean():.3f} {unite}
- Écart-type: {df.values.std():.3f} {unite}
- Min: {df.values.min():.3f} {unite}
- Max: {df.values.max():.3f} {unite}
- Étendue: {etendue:.3f} {unite}
- CV: {cv:.2f} %

CONFORMITÉ
- EMT/3: {emt/3:.3f} {unite}
- EMT/2: {emt/2:.3f} {unite}
- Écart-type mesuré: {ecart_type:.3f} {unite}
- Statut: {'✅ Excellent' if ecart_type <= emt/3 else '⚠️ Acceptable' if ecart_type <= emt/2 else '❌ Non conforme'}
        """
        st.download_button(
            "📄 Rapport TXT", 
            rapport, 
            f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            help="Rapport complet au format texte"
        )
    
    with col_e2:
        # Export CSV des mesures
        st.download_button(
            "📊 Mesures CSV", 
            df.to_csv(), 
            f"mesures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            help="Données brutes des mesures"
        )
    
    with col_e3:
        # Export CSV complet avec stats
        csv_complet = f"""MESURES BRUTES
{df.to_csv()}

STATISTIQUES PAR ÉCHANTILLON
{stats_echantillons.to_csv()}

STATISTIQUES PAR OPÉRATEUR
{stats_operateurs.to_csv()}

RÉSUMÉ
Moyenne,{df.values.mean():.3f}
Écart-type,{df.values.std():.3f}
Minimum,{df.values.min():.3f}
Maximum,{df.values.max():.3f}
Étendue,{etendue:.3f}
CV (%),{cv:.2f}
"""
        st.download_button(
            "📋 Export Complet CSV", 
            csv_complet, 
            f"rapport_complet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            help="Toutes les données et statistiques"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>Système de Métrologie v2.0 | Laboratoire de Mesures et Étalonnage</small>
</div>
""", unsafe_allow_html=True)