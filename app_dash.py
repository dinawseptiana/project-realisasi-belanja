import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

# === Page Configuration ===
st.set_page_config(
    page_title="Dashboard Anggaran & Realisasi Belanja", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === Custom CSS ===
st.markdown("""
<style>
    /* Set white background for entire app */
    .stApp {
        background-color: white !important;
    }
    
    .main > div {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        background-color: white !important;
    }
    
    /* Ensure sidebar is also white if used */
    .css-1d391kg {
        background-color: white !important;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .welcome-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .section-header {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    
    .info-box {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .success-box {
        background-color: #e8f5e8;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: white !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        color: #1f77b4;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    
    .download-button {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        border: none;
        font-weight: bold;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        margin: 1rem 0;
    }
    
    .logo-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .logo-header h2 {
        margin: 0;
        color: white !important;
        font-weight: bold !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Ensure content containers have white background */
    .block-container {
        background-color: white !important;
        padding-top: 1rem !important;
    }
    
    /* Tab content background */
    .stTabs > div > div > div > div {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# === Logo Header ===
st.markdown("""
    <div class='logo-header'>
        <img src='https://raw.githubusercontent.com/dinawseptiana/project-realisasi-belanja/main/logo.png' width='120'/>
        <div>
            <h2 style='color: white !important; font-weight: bold !important;'>Dashboard Anggaran & Realisasi Belanja</h2>
            <p style='margin: 0; opacity: 0.9; font-size: 1.1rem; color: white;'>Direktorat Jenderal Perbendaharaan (DJPb) Kementerian Keuangan Republik Indonesia</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# === Load data dari GitHub ===
@st.cache_data
def load_data():
    URL = "https://raw.githubusercontent.com/dinawseptiana/project-realisasi-belanja/main/data/RealisasiBelanja_cleaned.xlsx"
    df = pd.read_excel(URL)
    
    # Preprocessing
    df = df.dropna(subset=['Realisasi', 'Anggaran'])
    df['Realisasi'] = df['Realisasi'].astype(str).str.replace(",", "").astype(float)
    df['Anggaran'] = df['Anggaran'].astype(str).str.replace(",", "").astype(float)
    df['Sisa Anggaran'] = df['Anggaran'] - df['Realisasi']
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    df['TriwulanAngka'] = df['Triwulan'].replace({'I': 1, 'II': 2, 'III': 3, 'IV': 4})
    
    le_jenis = LabelEncoder()
    df['JenisEncoded'] = le_jenis.fit_transform(df['Jenis Belanja'])
    
    return df, le_jenis

df, le_jenis = load_data()

# === KPI Metrics ===
total_anggaran = df['Anggaran'].sum()
total_realisasi = df['Realisasi'].sum()
rata2_persen = df['Realisasi'].sum() / df['Anggaran'].sum() * 100
total_sisa = df['Sisa Anggaran'].sum()

# Custom KPI Display
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">💰 Total Anggaran</p>
        <p class="metric-value">Rp {total_anggaran:,.0f}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">✅ Total Realisasi</p>
        <p class="metric-value">Rp {total_realisasi:,.0f}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">📊 Persentase Realisasi</p>
        <p class="metric-value">{rata2_persen:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">💸 Sisa Anggaran</p>
        <p class="metric-value">Rp {total_sisa:,.0f}</p>
    </div>
    """, unsafe_allow_html=True)

# === Tab Layout ===
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Beranda", "📊 Realisasi Anggaran", "🔍 Analisis Jenis Belanja", "🔮 Prediksi", "💸 Sisa Anggaran", "📍 Eksplorasi Data"
])

# === Tab 1: Beranda ===
with tab1:
    st.markdown("""
    <div class='welcome-card'>
        <h3 style='color: #2c3e50; margin-bottom: 1rem;'>🎯 Selamat Datang di Dashboard Realisasi Belanja</h3>
        <p style='font-size: 1.1rem; color: #34495e; line-height: 1.6;'>
            Dashboard ini dikembangkan untuk menyajikan dan menganalisis data realisasi belanja berdasarkan jenis belanja 
            <b>Direktorat Jenderal Perbendaharaan (DJPb)</b> tahun 2023 - 2025.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature highlights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='info-box'>
            <h4>✨ Fitur Utama Dashboard</h4>
            <ul style='line-height: 1.8;'>
                <li>📈 Visualisasi tren realisasi & anggaran berdasarkan triwulan</li>
                <li>🥧 Distribusi realisasi berdasarkan jenis belanja</li>
                <li>🤖 Prediksi belanja untuk Triwulan III & IV Tahun 2025</li>
                <li>📥 Export data hasil prediksi dalam format Excel</li>
                <li>🔍 Eksplorasi data interaktif dengan filter dinamis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='success-box'>
            <h4>📊 Ringkasan Data</h4>
            <ul style='line-height: 1.8;'>
                <li><b>Periode:</b> 2023 - 2025</li>
                <li><b>Total Records:</b> """ + f"{len(df):,}" + """ data</li>
                <li><b>Jenis Belanja:</b> """ + f"{df['Jenis Belanja'].nunique()}" + """ kategori</li>
                <li><b>Efisiensi Rata-rata:</b> """ + f"{rata2_persen:.1f}%" + """</li>
                <li><b>Last Update:</b> """ + datetime.now().strftime("%d %B %Y") + """</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Quick insights
    st.markdown("<div class='section-header'><h3>🎯 Insight Cepat</h3></div>", unsafe_allow_html=True)
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    # Top performing year
    top_year = df.groupby('Tahun')['Realisasi'].sum().idxmax()
    top_year_value = df.groupby('Tahun')['Realisasi'].sum().max()
    
    # Best performing expense type
    top_expense = df.groupby('Jenis Belanja')['Realisasi'].sum().idxmax()
    top_expense_value = df.groupby('Jenis Belanja')['Realisasi'].sum().max()
    
    # Best quarter
    top_quarter = df.groupby('Triwulan')['Realisasi'].sum().idxmax()
    top_quarter_value = df.groupby('Triwulan')['Realisasi'].sum().max()
    
    with insight_col1:
        st.info(f"🏆 **Tahun Terbaik**\n\n{top_year} dengan realisasi Rp {top_year_value:,.0f}")
    
    with insight_col2:
        st.success(f"💼 **Jenis Belanja Tertinggi**\n\n{top_expense} dengan total Rp {top_expense_value:,.0f}")
    
    with insight_col3:
        st.warning(f"📅 **Triwulan Terbaik**\n\nTW-{top_quarter} dengan realisasi Rp {top_quarter_value:,.0f}")

# === Tab 2: Realisasi Anggaran ===
with tab2:
    st.markdown("<div class='section-header'><h3>📊 Analisis Realisasi Anggaran</h3></div>", unsafe_allow_html=True)
    
    df_agg = df.groupby(['Tahun', 'Triwulan'])[['Anggaran', 'Realisasi']].sum().reset_index()
    df_agg['Label'] = df_agg['Tahun'].astype(str) + "-TW" + df_agg['Triwulan'].astype(str)
    df_agg['Efisiensi'] = (df_agg['Realisasi'] / df_agg['Anggaran'] * 100).round(1)
    
    # Enhanced bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Anggaran',
        x=df_agg['Label'],
        y=df_agg['Anggaran'],
        marker_color='lightblue',
        text=df_agg['Anggaran'].apply(lambda x: f'Rp {x/1e9:.1f}M'),
        textposition='outside'
    ))
    fig.add_trace(go.Bar(
        name='Realisasi',
        x=df_agg['Label'],
        y=df_agg['Realisasi'],
        marker_color='darkblue',
        text=df_agg['Realisasi'].apply(lambda x: f'Rp {x/1e9:.1f}M'),
        textposition='outside'
    ))
    
    fig.update_layout(
        title="💰 Perbandingan Anggaran vs Realisasi per Triwulan",
        xaxis_title="Periode",
        yaxis_title="Nilai (Rupiah)",
        barmode='group',
        template='plotly_white',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Efficiency trend
    fig_eff = px.line(
        df_agg, 
        x='Label', 
        y='Efisiensi',
        markers=True,
        title="📈 Tren Efisiensi Realisasi Anggaran (%)",
        color_discrete_sequence=['#e74c3c']
    )
    fig_eff.update_layout(template='plotly_white', yaxis_title="Efisiensi (%)")
    st.plotly_chart(fig_eff, use_container_width=True)
    
    # Summary table
    st.markdown("### 📋 Ringkasan Efisiensi per Periode")
    summary_df = df_agg[['Label', 'Anggaran', 'Realisasi', 'Efisiensi']].copy()
    summary_df['Anggaran'] = summary_df['Anggaran'].apply(lambda x: f"Rp {x:,.0f}")
    summary_df['Realisasi'] = summary_df['Realisasi'].apply(lambda x: f"Rp {x:,.0f}")
    summary_df['Efisiensi'] = summary_df['Efisiensi'].apply(lambda x: f"{x}%")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

# === Tab 3: Analisis Jenis Belanja ===
with tab3:
    st.markdown("<div class='section-header'><h3>🔍 Analisis Distribusi Jenis Belanja</h3></div>", unsafe_allow_html=True)

    # Overall distribution
    df_pie_total = df.groupby('Jenis Belanja')['Realisasi'].sum().reset_index()
    df_pie_total['Persentase'] = (df_pie_total['Realisasi'] / df_pie_total['Realisasi'].sum() * 100).round(1)
    
    fig_pie_total = px.pie(
        df_pie_total, 
        names='Jenis Belanja', 
        values='Realisasi',
        title="🥧 Distribusi Total Realisasi per Jenis Belanja (2023-2025)",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie_total.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie_total.update_layout(height=500)
    st.plotly_chart(fig_pie_total, use_container_width=True)

    # Year-by-year analysis
    for tahun in sorted(df['Tahun'].unique()):
        st.markdown(f"### 📅 Analisis Tahun {tahun}")
        
        df_tahun = df[df['Tahun'] == tahun]
        total_tahun = df_tahun['Realisasi'].sum()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            df_pie_tahun = df_tahun.groupby('Jenis Belanja')['Realisasi'].sum().reset_index()
            fig_pie_tahun = px.pie(
                df_pie_tahun, 
                names='Jenis Belanja', 
                values='Realisasi',
                title=f"Distribusi Realisasi Tahun {tahun}",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie_tahun.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie_tahun, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div class='info-box'>
                <h4>📊 Ringkasan {tahun}</h4>
                <p><b>Total Realisasi:</b><br>Rp {total_tahun:,.0f}</p>
                <p><b>Jenis Belanja Tertinggi:</b><br>{df_pie_tahun.loc[df_pie_tahun['Realisasi'].idxmax(), 'Jenis Belanja']}</p>
                <p><b>Nilai Tertinggi:</b><br>Rp {df_pie_tahun['Realisasi'].max():,.0f}</p>
            </div>
            """, unsafe_allow_html=True)

        # Quarterly breakdown
        st.markdown(f"#### 📊 Breakdown Triwulan {tahun}")
        triwulan_list = sorted(df_tahun['Triwulan'].unique())
        triwulan_cols = st.columns(len(triwulan_list))
        
        for i, tw in enumerate(triwulan_list):
            df_tw = df_tahun[df_tahun['Triwulan'] == tw].groupby('Jenis Belanja')[['Realisasi']].sum().reset_index()
            if not df_tw.empty:
                fig_tw = px.pie(
                    df_tw, 
                    names='Jenis Belanja', 
                    values='Realisasi',
                    title=f"TW-{tw}",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_tw.update_traces(textposition='inside', textinfo='percent')
                fig_tw.update_layout(height=300, showlegend=False)
                triwulan_cols[i].plotly_chart(fig_tw, use_container_width=True)

# === Tab 4: Prediksi ===
with tab4:
    st.markdown("<div class='section-header'><h3>🔮 Prediksi Realisasi Belanja</h3></div>", unsafe_allow_html=True)
    
    # Model training
    df_model = df.groupby(['Tahun', 'Triwulan', 'JenisEncoded'])[['Realisasi', 'Anggaran', 'Sisa Anggaran']].sum().reset_index()
    X = df_model[['Tahun', 'Triwulan', 'JenisEncoded', 'Anggaran', 'Sisa Anggaran']]
    y = df_model['Realisasi']

    model = LinearRegression()
    model.fit(X, y)
    
    # Model performance
    score = model.score(X, y)
    st.markdown(f"""
    <div class='info-box'>
        <h4>🤖 Informasi Model</h4>
        <p><b>Algorithm:</b> Linear Regression</p>
        <p><b>R² Score:</b> {score:.3f}</p>
        <p><b>Status:</b> {'✅ Model Baik' if score > 0.7 else '⚠️ Model Perlu Perbaikan'}</p>
    </div>
    """, unsafe_allow_html=True)

    # Prediction for Q3 & Q4 2025
    pred_data = []
    for tri in [3, 4]:
        for jenis in df['JenisEncoded'].unique():
            rata2_anggaran = df[df['JenisEncoded'] == jenis]['Anggaran'].mean()
            rata2_sisa = df[df['JenisEncoded'] == jenis]['Sisa Anggaran'].mean()
            pred_data.append({
                'Tahun': 2025,
                'Triwulan': tri,
                'JenisEncoded': jenis,
                'Anggaran': rata2_anggaran,
                'Sisa Anggaran': rata2_sisa
            })

    df_pred = pd.DataFrame(pred_data)
    df_pred['Prediksi'] = model.predict(df_pred[['Tahun', 'Triwulan', 'JenisEncoded', 'Anggaran', 'Sisa Anggaran']])
    df_pred['Jenis Belanja'] = le_jenis.inverse_transform(df_pred['JenisEncoded'])
    df_pred['Label'] = df_pred['Tahun'].astype(str) + "-TW" + df_pred['Triwulan'].astype(str)

    # Display predictions
    st.markdown("### 📊 Hasil Prediksi TW III & IV 2025")
    
    # Format the prediction table
    display_pred = df_pred[['Label', 'Jenis Belanja', 'Anggaran', 'Sisa Anggaran', 'Prediksi']].copy()
    display_pred['Anggaran'] = display_pred['Anggaran'].apply(lambda x: f"Rp {x:,.0f}")
    display_pred['Sisa Anggaran'] = display_pred['Sisa Anggaran'].apply(lambda x: f"Rp {x:,.0f}")
    display_pred['Prediksi'] = display_pred['Prediksi'].apply(lambda x: f"Rp {x:,.0f}")
    
    st.dataframe(display_pred, use_container_width=True, hide_index=True)

    # Prediction visualization
    fig_pred = px.bar(
        df_pred, 
        x='Label', 
        y='Prediksi', 
        color='Jenis Belanja',
        title="📈 Prediksi Realisasi per Jenis Belanja",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_pred.update_layout(template='plotly_white', height=500)
    st.plotly_chart(fig_pred, use_container_width=True)

    # Download functionality
    buffer = io.BytesIO()
    df_pred.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="💾 Unduh Hasil Prediksi (Excel)",
        data=buffer,
        file_name=f"prediksi_TW3_TW4_2025_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Klik untuk mengunduh hasil prediksi dalam format Excel"
    )
    
    # Prediction summary
    total_pred_tw3 = df_pred[df_pred['Triwulan'] == 3]['Prediksi'].sum()
    total_pred_tw4 = df_pred[df_pred['Triwulan'] == 4]['Prediksi'].sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"📊 **Prediksi TW III 2025**\n\nRp {total_pred_tw3:,.0f}")
    with col2:
        st.info(f"📊 **Prediksi TW IV 2025**\n\nRp {total_pred_tw4:,.0f}")

# === Tab 5: Sisa Anggaran ===
with tab5:
    st.markdown("<div class='section-header'><h3>💸 Analisis Sisa Anggaran</h3></div>", unsafe_allow_html=True)
    
    df_sisa = df.groupby('Jenis Belanja')[['Sisa Anggaran', 'Anggaran', 'Realisasi']].sum().reset_index()
    df_sisa['Persentase_Sisa'] = (df_sisa['Sisa Anggaran'] / df_sisa['Anggaran'] * 100).round(1)
    df_sisa = df_sisa.sort_values('Sisa Anggaran', ascending=False)
    
    # Bar chart for remaining budget
    fig_sisa = px.bar(
        df_sisa, 
        x='Jenis Belanja', 
        y='Sisa Anggaran',
        title="💰 Total Sisa Anggaran per Jenis Belanja",
        color='Persentase_Sisa',
        color_continuous_scale='RdYlBu_r',
        text='Sisa Anggaran'
    )
    fig_sisa.update_traces(texttemplate='Rp %{text:,.0f}', textposition='outside')
    fig_sisa.update_layout(template='plotly_white', height=500)
    st.plotly_chart(fig_sisa, use_container_width=True)
    
    # Efficiency analysis
    st.markdown("### 📊 Analisis Efisiensi Anggaran")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Most efficient
        most_efficient = df_sisa.loc[df_sisa['Persentase_Sisa'].idxmin()]
        st.success(f"""
        **🏆 Paling Efisien**
        
        **{most_efficient['Jenis Belanja']}**
        
        Sisa: {most_efficient['Persentase_Sisa']}%
        
        Rp {most_efficient['Sisa Anggaran']:,.0f}
        """)
    
    with col2:
        # Least efficient
        least_efficient = df_sisa.loc[df_sisa['Persentase_Sisa'].idxmax()]
        st.error(f"""
        **⚠️ Perlu Perhatian**
        
        **{least_efficient['Jenis Belanja']}**
        
        Sisa: {least_efficient['Persentase_Sisa']}%
        
        Rp {least_efficient['Sisa Anggaran']:,.0f}
        """)
    
    # Detailed table
    st.markdown("### 📋 Detail Sisa Anggaran")
    display_sisa = df_sisa.copy()
    display_sisa['Anggaran'] = display_sisa['Anggaran'].apply(lambda x: f"Rp {x:,.0f}")
    display_sisa['Realisasi'] = display_sisa['Realisasi'].apply(lambda x: f"Rp {x:,.0f}")
    display_sisa['Sisa Anggaran'] = display_sisa['Sisa Anggaran'].apply(lambda x: f"Rp {x:,.0f}")
    display_sisa['Persentase_Sisa'] = display_sisa['Persentase_Sisa'].apply(lambda x: f"{x}%")
    
    st.dataframe(display_sisa, use_container_width=True, hide_index=True)

# === Tab 6: Eksplorasi Data ===
with tab6:
    st.markdown("<div class='section-header'><h3>📍 Eksplorasi Data Interaktif</h3></div>", unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        jenis_opsi = df['Jenis Belanja'].unique().tolist()
        pilihan_jenis = st.multiselect(
            "🔍 Pilih Jenis Belanja:", 
            options=jenis_opsi, 
            default=jenis_opsi,
            help="Pilih satu atau lebih jenis belanja untuk dianalisis"
        )
    
    with col2:
        pilihan_tahun = st.selectbox(
            "📅 Pilih Tahun:", 
            sorted(df['Tahun'].unique(), reverse=True),
            help="Pilih tahun untuk analisis"
        )
    
    with col3:
        # Get available quarters for selected year
        available_quarters = sorted(df[df['Tahun'] == pilihan_tahun]['Triwulan'].unique())
        pilihan_triwulan = st.multiselect(
            "📊 Pilih Triwulan:",
            options=available_quarters,
            default=available_quarters,
            help="Pilih triwulan untuk analisis"
        )

    # Debug information (will be hidden in production)
    with st.expander("🔍 Debug Info - Data Availability", expanded=False):
        st.write("**Available data summary:**")
        st.write(f"- Total records: {len(df)}")
        st.write(f"- Available years: {sorted(df['Tahun'].unique())}")
        st.write(f"- Available quarters for {pilihan_tahun}: {sorted(df[df['Tahun'] == pilihan_tahun]['Triwulan'].unique())}")
        st.write(f"- Available expense types: {df['Jenis Belanja'].unique()}")
        st.write(f"- Selected expense types: {pilihan_jenis}")
        st.write(f"- Selected quarters: {pilihan_triwulan}")

    # Apply filters with more defensive approach
    df_filtered = df.copy()
    
    # Apply filters step by step
    if pilihan_jenis:
        df_filtered = df_filtered[df_filtered['Jenis Belanja'].isin(pilihan_jenis)]
    
    df_filtered = df_filtered[df_filtered['Tahun'] == pilihan_tahun]
    
    if pilihan_triwulan:
        df_filtered = df_filtered[df_filtered['Triwulan'].isin(pilihan_triwulan)]
    
    if df_filtered.empty:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih. Silakan ubah filter.")
        
        # Show available data to help user understand the issue
        st.info("💡 **Tip**: Coba pilih filter yang berbeda atau reset ke default")
        
        # Show sample data structure
        sample_data = df.head(10)[['Tahun', 'Triwulan', 'Jenis Belanja', 'Anggaran', 'Realisasi']]
        st.write("**Sample data yang tersedia:**")
        st.dataframe(sample_data, use_container_width=True)
        
    else:
        # Show current filter results
        st.success(f"✅ Menampilkan {len(df_filtered)} records dengan filter yang dipilih")
        
        # Summary metrics for filtered data
        st.markdown("### 📊 Ringkasan Data Terpilih")
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        filtered_anggaran = df_filtered['Anggaran'].sum()
        filtered_realisasi = df_filtered['Realisasi'].sum()
        filtered_efisiensi = (filtered_realisasi / filtered_anggaran * 100) if filtered_anggaran > 0 else 0
        filtered_records = len(df_filtered)
        
        with metric_col1:
            st.metric("📋 Total Records", f"{filtered_records:,}")
        with metric_col2:
            st.metric("💰 Anggaran", f"Rp {filtered_anggaran:,.0f}")
        with metric_col3:
            st.metric("✅ Realisasi", f"Rp {filtered_realisasi:,.0f}")
        with metric_col4:
            st.metric("📈 Efisiensi", f"{filtered_efisiensi:.1f}%")
        
        # Interactive scatter plot
        st.markdown("### 🔍 Scatter Plot: Anggaran vs Realisasi")
        
        fig_scatter = px.scatter(
            df_filtered,
            x='Anggaran',
            y='Realisasi',
            size='Sisa Anggaran',
            color='Jenis Belanja',
            hover_data=['Tahun', 'Triwulan'],
            title=f"💡 Analisis Anggaran vs Realisasi - {pilihan_tahun}",
            size_max=50,
            opacity=0.7
        )
        
        # Add diagonal line (perfect efficiency)
        max_val = max(df_filtered['Anggaran'].max(), df_filtered['Realisasi'].max())
        fig_scatter.add_shape(
            type="line",
            x0=0, y0=0, x1=max_val, y1=max_val,
            line=dict(color="red", width=2, dash="dash"),
            name="Efisiensi 100%"
        )
        
        fig_scatter.update_layout(
            template='plotly_white',
            height=600,
            xaxis_title="Anggaran (Rp)",
            yaxis_title="Realisasi (Rp)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Performance analysis
        st.markdown("### 📈 Analisis Performa per Triwulan")
        
        df_performance = df_filtered.groupby('Triwulan').agg({
            'Anggaran': 'sum',
            'Realisasi': 'sum',
            'Sisa Anggaran': 'sum'
        }).reset_index()
        df_performance['Efisiensi'] = (df_performance['Realisasi'] / df_performance['Anggaran'] * 100).round(1)
        
        fig_performance = go.Figure()
        
        # Add bars for budget and realization
        fig_performance.add_trace(go.Bar(
            name='Anggaran',
            x=df_performance['Triwulan'],
            y=df_performance['Anggaran'],
            marker_color='lightcoral',
            yaxis='y',
            offsetgroup=1
        ))
        
        fig_performance.add_trace(go.Bar(
            name='Realisasi',
            x=df_performance['Triwulan'],
            y=df_performance['Realisasi'],
            marker_color='lightblue',
            yaxis='y',
            offsetgroup=2
        ))
        
        # Add line for efficiency
        fig_performance.add_trace(go.Scatter(
            name='Efisiensi (%)',
            x=df_performance['Triwulan'],
            y=df_performance['Efisiensi'],
            mode='lines+markers',
            marker_color='green',
            yaxis='y2',
            line=dict(width=3)
        ))
        
        fig_performance.update_layout(
            title=f"📊 Performa Anggaran & Efisiensi per Triwulan - {pilihan_tahun}",
            xaxis_title="Triwulan",
            yaxis=dict(title="Nilai (Rupiah)", side="left"),
            yaxis2=dict(title="Efisiensi (%)", side="right", overlaying="y"),
            template='plotly_white',
            height=500,
            barmode='group'
        )
        st.plotly_chart(fig_performance, use_container_width=True)
        
        # Detailed data table
        st.markdown("### 📋 Detail Data Terpilih")
        
        # Format data for display
        display_data = df_filtered[['Tanggal', 'Tahun', 'Triwulan', 'Jenis Belanja', 'Anggaran', 'Realisasi', 'Sisa Anggaran']].copy()
        display_data['Efisiensi (%)'] = (display_data['Realisasi'] / display_data['Anggaran'] * 100).round(1)
        display_data['Anggaran'] = display_data['Anggaran'].apply(lambda x: f"Rp {x:,.0f}")
        display_data['Realisasi'] = display_data['Realisasi'].apply(lambda x: f"Rp {x:,.0f}")
        display_data['Sisa Anggaran'] = display_data['Sisa Anggaran'].apply(lambda x: f"Rp {x:,.0f}")
        
        st.dataframe(
            display_data, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Tanggal": st.column_config.DateColumn("📅 Tanggal"),
                "Tahun": st.column_config.NumberColumn("📆 Tahun"),
                "Triwulan": st.column_config.TextColumn("📊 Triwulan"),
                "Jenis Belanja": st.column_config.TextColumn("💼 Jenis Belanja"),
                "Anggaran": st.column_config.TextColumn("💰 Anggaran"),
                "Realisasi": st.column_config.TextColumn("✅ Realisasi"),
                "Sisa Anggaran": st.column_config.TextColumn("💸 Sisa Anggaran"),
                "Efisiensi (%)": st.column_config.NumberColumn("📈 Efisiensi (%)", format="%.1f%%")
            }
        )
        
        # Export filtered data
        if st.button("📥 Export Data Terpilih ke Excel", type="primary"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_filtered.to_excel(writer, sheet_name='Data_Filtered', index=False)
                df_performance.to_excel(writer, sheet_name='Performance_Summary', index=False)
            
            output.seek(0)
            st.download_button(
                label="💾 Unduh File Excel",
                data=output,
                file_name=f"data_eksplorasi_{pilihan_tahun}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# === Footer ===
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 10px; margin-top: 2rem;'>
    <p style='margin: 0; color: #6c757d;'>
        📊 <b>Dashboard Realisasi Belanja DJPb</b> | 
        🏛️ Kementerian Keuangan Republik Indonesia | 
        📅 {current_year}
    </p>
    <p style='margin: 0.5rem 0 0 0; color: #6c757d; font-size: 0.9rem;'>
        💡 Dikembangkan dengan Streamlit & Plotly untuk analisis data yang lebih interaktif
    </p>
</div>
""".format(current_year=datetime.now().year), unsafe_allow_html=True)
