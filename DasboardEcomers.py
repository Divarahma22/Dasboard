import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

sns.set(style='dark')

# 🔹 Fungsi untuk membaca file CSV dengan fallback ke file_uploader
def load_csv(file_name, label):
    if os.path.exists(file_name):  # Cek apakah file ada di direktori yang sama
        return pd.read_csv(file_name)
    else:
        st.warning(f"File {file_name} tidak ditemukan. Silakan unggah file CSV.")
        uploaded_file = st.file_uploader(f"Unggah {label}", type=["csv"])
        if uploaded_file is not None:
            return pd.read_csv(uploaded_file)
        else:
            return None

# 🔹 Load dataset
order_items_df = load_csv("order_items_dataset.csv", "Order Items Dataset")
order_payments_df = load_csv("order_payments_dataset.csv", "Order Payments Dataset")

# 🔹 Pastikan kedua file berhasil di-load sebelum lanjut
if order_items_df is None or order_payments_df is None:
    st.error("Mohon unggah file yang diperlukan untuk melanjutkan.")
    st.stop()

# 🔹 Cek apakah 'order_id' ada di kedua dataset
if 'order_id' not in order_items_df.columns or 'order_id' not in order_payments_df.columns:
    st.error("Kolom 'order_id' tidak ditemukan di salah satu dataset.")
    st.stop()

# 🔹 Merge datasets berdasarkan 'order_id'
merged_df = order_items_df.merge(order_payments_df, on="order_id", how="inner")

# 🔹 Konversi tanggal jika kolomnya ada
if 'shipping_limit_date' in merged_df.columns:
    merged_df['shipping_limit_date'] = pd.to_datetime(merged_df['shipping_limit_date'])
else:
    st.error("Kolom 'shipping_limit_date' tidak ditemukan dalam dataset.")
    st.stop()

# 🔹 Sidebar untuk filter berdasarkan rentang tanggal
st.sidebar.header("Filter Data")
min_date, max_date = merged_df['shipping_limit_date'].min(), merged_df['shipping_limit_date'].max()

start_date, end_date = st.sidebar.date_input("Rentang Waktu", [min_date, max_date], min_value=min_date, max_value=max_date)

filtered_df = merged_df[(merged_df['shipping_limit_date'] >= str(start_date)) & 
                         (merged_df['shipping_limit_date'] <= str(end_date))]

# 🔹 Pastikan kolom 'payment_type' dan 'payment_value' ada
if 'payment_type' in filtered_df.columns and 'payment_value' in filtered_df.columns:
    st.header("Total Nilai Pembayaran Berdasarkan Metode Pembayaran")
    payment_summary = filtered_df.groupby("payment_type")['payment_value'].sum().reset_index()
    st.dataframe(payment_summary)
else:
    st.warning("Kolom 'payment_type' atau 'payment_value' tidak ditemukan.")

# 🔹 Pastikan kolom 'payment_installments' dan 'price' ada sebelum lanjut
if 'payment_installments' in filtered_df.columns and 'price' in filtered_df.columns:
    st.header("Rata-rata Harga Produk Berdasarkan Jumlah Cicilan")
    installment_price = filtered_df.groupby("payment_installments")['price'].mean().reset_index()
    st.dataframe(installment_price)
else:
    st.warning("Kolom 'payment_installments' atau 'price' tidak ditemukan.")

# 🔹 Visualisasi Total Pembayaran per Metode
if 'payment_type' in filtered_df.columns and 'payment_value' in filtered_df.columns:
    st.subheader("Visualisasi Pembayaran")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='payment_type', y='payment_value', data=payment_summary, ax=ax, palette="Blues")
    ax.set_title("Total Pembayaran per Metode")
    st.pyplot(fig)

# 🔹 Visualisasi Harga Rata-rata vs Cicilan
if 'payment_installments' in filtered_df.columns and 'price' in filtered_df.columns:
    st.subheader("Visualisasi Harga vs Cicilan")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(x='payment_installments', y='price', data=installment_price, marker='o', color='b')
    ax.set_title("Harga Rata-rata vs Cicilan")
    st.pyplot(fig)

st.caption("Copyright © 2024")

