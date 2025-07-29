import streamlit as st
import pandas as pd
import plotly.express as px
import io
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

st.set_page_config(page_title="Dashboard Anggaran & Realisasi Belanja", layout="wide")

# === Logo Header ===
st.markdown("""
    <div style='display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;'>
        <img src='https://raw.githubusercontent.com/dinawseptiana/project-realisasi-belanja/main/logo.png' width='140'/>
        <div style='flex: 1; min-width: 250px;'>
            <h4 style='margin: 0; font-size: 1.1rem;'>💼 Analisis Anggaran dan Realisasi Belanja Direktorat Jenderal Perbendaharaan (DJPb) Kementerian Keuangan</h4>
        </div>
    </div>
    <hr style='margin-top: 10px; margin-bottom: 20px;'>
""", unsafe_allow_html=True)

# === Load data dari GitHub ===
URL = "https://raw.githubusercontent.com/dinawseptiana/project-realisasi-belanja/main/data/RealisasiBelanja_cleaned.xlsx"
df = pd.read_excel(URL)

# === Preprocessing ===
df = df.dropna(subset=['Realisasi', 'Anggaran'])
df['Realisasi'] = df['Realisasi'].astype(str).str.replace(",", "").astype(float)
df['Anggaran'] = df['Anggaran'].astype(str).str.replace(",", "").astype(float)
df['Sisa Anggaran'] = df['Anggaran'] - df['Realisasi']
df['Tanggal'] = pd.to_datetime(df['Tanggal'])
df['TriwulanAngka'] = df['Triwulan'].replace({'I': 1, 'II': 2, 'III': 3, 'IV': 4})

le_jenis = LabelEncoder()
df['JenisEncoded'] = le_jenis.fit_transform(df['Jenis Belanja'])

# === KPI ===
total_anggaran = df['Anggaran'].sum()
total_realisasi = df['Realisasi'].sum()
rata2_persen = df['Realisasi'].sum() / df['Anggaran'].sum() * 100
total_sisa = df['Sisa Anggaran'].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Anggaran", f"Rp {total_anggaran:,.0f}")
col2.metric("Total Realisasi", f"Rp {total_realisasi:,.0f}")
col3.metric("Rata-rata % Realisasi", f"{rata2_persen:.2f}%")
col4.metric("Total Sisa Anggaran", f"Rp {total_sisa:,.0f}")

# === Tab Layout ===
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Beranda", "📊 Realisasi Anggaran", "🔍 Analisis Jenis Belanja", "🔮 Prediksi", "💸 Sisa Anggaran", "📍 Eksplorasi Data"
])

# === Tab 1: Beranda ===
with tab1:
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 25px; border-radius: 12px;'>
        <h3 style='color: #004085;'>📊 Selamat Datang di Dashboard Realisasi Belanja</h3>
        <p style='font-size: 16px; color: black;'>
            Dashboard ini dikembangkan untuk menyajikan dan menganalisis data realisasi belanja berdasarkan jenis belanja Direktorat Jenderal Perbendaharaan (DJPb) tahun 2023 - 2025.</b>
            Dengan antarmuka yang <i>user-friendly</i> dan interaktif, pengguna dapat dengan mudah:
        <ul style='font-size: 16px; color: black;'>
            \n✅ Melihat tren realisasi & anggaran berdasarkan triwulan</li>
            \n✅ Menjelajahi distribusi realisasi berdasarkan jenis belanja</li>
            \n✅ Mengakses prediksi belanja untuk Triwulan III & IV Tahun 2025</li>
            \n✅ Mengunduh data hasil prediksi dalam format Excel</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

# === Tab 2: Realisasi Anggaran ===
with tab2:
    df_agg = df.groupby(['Tahun', 'Triwulan'])[['Anggaran', 'Realisasi']].sum().reset_index()
    df_agg['Label'] = df_agg['Tahun'].astype(str) + "-TW" + df_agg['Triwulan'].astype(str)
    fig = px.bar(df_agg, x='Label', y=['Anggaran', 'Realisasi'], barmode='group', title="📊 Anggaran vs Realisasi per Triwulan")
    st.plotly_chart(fig, use_container_width=True)

    fig_line = px.line(df_agg, x='Triwulan', y='Realisasi', color='Tahun', markers=True,
                       title="📈 Tren Realisasi per Triwulan Tiap Tahun")
    st.plotly_chart(fig_line, use_container_width=True)
    
