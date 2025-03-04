import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Load dataset
order_items_df = pd.read_csv("order_items_dataset.csv")
order_payments_df = pd.read_csv("order_payments_dataset.csv")

# Merge datasets
merged_df = order_items_df.merge(order_payments_df, on="order_id", how="inner")

# Convert dates to datetime format
merged_df['shipping_limit_date'] = pd.to_datetime(merged_df['shipping_limit_date'])

# Sidebar filter
st.sidebar.header("Filter Data")
min_date = merged_df['shipping_limit_date'].min()
max_date = merged_df['shipping_limit_date'].max()

start_date, end_date = st.sidebar.date_input(
    "Rentang Waktu", [min_date, max_date], min_value=min_date, max_value=max_date
)

filtered_df = merged_df[(merged_df['shipping_limit_date'] >= str(start_date)) & 
                         (merged_df['shipping_limit_date'] <= str(end_date))]

# Total nilai pembayaran per metode pembayaran
st.header("Total Nilai Pembayaran Berdasarkan Metode Pembayaran")
payment_summary = filtered_df.groupby("payment_type")['payment_value'].sum().reset_index()
st.dataframe(payment_summary)

# Rata-rata harga produk berdasarkan jumlah cicilan
st.header("Rata-rata Harga Produk Berdasarkan Jumlah Cicilan")
installment_price = filtered_df.groupby("payment_installments")['price'].mean().reset_index()
st.dataframe(installment_price)

# Visualisasi
st.subheader("Visualisasi Pembayaran")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='payment_type', y='payment_value', data=payment_summary, ax=ax, palette="Blues")
ax.set_title("Total Pembayaran per Metode")
st.pyplot(fig)

st.subheader("Visualisasi Harga vs Cicilan")
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(x='payment_installments', y='price', data=installment_price, marker='o', color='b')
ax.set_title("Harga Rata-rata vs Cicilan")
st.pyplot(fig)

st.caption("Copyright © 2023")
