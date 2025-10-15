# ==================================================
# File: professional_styles.py
# Styles CSS professionnels et components UI
# ==================================================

import streamlit as st
from typing import Optional, Dict, Any
import pandas as pd

class ProfessionalUI:
    """Composants UI professionnels et réutilisables"""
    
    @staticmethod
    def inject_custom_css():
        """CSS professionnel moderne"""
        st.markdown("""
        <style>
            /* Reset et base */
            .stApp {
                background-color: #f8f9fa;
                color: #212529;
            }
            
            /* Tables professionnelles */
            .dataframe {
                font-size: 14px !important;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }
            
            .dataframe thead th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white !important;
                font-weight: 600;
                padding: 12px !important;
                text-align: left;
            }
            
            .dataframe tbody td {
                padding: 10px !important;
                border-bottom: 1px solid #e9ecef;
            }
            
            .dataframe tbody tr:hover {
                background-color: #f1f3f5;
            }
            
            /* Header élégant */
            .main-header {
                font-size: 2.5rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                padding: 1rem 0;
            }
            
            /* Cards métriques */
            .metric-card {
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                border: 1px solid #e9ecef;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .metric-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 8px 20px rgba(102,126,234,0.15);
            }
            
            /* Info tooltips discrets */
            .info-tooltip {
                display: inline-block;
                width: 16px;
                height: 16px;
                background: #6c757d;
                color: white;
                border-radius: 50%;
                text-align: center;
                font-size: 11px;
                line-height: 16px;
                margin-left: 4px;
                cursor: help;
                font-weight: bold;
            }
            
            .info-tooltip:hover {
                background: #667eea;
            }
            
            /* Boutons flottants pour rapports */
            .floating-report-btn {
                position: fixed;
                right: 20px;
                bottom: 100px;
                z-index: 1000;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 20px;
                border-radius: 50px;
                box-shadow: 0 4px 16px rgba(102,126,234,0.4);
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .floating-report-btn:hover {
                transform: scale(1.05);
                box-shadow: 0 6px 24px rgba(102,126,234,0.6);
            }
            
            /* Sections */
            .section-header {
                font-size: 1.75rem;
                font-weight: 600;
                margin: 2rem 0 1rem 0;
                padding: 0.75rem 1rem;
                background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
                border-left: 4px solid #667eea;
                border-radius: 4px;
            }
            
            /* Status badges */
            .status-badge {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.875rem;
                font-weight: 600;
                color: white;
            }
            
            .status-high { background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); }
            .status-opening { background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%); }
            .status-limited { background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }
            .status-none { background: linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%); }
            
            /* Footer fixe professionnel */
            .fixed-footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 0.75rem 1rem;
                text-align: center;
                font-size: 0.875rem;
                z-index: 999;
                box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
            }
            
            /* Suppression des marges streamlit par défaut */
            .block-container {
                padding-bottom: 100px !important;
            }
            
            /* Radio buttons professionnels */
            .stRadio > label {
                font-weight: 500;
                color: #495057;
            }
            
            .stRadio > div {
                gap: 8px;
            }
            
            /* Select boxes élégants */
            .stSelectbox > div > div {
                border-radius: 8px;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def metric_card_with_tooltip(
        label: str, 
        value: str, 
        tooltip: str,
        icon: str = "📊"
    ):
        """Carte métrique avec tooltip hover discret"""
        
        # Utiliser HTML avec title pour hover natif
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #6c757d; font-size: 0.875rem; margin-bottom: 8px;">
                {icon} {label} 
                <span class="info-tooltip" title="{tooltip}">i</span>
            </div>
            <div style="font-size: 1.75rem; font-weight: 700; color: #212529;">
                {value}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def status_badge(status: str, ml_config):
        """Badge de statut élégant"""
        
        status_map = {
            'High Opportunity': ('status-high', '🟢'),
            'Opening Window': ('status-opening', '🟡'),
            'Limited Window': ('status-limited', '🔴'),
            'No Window': ('status-none', '⚪')
        }
        
        css_class, emoji = status_map.get(status, ('status-none', '⚪'))
        status_translated = ml_config.translator.get_text(
            status.lower().replace(" ", "_"), 
            ml_config.get_language()
        )
        
        st.markdown(f"""
        <span class="status-badge {css_class}">
            {emoji} {status_translated}
        </span>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def format_value_safe(value: Any, decimals: int = 2) -> str:
        """Formatage sûr avec gestion NaN"""
        
        if value is None or pd.isna(value):
            return "—"  # Em dash pour valeurs manquantes
        
        if isinstance(value, (int, float)):
            if value == 0:
                return "0"
            return f"{value:,.{decimals}f}".replace(",", " ")
        
        return str(value)
    
    @staticmethod
    def section_header(title: str, icon: str = "📊"):
        """En-tête de section professionnel"""
        st.markdown(f"""
        <div class="section-header">
            {icon} {title}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def floating_report_button(module_name: str, on_click_callback):
        """Bouton flottant pour rapports (CSS uniquement, logique séparée)"""
        
        # Note: L'implémentation réelle nécessite JavaScript pour position fixe
        # Dans Streamlit, on utilise sidebar pour approximation
        pass
    
    @staticmethod
    def data_quality_badge(missing_pct: float) -> str:
        """Badge qualité des données"""
        
        if missing_pct < 5:
            return "🟢 Excellente"
        elif missing_pct < 15:
            return "🟡 Bonne"
        elif missing_pct < 30:
            return "🟠 Acceptable"
        else:
            return "🔴 Limitée"
    
    @staticmethod
    def render_clean_dataframe(df: pd.DataFrame, precision: int = 2):
        """Affiche DataFrame nettoyé sans NaN visibles"""
        
        df_display = df.copy()
        
        # Remplacer NaN par em dash
        for col in df_display.columns:
            if df_display[col].dtype in ['float64', 'float32']:
                df_display[col] = df_display[col].apply(
                    lambda x: f"{x:.{precision}f}" if pd.notna(x) else "—"
                )
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
