# ==================================================
# File: config_loader.py
# Configuration loader avec .env et UI fallback
# ==================================================

import os
from pathlib import Path
from typing import Optional
import streamlit as st

class ConfigLoader:
    """Gestion configuration avec .env et UI"""
    
    def __init__(self):
        self.env_file = Path(".env")
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Charge config depuis .env ou crée fichier"""
        config = {}
        
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"').strip("'")
        
        # Fallback sur variables d'environnement
        if not config.get('GEMINI_API_KEY'):
            config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', '')
        
        return config
    
    def get(self, key: str, default: str = '') -> str:
        """Récupère valeur config"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: str):
        """Définit valeur et sauvegarde"""
        self.config[key] = value
        self._save_config()
    
    def _save_config(self):
        """Sauvegarde dans .env"""
        with open(self.env_file, 'w') as f:
            f.write("# Africa Demographics Platform Configuration\n")
            f.write("# Auto-generated file\n\n")
            for key, value in self.config.items():
                f.write(f'{key}="{value}"\n')
    
    def render_ui_config(self, ml_config):
        """Affiche UI configuration dans sidebar"""
        
        st.markdown("**🔑 API Configuration**")
        
        current_key = self.get('GEMINI_API_KEY', '')
        has_key = bool(current_key)
        
        if has_key:
            st.success("✅ Gemini API configurée")
            if st.button("🔄 Modifier clé", key="change_gemini_key"):
                st.session_state.show_api_input = True
        else:
            st.warning("⚠️ Gemini API non configurée")
            st.session_state.show_api_input = True
        
        if st.session_state.get('show_api_input', False) or not has_key:
            api_key_input = st.text_input(
                "Clé API Gemini:" if ml_config.get_language() == "fr" else "Gemini API Key:",
                value=current_key if current_key else "",
                type="password",
                key="gemini_api_key_input",
                help="Obtenez votre clé sur: https://makersuite.google.com/app/apikey"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Sauvegarder", key="save_api_key"):
                    if api_key_input:
                        self.set('GEMINI_API_KEY', api_key_input)
                        st.success("✅ Clé sauvegardée!")
                        st.session_state.show_api_input = False
                        st.rerun()
                    else:
                        st.error("Clé vide")
            
            with col2:
                if st.button("❌ Annuler", key="cancel_api_key"):
                    st.session_state.show_api_input = False
                    st.rerun()
