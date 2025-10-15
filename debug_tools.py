# ==================================================
# File: debug_tools.py
# Outils de diagnostic API
# ==================================================

import requests
import streamlit as st
from typing import Dict, List
from multilingual_config import Config

class DebugTools:
    """Outils de débogage pour API et problèmes de données"""
    
    @staticmethod
    def test_basic_connectivity() -> Dict:
        """Tester connectivité internet et API de base"""
        tests = []
        
        # Test 1: Internet de base
        try:
            response = requests.get("https://httpbin.org/get", timeout=10)
            tests.append({
                'test': 'Connectivité Internet',
                'status': 'RÉUSSI' if response.status_code == 200 else 'ÉCHEC',
                'details': f"Status: {response.status_code}"
            })
        except Exception as e:
            tests.append({
                'test': 'Connectivité Internet',
                'status': 'ÉCHEC',
                'details': str(e)
            })
        
        # Test 2: Accès API Banque Mondiale
        try:
            response = requests.get(f"{Config.WORLD_BANK_BASE_URL}/country?format=json&per_page=1", timeout=15)
            tests.append({
                'test': 'Accès API Banque Mondiale',
                'status': 'RÉUSSI' if response.status_code == 200 else 'ÉCHEC',
                'details': f"Status: {response.status_code}, Type de réponse: {type(response.json())}"
            })
        except Exception as e:
            tests.append({
                'test': 'Accès API Banque Mondiale',
                'status': 'ÉCHEC',
                'details': str(e)
            })
        
        return {'tests': tests}
    
    @staticmethod
    def test_single_indicator(indicator_code: str, countries: List[str] = None) -> Dict:
        """Tester récupération d'un seul indicateur"""
        if countries is None:
            countries = ['NGA', 'KEN', 'ZAF']  # Pays de test
        
        country_codes = ';'.join(countries)
        url = f"{Config.WORLD_BANK_BASE_URL}/country/{country_codes}/indicator/{indicator_code}"
        params = {
            'format': 'json',
            'date': '2020:2023',
            'per_page': 100
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            result = {
                'status': 'SUCCÈS',
                'url': response.url,
                'response_type': type(data).__name__,
                'response_length': len(data) if isinstance(data, list) else 'Pas une liste',
                'has_metadata': isinstance(data, list) and len(data) > 0,
                'has_data': isinstance(data, list) and len(data) > 1 and data[1] is not None,
                'data_count': len(data[1]) if isinstance(data, list) and len(data) > 1 and data[1] else 0,
                'sample_record': None
            }
            
            if result['has_data'] and data[1]:
                result['sample_record'] = data[1][0]
            
            return result
            
        except Exception as e:
            return {
                'status': 'ERREUR',
                'error': str(e),
                'url': f"{url}?{requests.compat.urlencode(params)}"
            }
    
    @staticmethod
    def run_comprehensive_test() -> Dict:
        """Exécuter test système complet"""
        
        # CSS pour tableaux avec police augmentée
        st.markdown("""
        <style>
            .dataframe { font-size: 16px !important; }
            .dataframe td, .dataframe th { font-size: 16px !important; padding: 8px !important; }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔧 Test Système Complet")
        
        results = {
            'connectivity': DebugTools.test_basic_connectivity(),
            'indicators': {},
            'summary': {'passed': 0, 'failed': 0}
        }
        
        # Tester indicateurs principaux
        for wb_code, indicator_name in Config.CORE_INDICATORS.items():
            st.write(f"Test de {indicator_name}...")
            test_result = DebugTools.test_single_indicator(wb_code)
            results['indicators'][indicator_name] = test_result
            
            if test_result.get('status') == 'SUCCÈS' and test_result.get('data_count', 0) > 0:
                results['summary']['passed'] += 1
                st.success(f"✅ {indicator_name}: {test_result.get('data_count', 0)} enregistrements")
            else:
                results['summary']['failed'] += 1
                st.error(f"❌ {indicator_name}: Échec")
        
        return results