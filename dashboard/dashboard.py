import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency

# Atur tema Seaborn
sns.set(style='dark')

# Path folder 'data'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Gunakan absolute path
DATA_DIR = os.path.join(BASE_DIR, "data")

# Cek apakah folder 'data' sudah ada
if not os.path.exists(DATA_DIR):
    st.error("❌ Folder 'data/' tidak ditemukan! Pastikan dataset tersedia.")
    st.stop()

# Fungsi untuk memuat CSV dari folder 'data'
@st.cache_data
def load_csv(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

# Load dataset
df_orders = load_csv("order_items_dataset.csv")
df_payments = load_csv("order_payments_dataset.csv")
df_all = load_csv("all_data.csv")

# Pastikan dataset tersedia sebelum diproses
if df_orders is None or df_payments is None or df_all is None:
    st.error("❌ Data tidak tersedia. Pastikan file CSV ada di folder 'data/'.")
    st.stop()

# Konversi kolom tanggal ke format datetime
datetime_columns = ["order_date", "delivery_date"]
for column in datetime_columns:
    df_all[column] = pd.to_datetime(df_all[column])

df_all.sort_values(by="order_date", inplace=True)
df_all.reset_index(drop=True, inplace=True)

# Filter data berdasarkan rentang tanggal
min_date = df_all["order_date"].min()
max_date = df_all["order_date"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Ambil data berdasarkan rentang tanggal
main_df = df_all[(df_all["order_date"] >= str(start_date)) & (df_all["order_date"] <= str(end_date))]

# Helper function untuk membuat dataframe yang diperlukan
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_date').agg({
        "order_id": "nunique",
        "total_price": "sum"
    }).reset_index()
    
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_sum_order_items_df(df):
    return df.groupby("product_name").quantity_x.sum().sort_values(ascending=False).reset_index()

def create_bygender_df(df):
    return df.groupby("gender").customer_id.nunique().reset_index().rename(columns={"customer_id": "customer_count"})

def create_byage_df(df):
    byage_df = df.groupby("age_group").customer_id.nunique().reset_index().rename(columns={"customer_id": "customer_count"})
    byage_df['age_group'] = pd.Categorical(byage_df['age_group'], ["Youth", "Adults", "Seniors"])
    return byage_df

def create_bystate_df(df):
    return df.groupby("state").customer_id.nunique().reset_index().rename(columns={"customer_id": "customer_count"})

def create_rfm_df(df):
    rfm_df = df.groupby("customer_id").agg({
        "order_date": "max",
        "order_id": "nunique",
        "total_price": "sum"
    }).reset_index()

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_date"].dt.date.max()
    rfm_df["recency"] = (recent_date - rfm_df["max_order_timestamp"]).dt.days
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# Buat berbagai dataframe berdasarkan filter
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bygender_df = create_bygender_df(main_df)
byage_df = create_byage_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

# --- VISUALISASI --- #
st.title("📊 Dashboard E-Commerce")

# **Total Order dan Revenue**
st.subheader("Daily Orders")
col1, col2 = st.columns(2)

with col1:
    st.metric("Total orders", value=daily_orders_df.order_count.sum())

with col2:
    st.metric("Total Revenue", value=format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO'))

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(daily_orders_df["order_date"], daily_orders_df["order_count"], marker='o', linewidth=2, color="#90CAF9")
st.pyplot(fig)

# **Best & Worst Performing Product**
st.subheader("Best & Worst Performing Product")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(x="quantity_x", y="product_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_title("Best Performing Product", fontsize=30)

sns.barplot(x="quantity_x", y="product_name", data=sum_order_items_df.sort_values(by="quantity_x", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_title("Worst Performing Product", fontsize=30)
st.pyplot(fig)

# **Customer Demographics**
st.subheader("Customer Demographics")
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(y="customer_count", x="gender", data=bygender_df, palette=colors, ax=ax)
    ax.set_title("Number of Customer by Gender", fontsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(y="customer_count", x="age_group", data=byage_df, palette=colors, ax=ax)
    ax.set_title("Number of Customer by Age", fontsize=30)
    st.pyplot(fig)

# **Best Customer Based on RFM Parameters**
st.subheader("Best Customer Based on RFM Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average Recency (days)", value=round(rfm_df.recency.mean(), 1))

with col2:
    st.metric("Average Frequency", value=round(rfm_df.frequency.mean(), 2))

with col3:
    st.metric("Average Monetary", value=format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO'))

fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax)
ax.set_title("Top Customers by Monetary", fontsize=30)
st.pyplot(fig)

st.caption("📌 Copyright © 2024 | Dashboard E-Commerce")
