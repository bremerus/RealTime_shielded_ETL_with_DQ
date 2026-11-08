import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('el_GR')

# ==========================================
# 1. ORDERS
# ==========================================
df_orders = pd.read_csv('data/archive/olist_orders_dataset.csv')

columns_to_keep = [
    'order_id', 'customer_id', 'order_status',
    'order_purchase_timestamp','order_approved_at', 
    'order_delivered_carrier_date','order_delivered_customer_date', 
    'order_estimated_delivery_date','shipping_country', 
    'zipcode', 'shipping_street'
]

df_orders = df_orders[columns_to_keep]

n = len(df_orders)

df_orders['shipping_country'] = [fake.country() for _ in range(n)]
df_orders['zipcode'] = [fake.postcode() for _ in range(n)]
df_orders['shipping_street'] = [fake.street_address() for _ in range(n)]

date_columns = [
    'order_purchase_timestamp', 'order_approved_at', 
    'order_delivered_carrier_date', 'order_delivered_customer_date', 
    'order_estimated_delivery_date'
]
for col in date_columns:
    df_orders[col] = pd.to_datetime(df_orders[col])

#data poisoning

# DQ1: Null values στο ΤΚ (2%)
null_zip_idx = df_orders.sample(frac=0.02).index
df_orders.loc[null_zip_idx, 'zipcode'] = np.nan

# DQ2: Ασυνέπεια Ονομάτων Χωρών (πεζά γράμματα στο 3%)
lower_country_idx = df_orders.sample(frac=0.03).index
df_orders.loc[lower_country_idx, 'shipping_country'] = df_orders.loc[lower_country_idx, 'shipping_country'].str.lower()

# DQ3: Λογικό Σφάλμα Status (Ακυρωμένες παραγγελίες που "παραδόθηκαν")
# Βρίσκουμε τις ακυρωμένες και βάζουμε σε ένα 10% από αυτές ημερομηνία παράδοσης ίδια με την εκτιμώμενη
canceled_idx = df_orders[df_orders['order_status'] == 'canceled'].sample(frac=0.1).index
df_orders.loc[canceled_idx, 'order_delivered_customer_date'] = df_orders.loc[canceled_idx, 'order_estimated_delivery_date']

# DQ4: Time Travel (Ημερομηνία παράδοσης πριν την αγορά 2%)
time_travel_idx = df_orders.sample(frac=0.02).index
random_days = np.random.randint(1, 10, size=len(time_travel_idx))
random_dt = pd.to_timedelta(random_days, unit='D')
df_orders.loc[time_travel_idx, 'order_delivered_customer_date'] = df_orders.loc[time_travel_idx, 'order_purchase_timestamp'] - random_dt


# DQ5: Mixed Date Formats (Απόλυτο χάος στα timestamps)
mixed_formats = [
    '%Y/%m/%d %H:%M',    
    '%m/%d/%Y %H:%M:%S', 
    '%d-%b-%Y',          
    '%b %d, %y',         
    '%d.%m.%Y %H:%M',    
    '%Y-%m-%d %H:%M:%S'  
]

def randomize_date_format(date_obj):
    if pd.isnull(date_obj):
        return np.nan
    chosen_format = random.choice(mixed_formats)
    return date_obj.strftime(chosen_format)

for col in date_columns:
    df_orders[col] = df_orders[col].apply(randomize_date_format)

df_orders.to_csv('data/archive/olist_orders_dataset.csv', index=False)





# ==========================================
# 2. Reviews
# ==========================================
df_reviews = pd.read_csv('data/archive/olist_order_reviews_dataset.csv')

# print(df_reviews.columns)

columns_to_keep = [
    'review_id', 'order_id', 'review_score', 
    'review_comment_message', 'review_creation_date', 'review_answer_timestamp'
]

df_reviews = df_reviews[columns_to_keep]

languages = ['el', 'en', 'ru'] # να βαλω και κυριλικό αλφαβητο?

df_reviews['review_creation_date'] = pd.to_datetime((df_reviews['review_creation_date']))
df_reviews['review_answer_timestamp'] = pd.to_datetime(df_reviews['review_answer_timestamp'])

