import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from multilingual_config import Config, MultilingualConfig
from api_service import WorldBankAPIService
from analytics import DemographicAnalytics
from cache_manager import CacheManager
from debug_tools import DebugTools
from tooltips import TooltipManager
from generator_utils import ReportGenerator
from config_loader import ConfigLoader
from professional_styles import ProfessionalUI
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="🌍 Africa Demographics Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=3600, show_spinner=False)
def load_demographic_data(use_core_only: bool = False):
    service = WorldBankAPIService()
    return service.load_all_demographic_data(use_core_only=use_core_only)

def create_continental_overview_professional(df: pd.DataFrame, ml_config: MultilingualConfig, analytics: DemographicAnalytics):
    if df.empty:
        st.error(ml_config.t("no_data"))
        return None
    
    continental_metrics = analytics.calculate_continental_metrics(df)
    
    if 'error' in continental_metrics:
        st.error(f"❌ {continental_metrics['error']}")
        return None
    
    pop_millions = continental_metrics.get('total_population_millions', 0)
    
    if pop_millions > 0:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; 
                   padding: 1.5rem; border-radius: 12px; text-align: center; margin: 1rem 0; box-shadow: 0 4px 12px rgba(102,126,234,0.3);">
            <h3 style="margin:0;">🌍 {ml_config.t("population")} ({ml_config.t("world_bank_api")})</h3>
            <h1 style="margin:0.5rem 0;">{ProfessionalUI.format_value_safe(pop_millions, 0)} {ml_config.t("million")}</h1>
            <p style="margin:0; opacity:0.9;">{ml_config.t("population_calculation")}</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pop_display = ProfessionalUI.format_value_safe(pop_millions, 0) + "M"
        tooltip = TooltipManager.get_tooltip("total_population", ml_config.get_language())
        ProfessionalUI.metric_card_with_tooltip(
            ml_config.t('population'), pop_display, tooltip, "🌍"
        )
    
    with col2:
        median_age = continental_metrics.get('weighted_median_age')
        age_display = ProfessionalUI.format_value_safe(median_age, 1) + f" {ml_config.t('years')}"
        tooltip = TooltipManager.get_tooltip("median_age", ml_config.get_language())
        ProfessionalUI.metric_card_with_tooltip(
            ml_config.t('median_age'), age_display, tooltip, "👥"
        )
    
    with col3:
        tfr = continental_metrics.get('weighted_tfr')
        tfr_display = ProfessionalUI.format_value_safe(tfr, 1)
        tooltip = TooltipManager.get_tooltip("total_fertility_rate", ml_config.get_language())
        ProfessionalUI.metric_card_with_tooltip(
            ml_config.t('fertility_rate'), tfr_display, tooltip, "👶"
        )
    
    with col4:
        growth_rate = continental_metrics.get('weighted_growth_rate')
        growth_display = ProfessionalUI.format_value_safe(growth_rate, 1) + "%"
        tooltip = TooltipManager.get_tooltip("population_growth_rate", ml_config.get_language())
        ProfessionalUI.metric_card_with_tooltip(
            ml_config.t('growth_rate'), growth_display, tooltip, "📈"
        )
    
    ProfessionalUI.section_header(f"{ml_config.t('demographic_dividend')} - {ml_config.t('real_time_data')}", "🎯")
    
    dividend_dist = continental_metrics.get('dividend_distribution', {})
    col1, col2, col3, col4 = st.columns(4)
    
    status_configs = [
        ("high_opportunity", "🟢", "High Opportunity"),
        ("opening_window", "🟡", "Opening Window"),
        ("limited_window", "🔴", "Limited Window"),
        ("no_window", "⚪", "No Window")
    ]
    
    for (col, (status_key, emoji, english_status)) in zip([col1, col2, col3, col4], status_configs):
        with col:
            count = dividend_dist.get(english_status, 0)
            status_name = ml_config.t(status_key)
            countries_text = "pays" if ml_config.get_language() == "fr" else "countries"
            tooltip = TooltipManager.get_tooltip(status_key, ml_config.get_language())
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="color: #6c757d; font-size: 0.875rem; margin-bottom: 8px;">
                    {emoji} {status_name}
                    <span class="info-tooltip" title="{tooltip[:200]}...">i</span>
                </div>
                <div style="font-size: 1.75rem; font-weight: 700;">{count} {countries_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    return continental_metrics

def create_africa_map(df: pd.DataFrame, indicator: str, year: int, ml_config: MultilingualConfig):
    map_data = get_best_available_data(df, indicator, year, 3)
    
    if map_data.empty:
        st.warning(f"Aucune donnée disponible pour {indicator}")
        return None
    
    iso2_to_iso3 = {
        'DZ': 'DZA', 'AO': 'AGO', 'BJ': 'BEN', 'BW': 'BWA', 'BF': 'BFA',
        'BI': 'BDI', 'CM': 'CMR', 'CV': 'CPV', 'CF': 'CAF', 'TD': 'TCD',
        'KM': 'COM', 'CG': 'COG', 'CD': 'COD', 'CI': 'CIV', 'DJ': 'DJI',
        'EG': 'EGY', 'GQ': 'GNQ', 'ER': 'ERI', 'SZ': 'SWZ', 'ET': 'ETH',
        'GA': 'GAB', 'GM': 'GMB', 'GH': 'GHA', 'GN': 'GIN', 'GW': 'GNB',
        'KE': 'KEN', 'LS': 'LSO', 'LR': 'LBR', 'LY': 'LBY', 'MG': 'MDG',
        'MW': 'MWI', 'ML': 'MLI', 'MR': 'MRT', 'MU': 'MUS', 'MA': 'MAR',
        'MZ': 'MOZ', 'NA': 'NAM', 'NE': 'NER', 'NG': 'NGA', 'RW': 'RWA',
        'ST': 'STP', 'SN': 'SEN', 'SC': 'SYC', 'SL': 'SLE', 'SO': 'SOM',
        'ZA': 'ZAF', 'SS': 'SSD', 'SD': 'SDN', 'TZ': 'TZA', 'TG': 'TGO',
        'TN': 'TUN', 'UG': 'UGA', 'ZM': 'ZMB', 'ZW': 'ZWE'
    }
    
    map_data['country_iso3'] = map_data['country_iso2'].map(iso2_to_iso3)
    map_data = map_data.dropna(subset=['country_iso3'])
    
    morocco_data = map_data[map_data['country_iso3'] == 'MAR']
    if not morocco_data.empty:
        sahara_data = morocco_data.copy()
        sahara_data['country_iso3'] = 'ESH'
        map_data = pd.concat([map_data, sahara_data], ignore_index=True)
    
    indicator_name = ml_config.translator.get_indicator_name(indicator, ml_config.get_language())
    title = f"Afrique: {indicator_name} ({year})" if ml_config.get_language() == "fr" else f"Africa: {indicator_name} ({year})"
    
    fig = px.choropleth(
        map_data, locations='country_iso3', color=indicator,
        hover_name='country_name', color_continuous_scale='Viridis',
        title=title, labels={indicator: indicator_name}
    )
    
    fig.update_geos(
        projection_type="natural earth", showframe=False, showcoastlines=True,
        lonaxis_range=[-25, 55], lataxis_range=[-40, 40]
    )
    fig.update_layout(height=600, title_x=0.5)
    
    st.plotly_chart(fig, use_container_width=True)
    return fig

def get_best_available_data(df, indicator, target_year, max_years_back=3):
    result = []
    for country in df['country_iso2'].unique():
        country_data = df[df['country_iso2'] == country]
        for offset in range(max_years_back + 1):
            year = target_year - offset
            year_data = country_data[country_data['year'] == year]
            if not year_data.empty and pd.notna(year_data[indicator].iloc[0]):
                result.append({
                    'country_iso2': country,
                    'country_name': year_data['country_name'].iloc[0],
                    'year': year,
                    indicator: round(year_data[indicator].iloc[0], 2)
                })
                break
    return pd.DataFrame(result)

def create_population_pyramid(df: pd.DataFrame, country: str, year: int = 2023, animate: bool = False):
    country_data = df[df['country_name'] == country].copy()
    if country_data.empty:
        st.error(f"No data for {country}")
        return None
    
    pyramid_data = country_data if animate else country_data[country_data['year'] == year]
    animation_years = sorted(country_data['year'].unique()) if animate else [year]
    
    if pyramid_data.empty:
        return None
    
    age_groups = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80+']
    
    def generate_distribution(tfr, life_exp, growth):
        tfr = np.clip(tfr if pd.notna(tfr) else 4.0, 1.5, 8.0)
        life_exp = np.clip(life_exp if pd.notna(life_exp) else 60, 40, 85)
        growth = np.clip(growth if pd.notna(growth) else 2.5, -1, 5)
        
        survival = []
        for i in range(17):
            if i < 3:
                s = 0.95 + (life_exp - 50) * 0.001
            elif i < 13:
                s = 0.98 - (i - 3) * 0.005
            else:
                s = max(0.3, 0.85 - (i - 13) * 0.1 - (85 - life_exp) * 0.01)
            survival.append(max(0.1, min(0.99, s)))
        
        dist = []
        base = 100000 * (tfr / 5.0) * 0.048
        
        for i in range(17):
            if i == 0:
                pop = base * survival[i]
            else:
                pop = dist[i-1] * survival[i] * (1 + growth/100) ** (-(i * 5))
                if i >= 15:
                    pop *= 0.6
            dist.append(max(100, pop))
        
        total = sum(dist)
        return [round(p / total * 100, 2) for p in dist] if total > 0 else [5.5]*3 + [4.0]*10 + [2.0]*4
    
    fig = go.Figure()
    
    for yr in animation_years:
        year_data = pyramid_data[pyramid_data['year'] == yr]
        if year_data.empty:
            continue
        
        data = year_data.iloc[0]
        pop_age = generate_distribution(
            data.get('total_fertility_rate', 4.0),
            data.get('life_expectancy', 60),
            data.get('population_growth_rate', 2.5)
        )
        
        male = [round(-p * 0.515, 2) for p in pop_age]
        female = [round(p * 0.485, 2) for p in pop_age]
        
        fig.add_trace(go.Bar(y=age_groups, x=male, name='Male', orientation='h', marker_color='lightblue', visible=(yr == animation_years[0])))
        fig.add_trace(go.Bar(y=age_groups, x=female, name='Female', orientation='h', marker_color='pink', visible=(yr == animation_years[0])))
    
    if animate and len(animation_years) > 1:
        frames = []
        for yr in animation_years:
            year_data = pyramid_data[pyramid_data['year'] == yr]
            if year_data.empty:
                continue
            data = year_data.iloc[0]
            pop_age = generate_distribution(data.get('total_fertility_rate', 4.0), data.get('life_expectancy', 60), data.get('population_growth_rate', 2.5))
            male = [round(-p * 0.515, 2) for p in pop_age]
            female = [round(p * 0.485, 2) for p in pop_age]
            frames.append(go.Frame(data=[go.Bar(y=age_groups, x=male, marker_color='lightblue'), go.Bar(y=age_groups, x=female, marker_color='pink')], name=str(yr)))
        
        fig.frames = frames
        fig.update_layout(
            updatemenus=[{'type': 'buttons', 'buttons': [{'label': 'Play', 'method': 'animate', 'args': [None]}, {'label': 'Pause', 'method': 'animate', 'args': [[None]]}]}],
            sliders=[{'steps': [{'args': [[str(yr)]], 'label': str(yr), 'method': 'animate'} for yr in animation_years]}]
        )
    
    fig.update_layout(title=f"Population Pyramid - {country} ({year})", xaxis_title='Population (%)', yaxis_title='Age Groups', barmode='relative', height=600)
    st.plotly_chart(fig, use_container_width=True)
    return fig

def create_trend_comparison(df: pd.DataFrame, countries: list, indicators: list):
    if not countries or not indicators:
        return None
    
    trend_data = df[df['country_name'].isin(countries)].copy()
    fig = make_subplots(rows=len(indicators), cols=1, subplot_titles=[i.replace('_', ' ').title() for i in indicators], vertical_spacing=0.08)
    colors = px.colors.qualitative.Set1[:len(countries)]
    
    for i, indicator in enumerate(indicators):
        if indicator not in trend_data.columns:
            continue
        for j, country in enumerate(countries):
            data = trend_data[trend_data['country_name'] == country][['year', indicator]].dropna()
            if not data.empty:
                data[indicator] = data[indicator].round(2)
                fig.add_trace(go.Scatter(x=data['year'], y=data[indicator], mode='lines+markers', name=country, line=dict(color=colors[j]), showlegend=(i == 0)), row=i+1, col=1)
    
    fig.update_layout(height=300 * len(indicators), title="Multi-Country Trends")
    st.plotly_chart(fig, use_container_width=True)
    return fig

def create_clustering_viz(clustered_data: pd.DataFrame):
    if clustered_data.empty:
        return None, None
    
    indicators = ['total_fertility_rate', 'median_age', 'population_growth_rate', 'life_expectancy']
    valid = [i for i in indicators if i in clustered_data.columns]
    
    if len(valid) < 2:
        return None, None
    
    x_ind, y_ind = valid[0], valid[1]
    data = clustered_data.copy()
    data[x_ind] = data[x_ind].round(2)
    data[y_ind] = data[y_ind].round(2)
    
    size_col = None
    if 'population_growth_rate' in data.columns:
        size_col = np.abs(data['population_growth_rate'].fillna(0)) + 1
    
    fig = px.scatter(data, x=x_ind, y=y_ind, color='cluster_label' if 'cluster_label' in data.columns else 'cluster', size=size_col, hover_name='country_name', title='Clustering by Demographic Profile')
    fig.update_layout(height=500)
    
    summary = None
    if 'cluster_label' in data.columns:
        summary = data.groupby('cluster_label').agg({**{i: ['mean', 'count'] for i in valid[:3]}, 'country_name': 'count'}).round(2)
    
    return fig, summary

def main():
    Config.setup_directories()
    
    if 'ml_config' not in st.session_state:
        st.session_state.ml_config = MultilingualConfig()
    if 'config_loader' not in st.session_state:
        st.session_state.config_loader = ConfigLoader()
    
    ml_config = st.session_state.ml_config
    config_loader = st.session_state.config_loader
    
    ProfessionalUI.inject_custom_css()
    
    analytics = DemographicAnalytics()
    cache = CacheManager()
    debug = DebugTools()
    
    # Sidebar
    st.sidebar.markdown("## 🌍 Language")
    lang = st.sidebar.selectbox("", ["fr", "en"], index=0 if ml_config.get_language() == "fr" else 1, format_func=lambda x: "🇫🇷 Français" if x == "fr" else "🇬🇧 English")
    if lang != ml_config.get_language():
        ml_config.set_language(lang)
        st.rerun()
    
    st.markdown(f'<h1 class="main-header">🌍 {ml_config.t("app_title")}</h1>', unsafe_allow_html=True)
    
    st.sidebar.markdown(f"## 🌍 {ml_config.t('navigation')}")
    page = st.sidebar.radio("", [ml_config.t("continental_overview"), ml_config.t("country_profiles"), ml_config.t("trend_analysis"), ml_config.t("clustering_analysis"), ml_config.t("data_explorer")], index=0)
    
    st.sidebar.markdown(f"## 📊 {ml_config.t('data_source')}")
    st.sidebar.info(f"**{ml_config.t('world_bank_api')}**\n- {ml_config.t('real_time_data')}\n- {ml_config.t('african_countries')}\n- {ml_config.t('years_coverage')}")
    
    # Boutons rapports sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📄 Rapports")
    if st.sidebar.button("📝 Simple", key="sidebar_simple", use_container_width=True):
        st.session_state.gen_simple = True
    if st.sidebar.button("🤖 IA", key="sidebar_ai", use_container_width=True):
        st.session_state.gen_ai = True
    
    # Paramètres
    st.sidebar.markdown("---")
    with st.sidebar.expander(f"⚙️ {'Paramètres' if ml_config.get_language() == 'fr' else 'Settings'}", expanded=False):
        st.markdown(f"**⚙️ {'Chargement' if ml_config.get_language() == 'fr' else 'Data Loading'}**")
        use_core = st.checkbox("Core indicators only" if ml_config.get_language() == "en" else "Indicateurs principaux", value=False)
        if st.button("🔄 Reload"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"**💾 Cache**")
        cache_info = cache.get_cache_info()
        if cache_info['total_files'] > 0:
            st.success(f"🗃 {cache_info['total_files']} fichiers")
            if st.button("🗑️ Clear"):
                cache.clear_cache()
                st.rerun()
        
        st.markdown("---")
        config_loader.render_ui_config(ml_config)
    
    # Main
    if page == ml_config.t("continental_overview"):
        try:
            with st.spinner(ml_config.t("loading_data")):
                df = load_demographic_data(use_core)
            
            if df.empty:
                st.error(ml_config.t("no_data"))
                return
            
            report_data = create_continental_overview_professional(df, ml_config, analytics)
            
            if report_data:
                st.markdown("---")
                ProfessionalUI.section_header(ml_config.t('select_indicator'), "🗺️")
                
                indicators = [c for c in df.columns if c in ['total_fertility_rate', 'population_growth_rate', 'median_age', 'dividend_score']]
                if indicators:
                    col1, col2 = st.columns(2)
                    with col1:
                        ind = st.selectbox("Indicator:", indicators, format_func=lambda x: ml_config.translator.get_indicator_name(x, ml_config.get_language()))
                    with col2:
                        yr = st.selectbox("Year:", sorted(df['year'].unique(), reverse=True))
                    create_africa_map(df, ind, yr, ml_config)
                
                # Génération rapports
                if st.session_state.get('gen_simple'):
                    with st.spinner("Génération..."):
                        gen = ReportGenerator(ml_config, config_loader)
                        bytes_data = gen.create_simple_report(ml_config.t("continental_overview"), report_data, None)
                        st.download_button("⬇️ Télécharger", bytes_data, f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    st.session_state.gen_simple = False
                
                if st.session_state.get('gen_ai'):
                    if config_loader.get('GEMINI_API_KEY'):
                        with st.spinner("Analyse IA..."):
                            gen = ReportGenerator(ml_config, config_loader)
                            bytes_data = gen.create_ai_report(ml_config.t("continental_overview"), report_data, None)
                            st.download_button("⬇️ Télécharger IA", bytes_data, f"rapport_ia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        st.warning("Configurez GEMINI_API_KEY dans Paramètres")
                    st.session_state.gen_ai = False
        
        except Exception as e:
            st.error(f"Error: {e}")
    
    elif page == ml_config.t("country_profiles"):
        try:
            df = load_demographic_data(use_core)
            if df.empty:
                st.error(ml_config.t("no_data"))
                return
            
            ProfessionalUI.section_header(ml_config.t("country_profiles"), "🏛️")
            country = st.selectbox("Country:", sorted(df['country_name'].unique()))
            data = df[df['country_name'] == country].copy()
            
            if not data.empty:
                latest = data[data['year'] == data['year'].max()].iloc[0]
                
                st.markdown(f"### 📊 {country} - {latest['year']:.0f}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    val = ProfessionalUI.format_value_safe(latest.get('total_fertility_rate'), 1)
                    tooltip = TooltipManager.get_tooltip("total_fertility_rate", ml_config.get_language())
                    ProfessionalUI.metric_card_with_tooltip(ml_config.t("fertility_rate"), val, tooltip, "👶")
                
                with col2:
                    pop = latest.get('total_population')
                    val = ProfessionalUI.format_value_safe(pop / 1e6 if pd.notna(pop) else None, 1) + "M"
                    ProfessionalUI.metric_card_with_tooltip(ml_config.t("population"), val, "", "🌍")
                
                with col3:
                    val = ProfessionalUI.format_value_safe(latest.get('median_age'), 1) + f" {ml_config.t('years')}"
                    tooltip = TooltipManager.get_tooltip("median_age", ml_config.get_language())
                    ProfessionalUI.metric_card_with_tooltip(ml_config.t("median_age"), val, tooltip, "👥")
                
                with col4:
                    status = latest.get('dividend_status')
                    if pd.notna(status):
                        ProfessionalUI.status_badge(status, ml_config)
                
                ProfessionalUI.section_header(ml_config.t('population_pyramid'), "📈")
                col1, col2 = st.columns([3, 1])
                with col2:
                    yr = st.selectbox("Year:", sorted(data['year'].unique(), reverse=True))
                    animate = st.checkbox("🎬 Animate")
                with col1:
                    create_population_pyramid(df, country, yr, animate)
        
        except Exception as e:
            st.error(f"Error: {e}")
    
    elif page == ml_config.t("trend_analysis"):
        try:
            df = load_demographic_data(use_core)
            if df.empty:
                st.error(ml_config.t("no_data"))
                return
            
            ProfessionalUI.section_header(ml_config.t("trend_analysis"), "📈")
            
            col1, col2 = st.columns(2)
            with col1:
                countries = st.multiselect("Countries:", sorted(df['country_name'].unique()), default=sorted(df['country_name'].unique())[:4], max_selections=6)
            with col2:
                indicators = [c for c in df.select_dtypes(include=['number']).columns if c not in ['year'] and df[c].notna().sum() > 50]
                sel_ind = st.multiselect("Indicators:", indicators, default=['total_fertility_rate', 'population_growth_rate'] if all(x in indicators for x in ['total_fertility_rate', 'population_growth_rate']) else indicators[:2], format_func=lambda x: ml_config.translator.get_indicator_name(x, ml_config.get_language()))
            
            if countries and sel_ind:
                create_trend_comparison(df, countries, sel_ind)
        
        except Exception as e:
            st.error(f"Error: {e}")
    
    elif page == ml_config.t("clustering_analysis"):
        try:
            df = load_demographic_data(use_core)
            if df.empty:
                st.error(ml_config.t("no_data"))
                return
            
            ProfessionalUI.section_header(ml_config.t("clustering_analysis"), "🔬")
            yr = st.selectbox("Year:", sorted(df['year'].unique(), reverse=True))
            clustered = analytics.get_country_clusters(df, yr)
            
            if not clustered.empty:
                fig, summary = create_clustering_viz(clustered)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                if summary is not None:
                    st.dataframe(summary)
        
        except Exception as e:
            st.error(f"Error: {e}")
    
    elif page == ml_config.t("data_explorer"):
        try:
            df = load_demographic_data(use_core)
            if df.empty:
                st.error(ml_config.t("no_data"))
                return
            
            ProfessionalUI.section_header(ml_config.t("data_explorer"), "🔍")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                countries = st.multiselect("Countries:", sorted(df['country_name'].unique()), default=sorted(df['country_name'].unique()))
            with col2:
                yr_range = st.slider("Years:", int(df['year'].min()), int(df['year'].max()), (int(df['year'].min()), int(df['year'].max())))
            with col3:
                indicators = [c for c in df.select_dtypes(include=['number']).columns if c not in ['year']]
                sel_ind = st.multiselect("Indicators:", indicators, default=indicators[:5], format_func=lambda x: ml_config.translator.get_indicator_name(x, ml_config.get_language()))
            
            filtered = df[(df['country_name'].isin(countries)) & (df['year'] >= yr_range[0]) & (df['year'] <= yr_range[1])].copy()
            display = filtered[['country_name', 'year'] + sel_ind].copy()
            
            ProfessionalUI.render_clean_dataframe(display, precision=2)
            
            col1, col2 = st.columns(2)
            with col1:
                csv = display.to_csv(index=False)
                st.download_button(ml_config.t("download_csv"), csv, f"data_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
            with col2:
                json = display.to_json(orient='records', indent=2)
                st.download_button(ml_config.t("download_json"), json, f"data_{datetime.now().strftime('%Y%m%d')}.json", "application/json")
        
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Footer
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    date = datetime.now().strftime("%d %B %Y") if ml_config.get_language() == "fr" else datetime.now().strftime("%B %d, %Y")
    st.markdown(f"""
    <div class='fixed-footer'>
        <strong>🌍 Africa Demographics Platform (ADP)</strong> v2.5 | 
        Zakaria Benhoumad | Anthropic Claude | 
        📊 {ml_config.t("data_attribution")} • {date}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()