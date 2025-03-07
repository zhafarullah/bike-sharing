import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Load dataset
day_df = pd.read_csv("day_df_final.csv")
hour_df=pd.read_csv("hour_df_final.csv")

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
    st.write("### Analisis Cuaca dan Penyewaan")
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
    st.write("### Pola Penyewaan Registered_Rentals pada Hari Kerja vs Non-Kerja")
    result = filtered_df.groupby("workingday").agg({
        "registered_rentals": "mean"
    }).reset_index()
    result['workingday'] = result['workingday'].replace({0: 'Non-Working Day', 1: 'Working Day'})

    # Pola Penyewaan Registered_Rentals pada Hari Kerja vs Non-Kerja
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

    # Tabel RFM
    st.write("### Tabel RFM")
    rfm_df = filtered_df.copy()
    weekday_mapping = {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday'
    }
    rfm_df['weekday'] = rfm_df['weekday'].map(weekday_mapping)

    latest_date = rfm_df['date'].max()
    rfm_df['Recency'] = (latest_date - rfm_df['date']).dt.days

    frequency = rfm_df.groupby("weekday").agg({"date": "nunique"}).reset_index()
    frequency.columns = ["weekday", "Frequency"]

    monetary = rfm_df.groupby("weekday").agg({"total_rentals": "sum"}).reset_index()
    monetary.columns = ["weekday", "Monetary"]

    rfm_table = frequency.merge(monetary, on="weekday")
    rfm_table = rfm_table.merge(rfm_df[['weekday', 'Recency']].drop_duplicates(), on='weekday')
    rfm_table = rfm_table.sort_values(by=["Monetary"], ascending=False)

    st.dataframe(rfm_table)

    # Bar Chart RFM
    st.write("### Monetary Value by Weekday")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=rfm_table, x='weekday', y='Monetary', palette='viridis', order=[
        'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
    ], ax=ax)
    ax.set_title("Monetary Value by Weekday")
    ax.set_xlabel("Weekday")
    ax.set_ylabel("Total Rentals")
    st.pyplot(fig)

else:
    st.warning("Silakan pilih rentang tanggal yang valid")
