"""
Customer Segmentation Page — K-Means Clustering & PCA Analysis on Real Customer Data.
======================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from db import run_query, test_connection
from styles import metric_card, gradient_divider
from utils import format_rupee, format_number
from config import CHART_COLORS


def _load_segmentation_data() -> pd.DataFrame:
    """Load customer data for segmentation from PostgreSQL."""
    if not test_connection():
        return pd.DataFrame()
    sql = """
    SELECT age, job, marital, education, balance,
           housing, loan, duration, campaign
    FROM silver.customer_clean;
    """
    return run_query(sql)


def render():
    # ─── Navigation Back Button ────────────────────────────────
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state["nav_page"] = "🏠 Dashboard"
            st.rerun()

    # ─── Header ────────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <h1>👥 Customer Segmentation Analysis</h1>
        <p>Unsupervised K-Means clustering & Principal Component Analysis (PCA) on PostgreSQL customer records</p>
    </div>
    """, unsafe_allow_html=True)

    if not test_connection():
        st.error("❌ Unable to connect to PostgreSQL database.")
        return

    # ─── Load Data ─────────────────────────────────────────────
    with st.spinner("📡 Loading customer dataset..."):
        df = _load_segmentation_data()

    if df.empty:
        st.error("❌ No data in silver.customer_clean. Run the data pipeline first.")
        return

    st.info(f"📊 Loaded **{len(df):,}** customer records for clustering")

    # ─── Clustering Controls ───────────────────────────────────
    st.markdown(gradient_divider(), unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙️ Clustering Configuration</div>', unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3 = st.columns(3)
    with ctrl1:
        n_clusters = st.slider("Number of Clusters (K)", min_value=2, max_value=8, value=4)
    with ctrl2:
        features = st.multiselect(
            "Features for Clustering",
            options=["age", "balance", "duration", "campaign"],
            default=["age", "balance", "duration"],
        )
    with ctrl3:
        viz_mode = st.radio("Visualization", ["2D (PCA)", "3D (PCA)"], horizontal=True)

    if len(features) < 2:
        st.warning("⚠️ Please select at least 2 features for clustering.")
        return

    # ─── Run K-Means ───────────────────────────────────────────
    if st.button("🔬 Run Clustering", type="primary", use_container_width=True):
        with st.spinner("🔄 Running K-Means clustering..."):
            df_features = df[features].fillna(0)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(df_features)

            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            df["Cluster"] = clusters

            # PCA for visualization
            n_components = 3 if viz_mode == "3D (PCA)" else 2
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(X_scaled)

            df["PC1"] = pca_result[:, 0]
            df["PC2"] = pca_result[:, 1]
            if n_components == 3:
                df["PC3"] = pca_result[:, 2]

            st.session_state["seg_df"] = df
            st.session_state["seg_kmeans"] = kmeans
            st.session_state["seg_pca"] = pca
            st.session_state["seg_features"] = features
            st.session_state["seg_n_clusters"] = n_clusters
            st.session_state["seg_viz_mode"] = viz_mode

    # Auto-run if not yet run
    if "seg_df" not in st.session_state:
        df_features = df[features].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_features)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        df["Cluster"] = clusters
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(X_scaled)
        df["PC1"] = pca_result[:, 0]
        df["PC2"] = pca_result[:, 1]
        st.session_state["seg_df"] = df
        st.session_state["seg_kmeans"] = kmeans
        st.session_state["seg_pca"] = pca
        st.session_state["seg_features"] = features
        st.session_state["seg_n_clusters"] = n_clusters
        st.session_state["seg_viz_mode"] = "2D (PCA)"

    # ─── Display Results ───────────────────────────────────────
    if "seg_df" in st.session_state:
        df = st.session_state["seg_df"]
        n_clusters = st.session_state["seg_n_clusters"]
        features = st.session_state["seg_features"]
        viz_mode = st.session_state["seg_viz_mode"]

        st.markdown(gradient_divider(), unsafe_allow_html=True)

        # ─── Cluster KPIs ──────────────────────────────────────
        st.markdown('<div class="section-title">📊 Cluster Overview</div>', unsafe_allow_html=True)
        kpi_cols = st.columns(n_clusters)
        cluster_colors = CHART_COLORS[:n_clusters]

        for i, col in enumerate(kpi_cols):
            cluster_df = df[df["Cluster"] == i]
            with col:
                st.markdown(f"""
                <div class="metric-card" style="border-color: {cluster_colors[i]}40;">
                    <div class="metric-icon" style="color:{cluster_colors[i]};">🎯</div>
                    <div class="metric-value" style="background:none; -webkit-text-fill-color:{cluster_colors[i]};">{len(cluster_df):,}</div>
                    <div class="metric-label">Cluster {i}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(gradient_divider(), unsafe_allow_html=True)

        # ─── Scatter Plot ──────────────────────────────────────
        chart_col, profile_col = st.columns([3, 2])

        with chart_col:
            st.markdown('<div class="section-title">🌌 Cluster Visualization</div>', unsafe_allow_html=True)

            if viz_mode == "3D (PCA)" and "PC3" in df.columns:
                fig = px.scatter_3d(
                    df, x="PC1", y="PC2", z="PC3",
                    color=df["Cluster"].astype(str),
                    color_discrete_sequence=CHART_COLORS,
                    title="Customer Segments (3D PCA)",
                    labels={"color": "Cluster"},
                    opacity=0.6,
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E0E1DD"),
                    title_font=dict(size=16, color="#00B4D8"),
                    height=500,
                    scene=dict(
                        xaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(0,180,216,0.1)"),
                        yaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(0,180,216,0.1)"),
                        zaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(0,180,216,0.1)"),
                    ),
                )
            else:
                fig = px.scatter(
                    df, x="PC1", y="PC2",
                    color=df["Cluster"].astype(str),
                    color_discrete_sequence=CHART_COLORS,
                    title="Customer Segments (2D PCA)",
                    labels={"color": "Cluster"},
                    opacity=0.6,
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E0E1DD"),
                    title_font=dict(size=16, color="#00B4D8"),
                    xaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                    yaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                    height=500,
                )

            st.plotly_chart(fig, use_container_width=True)

        # ─── Cluster Profiles ──────────────────────────────────
        with profile_col:
            st.markdown('<div class="section-title">📋 Cluster Profiles</div>', unsafe_allow_html=True)

            for i in range(n_clusters):
                cluster_df = df[df["Cluster"] == i]
                with st.expander(f"🎯 Cluster {i} — {len(cluster_df):,} customers", expanded=(i == 0)):
                    profile = {}
                    for feat in features:
                        if feat in cluster_df.columns:
                            if feat == "balance":
                                profile[f"Avg Balance"] = format_rupee(cluster_df[feat].mean(), decimals=True)
                                profile[f"Median Balance"] = format_rupee(cluster_df[feat].median())
                            else:
                                profile[f"Avg {feat.title()}"] = f"{cluster_df[feat].mean():.1f}"
                                profile[f"Med {feat.title()}"] = f"{cluster_df[feat].median():.1f}"

                    for k, v in profile.items():
                        st.markdown(f"**{k}:** {v}")

        # ─── Segment Comparison ────────────────────────────────
        st.markdown(gradient_divider(), unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Segment Comparison</div>', unsafe_allow_html=True)

        comparison_data = []
        for i in range(n_clusters):
            cluster_df = df[df["Cluster"] == i]
            row = {"Cluster": f"Cluster {i}", "Size": format_number(len(cluster_df))}
            for feat in features:
                if feat in cluster_df.columns:
                    if feat == "balance":
                        row[f"Avg Balance (₹)"] = format_rupee(cluster_df[feat].mean(), decimals=True)
                    else:
                        row[f"Avg {feat.title()}"] = round(cluster_df[feat].mean(), 2)
            comparison_data.append(row)

        comp_df = pd.DataFrame(comparison_data)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
