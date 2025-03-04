import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Atur tema Seaborn
sns.set_theme(style="whitegrid", context="talk")

# Path folder 'data'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Fungsi membaca dataset atau membuat dummy jika kosong
@st.cache_data
def load_csv(file_name, label):
    file_path = os.path.join(DATA_DIR, file_name)

    if os.path.exists(file_path):
        st.success(f"✅ File {file_name} ditemukan.")
        return pd.read_csv(file_path)

    # Jika file tidak ada, buat dummy dataset agar dashboard tetap tampil
    st.warning(f"⚠️ File {file_name} tidak ditemukan. Menggunakan data dummy sementara.")
    
    if file_name == "order_items_dataset.csv":
        return pd.DataFrame({
            "order_id": ["ORD1", "ORD2", "ORD3"],
            "price": [100000, 150000, 200000]
        })
    elif file_name == "order_payments_dataset.csv":
        return pd.DataFrame({
            "order_id": ["ORD1", "ORD2", "ORD3"],
            "payment_type": ["credit_card", "boleto", "debit_card"],
            "payment_value": [100000, 150000, 200000],
            "payment_installments": [1, 2, 3]
        })
    return None

# Load dataset
df_orders = load_csv("order_items_dataset.csv", "Order Items Dataset")
df_payments = load_csv("order_payments_dataset.csv", "Order Payments Dataset")

# Merge dataset berdasarkan 'order_id'
merged_df = df_orders.merge(df_payments, on="order_id", how="left")

# Jika kolom 'shipping_limit_date' ada, konversi ke datetime
if 'shipping_limit_date' in merged_df.columns:
    merged_df['shipping_limit_date'] = pd.to_datetime(merged_df['shipping_limit_date'], errors='coerce')

# Sidebar filter rentang tanggal jika ada tanggal
if 'shipping_limit_date' in merged_df.columns and not merged_df['shipping_limit_date'].isna().all():
    st.sidebar.header("🗂️ Filter Data")
    min_date, max_date = merged_df['shipping_limit_date'].min(), merged_df['shipping_limit_date'].max()
    start_date, end_date = st.sidebar.date_input("📆 Rentang Waktu", [min_date, max_date], min_value=min_date, max_value=max_date)
    merged_df = merged_df[(merged_df['shipping_limit_date'] >= pd.Timestamp(start_date)) & (merged_df['shipping_limit_date'] <= pd.Timestamp(end_date))]

# --- VISUALISASI ---
st.header("💰 Total Pembayaran per Metode")
if 'payment_type' in merged_df.columns and 'payment_value' in merged_df.columns:
    payment_summary = merged_df.groupby("payment_type")['payment_value'].sum().reset_index()
    st.dataframe(payment_summary)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='payment_type', y='payment_value', data=payment_summary, ax=ax, palette="Blues")
    ax.set_title("Total Pembayaran per Metode")
    st.pyplot(fig)

st.header("📊 Rata-rata Harga Produk per Cicilan")
if 'payment_installments' in merged_df.columns and 'price' in merged_df.columns:
    installment_price = merged_df.groupby("payment_installments")['price'].mean().reset_index()
    st.dataframe(installment_price)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(x='payment_installments', y='price', data=installment_price, marker='o', color='b')
    ax.set_title("Harga Rata-rata vs Cicilan")
    st.pyplot(fig)

st.caption("📌 Copyright © 2024 | Dashboard E-Commerce")
