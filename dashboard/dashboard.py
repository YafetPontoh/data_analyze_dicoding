import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency


# load_data() untuk memanggil data
def load_data():
    df = pd.read_csv('all_data.csv')
    date_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',
                    'order_delivered_customer_date', 'order_estimated_delivery_date']
    for column in date_columns:
        df[column] = pd.to_datetime(df[column])
    return df


# Fungsi untuk membuat daily_orders
def create_daily_orders_df(df):
    daily_orders = df.resample(rule='D', on='order_purchase_timestamp').agg({
        'order_id': 'nunique',
        'payment_value': 'sum'
    })
    daily_orders = daily_orders.reset_index()
    return daily_orders


# Fungsi untuk membuat month_orders
def create_month_orders_df(df):
    month_orders = df.resample(rule='ME', on='order_purchase_timestamp').agg({
        'order_id': 'nunique',
        'payment_value': 'sum'
    })
    month_orders = month_orders.reset_index()

    return month_orders


# Fungsi untuk membuat sidebar
def create_sidebar(df):
    with st.sidebar:
        min_date = df['order_purchase_timestamp'].min().date()
        max_date = df['order_purchase_timestamp'].max().date()

        start_date, end_date = st.date_input(
            label='Rentang Waktu', min_value=min_date, max_value=max_date,
            value=[min_date, max_date]
        )

        order_status = ['ALL'] + list(df['order_status'].unique())
        select_status = st.radio('Pilih Order Status: ', order_status)

    return start_date, end_date, select_status


# Fungsi untuk memfilter data
def filter_data(df, start_date, end_date, select_status):
    filtered_df = df[(df["order_purchase_timestamp"].dt.date >= start_date) &
                     (df["order_purchase_timestamp"].dt.date <= end_date)]

    if select_status != 'ALL':
        filtered_df = filtered_df[filtered_df['order_status'] == select_status]

    return filtered_df


# Fungsi untuk membuat top 5 best and worst
def create_best_worst_category_df(df):
    products_visualization = df.groupby('product_category_name_english')['qty_order'].sum().reset_index()

    return products_visualization


# Fungsi untuk membuat RFM Analysis
def rfm_anaysis_df(df):
    now = df['order_purchase_timestamp'].max()
    rfm_df = df.groupby(by='customer_id', as_index=False).agg({
        'order_purchase_timestamp': lambda x: (now - x.max()).days,
        'order_id': 'count',
        'payment_value': 'sum'
    })
    rfm_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    rfm_df['numeric_id'] = pd.factorize(rfm_df['customer_id'])[0] + 1

    return rfm_df


# Fungsi untuk Membuat Geoanalysis
def geoanalyze_df(df):
    sales_by_state = df.groupby('customer_state')['payment_value'].sum().sort_values(ascending=True)

    return sales_by_state


# Fungsi untuk menampilkan grafik pesanan bulanan
def create_month_orders(df):
    month_orders_df = create_month_orders_df(df)
    st.subheader('Grafik Penjualan (Bulanan)')

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(month_orders_df['order_purchase_timestamp'], month_orders_df['order_id'])
    plt.title('Jumlah Penjualan Tiap (Bulanan)')
    plt.xlabel('Tanggal')
    plt.ylabel('Jumlah Penjualan (R$)')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x, 'BRL', locale='pt_BR')))

    st.pyplot(fig)


# Fungsi untuk menampilkan grafik pesanan harian
def create_daily_orders(df):
    daily_orders_df = create_daily_orders_df(df)
    st.subheader('Grafik Penjualan (Harian)')

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(daily_orders_df['order_purchase_timestamp'], daily_orders_df['order_id'])
    plt.title('Jumlah Penjualan Tiap (Harian)')
    plt.xlabel('Tanggal')
    plt.ylabel('Jumlah Penjualan')

    st.pyplot(fig)


# Fungsi untuk menampilkan top 5 best and worst
def create_best_worst_category(df):
    products_visualization_df = create_best_worst_category_df(df)

    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(16, 12))

    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(x='qty_order', y='product_category_name_english',
                data=products_visualization_df.sort_values(by='qty_order', ascending=False).head(5),
                hue='product_category_name_english', palette=colors, ax=ax[0])
    ax[0].set_xlabel('Total Quantity Orders')
    ax[0].set_ylabel('Category Product Name')
    ax[0].set_title('Top 5 Kategori Penjualan Product Terbaik', loc='center', fontsize=15)
    ax[0].tick_params(axis='y', labelsize=12)

    sns.barplot(x='qty_order', y='product_category_name_english',
                data=products_visualization_df.sort_values(by='qty_order', ascending=True).head(5),
                hue='product_category_name_english', palette=colors, ax=ax[1])
    ax[1].set_xlabel('Total Quantity Orders')
    ax[1].set_ylabel('Category Product Name')
    ax[1].set_title('Top 5 Kategori Penjualan Product Terburuk', loc='center', fontsize=15)
    ax[1].tick_params(axis='y', labelsize=12)

    st.subheader('Top 5 Kategori Penjualan Product Terbaik dan Terburuk Berdasarkan Quantity Order')
    st.pyplot(fig)


