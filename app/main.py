import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO

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

# Corps principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Saisie des Mesures")
    
    # Options d'import/export
    tab_input1, tab_input2, tab_input3 = st.tabs(["✏️ Saisie Manuelle", "📤 Import de Données", "🎲 Données de Test"])
    
    with tab_input1:
        # Créer le tableau de saisie
        if st.button("🔄 Initialiser le tableau de mesures", type="primary"):
            st.session_state.mesures = pd.DataFrame(
                np.nan,
                index=[f"Échantillon {i+1}" for i in range(int(nb_echantillons))],
                columns=[f"Opérateur {i+1}" for i in range(int(nb_operateurs))]
            )
            st.session_state.validated = False
            st.rerun()
    
    with tab_input2:
        st.subheader("📥 Importer vos données")
        
        # Format d'import
        format_import = st.radio(
            "Choisir le format d'import",
            ["CSV", "Excel", "Texte (valeurs séparées)"],
            horizontal=True
        )
        
        if format_import == "CSV":
            uploaded_file = st.file_uploader("Charger un fichier CSV", type=['csv'])
            st.info("💡 Format attendu: Lignes=Échantillons, Colonnes=Opérateurs avec en-têtes")
            
            if uploaded_file is not None:
                try:
                    df_import = pd.read_csv(uploaded_file, index_col=0)
                    st.success(f"✅ Fichier chargé: {df_import.shape[0]} échantillons × {df_import.shape[1]} opérateurs")
                    st.dataframe(df_import, use_container_width=True)
                    
                    if st.button("✅ Confirmer l'import CSV"):
                        st.session_state.mesures = df_import
                        st.session_state.validated = False
                        st.success("Données importées avec succès!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'import: {str(e)}")
        
        elif format_import == "Excel":
            uploaded_file = st.file_uploader("Charger un fichier Excel", type=['xlsx', 'xls'])
            st.info("💡 Format attendu: Lignes=Échantillons, Colonnes=Opérateurs avec en-têtes")
            
            if uploaded_file is not None:
                try:
                    df_import = pd.read_excel(uploaded_file, index_col=0)
                    st.success(f"✅ Fichier chargé: {df_import.shape[0]} échantillons × {df_import.shape[1]} opérateurs")
                    st.dataframe(df_import, use_container_width=True)
                    
                    if st.button("✅ Confirmer l'import Excel"):
                        st.session_state.mesures = df_import
                        st.session_state.validated = False
                        st.success("Données importées avec succès!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'import: {str(e)}")
        
        else:  # Texte
            st.write("Coller vos données (valeurs séparées par des tabulations ou virgules)")
            text_data = st.text_area("Données", height=200, placeholder="Échantillon1\t12.5\t12.6\t12.4\nÉchantillon2\t12.7\t12.5\t12.6")
            
            separateur = st.radio("Séparateur", ["Tabulation", "Virgule", "Point-virgule"], horizontal=True)
            sep_map = {"Tabulation": "\t", "Virgule": ",", "Point-virgule": ";"}
            
            if text_data and st.button("✅ Confirmer l'import Texte"):
                try:
                    from io import StringIO
                    df_import = pd.read_csv(StringIO(text_data), sep=sep_map[separateur], index_col=0, header=None)
                    df_import.columns = [f"Opérateur {i+1}" for i in range(df_import.shape[1])]
                    st.session_state.mesures = df_import
                    st.session_state.validated = False
                    st.success("Données importées avec succès!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'import: {str(e)}")
        
        # Template de téléchargement
        st.markdown("---")
        st.subheader("📋 Télécharger un modèle vide")
        template_df = pd.DataFrame(
            np.nan,
            index=[f"Échantillon {i+1}" for i in range(int(nb_echantillons))],
            columns=[f"Opérateur {i+1}" for i in range(int(nb_operateurs))]
        )
        
        col_temp1, col_temp2 = st.columns(2)
        with col_temp1:
            csv_template = template_df.to_csv()
            st.download_button(
                "📥 Template CSV",
                csv_template,
                "template_mesures.csv",
                "text/csv"
            )
        with col_temp2:
            # Pour Excel, on utilise un buffer
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                template_df.to_excel(writer, sheet_name='Mesures')
            excel_template = buffer.getvalue()
            st.download_button(
                "📥 Template Excel",
                excel_template,
                "template_mesures.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with tab_input3:
        st.subheader("🎲 Charger des Données de Test")
        st.write("Utilisez ces jeux de données prédéfinis pour tester rapidement l'application")
        
        # Sélection du type de test
        type_test = st.selectbox(
            "Choisir un scénario de test",
            [
                "Mesures Excellentes (faible dispersion)",
                "Mesures Acceptables (dispersion moyenne)",
                "Mesures avec Biais Opérateur",
                "Mesures Non Conformes (forte dispersion)",
                "Données Personnalisées (5×3)",
                "Grandes Séries (10×5)"
            ]
        )
        
        # Génération des données de test selon le scénario
        if type_test == "Mesures Excellentes (faible dispersion)":
            test_data = pd.DataFrame({
                'Opérateur 1': [20.15, 25.32, 30.48, 35.62, 40.78],
                'Opérateur 2': [20.18, 25.35, 30.52, 35.68, 40.82],
                'Opérateur 3': [20.12, 25.30, 30.45, 35.60, 40.75]
            }, index=[f"Échantillon {i+1}" for i in range(5)])
            
            st.info("✅ **Scénario** : Opérateurs très cohérents, écart-type ~0.05°C")
        
        elif type_test == "Mesures Acceptables (dispersion moyenne)":
            test_data = pd.DataFrame({
                'Opérateur 1': [20.1, 25.3, 30.5, 35.6, 40.8],
                'Opérateur 2': [20.3, 25.4, 30.7, 35.8, 41.0],
                'Opérateur 3': [19.9, 25.2, 30.4, 35.5, 40.6]
            }, index=[f"Échantillon {i+1}" for i in range(5)])
            
            st.info("ℹ️ **Scénario** : Dispersion acceptable, écart-type ~0.15°C")
        
        elif type_test == "Mesures avec Biais Opérateur":
            test_data = pd.DataFrame({
                'Opérateur 1': [20.15, 25.32, 30.48, 35.62, 40.78],
                'Opérateur 2': [20.45, 25.80, 31.05, 36.20, 41.35],
                'Opérateur 3': [19.95, 25.10, 30.20, 35.35, 40.50]
            }, index=[f"Échantillon {i+1}" for i in range(5)])
            
            st.warning("⚠️ **Scénario** : Opérateur 2 mesure systématiquement plus haut (+0.5°C)")
        
        elif type_test == "Mesures Non Conformes (forte dispersion)":
            test_data = pd.DataFrame({
                'Opérateur 1': [20.2, 25.5, 30.8, 35.9, 41.2],
                'Opérateur 2': [20.8, 26.2, 31.5, 36.8, 42.0],
                'Opérateur 3': [19.5, 24.8, 29.9, 35.0, 40.1]
            }, index=[f"Échantillon {i+1}" for i in range(5)])
            
            st.error("❌ **Scénario** : Forte dispersion, écart-type ~0.60°C, non conforme")
        
        elif type_test == "Données Personnalisées (5×3)":
            test_data = pd.DataFrame({
                'Opérateur 1': [12.45, 15.67, 18.23, 21.89, 24.12],
                'Opérateur 2': [12.50, 15.70, 18.28, 21.95, 24.18],
                'Opérateur 3': [12.42, 15.65, 18.20, 21.85, 24.08]
            }, index=[f"Échantillon {i+1}" for i in range(5)])
            
            st.info("📊 **Scénario** : Données mixtes pour test général")
        
        else:  # Grandes Séries
            np.random.seed(42)
            base_values = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65]
            test_data = pd.DataFrame({
                f'Opérateur {i+1}': [val + np.random.normal(0, 0.1) for val in base_values]
                for i in range(5)
            }, index=[f"Échantillon {i+1}" for i in range(10)])
            
            st.info("📈 **Scénario** : Grande série de mesures (10 échantillons × 5 opérateurs)")
        
        # Affichage du tableau de test
        st.dataframe(test_data.round(3), use_container_width=True)
        
        # Statistiques rapides du jeu de test
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Moyenne", f"{test_data.values.mean():.3f}")
        with col_stat2:
            st.metric("Écart-type", f"{test_data.values.std():.3f}")
        with col_stat3:
            st.metric("Étendue", f"{(test_data.values.max() - test_data.values.min()):.3f}")
        
        # Bouton de chargement
        if st.button("✅ Charger ces Données de Test", type="primary", key="load_test"):
            st.session_state.mesures = test_data
            st.session_state.validated = False
            st.success(f"✅ Données de test chargées : {test_data.shape[0]} échantillons × {test_data.shape[1]} opérateurs")
            st.rerun()
    
    if st.session_state.mesures is not None:
        st.markdown("---")
        st.write(f"**Mesurande:** {mesurande} ({unite})")
        st.write(f"**Configuration:** {st.session_state.mesures.shape[0]} échantillons × {st.session_state.mesures.shape[1]} opérateurs")
        
        # Éditeur de données
        edited_df = st.data_editor(
            st.session_state.mesures,
            use_container_width=True,
            num_rows="fixed",
            key="data_editor"
        )
        
        # Bouton de validation
        if st.button("✅ Valider les mesures", type="primary"):
            if edited_df.isna().any().any():
                st.warning("⚠️ Certaines cellules sont vides. Veuillez remplir toutes les mesures.")
            else:
                st.session_state.mesures = edited_df
                st.session_state.validated = True
                st.success("✅ Mesures validées avec succès!")
                st.rerun()

