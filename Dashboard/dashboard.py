import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style="dark")

all_df = pd.read_csv("all_data.csv")


def create_best_product_performing_df(df):
    best_product_performing_df = (
        df.groupby("product_category_name")
        .size()
        .sort_values(ascending=False)
        .reset_index(name="quantity")
        .head(5)
    )
    return best_product_performing_df


def create_worst_product_performing_df(df):
    worst_product_performing_df = (
        df.groupby("product_category_name")
        .size()
        .sort_values(ascending=True)
        .reset_index(name="quantity")
        .head(5)
    )
    return worst_product_performing_df


def create_best_sellers_df(df):
    top_rated_sellers = df[df["review_score"].isin([4, 5])]
    best_sellers_df = (
        top_rated_sellers.groupby(by="seller_id")["review_score"]
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
        .head(10)
    )
    return best_sellers_df


def create_by_state_df(df):
    by_state_df = (
        df.groupby(by="customer_state")
        .customer_id.nunique()
        .sort_values(ascending=False)
        .reset_index()
        .head(10)
    )
    by_state_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    return by_state_df


def create_by_city_df(df):
    by_city_df = (
        df.groupby(by="customer_city")
        .customer_id.nunique()
        .sort_values(ascending=False)
        .reset_index()
        .head(10)
    )
    by_city_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    return by_city_df


def create_rfm_df(df):
    rfm_df = all_df.groupby(by="customer_id", as_index=False).agg(
        {"order_id": "nunique", "order_purchase_timestamp": "max", "price": "sum"}
    )

    rfm_df.columns = ["customer_id", "frequency", "max_order_date", "monetary"]

    # Kapan pelanggan melakukan transaksi
    rfm_df["max_order_date"] = pd.to_datetime(rfm_df["max_order_date"])
    rfm_df["max_order_date"] = rfm_df["max_order_date"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_date"].apply(lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_date", axis=1, inplace=True)

    return rfm_df


datetime_columns = ["order_purchase_timestamp", "order_delivered_carrier_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

main_df = all_df[
    (all_df["order_purchase_timestamp"] >= str(start_date))
    & (all_df["order_purchase_timestamp"] <= str(end_date))
]

best_product_performing_df = create_best_product_performing_df(main_df)
worst_product_performing_df = create_worst_product_performing_df(main_df)
best_sellers_df = create_best_sellers_df(main_df)
by_state_df = create_by_state_df(main_df)
by_city_df = create_by_city_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header("Ecommerce Collection Dashboard :sparkles:")
st.subheader("Best & Worst Performing Product")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="quantity",
    y="product_category_name",
    data=best_product_performing_df,
    palette=colors,
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Product", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis="y", labelsize=35)
ax[0].tick_params(axis="x", labelsize=30)

sns.barplot(
    x="quantity",
    y="product_category_name",
    data=worst_product_performing_df,
    palette=colors,
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Product", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis="y", labelsize=35)
ax[1].tick_params(axis="x", labelsize=30)

st.pyplot(fig)

st.subheader("Highest Reviews of Seller")
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
colors = [
    "#72BCD4",
    "#72BCD4",
    "#72BCD4",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
]
sns.barplot(x="seller_id", y="count", data=best_sellers_df, palette=colors, ax=ax)
ax.set_ylabel(None)
ax.set_xlabel("Seller ID", fontsize=15)
ax.set_title(None)
ax.set_ylabel("Number of 4 and 5 stars")
ax.tick_params(axis="x", labelsize=15)
plt.xticks(rotation=45, ha="right", fontsize=10)
plt.tight_layout()
st.pyplot(fig)

st.subheader("Customer Demographics")
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = [
        "#90CAF9",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
    ]
    sns.barplot(
        y="customer_count",
        x="customer_state",
        data=by_state_df.sort_values(by="customer_count", ascending=False),
        palette=colors,
        ax=ax,
    )
    ax.set_title("Number of Customer by State", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="x", labelsize=35)
    ax.tick_params(axis="y", labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))

    colors = [
        "#90CAF9",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
        "#D3D3D3",
    ]
    sns.barplot(
        y="customer_count",
        x="customer_city",
        data=by_city_df.sort_values(by="customer_count", ascending=False),
        palette=colors,
        ax=ax,
    )
    ax.set_title("Number of Customer by City", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="x", labelsize=35)
    ax.tick_params(axis="y", labelsize=30)
    plt.xticks(rotation=45, ha="right", fontsize=20)
    st.pyplot(fig)

st.subheader("Best Customer Besed on RFM Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale="es_CO")
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(50, 25))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(
    y="recency",
    x="customer_id",
    data=rfm_df.sort_values(by="recency", ascending=True).head(5),
    palette=colors,
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, ha="right", fontsize=20)
ax[0].tick_params(axis="y", labelsize=30)
ax[0].tick_params(axis="x", labelsize=35)

sns.barplot(
    y="frequency",
    x="customer_id",
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
    palette=colors,
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, ha="right", fontsize=20)
ax[1].tick_params(axis="y", labelsize=30)
ax[1].tick_params(axis="x", labelsize=35)

sns.barplot(
    y="monetary",
    x="customer_id",
    data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
    palette=colors,
    ax=ax[2],
)
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45, ha="right", fontsize=20)
ax[2].tick_params(axis="y", labelsize=30)
st.pyplot(fig)
