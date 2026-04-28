import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io
import os
import json
from scipy import stats

# ─────────────────────────────────────────────
# CONFIGURATION GÉNÉRALE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AgroData Élevage",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS PERSONNALISÉ
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f5f7f0; }
    .stApp { background-color: #f5f7f0; }
    h1 { color: #2e6b2e; font-family: 'Segoe UI', sans-serif; }
    h2, h3 { color: #3a7a3a; }
    .metric-card {
        background: white;
        border-left: 5px solid #4CAF50;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .success-box {
        background: #e8f5e9;
        border-radius: 8px;
        padding: 12px;
        color: #2e7d32;
        font-weight: bold;
    }
    div[data-testid="stSidebar"] {
        background-color: #1b5e20;
        color: white;
    }
    div[data-testid="stSidebar"] .stSelectbox label,
    div[data-testid="stSidebar"] .stRadio label,
    div[data-testid="stSidebar"] p,
    div[data-testid="stSidebar"] h1,
    div[data-testid="stSidebar"] h2,
    div[data-testid="stSidebar"] h3 {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GESTION DES DONNÉES (session state)
# ─────────────────────────────────────────────
if "donnees" not in st.session_state:
    st.session_state["donnees"] = pd.DataFrame(columns=[
        "ID", "Date", "Eleveur", "Localisation", "Type_Animal",
        "Race", "Nombre_Têtes", "Age_Moyen_Mois", "Poids_Moyen_Kg",
        "Production_Lait_L_Jour", "Gain_Quotidien_G",
        "Mortalite_Percent", "Alimentation", "Etat_Sante",
        "Superficie_Ha", "Remarques"
    ])

if "id_counter" not in st.session_state:
    st.session_state["id_counter"] = 1

# ─────────────────────────────────────────────
# BARRE LATÉRALE
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🐄 AgroData Élevage")
    st.markdown("---")
    menu = st.radio(
        "📋 Navigation",
        [
            "🏠 Accueil",
            "📝 Saisie des Données",
            "📊 Analyse Descriptive",
            "📈 Visualisations",
            "📥 Exporter les Données",
            "ℹ️ À propos"
        ]
    )
    st.markdown("---")
    nb = len(st.session_state["donnees"])
    st.markdown(f"**📦 Données enregistrées : `{nb}`**")
    st.markdown("---")
    st.markdown("*TP INF232 — EC2*")
    st.markdown("*Secteur : Élevage 🌿*")

# ─────────────────────────────────────────────
# PAGE : ACCUEIL
# ─────────────────────────────────────────────
if menu == "🏠 Accueil":
    st.markdown("# 🐄 AgroData Élevage")
    st.markdown("### *Plateforme intelligente de collecte et d'analyse des données d'élevage*")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🐐 Espèces supportées", "6", "Bovins, Ovins...")
    with col2:
        st.metric("📋 Formulaires actifs", "1", "Multi-critères")
    with col3:
        st.metric("📊 Types d'analyses", "8+", "Stats descriptives")
    with col4:
        st.metric("📁 Enregistrements", len(st.session_state["donnees"]), "total")

    st.markdown("---")
    st.markdown("## 🎯 Objectifs de l'application")
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("""
        **📝 Collecte structurée**
        - Saisie rapide des données de terrain
        - Gestion de plusieurs types d'animaux
        - Suivi par éleveur et localisation
        - Import de fichiers CSV/Excel
        """)
        st.success("""
        **📊 Analyse descriptive**
        - Statistiques de base (moyenne, médiane, écart-type)
        - Distribution des variables
        - Corrélations entre indicateurs
        - Détection des valeurs aberrantes
        """)
    with col_b:
        st.warning("""
        **📈 Visualisations interactives**
        - Histogrammes et boîtes à moustaches
        - Graphiques de dispersion
        - Cartes de chaleur des corrélations
        - Évolution temporelle
        """)
        st.error("""
        **📥 Export des résultats**
        - Export CSV et Excel
        - Rapport téléchargeable
        - Données filtrables
        """)

    st.markdown("---")
    st.markdown("## 📌 Comment utiliser l'application ?")
    steps = [
        ("1️⃣", "Saisie des Données", "Remplissez le formulaire avec les informations de votre exploitation."),
        ("2️⃣", "Importez vos données", "Vous pouvez aussi importer un fichier CSV ou Excel existant."),
        ("3️⃣", "Analyse Descriptive", "Consultez les statistiques automatiquement calculées."),
        ("4️⃣", "Visualisations", "Explorez vos données via des graphiques interactifs."),
        ("5️⃣", "Exportez", "Téléchargez vos données nettoyées et vos rapports.")
    ]
    for icon, titre, desc in steps:
        st.markdown(f"**{icon} {titre}** — {desc}")

# ─────────────────────────────────────────────
# PAGE : SAISIE DES DONNÉES
# ─────────────────────────────────────────────
elif menu == "📝 Saisie des Données":
    st.markdown("# 📝 Formulaire de Collecte")
    st.markdown("Renseignez les données de votre exploitation d'élevage.")
    st.markdown("---")

    # --- Import CSV/Excel ---
    st.markdown("### 📂 Importer un fichier existant (optionnel)")
    uploaded = st.file_uploader("Importer CSV ou Excel", type=["csv", "xlsx", "xls"])
    if uploaded:
        try:
            if uploaded.name.endswith(".csv"):
                df_import = pd.read_csv(uploaded)
            else:
                df_import = pd.read_excel(uploaded)
            st.success(f"✅ {len(df_import)} lignes importées avec succès !")
            st.dataframe(df_import.head())
            # Harmoniser les colonnes si possible
            for col in st.session_state["donnees"].columns:
                if col not in df_import.columns:
                    df_import[col] = None
            df_import = df_import[st.session_state["donnees"].columns]
            st.session_state["donnees"] = pd.concat(
                [st.session_state["donnees"], df_import], ignore_index=True
            )
        except Exception as e:
            st.error(f"Erreur lors de l'importation : {e}")

    st.markdown("---")
    st.markdown("### ✏️ Saisie manuelle")

    with st.form("formulaire_elevage", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 👤 Informations Éleveur")
            eleveur = st.text_input("Nom de l'éleveur *", placeholder="Ex: Jean Dupont")
            localisation = st.text_input("Localisation / Village *", placeholder="Ex: Mbalmayo")
            date_collecte = st.date_input("Date de collecte *", value=date.today())
            superficie = st.number_input("Superficie de l'exploitation (Ha)", min_value=0.0, step=0.5)

        with col2:
            st.markdown("#### 🐄 Informations Animaux")
            type_animal = st.selectbox("Type d'animal *", [
                "Bovins (Vaches)", "Ovins (Moutons)", "Caprins (Chèvres)",
                "Porcins (Porcs)", "Volaille (Poulets)", "Volaille (Dindes)"
            ])
            race = st.text_input("Race / Variété", placeholder="Ex: Goudali, Bororo...")
            nombre = st.number_input("Nombre de têtes *", min_value=1, step=1)
            age_moyen = st.number_input("Âge moyen (mois)", min_value=0, step=1)

        st.markdown("---")
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("#### ⚖️ Performances Zootechniques")
            poids = st.number_input("Poids moyen (kg)", min_value=0.0, step=0.5)
            lait = st.number_input("Production lait (L/jour) — si applicable", min_value=0.0, step=0.1)
            gmq = st.number_input("Gain Moyen Quotidien (g/jour)", min_value=0.0, step=1.0)
            mortalite = st.number_input("Taux de mortalité (%)", min_value=0.0, max_value=100.0, step=0.1)

        with col4:
            st.markdown("#### 🌿 Santé & Alimentation")
            alimentation = st.selectbox("Type d'alimentation", [
                "Pâturage naturel", "Fourrage cultivé", "Concentrés industriels",
                "Mixte (Pâturage + Concentrés)", "Résidus agricoles"
            ])
            sante = st.selectbox("État de santé général", [
                "Excellent", "Bon", "Moyen", "Mauvais", "Critique"
            ])
            remarques = st.text_area("Remarques / Observations", placeholder="Toute information utile...")

        submitted = st.form_submit_button("💾 Enregistrer les données", use_container_width=True)

        if submitted:
            if not eleveur or not localisation or nombre < 1:
                st.error("⚠️ Veuillez remplir tous les champs obligatoires (*).")
            else:
                nouvelle_ligne = {
                    "ID": st.session_state["id_counter"],
                    "Date": str(date_collecte),
                    "Eleveur": eleveur,
                    "Localisation": localisation,
                    "Type_Animal": type_animal,
                    "Race": race,
                    "Nombre_Têtes": nombre,
                    "Age_Moyen_Mois": age_moyen,
                    "Poids_Moyen_Kg": poids,
                    "Production_Lait_L_Jour": lait,
                    "Gain_Quotidien_G": gmq,
                    "Mortalite_Percent": mortalite,
                    "Alimentation": alimentation,
                    "Etat_Sante": sante,
                    "Superficie_Ha": superficie,
                    "Remarques": remarques
                }
                st.session_state["donnees"] = pd.concat(
                    [st.session_state["donnees"], pd.DataFrame([nouvelle_ligne])],
                    ignore_index=True
                )
                st.session_state["id_counter"] += 1
                st.success(f"✅ Données enregistrées avec succès ! (ID: {st.session_state['id_counter']-1})")

    # Affichage des données saisies
    if not st.session_state["donnees"].empty:
        st.markdown("---")
        st.markdown("### 📋 Données collectées")
        st.dataframe(st.session_state["donnees"], use_container_width=True)

        # Suppression d'une ligne
        st.markdown("#### 🗑️ Supprimer un enregistrement")
        ids_dispo = st.session_state["donnees"]["ID"].tolist()
        id_supp = st.selectbox("Sélectionner l'ID à supprimer", ids_dispo)
        if st.button("🗑️ Supprimer"):
            st.session_state["donnees"] = st.session_state["donnees"][
                st.session_state["donnees"]["ID"] != id_supp
            ].reset_index(drop=True)
            st.success("Enregistrement supprimé.")
            st.rerun()

# ─────────────────────────────────────────────
# PAGE : ANALYSE DESCRIPTIVE
# ─────────────────────────────────────────────
elif menu == "📊 Analyse Descriptive":
    st.markdown("# 📊 Analyse Descriptive des Données")
    st.markdown("---")

    df = st.session_state["donnees"]

    if df.empty:
        st.warning("⚠️ Aucune donnée disponible. Veuillez d'abord saisir des données.")
    else:
        # Filtres
        st.markdown("### 🔍 Filtres")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            types = ["Tous"] + df["Type_Animal"].unique().tolist()
            filtre_type = st.selectbox("Filtrer par type d'animal", types)
        with col_f2:
            locs = ["Tous"] + df["Localisation"].unique().tolist()
            filtre_loc = st.selectbox("Filtrer par localisation", locs)

        df_f = df.copy()
        if filtre_type != "Tous":
            df_f = df_f[df_f["Type_Animal"] == filtre_type]
        if filtre_loc != "Tous":
            df_f = df_f[df_f["Localisation"] == filtre_loc]

        st.markdown(f"**{len(df_f)} enregistrement(s) sélectionné(s)**")
        st.markdown("---")

        # KPIs
        st.markdown("### 📌 Indicateurs Clés")
        num_cols = ["Nombre_Têtes", "Poids_Moyen_Kg", "Production_Lait_L_Jour",
                    "Gain_Quotidien_G", "Mortalite_Percent", "Age_Moyen_Mois"]
        num_df = df_f[num_cols].dropna()

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("🐄 Total têtes", int(df_f["Nombre_Têtes"].sum()))
        with k2:
            st.metric("⚖️ Poids moyen (kg)", f"{df_f['Poids_Moyen_Kg'].mean():.1f}")
        with k3:
            st.metric("🥛 Lait moyen (L/j)", f"{df_f['Production_Lait_L_Jour'].mean():.2f}")
        with k4:
            st.metric("💀 Mortalité moy. (%)", f"{df_f['Mortalite_Percent'].mean():.2f}")

        st.markdown("---")

        # Statistiques descriptives complètes
        desc = num_df.describe().T
        desc["Variance"] = num_df.var()
        desc["Asymétrie"] = num_df.skew()
        desc["Aplatissement"] = num_df.kurtosis()
        mean_vals = num_df.mean()
        desc["CV (%)"] = (num_df.std() / mean_vals.replace(0, float('nan')) * 100).round(2)
        desc = desc.round(3)
        desc = desc.rename(columns={
            "count": "Nb obs",
            "mean": "Moyenne",
            "std": "Écart-type",
            "min": "Min",
            "25%": "Q1",
            "50%": "Médiane",
            "75%": "Q3",
            "max": "Max"
        })
        st.dataframe(desc, use_container_width=True)
        st.markdown("---")

        # Répartition par type et état
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### 🐄 Répartition par type d'animal")
            repartition = df_f["Type_Animal"].value_counts().reset_index()
            repartition.columns = ["Type", "Nombre"]
            st.dataframe(repartition, use_container_width=True)

        with col_b:
            st.markdown("### 💊 Répartition par état de santé")
            sante_rep = df_f["Etat_Sante"].value_counts().reset_index()
            sante_rep.columns = ["État", "Nombre"]
            st.dataframe(sante_rep, use_container_width=True)

        st.markdown("---")

        # Test de normalité
        st.markdown("### 🧪 Test de Normalité (Shapiro-Wilk)")
        col_test = st.selectbox("Variable à tester", num_cols)
        serie = df_f[col_test].dropna()
        if len(serie) >= 3:
            stat, p = stats.shapiro(serie)
            st.write(f"**Statistique W = {stat:.4f} | p-value = {p:.4f}**")
            if p > 0.05:
                st.success("✅ Distribution normale (p > 0.05)")
            else:
                st.warning("⚠️ Distribution non normale (p ≤ 0.05)")
        else:
            st.info("Pas assez de données pour le test (minimum 3 observations).")

        # Valeurs aberrantes (IQR)
        st.markdown("---")
        st.markdown("### 🚨 Détection des Valeurs Aberrantes (méthode IQR)")
        col_out = st.selectbox("Variable à analyser", num_cols, key="outlier")
        serie2 = df_f[col_out].dropna()
        Q1 = serie2.quantile(0.25)
        Q3 = serie2.quantile(0.75)
        IQR = Q3 - Q1
        borne_inf = Q1 - 1.5 * IQR
        borne_sup = Q3 + 1.5 * IQR
        outliers = serie2[(serie2 < borne_inf) | (serie2 > borne_sup)]
        st.write(f"Borne inférieure : **{borne_inf:.2f}** | Borne supérieure : **{borne_sup:.2f}**")
        if len(outliers) > 0:
            st.warning(f"⚠️ {len(outliers)} valeur(s) aberrante(s) détectée(s) : {outliers.values.tolist()}")
        else:
            st.success("✅ Aucune valeur aberrante détectée.")

# ─────────────────────────────────────────────
# PAGE : VISUALISATIONS
# ─────────────────────────────────────────────
elif menu == "📈 Visualisations":
    st.markdown("# 📈 Visualisations Interactives")
    st.markdown("---")

    df = st.session_state["donnees"]

    if df.empty:
        st.warning("⚠️ Aucune donnée disponible. Veuillez d'abord saisir des données.")
    else:
        num_cols = ["Nombre_Têtes", "Poids_Moyen_Kg", "Production_Lait_L_Jour",
                    "Gain_Quotidien_G", "Mortalite_Percent", "Age_Moyen_Mois", "Superficie_Ha"]

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Distribution", "📦 Boîte à Moustaches",
            "🔵 Nuage de Points", "🌡️ Corrélations", "🥧 Camemberts"
        ])

        with tab1:
            st.markdown("### Histogramme de distribution")
            var_hist = st.selectbox("Variable", num_cols, key="hist")
            fig = px.histogram(df, x=var_hist, nbins=20,
                               color="Type_Animal", barmode="overlay",
                               title=f"Distribution de {var_hist}",
                               color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(plot_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("### Boîte à moustaches")
            var_box = st.selectbox("Variable numérique", num_cols, key="box")
            fig2 = px.box(df, y=var_box, x="Type_Animal", color="Type_Animal",
                          title=f"Boîte à moustaches — {var_box} par type d'animal",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig2.update_layout(plot_bgcolor="white")
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            st.markdown("### Nuage de points (Scatter Plot)")
            col_x = st.selectbox("Axe X", num_cols, key="scatter_x")
            col_y = st.selectbox("Axe Y", num_cols, index=1, key="scatter_y")
            df_scatter = df.copy()
            df_scatter[col_x] = pd.to_numeric(df_scatter[col_x], errors="coerce")
            df_scatter[col_y] = pd.to_numeric(df_scatter[col_y], errors="coerce")
            df_scatter["Nombre_Têtes"] = pd.to_numeric(df_scatter["Nombre_Têtes"], errors="coerce")
            df_scatter = df_scatter.dropna(subset=[col_x, col_y, "Nombre_Têtes"])

            fig3 = px.scatter(df_scatter, x=col_x, y=col_y, color="Type_Animal",
                              size="Nombre_Têtes", hover_data=["Eleveur", "Localisation"],
                              title=f"{col_x} vs {col_y}",
                              trendline="ols",
                              color_discrete_sequence=px.colors.qualitative.Bold)
            fig3.update_layout(plot_bgcolor="white")
            st.plotly_chart(fig3, use_container_width=True)

        with tab4:
            st.markdown("### Carte de chaleur des corrélations")
            corr = df[num_cols].dropna().corr().round(2)
            fig4 = go.Figure(data=go.Heatmap(
                z=corr.values,
                x=corr.columns.tolist(),
                y=corr.index.tolist(),
                colorscale="RdYlGn",
                text=corr.values,
                texttemplate="%{text}",
                showscale=True
            ))
            fig4.update_layout(title="Matrice de corrélation", height=500)
            st.plotly_chart(fig4, use_container_width=True)

        with tab5:
            st.markdown("### Répartition par catégorie")
            col_pie = st.selectbox("Variable catégorielle", ["Type_Animal", "Alimentation", "Etat_Sante", "Localisation"])
            pie_data = df[col_pie].value_counts().reset_index()
            pie_data.columns = ["Catégorie", "Nombre"]
            fig5 = px.pie(pie_data, names="Catégorie", values="Nombre",
                          title=f"Répartition — {col_pie}",
                          color_discrete_sequence=px.colors.qualitative.Set3,
                          hole=0.35)
            st.plotly_chart(fig5, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE : EXPORT
# ─────────────────────────────────────────────
elif menu == "📥 Exporter les Données":
    st.markdown("# 📥 Export des Données")
    st.markdown("---")

    df = st.session_state["donnees"]

    if df.empty:
        st.warning("⚠️ Aucune donnée à exporter.")
    else:
        st.success(f"✅ {len(df)} enregistrement(s) prêt(s) à l'export.")
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            csv_data = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📄 Télécharger en CSV",
                data=csv_data,
                file_name=f"agrodata_elevage_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Données Élevage")
                num_cols = ["Nombre_Têtes", "Poids_Moyen_Kg", "Production_Lait_L_Jour",
                            "Gain_Quotidien_G", "Mortalite_Percent"]
                desc = df[num_cols].describe().round(2)
                desc.to_excel(writer, sheet_name="Statistiques")
            st.download_button(
                label="📊 Télécharger en Excel (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"agrodata_elevage_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # Rapport résumé
        st.markdown("---")
        st.markdown("### 📝 Rapport Résumé Automatique")
        num_cols2 = ["Nombre_Têtes", "Poids_Moyen_Kg", "Production_Lait_L_Jour",
                     "Gain_Quotidien_G", "Mortalite_Percent"]
        rapport = f"""
=== RAPPORT AGRODATA ÉLEVAGE ===
Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}
Nombre d'enregistrements : {len(df)}
Éleveurs distincts : {df['Eleveur'].nunique()}
Localisations : {', '.join(df['Localisation'].unique().tolist())}

--- STATISTIQUES CLÉS ---
Total têtes d'animaux : {int(df['Nombre_Têtes'].sum())}
Poids moyen général : {df['Poids_Moyen_Kg'].mean():.2f} kg
Production lait moyenne : {df['Production_Lait_L_Jour'].mean():.2f} L/jour
Taux de mortalité moyen : {df['Mortalite_Percent'].mean():.2f} %
GMQ moyen : {df['Gain_Quotidien_G'].mean():.2f} g/jour

--- RÉPARTITION ANIMAUX ---
{df['Type_Animal'].value_counts().to_string()}

--- ÉTAT DE SANTÉ ---
{df['Etat_Sante'].value_counts().to_string()}
================================
        """
        st.text_area("Rapport", rapport, height=350)
        st.download_button(
            "📥 Télécharger le rapport (.txt)",
            rapport,
            file_name="rapport_agrodata.txt",
            mime="text/plain",
            use_container_width=True
        )

# ─────────────────────────────────────────────
# PAGE : À PROPOS
# ─────────────────────────────────────────────
elif menu == "ℹ️ À propos":
    st.markdown("# ℹ️ À propos de AgroData Élevage")
    st.markdown("---")
    st.info("""
    **AgroData Élevage** est une application web développée dans le cadre du **TP INF232 — EC2**.

    **Secteur :** Élevage 🐄🐐🐖🐓

    **Objectif :** Permettre aux éleveurs et techniciens de terrain de collecter, stocker,
    analyser et exporter des données zootechniques de façon simple, rapide et fiable.

    **Technologies utilisées :**
    - Python 3.11+
    - Streamlit (interface web)
    - Pandas (manipulation des données)
    - Plotly (visualisations interactives)
    - SciPy (tests statistiques)
    - OpenPyXL (export Excel)

    **Fonctionnalités :**
    - Formulaire de saisie complet (15 variables)
    - Import CSV / Excel
    - Statistiques descriptives avancées
    - Tests de normalité (Shapiro-Wilk)
    - Détection des valeurs aberrantes (IQR)
    - Visualisations interactives (5 types de graphiques)
    - Export CSV, Excel et rapport texte

    ---
    *TP INF232 | EC2 | 2025-2026*
    """)