#DQ1 εδω απλα αφαιρούμε το Orderid απο 5% των reviwes γιατι είναι για το site
general_review_idx = df_reviews.sample(frac=0.05).index
df_reviews.loc[general_review_idx, 'order_id'] = np.nan

#DQ2 εδω κάνω δυσανάλογο το review_creation_date και review_answer_timestamp για το 2%
time_travel_idx = df_reviews.sample(frac=0.02).index
n_sample = len(time_travel_idx)

random_days = np.random.randint(1, 8, size=n_sample)
random_mins = np.random.randint(1, 60, size=n_sample)

random_dt = pd.to_timedelta(random_days, unit='D') + pd.to_timedelta(random_mins, unit='m')

df_reviews.loc[time_travel_idx, 'review_answer_timestamp'] = df_reviews.loc[time_travel_idx, 'review_creation_date'] - random_dt

#DQ3 εδω δίνω μη αποδεκτό σκορ εκτός των ορίων 1 - 5

invalid_score_idx = df_reviews.sample(frac=0.01).index
df_reviews.loc[invalid_score_idx, 'review_score'] = 6

#DQ4 διαφορετικά Formats για την ημερομηνία 

mixed_formats = [
    '%Y/%m/%d',          # π.χ. 2026/02/26
    '%m/%d/%Y',          # π.χ. 05/23/2025
    '%d-%b-%Y',          # π.χ. 30-Nov-2025
    '%b %d, %y',         # π.χ. May 18, 25
    '%d.%m.%Y %H:%M',    # π.χ. 26.02.2026 14:30 
    '%Y-%m-%d %H:%M:%S'  # Το κανονικό
]

def randomize_date_format(date_obj):
    if pd.isnull(date_obj):
        return np.nan
    chosen_format = random.choice(mixed_formats)
    return date_obj.strftime(chosen_format)

df_reviews['review_creation_date'] = df_reviews['review_creation_date'].apply(randomize_date_format)
df_reviews['review_answer_timestamp'] = df_reviews['review_answer_timestamp'].apply(randomize_date_format)

df_reviews.to_csv('data/shielded_reviews_dataset.csv', index=False)



# ==========================================
# 4. PRODUCTS
# ==========================================
df_products = pd.read_csv('data/archive/olist_products_dataset.csv')

columns_to_keep = [
    'product_id', 'product_category_name', 'product_weight_g',
    'product_length_cm', 'product_height_cm', 'product_width_cm'
]
df_products = df_products[columns_to_keep].copy()

n = len(df_products)

# 3. Προσθήκη ονοματοςε
df_products['product_name'] = [f"{fake.word().capitalize()} {fake.word()}" for _ in range(n)]

# ==========================================
# DATA POISONING (PRODUCTS)
# ==========================================

# DQ1: Null values στο όνομα προϊόντος (2%)
null_name_idx = df_products.sample(frac=0.02).index
df_products.loc[null_name_idx, 'product_name'] = np.nan

# DQ2: Null values στην κατηγορία προϊόντος (3%)
null_cat_idx = df_products.sample(frac=0.03).index
df_products.loc[null_cat_idx, 'product_category_name'] = np.nan

# DQ3: Αρνητικό Βάρος (2%)
neg_weight_idx = df_products.sample(frac=0.02).index
df_products.loc[neg_weight_idx, 'product_weight_g'] = df_products.loc[neg_weight_idx, 'product_weight_g'] * -1

# DQ4: Αρνητικές ή Μηδενικές Διαστάσεις (2%)
neg_dim_idx = df_products.sample(frac=0.02).index
df_products.loc[neg_dim_idx, 'product_length_cm'] = -10.0
df_products.loc[neg_dim_idx, 'product_width_cm'] = 0.0

# DQ5: Ασυνέπεια στην Κατηγορία (Κεφαλαία και έξτρα κενά στο 4%)
messy_cat_idx = df_products.dropna(subset=['product_category_name']).sample(frac=0.04).index
df_products.loc[messy_cat_idx, 'product_category_name'] = df_products.loc[messy_cat_idx, 'product_category_name'].str.upper() + "   "

df_products.to_csv('data/archive/olist_products_dataset.csv', index=False)





