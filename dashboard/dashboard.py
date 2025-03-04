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

@st.cache_data
def load_csv(file_name):
    """Memuat file CSV dari folder 'data/'."""
    file_path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return None  # Jangan tampilkan warning, cukup return None

# Load dataset
df_orders = load_csv("order_items_dataset.csv")
df_payments = load_csv("order_payments_dataset.csv")

# Merge dataset berdasarkan 'order_id'
merged_df = df_orders.merge(df_payments, on="order_id", how="left")

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