with col2:
    st.header("📊 Base de Données")
    
    # Afficher la base de données complète
    df_classes = pd.DataFrame(CLASSES_DB).T
    st.dataframe(df_classes, use_container_width=True)
    
    st.info("💡 **Info:** EMT = Erreur Maximale Tolérée")

# Section des résultats
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
        st.metric("Valeur minimale", f"{df.values.min():.3f} {unite}")
        st.metric("Valeur maximale", f"{df.values.max():.3f} {unite}")
    
    with col3:
        etendue = df.values.max() - df.values.min()
        st.metric("Étendue", f"{etendue:.3f} {unite}")
        cv = (df.values.std() / df.values.mean() * 100) if df.values.mean() != 0 else 0
        st.metric("Coeff. Variation", f"{cv:.2f} %")
    
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
        st.dataframe(stats_echantillons.round(3), use_container_width=True)
    
    with tab2:
        st.subheader("Statistiques par opérateur")
        stats_operateurs = pd.DataFrame({
            'Moyenne': df.mean(axis=0),
            'Écart-type': df.std(axis=0),
            'Min': df.min(axis=0),
            'Max': df.max(axis=0),
            'Étendue': df.max(axis=0) - df.min(axis=0)
        })
        st.dataframe(stats_operateurs.round(3), use_container_width=True)
    
    with tab3:
        st.subheader("Tableau complet des mesures")
        st.dataframe(df.round(3), use_container_width=True)
    
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
        st.write(f"- EMT: ±{emt} {unite}")
        st.write(f"- Résolution: {CLASSES_DB[classe]['Resolution']} {unite}")
        st.write(f"- Température: {temperature}°C")
        st.write(f"- Homogénéité: {homogeneite}")
    
    # Bouton d'export
    st.markdown("---")
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        # Export rapport texte
        rapport = f"""
RAPPORT DE MÉTROLOGIE
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

RÉSULTATS
- Moyenne: {df.values.mean():.3f} {unite}
- Écart-type: {df.values.std():.3f} {unite}
- Min: {df.values.min():.3f} {unite}
- Max: {df.values.max():.3f} {unite}
- Étendue: {etendue:.3f} {unite}
        """
        st.download_button(
            label="📥 Rapport TXT",
            data=rapport,
            file_name=f"rapport_metrologie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    with col_export2:
        # Export CSV
        csv_export = df.to_csv()
        st.download_button(
            label="📥 Export CSV",
            data=csv_export,
            file_name=f"mesures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col_export3:
        # Export Excel avec statistiques
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Mesures')
            stats_echantillons.to_excel(writer, sheet_name='Stats_Échantillons')
            stats_operateurs.to_excel(writer, sheet_name='Stats_Opérateurs')
        excel_export = buffer.getvalue()
        st.download_button(
            label="📥 Export Excel",
            data=excel_export,
            file_name=f"mesures_completes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small> Laboratoire de Mesures et Étalonnage</small>
</div>
""", unsafe_allow_html=True)