# ==========================================
# 5. Customers
# ==========================================
df_customers = pd.read_csv('data/archive/olist_customers_dataset.csv')

df_customers = df_customers[['customer_id']].copy()

n = len(df_customers)

df_customers['customer_fullname'] = [fake.name() for _ in range(n)]
df_customers['Customer_email'] = [fake.free_email() for _ in range(n)]
df_customers['Customer_afm'] = [str(random.randint(100000000, 999999999)) for _ in range(n)]
df_customers['Customer_phone_number'] = [fake.phone_number() for _ in range(n)]
df_customers['Customer_country'] = [fake.country() for _ in range(n)]
df_customers['Customer_ip'] = [fake.ipv4() for _ in range(n)]

df_customers['Customer_date_of_birth'] = [fake.date_of_birth(minimum_age=18, maximum_age=70) for _ in range(n)]
df_customers['Customer_last_login_timestamp'] = [fake.date_time_between(start_date='-1y', end_date='now') for _ in range(n)]

df_customers['Customer_date_of_birth'] = pd.to_datetime(df_customers['Customer_date_of_birth'])
df_customers['Customer_last_login_timestamp'] = pd.to_datetime(df_customers['Customer_last_login_timestamp'])

# Data poisoning

# DQ1: Emails (αφαιρω το @ στο 3%)
invalid_email_idx = df_customers.sample(frac=0.03).index
df_customers.loc[invalid_email_idx, 'Customer_email'] = df_customers.loc[invalid_email_idx, 'Customer_email'].str.replace('@', '', regex=False)

# DQ2: Time Travel για dob
time_travel_cust_idx = df_customers.sample(frac=0.02).index
n_sample_cust = len(time_travel_cust_idx)

random_days_cust = np.random.randint(1, 1800, size=n_sample_cust) 
random_dt_cust = pd.to_timedelta(random_days_cust, unit='D')
df_customers.loc[time_travel_cust_idx, 'Customer_date_of_birth'] = df_customers.loc[time_travel_cust_idx, 'Customer_last_login_timestamp'] + random_dt_cust

# DQ3: Άκυρα Τηλέφωνα (2%) Missing Ονόματα (1%)
invalid_phone_idx = df_customers.sample(frac=0.02).index
df_customers.loc[invalid_phone_idx, 'Customer_phone_number'] = "ERR_" + df_customers.loc[invalid_phone_idx, 'Customer_phone_number'].astype(str)

null_name_idx = df_customers.sample(frac=0.01).index
df_customers.loc[null_name_idx, 'customer_fullname'] = np.nan

# DQ4: Ασυνέπεια στις Χώρες (GREECE με έξτρα κενό στο 4%)
messy_country_idx = df_customers.sample(frac=0.04).index
df_customers.loc[messy_country_idx, 'Customer_country'] = df_customers.loc[messy_country_idx, 'Customer_country'].str.upper() + " "

# DQ5: Διαφορετικά date Formats 
mixed_formats = [
    '%Y/%m/%d',          
    '%m/%d/%Y',          
    '%d-%b-%Y',          
    '%b %d, %y',         
    '%d.%m.%Y %H:%M',    
    '%Y-%m-%d %H:%M:%S'  
]

def randomize_date_format(date_obj):
    if pd.isnull(date_obj):
        return np.nan
    chosen_format = random.choice(mixed_formats)
    return date_obj.strftime(chosen_format)

df_customers['Customer_date_of_birth'] = df_customers['Customer_date_of_birth'].apply(randomize_date_format)
df_customers['Customer_last_login_timestamp'] = df_customers['Customer_last_login_timestamp'].apply(randomize_date_format)

df_customers.to_csv('data/archive/olist_customers_dataset.csv', index=False)


#order items


df_order_items = pd.read_csv('data/archive/olist_order_items_dataset.csv')


df_order_items = df_order_items[['order_id', 'product_id', 'shipping_limit_date', 'price']].copy()


df_order_items['item_discount'] = (df_order_items['price'] * np.random.uniform(0, 0.25, size=len(df_order_items))).round(2)

df_order_items['shipping_limit_date'] = pd.to_datetime(df_order_items['shipping_limit_date'])

df_order_items.to_csv('data/archive/olist_order_items_dataset.csv', index=False)