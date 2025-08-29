#!/usr/bin/env python3
"""
Mariupol Urbicide Forensic Analytics Dashboard
Interactive Streamlit dashboard for advanced forensic analysis of administrative violence.

Features:
- Temporal address analysis
- Administrative violence patterns
- Cross-dataset correlation
- Interactive maps and visualizations
- Evidence provenance tracking
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import networkx as nx
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path
from config import PROJECT_ROOT

from scripts.toponymic_lookup_service import ToponymicLookup

# Convert string to Path
PROJECT_ROOT = Path(PROJECT_ROOT)

# Page configuration
st.set_page_config(
    page_title="Mariupol Urbicide Forensic Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #f0f2f6, #ffffff);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .evidence-alert {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .forensic-warning {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_forensic_data():
    """Load and cache forensic data from all sources"""
    try:
        # Load seized properties
        seized_df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "seized_properties_combined.csv")
        
        # Load damage assessment
        damage_df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "damage_assessment_clean_en.csv")
        
        # Load PDF metadata
        pdf_df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "pdf_metadata.csv")
        
        return seized_df, damage_df, pdf_df
    except Exception as e:
        st.error(f"Failed to load forensic data: {e}")
        return None, None, None

@st.cache_data
def get_database_statistics():
    """Get forensic database statistics"""
    try:
        with ToponymicLookup() as lookup:
            return lookup.get_statistics()
    except Exception as e:
        st.error(f"Failed to connect to forensic database: {e}")
        return {}

def create_temporal_analysis():
    """Create temporal analysis of administrative violence"""
    st.header("🕐 Temporal Analysis of Administrative Violence")
    
    seized_df, damage_df, pdf_df = load_forensic_data()
    if seized_df is None:
        return
    
    # Parse dates and create timeline
    if 'date' in pdf_df.columns:
        pdf_df['date'] = pd.to_datetime(pdf_df['date'], errors='coerce')
        
        # Group by month
        monthly_docs = pdf_df.groupby(pdf_df['date'].dt.to_period('M')).size().reset_index()
        monthly_docs.columns = ['month', 'document_count']
        monthly_docs['month'] = monthly_docs['month'].astype(str)
        
        # Create timeline visualization
        fig = px.line(monthly_docs, x='month', y='document_count',
                     title='Administrative Documents Over Time',
                     labels={'document_count': 'Number of Documents', 'month': 'Month'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Administrative periods analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Seizure Patterns by District")
        if 'district' in seized_df.columns:
            district_counts = seized_df['district'].value_counts()
            fig = px.bar(x=district_counts.index, y=district_counts.values,
                        title='Seized Properties by District')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏢 Property Types Seized")
        if 'property_type' in seized_df.columns:
            property_counts = seized_df['property_type'].value_counts()
            fig = px.pie(values=property_counts.values, names=property_counts.index,
                        title='Distribution of Seized Property Types')
            st.plotly_chart(fig, use_container_width=True)

def create_address_analysis():
    """Create advanced address and toponymic analysis"""
    st.header("🗺️ Toponymic and Address Analysis")
    
    db_stats = get_database_statistics()
    
    # Database statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Streets", db_stats.get('total_streets', 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Address Variants", db_stats.get('total_variants', 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        languages = db_stats.get('by_language', {})
        st.metric("Languages", len(languages))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        evidence_types = db_stats.get('by_evidence_type', {})
        st.metric("Evidence Sources", len(evidence_types))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Language distribution
    if 'by_language' in db_stats:
        st.subheader("🌐 Multilingual Address Coverage")
        lang_data = db_stats['by_language']
        fig = px.bar(x=list(lang_data.keys()), y=list(lang_data.values()),
                    title='Address Variants by Language',
                    labels={'x': 'Language Code', 'y': 'Number of Variants'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Interactive address lookup
    st.subheader("🔍 Interactive Address Lookup")
    
    search_address = st.text_input("Enter an address to find all variants:", 
                                  placeholder="e.g., Морской 46, Komsomolsky Boulevard")
    
    if search_address:
        try:
            with ToponymicLookup() as lookup:
                variants = lookup.get_all_variants(search_address, include_fuzzy=True)
                
                if variants:
                    st.success(f"Found {len(variants)} variants for '{search_address}':")
                    
                    # Create variants dataframe
                    variants_data = []
                    for v in variants:
                        variants_data.append({
                            'Address': v.name_text,
                            'Language': v.language_code,
                            'Period': v.administrative_period,
                            'Confidence': f"{v.confidence_score:.2f}",
                            'Source': v.source_document,
                            'Evidence Type': v.evidence_type
                        })
                    
                    variants_df = pd.DataFrame(variants_data)
                    st.dataframe(variants_df, use_container_width=True)
                    
                    # Normalized form
                    normalized = lookup.normalize_address(search_address)
                    st.info(f"**Canonical Form:** {normalized}")
                else:
                    st.warning("No variants found for this address.")
        except Exception as e:
            st.error(f"Address lookup failed: {e}")

def create_network_analysis():
    """Create network analysis of administrative relationships"""
    st.header("🕸️ Administrative Network Analysis")
    
    seized_df, damage_df, pdf_df = load_forensic_data()
    if seized_df is None:
        return
    
    # Create network graph of relationships
    st.subheader("🏛️ Administrative Actor Networks")
    
    # Load actor data if available
    try:
        actors_df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "actor_roles_nominative.csv")
        
        # Create network visualization
        G = nx.Graph()
        
        # Add nodes and edges based on document co-occurrence
        actor_pairs = []
        for _, row in actors_df.iterrows():
            if pd.notna(row.get('role')) and pd.notna(row.get('name')):
                G.add_node(row['name'], role=row['role'])
        
        # Simple network metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Actors", len(G.nodes()))
        with col2:
            st.metric("Connections", len(G.edges()))
        with col3:
            if len(G.nodes()) > 0:
                centrality = nx.degree_centrality(G)
                most_central = max(centrality, key=centrality.get) if centrality else "N/A"
                st.metric("Most Central Actor", most_central)
        
        # Role distribution
        if len(G.nodes()) > 0:
            roles = [G.nodes[node].get('role', 'Unknown') for node in G.nodes()]
            role_counts = pd.Series(roles).value_counts()
            
            fig = px.bar(x=role_counts.index, y=role_counts.values,
                        title='Distribution of Administrative Roles')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    except FileNotFoundError:
        st.warning("Actor network data not available. Run actor extraction scripts first.")

def create_evidence_provenance():
    """Create evidence provenance and chain-of-custody tracking"""
    st.header("📋 Evidence Provenance & Chain of Custody")
    
    seized_df, damage_df, pdf_df = load_forensic_data()
    
    # Evidence source breakdown
    st.subheader("📄 Evidence Source Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if pdf_df is not None and 'file_size_bytes' in pdf_df.columns:
            st.metric("Total Documents", len(pdf_df))
            total_size_mb = pdf_df['file_size_bytes'].sum() / (1024 * 1024)
            st.metric("Total Size (MB)", f"{total_size_mb:.1f}")
    
    with col2:
        if seized_df is not None:
            st.metric("Seized Properties", len(seized_df))
        if damage_df is not None:
            st.metric("Damage Records", len(damage_df))
    
    # Document integrity verification
    st.subheader("🔐 Document Integrity Verification")
    
    if pdf_df is not None and 'sha256' in pdf_df.columns:
        # Check for duplicate hashes (potential integrity issues)
        duplicate_hashes = pdf_df['sha256'].duplicated().sum()
        
        if duplicate_hashes > 0:
            st.markdown('<div class="forensic-warning">', unsafe_allow_html=True)
            st.warning(f"⚠️ Found {duplicate_hashes} documents with duplicate SHA-256 hashes. This may indicate file corruption or duplication.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("✅ All documents have unique SHA-256 hashes - integrity verified.")
        
        # File size distribution
        fig = px.histogram(pdf_df, x='file_size_bytes', nbins=30,
                          title='Document Size Distribution')
        fig.update_xaxis(title='File Size (bytes)')
        st.plotly_chart(fig, use_container_width=True)

def create_cross_dataset_correlation():
    """Create cross-dataset correlation analysis"""
    st.header("🔗 Cross-Dataset Correlation Analysis")
    
    seized_df, damage_df, pdf_df = load_forensic_data()
    
    # Address matching across datasets
    st.subheader("🏠 Address Correlation Across Evidence Sources")
    
    if seized_df is not None and damage_df is not None:
        # Find common addresses using the toponymic lookup service
        try:
            with ToponymicLookup() as lookup:
                # Sample analysis of address overlap
                seized_addresses = seized_df.get('orig_address_ru', pd.Series()).dropna().unique()[:100]  # Limit for performance
                damage_addresses = damage_df.get('address', pd.Series()).dropna().unique()[:100]
                
                matches = 0
                for addr in seized_addresses:
                    variants = lookup.get_all_variants(str(addr), include_fuzzy=True)
                    variant_names = [v.name_text.lower() for v in variants]
                    
                    for damage_addr in damage_addresses:
                        if str(damage_addr).lower() in variant_names:
                            matches += 1
                            break
                
                match_rate = (matches / len(seized_addresses)) * 100 if len(seized_addresses) > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Seized Addresses", len(seized_addresses))
                with col2:
                    st.metric("Damage Addresses", len(damage_addresses))
                with col3:
                    st.metric("Match Rate", f"{match_rate:.1f}%")
                
                if match_rate > 0:
                    st.success(f"✅ Found {matches} address matches between seized properties and damage assessments.")
                else:
                    st.info("ℹ️ No direct address matches found. This may indicate different address formats or coverage areas.")
        
        except Exception as e:
            st.error(f"Cross-dataset correlation failed: {e}")

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Mariupol Urbicide Forensic Analytics</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="evidence-alert">
    <strong>⚖️ Legal Notice:</strong> This platform contains forensic evidence of administrative violence 
    and systematic property seizures in occupied Mariupol. All data maintains chain-of-custody for potential legal proceedings.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🔍 Analysis Modules")
    
    analysis_type = st.sidebar.selectbox(
        "Select Analysis Type:",
        [
            "📊 Overview Dashboard",
            "🕐 Temporal Analysis", 
            "🗺️ Address & Toponymic Analysis",
            "🕸️ Network Analysis",
            "📋 Evidence Provenance",
            "🔗 Cross-Dataset Correlation"
        ]
    )
    
    # Database connection status
    st.sidebar.subheader("🔌 System Status")
    try:
        db_stats = get_database_statistics()
        if db_stats:
            st.sidebar.success("✅ Database Connected")
            st.sidebar.info(f"Streets: {db_stats.get('total_streets', 0)}")
            st.sidebar.info(f"Variants: {db_stats.get('total_variants', 0)}")
        else:
            st.sidebar.error("❌ Database Disconnected")
    except:
        st.sidebar.error("❌ Database Error")
    
    # Route to selected analysis
    if analysis_type == "📊 Overview Dashboard":
        create_temporal_analysis()
        create_address_analysis()
    elif analysis_type == "🕐 Temporal Analysis":
        create_temporal_analysis()
    elif analysis_type == "🗺️ Address & Toponymic Analysis":
        create_address_analysis()
    elif analysis_type == "🕸️ Network Analysis":
        create_network_analysis()
    elif analysis_type == "📋 Evidence Provenance":
        create_evidence_provenance()
    elif analysis_type == "🔗 Cross-Dataset Correlation":
        create_cross_dataset_correlation()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8em;">
    🎯 Mariupol Urbicide Forensic Analytics Platform | 
    Built with Streamlit, PostgreSQL, and PostGIS | 
    Forensic Database Integration Layer Active
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
