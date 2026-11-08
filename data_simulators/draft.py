import pandas as pd
import numpy as np
from faker import Faker 
from datetime import datetime, timedelta
import random

fake = Faker('el_GR')

df_order_items = pd.read_csv('data/archive/olist_order_items_dataset.csv')


df_order_items = df_order_items[['order_id', 'product_id', 'shipping_limit_date', 'price']].copy()


df_order_items['item_discount'] = (df_order_items['price'] * np.random.uniform(0, 0.25, size=len(df_order_items))).round(2)

df_order_items['shipping_limit_date'] = pd.to_datetime(df_order_items['shipping_limit_date'])

df_order_items.to_csv('data/archive/olist_order_items_dataset.csv', index=False)