import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency



sns.set(style='dark')

# Helper functions untuk bike-sharing data
def create_daily_rentals_df(df):
    # Pastikan menggunakan kolom yang ada di all_df
    daily_rentals = df.resample('D', on='dteday').agg({
        'casual_day': 'sum',
        'registered_day': 'sum',
        'cnt_day': 'sum'
    }).reset_index()
    return daily_rentals

def create_hourly_rentals_df(df):
    hourly_rentals = df.groupby('hr').agg({
        'casual_hour': 'mean',
        'registered_hour': 'mean',
        'cnt_hour': 'mean'
    }).reset_index()
    return hourly_rentals

def create_weather_impact_df(df):
    weather_impact = df.groupby('weathersit_day').agg({
        'cnt_day': 'mean',
        'temp_day': 'mean',
        'hum_day': 'mean'
    }).reset_index()
    return weather_impact

def create_seasonal_analysis_df(df):
    season_analysis = df.groupby('season_day').agg({
        'casual_day': 'sum',
        'registered_day': 'sum',
        'cnt_day': 'sum'
    }).reset_index()
    return season_analysis

# Load data
all_df = pd.read_csv("all_data.csv")
all_df['dteday'] = pd.to_datetime(all_df['dteday'])

# Sidebar filter
min_date = all_df['dteday'].min().date()
max_date = all_df['dteday'].max().date()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data
main_df = all_df[(all_df['dteday'].dt.date >= start_date) & (all_df['dteday'].dt.date <= end_date)]

# Prepare dataframes (seperti daily_rentals, hourly_rentals, dll.)
daily_rentals = create_daily_rentals_df(main_df)
hourly_rentals = create_hourly_rentals_df(main_df)
weather_impact = create_weather_impact_df(main_df)
season_analysis = create_seasonal_analysis_df(main_df)

# Jika belum ada, gunakan main_df sebagai merged_df
merged_df = main_df.copy()

# Dashboard header
st.header('Bike Sharing Analytics Dashboard 🚴')

# 1. Daily Rentals Overview
st.subheader('Daily Rentals Trend')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Casual", value=f"{daily_rentals['casual_day'].sum():,}")
with col2:
    st.metric("Total Registered", value=f"{daily_rentals['registered_day'].sum():,}")
with col3:
    st.metric("Peak Day", value=daily_rentals.loc[daily_rentals['cnt_day'].idxmax(), 'dteday'].strftime('%d %b %Y'))

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(daily_rentals['dteday'], daily_rentals['cnt_day'], color='#90CAF9')
ax.set_title("Total Peminjaman Harian", fontsize=20)
ax.set_xlabel("Tanggal")
ax.set_ylabel("Total Peminjaman")
st.pyplot(fig)

# 2. Hourly Pattern Analysis (Casual vs Registered)
st.subheader('Rata-Rata Peminjaman per Jam (Casual vs Registered)')
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=hourly_rentals, x='hr', y='casual_hour', label="Casual", color='steelblue', marker='o', ax=ax)
sns.lineplot(data=hourly_rentals, x='hr', y='registered_hour', label="Registered", color='darkorange', marker='o', ax=ax)
ax.set_title("Rata-Rata Peminjaman per Jam (Casual vs Registered)")
ax.set_xlabel("Jam (0-23)")
ax.set_ylabel("Rata-Rata Peminjaman")
ax.legend()
st.pyplot(fig)

# 3. Pola Peminjaman per Jam: Hari Kerja vs Libur
st.subheader('Pola Peminjaman per Jam: Hari Kerja vs Libur')
fig, ax = plt.subplots(figsize=(12, 6))

sns.lineplot(
    data=merged_df,
    x="hr",
    y="cnt_hour",
    hue="workingday_hour",  # Pastikan kolom ini ada (1 untuk hari kerja, 0 untuk hari libur)
    estimator="mean",
    errorbar=None,
    ax=ax,
    palette=['#1f77b4', '#ff7f0e'],  # Biru untuk hari kerja, oranye untuk hari libur
    linewidth=2.5
)

