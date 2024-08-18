import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='ME', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return monthly_orders_df

def create_sum_income_df(df):
    # Cek nama kolom
    if 'product_category_name' not in df.columns:
        raise ValueError("Kolom 'product_category_name' tidak ditemukan dalam DataFrame")
    
    sum_income_df = df.groupby("product_category_name").price.sum().sort_values(ascending=False).reset_index()
    return sum_income_df

# Load cleaned data
orders_items_df = pd.read_csv("orders_items.csv")
order_items_product_df = pd.read_csv("order_items_product.csv")

# Cek nama kolom di order_items_product_df
print(order_items_product_df.columns)

datetime_columns = ["order_purchase_timestamp", "year_month"]
orders_items_df.sort_values(by="order_purchase_timestamp", inplace=True)
orders_items_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    orders_items_df[column] = pd.to_datetime(orders_items_df[column])

# Filter data
min_date = orders_items_df["order_purchase_timestamp"].min()
max_date = orders_items_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://seeklogo.com/images/O/olist-logo-9DCE4443F8-seeklogo.com.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = orders_items_df[(orders_items_df["order_purchase_timestamp"] >= pd.Timestamp(start_date)) &
                            (orders_items_df["order_purchase_timestamp"] <= pd.Timestamp(end_date))]
# Menyiapkan berbagai dataframe
monthly_orders_df = create_monthly_orders_df(main_df)
sum_income_df = create_sum_income_df(order_items_product_df)  # Pastikan DataFrame yang benar digunakan

# Plot number of monthly orders (2016-2018)
st.header('Brazilian E-Commerce Dashboard')
st.subheader('Monthly Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "BRL", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#72BCD4"
)
ax.set_title("Number of orders per Month (2016 - 2018)", loc="center", fontsize=20)
ax.set_xticks(monthly_orders_df["order_purchase_timestamp"])
ax.set_xticklabels(monthly_orders_df["order_purchase_timestamp"].dt.strftime('%Y-%m'), fontsize=10, rotation=90)
ax.set_yticklabels(ax.get_yticks(), fontsize=10)
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["revenue"],
    marker='o',
    linewidth=2,
    color="#72BCD4"
)
ax.set_title("Total Revenue per Month in 2016 - 2018 (BRL)", loc="center", fontsize=20)
ax.set_xticklabels(monthly_orders_df["order_purchase_timestamp"], fontsize=10, rotation=90)
ax.set_yticklabels(ax.get_yticks(), fontsize=10)

# Tampilkan plot di Streamlit
st.pyplot(fig)

# Product performance
st.subheader("Highest and Lowest Income (BRL)")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="price", y="product_category_name", data=sum_income_df.head(5), palette=colors,
            ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Highest Product Revenue", loc="center", fontsize=35)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="price", y="product_category_name",
            data=sum_income_df.sort_values(by="price", ascending=True).head(5), palette=colors,
            ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Lowest Product Revenue", loc="center", fontsize=35)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)
