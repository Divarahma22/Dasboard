import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Atur gaya Seaborn
sns.set_theme(style="whitegrid", context="talk")

# Tentukan path absolut ke file CSV dan gambar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "dataset_baru.csv")

@st.cache_data
def load_data():
    """Load dataset dengan pengecekan error."""
    if not os.path.exists(data_path):
        st.error(f"File data tidak ditemukan: {data_path}")
        return None
    try:
        return pd.read_csv(data_path)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    st.title("📊 Dashboard E-Commerce")

    # Load data
    merged_df = load_data()
    if merged_df is None or merged_df.empty:
        st.warning("Data tidak tersedia atau kosong.")
        return

    # Sidebar untuk filter interaktif
    st.sidebar.header("Navigasi")

    # 1️⃣ **Total Pembayaran per Metode**
    st.header("💰 Total Pembayaran per Metode")
    if 'payment_type' in merged_df.columns and 'payment_value' in merged_df.columns:
        payment_summary = merged_df.groupby("payment_type")["payment_value"].sum().reset_index()
        st.dataframe(payment_summary)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x='payment_type', y='payment_value', data=payment_summary, ax=ax, palette="Blues")
        ax.set_title("Total Pembayaran per Metode")
        st.pyplot(fig)

    # 2️⃣ **Rata-rata Harga Produk per Cicilan**
    st.header("📊 Rata-rata Harga Produk per Cicilan")
    if 'payment_installments' in merged_df.columns and 'price' in merged_df.columns:
        installment_price = merged_df.groupby("payment_installments")["price"].mean().reset_index()
        st.dataframe(installment_price)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(x='payment_installments', y='price', data=installment_price, marker='o', color='b')
        ax.set_title("Harga Rata-rata vs Cicilan")
        st.pyplot(fig)

    st.caption("📌 Copyright © 2024 | Dashboard E-Commerce")

if __name__ == "__main__":
    main()

