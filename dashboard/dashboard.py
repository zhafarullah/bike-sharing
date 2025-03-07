import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Load dataset
day_df = pd.read_csv("dashboard/day_df_final.csv")
hour_df = pd.read_csv("dashboard/hour_df_final.csv")

day_df['date'] = pd.to_datetime(day_df['date'])

# Judul Dashboard
st.title("Bike Sharing Dashboard")

# Pilihan Tanggal dengan Rentang
st.sidebar.header("Filter Tanggal")
start_date, end_date = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    [day_df['date'].min().date(), day_df['date'].max().date()],
    min_value=day_df['date'].min().date(),
    max_value=day_df['date'].max().date()
)

# Filter data berdasarkan rentang tanggal
if start_date and end_date:
    filtered_df = day_df[(day_df['date'].dt.date >= start_date) & (day_df['date'].dt.date <= end_date)]

    # Tampilkan Total Penyewaan Sepeda
    total_rentals = filtered_df['total_rentals'].sum()
    st.write("### Total Penyewaan Sepeda")
    st.metric(label="Total Rentals", value=total_rentals)

    # Bar Chart untuk Menganalisis Cuaca dan Penyewaan
    st.write("### Analasis Cuaca terhadap rata-rata Penyewaan")
    pivot_weather = filtered_df.groupby("weathersit").agg({
        "total_rentals": ["mean", "sum", "count"]
    }).reset_index()
    pivot_weather.columns = ["Weather Situation", "Average Rentals", "Total Rentals", "Total Occurrences"]

    fig, ax = plt.subplots()
    sns.barplot(x="Weather Situation", y="Average Rentals", data=pivot_weather, palette="coolwarm", ax=ax)
    ax.set_xlabel("Weather Situation")
    ax.set_ylabel("Average Rentals")
    ax.set_title("Average Bike Rentals by Weather Situation")
    st.pyplot(fig)

    # Pola Penyewaan Registered_Rentals pada Hari Kerja vs Non-Kerja
    st.write("### Pola Penyewaan Registered_Rentals pada Hari Kerja vs Non-Kerja")
    result = filtered_df.groupby("workingday").agg({
        "registered_rentals": "mean"
    }).reset_index()
    result['workingday'] = result['workingday'].replace({0: 'Non-Working Day', 1: 'Working Day'})

    fig, ax = plt.subplots()
    sns.barplot(x="workingday", y="registered_rentals", data=result, palette="Blues", ax=ax)
    ax.set_xlabel("Hari")
    ax.set_ylabel("Rata-rata Penyewaan")
    ax.set_title("Rata-rata Penyewaan Sepeda oleh Pengguna Terdaftar pada Hari Kerja vs Non-Kerja")
    st.pyplot(fig)

    # Pie Chart untuk Penyewaan Berdasarkan Musim
    st.write("### Distribusi Penyewaan Sepeda Berdasarkan Musim")
    season_table = filtered_df.groupby("season").agg({
        "total_rentals": "sum"
    }).reset_index().sort_values(by="total_rentals", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(season_table["total_rentals"], labels=season_table["season"], autopct="%1.1f%%", colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
    ax.set_title("Distribusi Penyewaan Sepeda Berdasarkan Musim")
    st.pyplot(fig)

    # Equal Width Binning
    st.write("### Distribusi Penyewaan Sepeda dengan Equal Width Binning")
    bins = pd.cut(filtered_df['total_rentals'], bins=3, labels=["Rendah", "Sedang", "Tinggi"])
    filtered_df['rental_bins'] = bins

    bin_counts = filtered_df['rental_bins'].value_counts().sort_index()
    fig, ax = plt.subplots()
    sns.barplot(x=bin_counts.index, y=bin_counts.values, palette=["#92c5de", "#f4a582", "#b8e186"], ax=ax)
    ax.set_xlabel("Kategori Rental")
    ax.set_ylabel("Jumlah Data")
    ax.set_title("Distribusi Binning Total Rentals (Equal Width)")
    st.pyplot(fig)

else:
    st.warning("Silakan pilih rentang tanggal yang valid")
