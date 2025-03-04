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

# Buat dataset dummy jika belum ada
def create_dummy_data():
    dummy_files = {
        "order_items_dataset.csv": pd.DataFrame({
            "order_id": ["ORD1", "ORD2", "ORD3"],
            "price": [100000, 150000, 200000]
        }),
        "order_payments_dataset.csv": pd.DataFrame({
            "order_id": ["ORD1", "ORD2", "ORD3"],
            "payment_type": ["credit_card", "boleto", "debit_card"],
            "payment_value": [100000, 150000, 200000],
            "payment_installments": [1, 2, 3]
        })
    }

    for file_name, df in dummy_files.items():
        file_path = os.path.join(DATA_DIR, file_name)
        if not os.path.exists(file_path):  # Hanya buat jika belum ada
            df.to_csv(file_path, index=False)

# Pastikan dummy data ada sebelum load_csv
create_dummy_data()

@st.cache_data
def load_csv(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

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
