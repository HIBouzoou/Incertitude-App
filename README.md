# 📖 Documentation - Système de Métrologie Laboratoire

## 📋 Table des Matières

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Architecture de l'Application](#architecture)
4. [Guide d'Utilisation](#guide-utilisation)
5. [Fonctionnalités Détaillées](#fonctionnalites)
6. [Calculs et Formules](#calculs)
7. [Interprétation des Résultats](#interpretation)
8. [Cas d'Usage](#cas-usage)
9. [Dépannage](#depannage)
10. [FAQ](#faq)

---

## 🎯 Introduction {#introduction}

### Objectif de l'Application

Cette application Streamlit est un **système complet de gestion et d'analyse de mesures métrologiques** destiné aux laboratoires d'étalonnage, de contrôle qualité et de métrologie industrielle.

### Fonctionnalités Principales

- ✅ Configuration d'expériences de métrologie
- ✅ Saisie manuelle, import et données de test
- ✅ Calculs statistiques automatiques
- ✅ Analyse de conformité selon les classes d'instruments
- ✅ Export multi-formats (TXT, CSV, Excel)
- ✅ Interface intuitive et multilingue (français)

### Public Cible

- Techniciens de laboratoire
- Ingénieurs métrologie
- Responsables qualité
- Étudiants en métrologie/instrumentation

---

## 💻 Installation {#installation}

### Prérequis

```bash
Python 3.8 ou supérieur
```

### Installation des Dépendances

```bash
pip install streamlit pandas numpy openpyxl xlsxwriter
```

### Lancement de l'Application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`

---

## 🏗️ Architecture de l'Application {#architecture}

### Structure du Code

```
app.py
├── Configuration (Sidebar)
│   ├── Informations Mesurande
│   ├── Caractéristiques Instrument
│   └── Plan de Mesure
├── Base de Données Classes
├── Saisie/Import des Mesures
│   ├── Saisie Manuelle
│   ├── Import (CSV/Excel/Texte)
│   └── Données de Test
├── Calculs Statistiques
└── Analyses et Export
```

### Session State

L'application utilise `st.session_state` pour maintenir :
- `mesures` : DataFrame contenant toutes les mesures
- `validated` : État de validation des données

---

## 📘 Guide d'Utilisation {#guide-utilisation}

### Étape 1 : Configuration

**Dans la barre latérale (Sidebar) :**

#### 1.1 Informations Mesurande
- **Nom du mesurande** : Ce que vous mesurez (Température, Pression, Longueur, etc.)
- **Unité** : Sélectionnez parmi °C, °F, K, Pa, Bar, mm, m

#### 1.2 Caractéristiques Instrument
- **Classe** : Précision de votre instrument
  - Classe 0.5 : Haute précision (EMT ±0.5)
  - Classe 1.0 : Précision standard (EMT ±1.0)
  - Classe 1.5 : Précision moyenne (EMT ±1.5)
  - Classe 2.5 : Précision industrielle (EMT ±2.5)
- **Température ambiante** : Conditions environnementales (15-30°C)
- **Homogénéité** : Qualité de l'environnement de mesure

#### 1.3 Plan de Mesure
- **Nombre d'échantillons** : Combien d'objets/points à mesurer (1-20)
- **Nombre d'opérateurs** : Combien de personnes effectuent les mesures (1-10)

**Exemple :** 5 échantillons × 3 opérateurs = 15 mesures totales

---

### Étape 2 : Saisie/Import des Données

Vous avez **3 options** :

#### Option A : Saisie Manuelle ✏️

1. Cliquez sur **"Initialiser le tableau de mesures"**
2. Un tableau vide apparaît avec vos dimensions configurées
3. Remplissez chaque cellule avec les valeurs mesurées
4. Cliquez sur **"Valider les mesures"**

**Avantage** : Contrôle total, idéal pour saisie en temps réel

#### Option B : Import de Données 📤

##### Import CSV
1. Préparez un fichier CSV avec :
   - Première colonne : noms des échantillons
   - Colonnes suivantes : mesures par opérateur
   - En-têtes obligatoires
2. Uploadez le fichier
3. Vérifiez l'aperçu
4. Cliquez sur **"Confirmer l'import CSV"**

**Format CSV attendu :**
```csv
,Opérateur 1,Opérateur 2,Opérateur 3
Échantillon 1,20.15,20.18,20.12
Échantillon 2,25.32,25.35,25.30
```

##### Import Excel
- Même format que CSV
- Supporte .xlsx et .xls
- Peut contenir des formules (seules les valeurs sont importées)

##### Import Texte
- Copier-coller direct depuis n'importe quelle source
- Choisissez le séparateur : Tabulation, Virgule, Point-virgule
- Pratique pour données depuis Word, emails, etc.

**Téléchargement de Templates**
- Templates CSV et Excel vides disponibles
- Dimensions adaptées à votre configuration
- Pré-formatés et prêts à remplir

#### Option C : Données de Test 🎲

6 scénarios prédéfinis :

1. **Mesures Excellentes** : Faible dispersion, opérateurs cohérents
2. **Mesures Acceptables** : Dispersion normale
3. **Mesures avec Biais** : Un opérateur mesure différemment
4. **Mesures Non Conformes** : Forte dispersion
5. **Données Personnalisées** : Jeu mixte
6. **Grandes Séries** : 10×5 = 50 mesures

**Utilisation** :
- Sélectionnez un scénario
- Visualisez les données et statistiques
- Cliquez sur **"Charger ces Données de Test"**

---

### Étape 3 : Validation

Une fois les données saisies/importées :
1. Vérifiez visuellement le tableau
2. Cliquez sur **"Valider les mesures"**
3. L'application vérifie qu'aucune cellule n'est vide
4. Message de confirmation si succès

---

### Étape 4 : Analyse des Résultats

Après validation, l'application affiche automatiquement :

#### Métriques Générales
- **Moyenne générale** : Valeur centrale de toutes les mesures
- **Écart-type général** : Dispersion globale
- **Min/Max** : Valeurs extrêmes
- **Étendue** : Max - Min
- **Coefficient de variation** : (Écart-type / Moyenne) × 100

#### Analyses Détaillées (3 onglets)

**Onglet 1 : Par Échantillon 📊**
- Statistiques pour chaque échantillon
- Permet de détecter un échantillon anormal
- Colonnes : Moyenne, Écart-type, Min, Max, Étendue

**Onglet 2 : Par Opérateur 👥**
- Statistiques pour chaque opérateur
- Permet de détecter un biais d'opérateur
- Même structure que l'onglet échantillon

**Onglet 3 : Tableau Complet 📋**
- Visualisation complète des données validées
- Format : Échantillons × Opérateurs

#### Analyse de Conformité 🎯

L'application compare automatiquement votre écart-type avec l'EMT de la classe sélectionnée :

- ✅ **Excellent** : Écart-type < EMT/3
  - Processus très maîtrisé
  - Répétabilité excellente
  
- ℹ️ **Acceptable** : EMT/3 ≤ Écart-type < EMT/2
  - Processus conforme
  - Répétabilité satisfaisante
  
- ❌ **Non conforme** : Écart-type ≥ EMT/2
  - Processus à améliorer
  - Dispersion trop importante

---

### Étape 5 : Export des Résultats

3 formats d'export disponibles :

#### 📥 Rapport TXT
- Rapport texte complet
- Configuration + Résultats + Analyse
- Horodaté automatiquement
- Idéal pour archivage simple

**Contenu :**
```
RAPPORT DE MÉTROLOGIE
Date: 2025-10-12 14:30:00
=====================================

CONFIGURATION
- Mesurande: Température (°C)
- Classe: Classe 0.5
- EMT: ±0.5 °C
...

RÉSULTATS
- Moyenne: 30.450 °C
- Écart-type: 0.053 °C
...
```

#### 📥 Export CSV
- Données brutes seulement
- Format universel
- Compatible avec tous les logiciels
- Léger et rapide

#### 📥 Export Excel
- **3 feuilles incluses** :
  1. Mesures : tableau complet
  2. Stats_Échantillons : statistiques par échantillon
  3. Stats_Opérateurs : statistiques par opérateur
- Format professionnel
- Prêt pour présentations et rapports
- Conserve les formules et formats

---

## ⚙️ Fonctionnalités Détaillées {#fonctionnalites}

### Base de Données des Classes d'Instruments

| Classe | EMT | Résolution | Plage | Usage typique |
|--------|-----|------------|-------|---------------|
| 0.5 | ±0.5 | 0.01 | 0-100 | Étalonnage haute précision |
| 1.0 | ±1.0 | 0.1 | 0-200 | Contrôle qualité standard |
| 1.5 | ±1.5 | 0.1 | 0-500 | Mesures industrielles |
| 2.5 | ±2.5 | 0.5 | 0-1000 | Applications générales |

**EMT (Erreur Maximale Tolérée)** : Écart maximum accepté par rapport à la valeur vraie.

### Validation des Données

L'application effectue plusieurs vérifications :
- ✅ Aucune cellule vide
- ✅ Toutes les valeurs sont numériques
- ✅ Dimensions cohérentes avec la configuration
- ❌ Rejet si critères non respectés

### Gestion de la Session

- Les données restent en mémoire durant toute la session
- Possibilité de modifier la configuration sans perdre les données
- Rechargement des données après modification

---

## 🔢 Calculs et Formules {#calculs}

### Statistiques de Base

#### Moyenne
```
μ = (Σ xi) / n
```
où xi = valeur de mesure, n = nombre total de mesures

#### Écart-type (échantillon)
```
σ = √[(Σ(xi - μ)²) / (n-1)]
```

#### Étendue
```
R = Max - Min
```

#### Coefficient de Variation
```
CV = (σ / μ) × 100 (%)
```

### Analyse de Conformité

#### Critères de décision

```
Si σ < EMT/3  → Excellent
Si σ < EMT/2  → Acceptable
Si σ ≥ EMT/2  → Non conforme
```

**Justification** :
- EMT/3 : Règle des 3σ en métrologie
- EMT/2 : Limite de conformité ISO

### Statistiques par Groupe

#### Par Échantillon (moyennes par ligne)
```
μ_échantillon_i = (Σ mesures_ligne_i) / nb_opérateurs
```

#### Par Opérateur (moyennes par colonne)
```
μ_opérateur_j = (Σ mesures_colonne_j) / nb_échantillons
```

---

## 📊 Interprétation des Résultats {#interpretation}

### Analyse de la Dispersion

#### Écart-type Faible (< 0.1 × Valeur moyenne)
✅ **Interprétation** :
- Excellente répétabilité
- Opérateurs bien formés
- Instrument stable
- Conditions environnementales maîtrisées

#### Écart-type Moyen (0.1-0.3 × Valeur moyenne)
⚠️ **Interprétation** :
- Répétabilité acceptable
- Possibles variations opérateurs
- Vérifier les conditions de mesure

#### Écart-type Élevé (> 0.3 × Valeur moyenne)
❌ **Interprétation** :
- Problème de répétabilité
- Formation opérateurs nécessaire
- Instrument à vérifier/étalonner
- Conditions environnementales instables

### Analyse par Opérateur

#### Opérateur avec Biais Systématique
**Symptômes** :
- Moyenne opérateur significativement différente des autres
- Écart constant sur tous les échantillons

**Causes possibles** :
- Erreur de lecture systématique
- Mauvaise technique de mesure
- Problème de vision (parallaxe)
- Compréhension incorrecte de la procédure

**Actions correctives** :
- Reformation de l'opérateur
- Vérification de la procédure
- Contrôle de la vision

#### Opérateur avec Forte Dispersion
**Symptômes** :
- Écart-type opérateur >> autres opérateurs
- Mesures erratiques

**Causes possibles** :
- Manque d'expérience
- Non-respect de la procédure
- Conditions de mesure variables

**Actions correctives** :
- Formation pratique
- Supervision temporaire
- Audit de conformité

### Analyse par Échantillon

#### Échantillon Anormal
**Symptômes** :
- Forte dispersion pour un échantillon spécifique
- Moyenne très différente des autres

**Causes possibles** :
- Défaut de l'échantillon
- Contamination
- Échantillon mal identifié
- Conditions de mesure particulières

**Actions** :
- Vérifier l'échantillon
- Répéter les mesures
- Investiguer les conditions

---

## 💼 Cas d'Usage {#cas-usage}

### Cas 1 : Étalonnage d'Instruments

**Contexte** : Vérifier la conformité d'un thermomètre Classe 1.0

**Procédure** :
1. Configurer : Mesurande = Température, Classe = 1.0
2. Plan : 5 points d'étalonnage, 3 répétitions
3. Importer les données du bain thermostaté
4. Valider et analyser
5. Vérifier : Écart-type < 0.5°C (EMT/2)

**Décision** :
- ✅ Conforme → Étalonner et mettre en service
- ❌ Non conforme → Ajuster ou réformer

### Cas 2 : R&R (Répétabilité & Reproductibilité)

**Contexte** : Évaluer un nouveau processus de mesure

**Procédure** :
1. Sélectionner 5 échantillons représentatifs
2. 3 opérateurs mesurent chacun 3 fois
3. Utiliser "Données de Test" pour simulation
4. Analyser :
   - Répétabilité : écart-type par opérateur
   - Reproductibilité : écart entre opérateurs

**Critères d'acceptation** :
- R&R < 10% : Excellent
- R&R < 30% : Acceptable
- R&R > 30% : Inacceptable

### Cas 3 : Formation des Opérateurs

**Contexte** : Former de nouveaux techniciens

**Procédure** :
1. Charger "Mesures avec Biais Opérateur"
2. Faire observer le tableau de résultats
3. Analyser ensemble l'onglet "Par Opérateur"
4. Identifier l'opérateur problématique
5. Discuter des causes et corrections

**Pédagogie** :
- Visualisation concrète des erreurs
- Compréhension de l'impact des biais
- Sensibilisation à la rigueur

### Cas 4 : Audit Qualité

**Contexte** : Préparer un audit ISO 17025

**Procédure** :
1. Importer les données d'étalonnage récentes
2. Générer les analyses statistiques
3. Exporter le rapport Excel complet
4. Vérifier la conformité aux EMT
5. Archiver les rapports TXT

**Documents produits** :
- Rapport d'analyse statistique
- Preuve de conformité
- Traçabilité complète

### Cas 5 : Contrôle Production

**Contexte** : Contrôle dimensionnel en série

**Procédure** :
1. Mesurande : Diamètre (mm), Classe 1.5
2. "Grandes Séries" : 10 pièces × 3 mesures
3. Import CSV depuis pied à coulisse numérique
4. Analyse automatique
5. Export pour dossier de lot

**Avantages** :
- Rapidité
- Traçabilité
- Détection anomalies

---

## 🔧 Dépannage {#depannage}

### Problème : "Certaines cellules sont vides"

**Cause** : Validation avant remplissage complet

**Solution** :
- Vérifier visuellement le tableau
- Remplir toutes les cellules
- Revalider

### Problème : Import CSV échoue

**Causes possibles** :
- Encodage incorrect (UTF-8 requis)
- Séparateur incorrect
- En-têtes manquants

**Solutions** :
1. Ouvrir le CSV dans un éditeur de texte
2. Vérifier le séparateur (, ou ;)
3. S'assurer de la première ligne d'en-têtes
4. Sauvegarder en UTF-8

### Problème : Import Excel "Erreur"

**Causes** :
- Fichier corrompu
- Format trop ancien (.xls)
- Cellules fusionnées

**Solutions** :
- Enregistrer en .xlsx récent
- Supprimer les fusions de cellules
- Vérifier la structure (1 feuille, format simple)

### Problème : Résultats incohérents

**Vérifications** :
1. Classe d'instrument correcte ?
2. Unités cohérentes ?
3. Données importées complètes ?
4. Pas de valeurs aberrantes ?

**Action** : Recharger et revalider les données

### Problème : Application lente

**Causes** :
- Trop de données (>1000 mesures)
- Ressources système limitées

**Solutions** :
- Réduire le nombre d'échantillons/opérateurs
- Fermer les autres applications
- Relancer Streamlit

---

## ❓ FAQ {#faq}

### Questions Générales

**Q1 : Puis-je utiliser l'application hors ligne ?**
> Oui, une fois installée localement, aucune connexion internet n'est nécessaire.

**Q2 : Les données sont-elles sauvegardées automatiquement ?**
> Non, vous devez exporter manuellement. Les données restent en mémoire durant la session.

**Q3 : Combien de mesures maximum ?**
> Techniquement illimité, mais recommandé < 500 mesures pour des performances optimales.

**Q4 : Puis-je modifier une classe d'instrument ?**
> Non dans l'interface, mais vous pouvez modifier le code source (dictionnaire CLASSES_DB).

### Questions Techniques

**Q5 : Quelle version de Python ?**
> Python 3.8 minimum, recommandé 3.10+

**Q6 : Puis-je personnaliser l'interface ?**
> Oui, le code est open et modifiable. Streamlit permet une customisation facile.

**Q7 : Comment ajouter d'autres unités ?**
> Modifier la ligne `st.selectbox("Unité", ["°C", "°F", ...])` dans le code.

**Q8 : L'application fonctionne-t-elle sur mobile ?**
> Oui, Streamlit est responsive, mais l'expérience est meilleure sur tablette/ordinateur.

### Questions Métrologiques

**Q9 : Quelle est la différence entre répétabilité et reproductibilité ?**
> - **Répétabilité** : Même opérateur, mêmes conditions → Écart-type par opérateur
> - **Reproductibilité** : Différents opérateurs → Variation entre opérateurs

**Q10 : Pourquoi EMT/3 et EMT/2 ?**
> - EMT/3 : Règle des 3σ (99.7% des mesures dans ±3σ)
> - EMT/2 : Critère de conformité ISO (marge de sécurité)

**Q11 : Que faire si tous mes résultats sont "Non conforme" ?**
> Vérifier :
> 1. La classe d'instrument est-elle appropriée ?
> 2. L'instrument est-il étalonné récemment ?
> 3. Les opérateurs sont-ils formés ?
> 4. Les conditions environnementales sont-elles stables ?

**Q12 : Comment interpréter un coefficient de variation élevé ?**
> CV > 15% indique une forte dispersion relative. Causes : échelle de mesure inadaptée, méthode instable, ou variation naturelle du mesurande.

---

## 📚 Références

### Normes Applicables
- **ISO/IEC 17025** : Exigences générales concernant la compétence des laboratoires
- **ISO 5725** : Exactitude et fidélité des méthodes de mesure
- **VIM (JCGM 200:2012)** : Vocabulaire international de métrologie

### Ressources Complémentaires
- Guide Streamlit : https://docs.streamlit.io
- Pandas Documentation : https://pandas.pydata.org
- NumPy Documentation : https://numpy.org

### Support
- GitHub : [Lien du projet]
- Email : [Contact support]
- Forum : [Communauté]

---

## 📝 Changelog

### Version 1.0 (Octobre 2025)
- ✅ Saisie manuelle
- ✅ Import CSV/Excel/Texte
- ✅ 6 jeux de données de test
- ✅ Calculs statistiques complets
- ✅ Analyse de conformité
- ✅ Export multi-formats
- ✅ Interface française

### Évolutions Futures
- 🔜 Graphiques de contrôle
- 🔜 Analyse de tendance
- 🔜 Export PDF
- 🔜 Base de données persistante
- 🔜 Multi-utilisateurs

---

## 📄 Licence

Application développée pour usage éducatif et professionnel en métrologie.

---

**Documentation générée le : Octobre 2025**  
**Version de l'application : 1.0**  
**Auteur : Système de Métrologie Laboratoire**