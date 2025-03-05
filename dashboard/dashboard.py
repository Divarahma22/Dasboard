import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Atur tema Seaborn
sns.set_theme(style="whitegrid", context="talk")

# Path folder 'data'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data/")

# Cek apakah folder 'data' tersedia
if not os.path.exists(DATA_DIR):
    st.error("❌ Folder 'data/' tidak ditemukan! Pastikan dataset tersedia.")
    st.stop()

@st.cache_data
def load_csv(file_name):
    """Memuat file CSV dari folder 'data/'."""
    file_path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

# Load dataset
st.sidebar.header("📊 Dashboard Data")
df_orders = load_csv("order_items_dataset.csv")
df_payments = load_csv("order_payments_dataset.csv")

# Validasi dataset
if df_orders is None or df_payments is None:
    st.error("❌ Data tidak tersedia. Pastikan file CSV ada di folder 'data/'.")
    st.stop()

# Merge dataset
merged_df = df_orders.merge(df_payments, on="order_id", how="left")

# Konversi kolom tanggal
merged_df["order_purchase_timestamp"] = pd.to_datetime(merged_df["order_purchase_timestamp"])

# Filter rentang waktu
min_date = merged_df["order_purchase_timestamp"].min().date()
max_date = merged_df["order_purchase_timestamp"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Pilih Rentang Waktu", [min_date, max_date], min_value=min_date, max_value=max_date
)

filtered_df = merged_df[
    (merged_df["order_purchase_timestamp"].dt.date >= start_date) &
    (merged_df["order_purchase_timestamp"].dt.date <= end_date)
]

# Menampilkan metrik utama
total_orders = filtered_df["order_id"].nunique()
total_revenue = filtered_df["payment_value"].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Orders", total_orders)
with col2:
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

# Visualisasi jumlah pesanan harian
st.subheader("📈 Daily Orders")
daily_orders = filtered_df.resample("D", on="order_purchase_timestamp")["order_id"].nunique()

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(daily_orders.index, daily_orders.values, marker='o', linestyle='-', color='#007ACC')
ax.set_xlabel("Date")
ax.set_ylabel("Number of Orders")
ax.set_title("Orders Over Time")
st.pyplot(fig)

# Menampilkan data
st.subheader("📊 Order Data Sample")
st.dataframe(filtered_df.head())


# --- VISUALISASI --- #
st.title("📊 Dashboard E-Commerce")

# 1️⃣ **Total Pembayaran per Metode**
st.header("💰 Total Pembayaran per Metode")
if 'payment_type' in merged_df.columns and 'payment_value' in merged_df.columns:
    payment_summary = merged_df.groupby("payment_type")['payment_value'].sum().reset_index()
    st.dataframe(payment_summary)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='payment_type', y='payment_value', data=payment_summary, ax=ax, palette="Blues")
    ax.set_title("Total Pembayaran per Metode")
    st.pyplot(fig)

# 2️⃣ **Rata-rata Harga Produk per Cicilan**
st.header("📊 Rata-rata Harga Produk per Cicilan")
if 'payment_installments' in merged_df.columns and 'price' in merged_df.columns:
    installment_price = merged_df.groupby("payment_installments")['price'].mean().reset_index()
    st.dataframe(installment_price)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(x='payment_installments', y='price', data=installment_price, marker='o', color='b')
    ax.set_title("Harga Rata-rata vs Cicilan")
    st.pyplot(fig)

st.caption("📌 Copyright © 2024 | Dashboard E-Commerce")