ax.set_title("Pola Peminjaman per Jam: Hari Kerja vs Libur")
ax.set_xlabel("Jam (0-23)")
ax.set_ylabel("Rata-Rata Peminjaman")
ax.legend(title="Jenis Hari", labels=["Libur", "Kerja"])

st.pyplot(fig)

# 4. Pola Peminjaman per Jam Berdasarkan Musim
st.subheader('Pola Peminjaman per Jam Berdasarkan Musim')

# Pastikan palet warna tetap konsisten
palette = ["blue", "orange", "green", "red"]  # Sesuaikan dengan warna di gambar

fig, ax = plt.subplots(figsize=(14, 8))
sns.lineplot(
    data=merged_df,
    x="hr",
    y="cnt_hour",
    hue="season_day",
    estimator="mean",
    errorbar=None,
    ax=ax,
    palette=palette
)

ax.set_title("Pola Peminjaman per Jam Berdasarkan Musim")
ax.set_xlabel("Jam (0-23)")
ax.set_ylabel("Rata-Rata Peminjaman")

st.pyplot(fig)

# 5. Dampak Kondisi Cuaca Harian terhadap Peminjaman per Jam
st.subheader('Dampak Kondisi Cuaca Harian')

weather_analysis = merged_df.groupby(["weathersit_day", "hr"]).agg({
    "cnt_hour": "mean",
    "temp_day": "mean",
    "hum_day": "mean"
}).reset_index()

# Pastikan seaborn menggunakan palet warna yang sama
def set_sns_palette():
    palette = sns.color_palette("tab10")  # Sesuaikan palet warna yang digunakan sebelumnya
    return palette

# Visualisasi
fig, ax = plt.subplots(figsize=(14, 6))
sns.lineplot(
    data=weather_analysis,
    x="hr",
    y="cnt_hour",
    hue="weathersit_day",
    marker="o",
    palette=set_sns_palette(),  # Menjaga warna tetap konsisten
    ax=ax
)
ax.set_title("Rata-Rata Peminjaman per Jam Berdasarkan Kondisi Cuaca Harian")
ax.set_xlabel("Jam (0-23)")
ax.set_ylabel("Rata-Rata Peminjaman")
st.pyplot(fig)


# 6. Weather Impact Analysis (Pertanyaan Bisnis 2)
st.subheader('Dampak Kondisi Cuaca terhadap Peminjaman Harian')
fig, ax = plt.subplots(figsize=(10, 6))

sns.barplot(x='weathersit_day', y='cnt_day', data=weather_impact, color='skyblue', ax=ax)
ax.set_title("Peminjaman berdasarkan Kondisi Cuaca")
ax.set_xlabel("Skala Cuaca (1: Terbaik)")
ax.set_ylabel("Rata-rata Peminjaman Harian")
st.pyplot(fig)

# 7. Seasonal Analysis
st.subheader('Analisis Musiman')
fig, ax = plt.subplots(figsize=(12, 6))

sns.barplot(x='season_day', y='cnt_day', data=season_analysis, color='lightgreen', ax=ax)
ax.set_title("Total Peminjaman per Musim")
ax.set_xlabel("Musim (1: Spring, 2: Summer, 3: Fall, 4: Winter)")
ax.set_ylabel("Total Peminjaman")
st.pyplot(fig)

# 8. Peak Hours Analysis
st.subheader('Analisis Jam Sibuk')
peak_hours = hourly_rentals.nlargest(5, 'cnt_hour')
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='hr', y='cnt_hour', data=peak_hours, color='mediumpurple', ax=ax)
ax.set_title("5 Jam dengan Peminjaman Tertinggi")
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Peminjaman")
st.pyplot(fig)

st.caption('Analytics Dashboard © 2024 | Bike Sharing Data')
