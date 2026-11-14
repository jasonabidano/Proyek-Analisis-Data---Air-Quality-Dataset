import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Beijing Air Quality Dashboard (2013-2017)",
    page_icon="🌤️",
    layout="wide"
)

@st.cache_data
def load_data():
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "main_data.csv"),
        "dashboard/main_data.csv",
        "main_data.csv"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['date'] = pd.to_datetime(df['date'])
            return df
    st.error("File main_data.csv tidak ditemukan. Pastikan main_data.csv berada di folder yang sama dengan dashboard.py.")
    st.stop()

df = load_data()

# Sidebar Filter
with st.sidebar:
    st.title("🌍 Beijing Air Quality")
    st.markdown("**Oleh:** Jason Adriel Gerard Abidano  \n**Dataset:** PRSA Multi-Site (2013–2017)")
    st.divider()

    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    date_range = st.date_input(
        "📅 Rentang Waktu Analisis",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    zones = ["Semua Zona"] + sorted(df['station_zone'].unique().tolist())
    selected_zone = st.selectbox("🏙️ Filter Zona Wilayah", zones)

    if selected_zone == "Semua Zona":
        available_stations = sorted(df['station'].unique().tolist())
    else:
        available_stations = sorted(df[df['station_zone'] == selected_zone]['station'].unique().tolist())

    selected_stations = st.multiselect(
        "📍 Pilih Stasiun Pemantauan",
        options=available_stations,
        default=available_stations
    )

    st.divider()
    st.caption("Dashboard Interaktif Proyek Analisis Data Dicoding")

# Filter dataset
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_dt, end_dt = pd.to_datetime(min_date), pd.to_datetime(max_date)

filtered_df = df[
    (df['date'] >= start_dt) &
    (df['date'] <= end_dt) &
    (df['station'].isin(selected_stations if selected_stations else available_stations))
].copy()

# Header Utama
st.title("🌤️ Beijing Multi-Site Air Quality Analytics Dashboard (2013–2017)")
st.markdown(
    "Dashboard ini menyajikan hasil eksplorasi kualitas udara di **12 stasiun pemantauan Beijing** "
    "untuk menjawab pertanyaan bisnis terkait **perbandingan spasial stasiun**, **pola fluktuasi musiman**, "
    "**dampak faktor meteorologi**, serta **analisis lanjutan (Clustering AQI & Geospatial Analysis)**."
)

# KPI Metrics Row
col1, col2, col3, col4 = st.columns(4)
avg_pm25 = filtered_df['PM25'].mean()
avg_pm10 = filtered_df['PM10'].mean()
unhealthy_days_pct = (filtered_df['PM25'] > 55.4).mean() * 100
worst_station = filtered_df.groupby('station')['PM25'].mean().idxmax() if not filtered_df.empty else "-"

col1.metric("Rata-rata PM2.5", f"{avg_pm25:.2f} µg/m³", "Batas AQI Good EPA: 12.0 µg/m³", delta_color="inverse")
col2.metric("Rata-rata PM10", f"{avg_pm10:.2f} µg/m³", "Batas AQI Moderate EPA: 35.4 µg/m³", delta_color="inverse")
col3.metric("Proporsi Hari Tidak Sehat", f"{unhealthy_days_pct:.1f}%", "PM2.5 > 55.4 µg/m³", delta_color="inverse")
col4.metric("Stasiun Polusi Tertinggi", worst_station, "Berdasarkan filter aktif")

st.divider()

# Tab Navigasi Visualisasi
tab1, tab2, tab3, tab4 = st.tabs([
    "🏙️ 1. Perbandingan Stasiun & Zona",
    "📈 2. Pola Musiman & Tren Waktu",
    "💨 3. Faktor Meteorologi & Korelasi",
    "🗺️ 4. Analisis Lanjutan (Clustering & Geospasial)"
])

with tab1:
    st.subheader("Perbandingan Tingkat Polusi PM2.5 & PM10 Antar-Stasiun (Pertanyaan 1)")
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st_rank = filtered_df.groupby(['station', 'station_zone'], as_index=False)['PM25'].mean().sort_values('PM25', ascending=True)
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ['#1f77b4' if z == 'Suburban (Pinggiran/Utara)' else '#d62728' for z in st_rank['station_zone']]
        bars = ax.barh(st_rank['station'], st_rank['PM25'], color=colors)
        ax.axvline(avg_pm25, color='#333333', linestyle='--', label=f"Rata-rata ({avg_pm25:.1f} µg/m³)")
        for b in bars:
            w = b.get_width()
            ax.text(w + 1, b.get_y() + b.get_height()/2, f"{w:.1f}", va='center', fontsize=9, fontweight='bold')
        ax.set_xlim(0, max(st_rank['PM25'].max() * 1.18, 100))
        ax.set_xlabel("Rata-rata PM2.5 (µg/m³)")
        ax.set_title("Peringkat Stasiun Berdasarkan Rata-rata PM2.5")
        ax.legend(loc="lower right")
        st.pyplot(fig)

    with c2:
        yr_zone = filtered_df.groupby(['year', 'station_zone'], as_index=False)['PM25'].mean()
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        sns.lineplot(
            data=yr_zone, x='year', y='PM25', hue='station_zone',
            marker='o', linewidth=2.5,
            palette={'Urban (Pusat Kota)': '#d62728', 'Suburban (Pinggiran/Utara)': '#1f77b4'},
            ax=ax2
        )
        ax2.set_title("Tren Tahunan PM2.5: Urban vs Suburban")
        ax2.set_xlabel("Tahun")
        ax2.set_ylabel("Rata-rata PM2.5 (µg/m³)")
        st.pyplot(fig2)

with tab2:
    st.subheader("Pola Fluktuasi Bulanan & Musiman Polutan Udara (Pertanyaan 2)")
    c1, c2 = st.columns(2)

    with c1:
        m_df = filtered_df.groupby('month', as_index=False)[['PM25', 'PM10', 'O3', 'NO2']].mean()
        fig3, ax3 = plt.subplots(figsize=(7.5, 4.8))
        ax3.plot(m_df['month'], m_df['PM25'], marker='o', linewidth=2.5, color='#d62728', label='PM2.5')
        ax3.plot(m_df['month'], m_df['PM10'], marker='s', linewidth=2.0, color='#ff7f0e', label='PM10')
        ax3.plot(m_df['month'], m_df['O3'], marker='^', linewidth=2.0, color='#2ca02c', label='O3 (Ozon)')
        ax3.plot(m_df['month'], m_df['NO2'], marker='d', linewidth=1.8, color='#9467bd', label='NO2')
        ax3.set_xticks(range(1, 13))
        ax3.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'])
        ax3.set_title("Siklus Bulanan PM2.5, PM10, NO2, dan O3")
        ax3.set_xlabel("Bulan")
        ax3.set_ylabel("Konsentrasi (µg/m³)")
        ax3.legend()
        st.pyplot(fig3)

    with c2:
        season_order = ['Winter (Des-Feb)', 'Autumn (Sep-Nov)', 'Spring (Mar-Mei)', 'Summer (Jun-Agu)']
        s_df = filtered_df.groupby('season', as_index=False)[['PM25', 'PM10', 'O3']].mean()
        s_df['season'] = pd.Categorical(s_df['season'], categories=season_order, ordered=True)
        s_df = s_df.sort_values('season')

        fig4, ax4 = plt.subplots(figsize=(7.5, 4.8))
        x = np.arange(len(s_df))
        width = 0.26
        ax4.bar(x - width, s_df['PM25'], width, label='PM2.5', color='#d62728')
        ax4.bar(x, s_df['PM10'], width, label='PM10', color='#ff7f0e')
        ax4.bar(x + width, s_df['O3'], width, label='O3 (Ozon)', color='#2ca02c')
        ax4.set_xticks(x)
        ax4.set_xticklabels(s_df['season'], rotation=12)
        ax4.set_title("Perbandingan Rata-rata Polutan Berdasarkan Musim")
        ax4.set_ylabel("Konsentrasi (µg/m³)")
        ax4.legend()
        st.pyplot(fig4)

with tab3:
    st.subheader("Pengaruh Faktor Meteorologi terhadap Konsentrasi PM2.5 (Pertanyaan 3)")
    c1, c2 = st.columns(2)

    with c1:
        num_cols = ['PM25', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
        fig5, ax5 = plt.subplots(figsize=(7.5, 5.5))
        sns.heatmap(filtered_df[num_cols].corr(), annot=True, fmt=".2f", cmap='RdBu_r', vmin=-1, vmax=1, ax=ax5, annot_kws={'size': 8})
        ax5.set_title("Matriks Korelasi Polutan & Parameter Cuaca")
        st.pyplot(fig5)

    with c2:
        w_order = ['Calm (<=1.0 m/s)', 'Light Breeze (1.1-2.5 m/s)', 'Moderate Wind (2.6-4.0 m/s)', 'Strong Wind (>4.0 m/s)']
        w_df = filtered_df.groupby('wind_category', as_index=False)['PM25'].mean()
        w_df['wind_category'] = pd.Categorical(w_df['wind_category'], categories=w_order, ordered=True)
        w_df = w_df.sort_values('wind_category')

        fig6, ax6 = plt.subplots(figsize=(7.5, 5.5))
        wbars = ax6.bar(w_df['wind_category'].astype(str), w_df['PM25'], color=['#b2182b', '#ef8a62', '#67a9cf', '#2166ac'])
        for b in wbars:
            h = b.get_height()
            if not np.isnan(h):
                ax6.text(b.get_x() + b.get_width()/2, h + 1.5, f"{h:.1f}", ha='center', fontweight='bold')
        ax6.set_ylim(0, max(w_df['PM25'].max() * 1.18, 110))
        ax6.set_title("Rata-rata PM2.5 Berdasarkan Kategori Kecepatan Angin (WSPM)")
        ax6.set_ylabel("Rata-rata PM2.5 (µg/m³)")
        ax6.tick_params(axis='x', rotation=15)
        st.pyplot(fig6)

with tab4:
    st.subheader("Analisis Lanjutan: Clustering (Binning AQI) & Peta Geospasial Stasiun")
    c1, c2 = st.columns(2)

    with c1:
        aqi_order = [
            'Good (0-12)', 'Moderate (12.1-35.4)', 'Unhealthy for Sensitive (35.5-55.4)',
            'Unhealthy (55.5-150.4)', 'Very Unhealthy (150.5-250.4)', 'Hazardous (>250.4)'
        ]
        aqi_pct = (filtered_df['aqi_category'].value_counts(normalize=True).reindex(aqi_order).fillna(0) * 100)
        fig7, ax7 = plt.subplots(figsize=(7.5, 5))
        abars = ax7.barh(aqi_pct.index, aqi_pct.values, color=['#2ca02c', '#f1c40f', '#e67e22', '#e74c3c', '#8e44ad', '#7f0000'])
        for b in abars:
            w = b.get_width()
            ax7.text(w + 0.5, b.get_y() + b.get_height()/2, f"{w:.1f}%", va='center', fontweight='bold')
        ax7.set_xlim(0, max(aqi_pct.max() * 1.2, 45))
        ax7.invert_yaxis()
        ax7.set_title("Distribusi Kategori Kualitas Udara (Binning PM2.5)")
        ax7.set_xlabel("Proporsi Hari Observasi (%)")
        st.pyplot(fig7)

    with c2:
        geo_df = filtered_df.groupby(['station', 'station_zone', 'lat', 'lon'], as_index=False)['PM25'].mean()
        fig8, ax8 = plt.subplots(figsize=(7.5, 5))
        sc = ax8.scatter(
            geo_df['lon'], geo_df['lat'], c=geo_df['PM25'], cmap='YlOrRd',
            s=geo_df['PM25']*4.2, edgecolors='black', linewidth=1.2, alpha=0.9
        )
        for _, r in geo_df.iterrows():
            ax8.annotate(f"{r['station']}\n({r['PM25']:.1f})", (r['lon'], r['lat']),
                         textcoords="offset points", xytext=(0, 7), ha='center', fontsize=8, fontweight='bold')
        plt.colorbar(sc, ax=ax8, label="Rata-rata PM2.5 (µg/m³)")
        ax8.set_xlim(116.10, 116.75)
        ax8.set_ylim(39.82, 40.39)
        ax8.set_title("Distribusi Geospasial 12 Stasiun Pemantauan Beijing")
        ax8.set_xlabel("Longitude (°E)")
        ax8.set_ylabel("Latitude (°N)")
        st.pyplot(fig8)

    st.markdown("#### 🗺️ Peta Interaktif Lokasi Stasiun Pemantauan di Beijing")
    st.map(geo_df[['lat', 'lon']], zoom=9)
