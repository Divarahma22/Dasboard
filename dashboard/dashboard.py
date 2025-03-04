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

# Pastikan folder 'data' ada
os.makedirs(DATA_DIR, exist_ok=True)

# Fungsi untuk membaca dataset dengan fallback ke uploader
@st.cache_data
def load_csv(file_name, label):
    file_path = os.path.join(DATA_DIR, file_name)

    if os.path.exists(file_path):
        st.success(f"✅ File {file_name} ditemukan.")
        return pd.read_csv(file_path)

    # Jika file tidak ditemukan, tampilkan uploader
    with st.expander(f"📂 Unggah {label}", expanded=True):
        uploaded_file = st.file_uploader(f"Unggah {label} (CSV)", type=["csv"], key=file_name)
    
    if uploaded_file is not None:
        file_path = os.path.join(DATA_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())  # Simpan file ke folder 'data'
        return pd.read_csv(file_path)

    return None

# Load dataset
with st.spinner("🔄 Memuat dataset..."):
    df_orders = load_csv("order_items_dataset.csv", "Order Items Dataset")
    df_payments = load_csv("order_payments_dataset.csv", "Order Payments Dataset")

# Validasi dataset
if df_orders is None or df_payments is None:
    st.error("❌ Mohon unggah file yang diperlukan untuk melanjutkan.")
    st.stop()

# Pastikan kolom penting ada dalam dataset
required_columns_orders = {'order_id', 'price'}
required_columns_payments = {'order_id', 'payment_type', 'payment_value', 'payment_installments'}

if not required_columns_orders.issubset(df_orders.columns):
    st.error("❌ Dataset order_items_dataset.csv tidak memiliki kolom yang diperlukan.")
    st.stop()

if not required_columns_payments.issubset(df_payments.columns):
    st.error("❌ Dataset order_payments_dataset.csv tidak memiliki kolom yang diperlukan.")
    st.stop()

# Merge dataset berdasarkan 'order_id'
merged_df = df_orders.merge(df_payments, on="order_id", how="inner")

if merged_df.empty:
    st.error("❌ Tidak ada data yang dapat dianalisis setelah penggabungan dataset.")
    st.stop()

# Konversi 'shipping_limit_date' ke datetime jika ada
if 'shipping_limit_date' in merged_df.columns:
    merged_df['shipping_limit_date'] = pd.to_datetime(merged_df['shipping_limit_date'], errors='coerce')
    df_filtered = merged_df.dropna(subset=['shipping_limit_date'])
else:
    st.error("❌ Kolom 'shipping_limit_date' tidak ditemukan dalam dataset.")
    st.stop()

# Sidebar filter rentang tanggal
st.sidebar.header("🗂️ Filter Data")
if not df_filtered.empty:
    min_date, max_date = df_filtered['shipping_limit_date'].min(), df_filtered['shipping_limit_date'].max()

    if pd.isna(min_date) or pd.isna(max_date):
        st.error("❌ Rentang tanggal tidak valid. Pastikan data memiliki kolom 'shipping_limit_date'.")
        st.stop()

    start_date, end_date = st.sidebar.date_input(
        "📆 Rentang Waktu", [min_date, max_date], min_value=min_date, max_value=max_date
    )

    # Filter data berdasarkan tanggal
    df_filtered = df_filtered[(df_filtered['shipping_limit_date'] >= pd.Timestamp(start_date)) & 
                              (df_filtered['shipping_limit_date'] <= pd.Timestamp(end_date))]

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data dalam rentang tanggal yang dipilih.")
    st.stop()

# Analisis Total Pembayaran berdasarkan Metode
if 'payment_type' in df_filtered.columns and 'payment_value' in df_filtered.columns:
    st.header("💰 Total Pembayaran per Metode")
    payment_summary = df_filtered.groupby("payment_type")['payment_value'].sum().reset_index()
    st.dataframe(payment_summary)
    
    # Visualisasi Bar Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='payment_type', y='payment_value', data=payment_summary, ax=ax, palette="Blues")
    ax.set_title("Total Pembayaran per Metode")
    ax.set_xlabel("Metode Pembayaran")
    ax.set_ylabel("Total Pembayaran")
    st.pyplot(fig)
else:
    st.warning("⚠️ Kolom 'payment_type' atau 'payment_value' tidak ditemukan.")

# Analisis Harga Rata-rata vs Cicilan
if 'payment_installments' in df_filtered.columns and 'price' in df_filtered.columns:
    st.header("📊 Rata-rata Harga Produk per Cicilan")
    installment_price = df_filtered.groupby("payment_installments")['price'].mean().reset_index()
    st.dataframe(installment_price)
    
    # Visualisasi Line Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(x='payment_installments', y='price', data=installment_price, marker='o', color='b')
    ax.set_title("Harga Rata-rata vs Cicilan")
    ax.set_xlabel("Jumlah Cicilan")
    ax.set_ylabel("Harga Rata-rata (Rp)")
    st.pyplot(fig)
else:
    st.warning("⚠️ Kolom 'payment_installments' atau 'price' tidak ditemukan.")

st.caption("📌 Copyright © 2024 | Dashboard E-Commerce")
