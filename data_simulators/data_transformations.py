import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import timedelta

fake = Faker()

# ==========================================
# 1. ORDERS
# ==========================================
input_path = 'data/archive/olist_orders_dataset.csv'
df = pd.read_csv(input_path)

df['shipping_country'] = [fake.country() for _ in range(len(df))]
df['zipcode'] = [fake.postcode() for _ in range(len(df))]
df['shipping_street'] = [fake.street_address() for _ in range(len(df))]

null_zip_idx = df.sample(frac=0.02).index
df.loc[null_zip_idx, 'zipcode'] = np.nan

lower_country_idx = df.sample(frac=0.03).index
df.loc[lower_country_idx, 'shipping_country'] = df.loc[lower_country_idx, 'shipping_country'].str.lower()

canceled_idx = df[df['order_status'] == 'canceled'].sample(frac=0.1).index
df.loc[canceled_idx, 'order_delivered_customer_date'] = df.loc[canceled_idx, 'order_estimated_delivery_date']

output_path = 'data/shielded_orders_dataset.csv'
df.to_csv(output_path, index=False)


# ==========================================
# 2. REVIEWS
# ==========================================
input_path = 'data/archive/olist_order_reviews_dataset.csv'
df = pd.read_csv(input_path)

df.rename(columns={
    'review_comment_message': 'Review_comment_message',
    'review_creation_date': 'Date_review_sent',
    'review_answer_timestamp': 'Date_review_answered'
}, inplace=True)

columns_to_keep = [
    'review_id', 'order_id', 'review_score', 
    'Review_comment_message', 'Date_review_sent', 'Date_review_answered'
]
df = df[columns_to_keep]

languages = ['Portuguese', 'English', 'Spanish', 'French']
df['review_language'] = [random.choices(languages, weights=[0.8, 0.1, 0.05, 0.05])[0] for _ in range(len(df))]

df['Date_review_sent'] = pd.to_datetime(df['Date_review_sent'])
df['Date_review_answered'] = pd.to_datetime(df['Date_review_answered'])

general_review_idx = df.sample(frac=0.05).index
df.loc[general_review_idx, 'order_id'] = np.nan

time_travel_idx = df.sample(frac=0.02).index
df.loc[time_travel_idx, 'Date_review_answered'] = df.loc[time_travel_idx, 'Date_review_sent'] - timedelta(days=1)

invalid_score_idx = df.sample(frac=0.01).index
df.loc[invalid_score_idx, 'review_score'] = 6

output_path = 'data/shielded_reviews_dataset.csv'
df.to_csv(output_path, index=False)


# ==========================================
# 3. ORDER ITEMS
# ==========================================
input_path = 'data/archive/olist_order_items_dataset.csv'
df = pd.read_csv(input_path)

columns_to_keep = ['order_id', 'product_id', 'shipping_limit_date', 'price']
df = df[columns_to_keep]

df['item_discount'] = df['price'] * np.random.uniform(0.0, 0.3, size=len(df))
df['item_discount'] = df['item_discount'].round(2)

negative_price_idx = df.sample(frac=0.02).index
df.loc[negative_price_idx, 'price'] = -df.loc[negative_price_idx, 'price'].abs()

extreme_discount_idx = df.sample(frac=0.02).index
df.loc[extreme_discount_idx, 'item_discount'] = df.loc[extreme_discount_idx, 'price'] + 10.0

null_date_idx = df.sample(frac=0.03).index
df.loc[null_date_idx, 'shipping_limit_date'] = np.nan

output_path = 'data/shielded_order_items_dataset.csv'
df.to_csv(output_path, index=False)


# ==========================================
# 4. PRODUCTS
# ==========================================
input_path = 'data/archive/olist_products_dataset.csv'
df = pd.read_csv(input_path)

df.rename(columns={
    'product_id': 'Product_id',
    'product_category_name': 'Product_category',
    'product_weight_g': 'product_weight_grams'
}, inplace=True)

columns_to_keep = [
    'Product_id', 'Product_category', 'product_weight_grams', 
    'product_length_cm', 'product_height_cm', 'product_width_cm'
]
df = df[columns_to_keep]

negative_weight_idx = df.sample(frac=0.02).index
df.loc[negative_weight_idx, 'product_weight_grams'] = -df.loc[negative_weight_idx, 'product_weight_grams'].abs() - 1

null_category_idx = df.sample(frac=0.03).index
df.loc[null_category_idx, 'Product_category'] = np.nan

zero_dimension_idx = df.sample(frac=0.01).index
df.loc[zero_dimension_idx, 'product_length_cm'] = 0

output_path = 'data/shielded_products_dataset.csv'
df.to_csv(output_path, index=False)