# Fungsi untuk menampilkan rfm
def rfm_analysis(df):
    rfm_df = rfm_anaysis_df(df)

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

    colors = ['#72BCD4', '#72BCD4', '#72BCD4', '#72BCD4', '#72BCD4']

    sns.barplot(y="recency", x='numeric_id', data=rfm_df.sort_values(by='recency', ascending=True).head(5),
                hue='numeric_id', palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title('Penjualan Terakhir (days)', loc='center', fontsize=18)
    ax[0].tick_params(axis='x', labelsize=15)

    sns.barplot(y='frequency', x='numeric_id', data=rfm_df.sort_values(by='frequency', ascending=False).head(5),
                hue='numeric_id', palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title('Frekuensi Pembelian', loc="center", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=15)

    sns.barplot(y='monetary', x='numeric_id', data=rfm_df.sort_values(by='monetary', ascending=False).head(5),
                hue='numeric_id', palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].set_title('Banyak Uang yang Dihabiskan', loc='center', fontsize=18)
    ax[2].tick_params(axis='x', labelsize=15)
    ax[2].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x, 'BRL', locale='pt_BR')))

    st.subheader('Best Customer Based on RFM Parameters')
    st.pyplot(fig)


# Fungsi untuk menampilkan Geoanalysis
def geoanalyze(df):
    all_df = geoanalyze_df(df)
    st.subheader('Total Penjualan berdasarkan Negara Bagian')

    fig, ax = plt.subplots(figsize=(12, 6))

    all_df.plot(kind='barh', ax=ax)
    plt.title('Total Penjualan berdasarkan Negara Bagian')
    plt.ylabel('Negara Bagian')
    plt.xlabel('Total Penjualan')
    plt.tight_layout()
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x, 'BRL', locale='pt_BR')))

    st.pyplot(fig)


# Fungsi untuk menampilkan clustering
def clustering(df):
    st.subheader('Hubungan antara Harga, Biaya Pengiriman, dan Skor Review')

    fig, ax = plt.subplots(figsize=(14, 8))

    scatter = ax.scatter(df['price'], df['freight_value'], c=df['review_score'], cmap='viridis', alpha=0.5)
    plt.colorbar(scatter, label='Skor Review')

    plt.xlabel('Harga Produk')
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x, 'BRL', locale='pt_BR')))

    plt.ylabel('Biaya Pengiriman')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x, 'BRL', locale='pt_BR')))

    plt.title('Hubungan antara Harga, Biaya Pengiriman, dan Skor Review')

    st.pyplot(fig)


# Fungsi untuk menampilkan statistik pesanan
def create_order_stats(df):
    col1, col2 = st.columns(2)

    total_orders = df['order_id'].nunique()
    total_revenue = df['payment_value'].sum()

    with col1:
        st.metric('Total Orders', total_orders)

    with col2:
        formatted_revenue = format_currency(total_revenue, 'BRL', locale='pt_BR')
        st.metric('Total Revenue', formatted_revenue)


# Fungsi untuk menampilkan visualisasi status pesanan
def create_order_status_viz(df):
    st.subheader('Jumlah Pesanan berdasarkan Status')
    order_count = df['order_status'].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    order_count.plot(kind='bar', ax=ax)
    plt.title('Jumlah Pesanan berdasarkan Status')
    plt.xlabel('Status Pesanan')
    plt.ylabel('Jumlah Pesanan')
    st.pyplot(fig)


# Fungsi untuk menampilkan data pesanan
def create_order_data(df):
    st.subheader('Data Pesanan')
    st.dataframe(df)


# Main function
def main():
    st.title('Analisis Data Pesanan')

    # Load_data
    all_df = load_data()

    # sidebar_filterValues
    start_date, end_date, select_status = create_sidebar(all_df)

    # Filter_data
    main_df = filter_data(all_df, start_date, end_date, select_status)

    # Visualization
    st.subheader(f'Visualisasi Data untuk Status: {select_status}')

    st.subheader('Statistik Order Harian')
    create_order_stats(main_df)
    create_month_orders(main_df)
    create_daily_orders(main_df)
    create_best_worst_category(main_df)
    rfm_analysis(main_df)
    create_order_status_viz(main_df)
    geoanalyze(main_df)
    clustering(main_df)

    create_order_data(main_df)


if __name__ == "__main__":
    main()