# === Tab 3: Analisis Jenis Belanja ===
with tab3:
    st.subheader("Distribusi Realisasi per Jenis Belanja")

    # Diagram lingkaran total
    df_pie_total = df.groupby('Jenis Belanja')['Realisasi'].sum().reset_index()
    fig_pie_total = px.pie(df_pie_total, names='Jenis Belanja', values='Realisasi', title="Persentase Total Realisasi per Jenis Belanja (2023-2025)")
    st.plotly_chart(fig_pie_total, use_container_width=True)

    # Diagram lingkaran per tahun
    for tahun in sorted(df['Tahun'].unique()):
        st.markdown(f"### Persentase Realisasi Jenis Belanja Tahun {tahun}")
        df_pie_tahun = df[df['Tahun'] == tahun].groupby('Jenis Belanja')['Realisasi'].sum().reset_index()
        fig_pie_tahun = px.pie(df_pie_tahun, names='Jenis Belanja', values='Realisasi', title=f"Persentase Realisasi Jenis Belanja Tahun {tahun}")
        st.plotly_chart(fig_pie_tahun, use_container_width=True)

        # Diagram lingkaran per triwulan (4 untuk 2023 dan 2024, 2 untuk 2025)
        df_triwulan = df[df['Tahun'] == tahun]
        triwulan_list = sorted(df_triwulan['Triwulan'].unique())

        triwulan_cols = st.columns(len(triwulan_list))
        for i, tw in enumerate(triwulan_list):
            df_tw = df_triwulan[df_triwulan['Triwulan'] == tw].groupby('Jenis Belanja')[['Realisasi']].sum().reset_index()
            fig_tw = px.pie(df_tw, names='Jenis Belanja', values='Realisasi', title=f"TW-{tw} Tahun {tahun}")
            triwulan_cols[i].plotly_chart(fig_tw, use_container_width=True)

        total = df_triwulan['Realisasi'].sum()
        st.markdown(f"**Total Realisasi Tahun {tahun}: Rp {total:,.0f}**")

# === Tab 4: Prediksi ===
with tab4:
    df_model = df.groupby(['Tahun', 'Triwulan', 'JenisEncoded'])[['Realisasi', 'Anggaran', 'Sisa Anggaran']].sum().reset_index()
    X = df_model[['Tahun', 'Triwulan', 'JenisEncoded', 'Anggaran', 'Sisa Anggaran']]
    y = df_model['Realisasi']

    model = LinearRegression()
    model.fit(X, y)

    # Prediksi TW 3 & 4 2025
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

    st.subheader("Prediksi Realisasi Triwulan III & IV Tahun 2025")
    st.dataframe(df_pred[['Label', 'Jenis Belanja', 'Anggaran', 'Sisa Anggaran', 'Prediksi']].round(0))

    fig_pred = px.bar(df_pred, x='Label', y='Prediksi', color='Jenis Belanja', title="Prediksi Realisasi per Jenis Belanja")
    st.plotly_chart(fig_pred, use_container_width=True)

    buffer = io.BytesIO()
    df_pred.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="💾 Unduh Hasil Prediksi (Excel)",
        data=buffer,
        file_name="prediksi_TW3_TW4_2025.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# === Tab 5: Sisa Anggaran ===
with tab5:
    df_sisa = df.groupby('Jenis Belanja')[['Sisa Anggaran']].sum().reset_index()
    fig_sisa = px.bar(df_sisa, x='Jenis Belanja', y='Sisa Anggaran', title="💸 Total Sisa Anggaran per Jenis Belanja")
    st.plotly_chart(fig_sisa, use_container_width=True)

# === Tab 6: Interaktif ===
with tab6:
    jenis_opsi = df['Jenis Belanja'].unique().tolist()
    pilihan_jenis = st.multiselect("Pilih Jenis Belanja:", options=jenis_opsi, default=jenis_opsi)
    pilihan_tahun = st.selectbox("Pilih Tahun:", sorted(df['Tahun'].unique(), reverse=True))

    df_filtered = df[(df['Jenis Belanja'].isin(pilihan_jenis)) & (df['Tahun'] == pilihan_tahun)]

    fig_int = px.scatter(
        df_filtered,
        x='Anggaran',
        y='Realisasi',
        size='Sisa Anggaran',
        color='Jenis Belanja',
        hover_data=['Tahun', 'Triwulan'],
        title="🕹️ Anggaran vs Realisasi"
    )
    st.plotly_chart(fig_int, use_container_width=True)
