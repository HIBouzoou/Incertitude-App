import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO, StringIO
import base64

# Configuration de la page
st.set_page_config(page_title="Laboratoire de Métrologie", page_icon="🔬", layout="wide")

# Base de données des classes d'instruments
CLASSES_DB = {
    "Classe 0.5": {"EMT": 0.5, "Resolution": 0.01, "Plage": "0-100"},
    "Classe 1.0": {"EMT": 1.0, "Resolution": 0.1, "Plage": "0-200"},
    "Classe 1.5": {"EMT": 1.5, "Resolution": 0.1, "Plage": "0-500"},
    "Classe 2.5": {"EMT": 2.5, "Resolution": 0.5, "Plage": "0-1000"},
}

# Fonction pour créer un lien de téléchargement Excel
def create_excel_download(df, stats_echantillons, stats_operateurs, mesurande, unite, classe, emt, temperature, homogeneite, etendue):
    """Crée un fichier Excel avec plusieurs feuilles sans dépendances externes"""
    output = BytesIO()
    
    try:
        # Essayer avec xlsxwriter (plus fiable sur cloud)
        import xlsxwriter
        
        # Option pour gérer les NaN
        workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'nan_inf_to_errors': True})
        
        # Formats
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
        cell_format = workbook.add_format({'border': 1})
        title_format = workbook.add_format({'bold': True, 'font_size': 14})
        
        # Feuille 1: Mesures brutes
        worksheet1 = workbook.add_worksheet('Mesures')
        worksheet1.write(0, 0, 'Échantillons', header_format)
        for col, header in enumerate(df.columns):
            worksheet1.write(0, col + 1, header, header_format)
        for row, idx in enumerate(df.index):
            worksheet1.write(row + 1, 0, idx, cell_format)
            for col, val in enumerate(df.iloc[row]):
                # Gérer les NaN
                if pd.isna(val):
                    worksheet1.write(row + 1, col + 1, '', cell_format)
                else:
                    worksheet1.write(row + 1, col + 1, float(val), cell_format)
        
        # Feuille 2: Stats par échantillon
        worksheet2 = workbook.add_worksheet('Stats Échantillons')
        stats_echantillons_reset = stats_echantillons.reset_index()
        for col, header in enumerate(stats_echantillons_reset.columns):
            worksheet2.write(0, col, header, header_format)
        for row in range(len(stats_echantillons_reset)):
            for col in range(len(stats_echantillons_reset.columns)):
                worksheet2.write(row + 1, col, stats_echantillons_reset.iloc[row, col], cell_format)
        
        # Feuille 3: Stats par opérateur
        worksheet3 = workbook.add_worksheet('Stats Opérateurs')
        stats_operateurs_reset = stats_operateurs.reset_index()
        for col, header in enumerate(stats_operateurs_reset.columns):
            worksheet3.write(0, col, header, header_format)
        for row in range(len(stats_operateurs_reset)):
            for col in range(len(stats_operateurs_reset.columns)):
                worksheet3.write(row + 1, col, stats_operateurs_reset.iloc[row, col], cell_format)
        
        # Feuille 4: Résumé
        worksheet4 = workbook.add_worksheet('Résumé')
        worksheet4.write(0, 0, 'RÉSUMÉ GÉNÉRAL', title_format)
        resume_data = [
            ['Indicateur', 'Valeur'],
            ['Moyenne générale', f"{df.values.mean():.3f} {unite}"],
            ['Écart-type général', f"{df.values.std():.3f} {unite}"],
            ['Minimum', f"{df.values.min():.3f} {unite}"],
            ['Maximum', f"{df.values.max():.3f} {unite}"],
            ['Étendue', f"{etendue:.3f} {unite}"],
            ['Coefficient Variation (%)', f"{(df.values.std() / df.values.mean() * 100):.2f}%"]
        ]
        for row, data in enumerate(resume_data):
            for col, val in enumerate(data):
                fmt = header_format if row == 0 else cell_format
                worksheet4.write(row + 2, col, val, fmt)
        
        # Feuille 5: Configuration
        worksheet5 = workbook.add_worksheet('Configuration')
        worksheet5.write(0, 0, 'CONFIGURATION', title_format)
        config_data = [
            ['Paramètre', 'Valeur'],
            ['Mesurande', mesurande],
            ['Unité', unite],
            ['Classe', classe],
            ['EMT', f"±{emt} {unite}"],
            ['Résolution', f"{CLASSES_DB[classe]['Resolution']} {unite}"],
            ['Température', f"{temperature}°C"],
            ['Homogénéité', homogeneite],
            ['Nb Échantillons', df.shape[0]],
            ['Nb Opérateurs', df.shape[1]],
            ['Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        for row, data in enumerate(config_data):
            for col, val in enumerate(data):
                fmt = header_format if row == 0 else cell_format
                worksheet5.write(row + 2, col, val, fmt)
        
        workbook.close()
        return output.getvalue()
        
    except ImportError:
        # Fallback: utiliser openpyxl
        try:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Mesures')
                stats_echantillons.to_excel(writer, sheet_name='Stats_Échantillons')
                stats_operateurs.to_excel(writer, sheet_name='Stats_Opérateurs')
                
                resume = pd.DataFrame({
                    'Indicateur': ['Moyenne générale', 'Écart-type général', 'Minimum', 'Maximum', 'Étendue', 'CV (%)'],
                    'Valeur': [
                        f"{df.values.mean():.3f} {unite}",
                        f"{df.values.std():.3f} {unite}",
                        f"{df.values.min():.3f} {unite}",
                        f"{df.values.max():.3f} {unite}",
                        f"{etendue:.3f} {unite}",
                        f"{(df.values.std() / df.values.mean() * 100):.2f}%"
                    ]
                })
                resume.to_excel(writer, sheet_name='Résumé', index=False)
                
                config = pd.DataFrame({
                    'Paramètre': ['Mesurande', 'Unité', 'Classe', 'EMT', 'Résolution', 'Température', 
                                  'Homogénéité', 'Nb Échantillons', 'Nb Opérateurs', 'Date'],
                    'Valeur': [mesurande, unite, classe, f"±{emt} {unite}", 
                               f"{CLASSES_DB[classe]['Resolution']} {unite}", f"{temperature}°C",
                               homogeneite, df.shape[0], df.shape[1], 
                               datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                })
                config.to_excel(writer, sheet_name='Configuration', index=False)
            
            return output.getvalue()
        except:
            return None

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
        uploaded_file = st.file_uploader("Charger un fichier", type=['csv', 'xlsx', 'xls', 'txt'])
        
        if uploaded_file is not None:
            try:
                # Déterminer le type de fichier
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                if file_extension == 'csv':
                    df_import = pd.read_csv(uploaded_file, index_col=0)
                elif file_extension in ['xlsx', 'xls']:
                    df_import = pd.read_excel(uploaded_file, index_col=0)
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
        text_data = st.text_area("Données (séparées par tabulation ou virgule)", height=150)
        
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
        
        # Templates
        st.markdown("---")
        st.subheader("📋 Télécharger un modèle")
        template_df = pd.DataFrame(
            np.nan,
            index=[f"Échantillon {i+1}" for i in range(int(nb_echantillons))],
            columns=[f"Opérateur {i+1}" for i in range(int(nb_operateurs))]
        )
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.download_button("📥 Template CSV", template_df.to_csv(), "template.csv", "text/csv")
        with col_t2:
            # Template Excel simple
            excel_data = create_excel_download(
                template_df, template_df, template_df, 
                "Template", unite, classe, CLASSES_DB[classe]['EMT'], 
                temperature, homogeneite, 0
            )
            if excel_data:
                st.download_button("📥 Template Excel", excel_data, "template.xlsx", 
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
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
                st.warning("⚠️ Cellules vides détectées")
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
    st.header("📈 Résultats")
    
    df = st.session_state.mesures
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Moyenne", f"{df.values.mean():.3f} {unite}")
        st.metric("Écart-type", f"{df.values.std():.3f} {unite}")
    
    with col2:
        st.metric("Minimum", f"{df.values.min():.3f} {unite}")
        st.metric("Maximum", f"{df.values.max():.3f} {unite}")
    
    with col3:
        etendue = df.values.max() - df.values.min()
        st.metric("Étendue", f"{etendue:.3f} {unite}")
        cv = (df.values.std() / df.values.mean() * 100) if df.values.mean() != 0 else 0
        st.metric("CV", f"{cv:.2f} %")
    
    tab1, tab2, tab3 = st.tabs(["📊 Échantillons", "👥 Opérateurs", "📋 Complet"])
    
    with tab1:
        st.subheader("Stats par échantillon")
        stats_echantillons = pd.DataFrame({
            'Moyenne': df.mean(axis=1),
            'Écart-type': df.std(axis=1),
            'Min': df.min(axis=1),
            'Max': df.max(axis=1),
            'Étendue': df.max(axis=1) - df.min(axis=1)
        })
        st.dataframe(stats_echantillons.round(3), width=700)
    
    with tab2:
        st.subheader("Stats par opérateur")
        stats_operateurs = pd.DataFrame({
            'Moyenne': df.mean(axis=0),
            'Écart-type': df.std(axis=0),
            'Min': df.min(axis=0),
            'Max': df.max(axis=0),
            'Étendue': df.max(axis=0) - df.min(axis=0)
        })
        st.dataframe(stats_operateurs.round(3), width=700)
    
    with tab3:
        st.dataframe(df.round(3), width=700)
    
    st.markdown("---")
    st.subheader("🎯 Conformité")
    
    emt = CLASSES_DB[classe]['EMT']
    ecart_type = df.values.std()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if ecart_type <= emt / 3:
            st.success(f"✅ Excellent: {ecart_type:.3f} << {emt/3:.3f}")
        elif ecart_type <= emt / 2:
            st.info(f"ℹ️ Acceptable: {ecart_type:.3f} < {emt/2:.3f}")
        else:
            st.error(f"❌ Non conforme: {ecart_type:.3f} > {emt/2:.3f}")
    
    with col2:
        st.write(f"**Références:**")
        st.write(f"• EMT: ±{emt} {unite}")
        st.write(f"• Résolution: {CLASSES_DB[classe]['Resolution']} {unite}")
        st.write(f"• Température: {temperature}°C")
        st.write(f"• Homogénéité: {homogeneite}")
    
    st.markdown("---")
    st.subheader("📥 Exports")
    
    col_e1, col_e2, col_e3 = st.columns(3)
    
    with col_e1:
        rapport = f"""RAPPORT DE MÉTROLOGIE
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
=====================================

CONFIGURATION
- Mesurande: {mesurande} ({unite})
- Classe: {classe}
- EMT: ±{emt} {unite}
- Température: {temperature}°C
- Homogénéité: {homogeneite}

RÉSULTATS
- Moyenne: {df.values.mean():.3f} {unite}
- Écart-type: {df.values.std():.3f} {unite}
- Min: {df.values.min():.3f} {unite}
- Max: {df.values.max():.3f} {unite}
- Étendue: {etendue:.3f} {unite}
        """
        st.download_button("📄 Rapport TXT", rapport, f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    with col_e2:
        st.download_button("📊 Export CSV", df.to_csv(), f"mesures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    with col_e3:
        excel_data = create_excel_download(
            df, stats_echantillons, stats_operateurs,
            mesurande, unite, classe, emt, temperature, homogeneite, etendue
        )
        if excel_data:
            st.download_button(
                "📗 Export Excel",
                excel_data,
                f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="5 feuilles complètes"
            )
        else:
            st.warning("⚠️ Excel non disponible")
            st.download_button("📊 CSV (alternative)", df.to_csv(), f"mesures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'><small>Laboratoire de Métrologie </small></div>", unsafe_allow_html=True)