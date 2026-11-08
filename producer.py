import json
import random
from datetime import datetime
import pandas as pd
from faker import Faker

fake = Faker('el_GR')

def build_and_save_dataset():
    try:
        #diavazo ta data apo ta csv arxeia
        customers_df = pd.read_csv('data/olist_customers_dataset.csv')
        orders_df = pd.read_csv('data/olist_orders_dataset.csv')
        payments_df = pd.read_csv('data/olist_order_payments_dataset.csv')
        reviews_df = pd.read_csv('data/olist_order_reviews_dataset.csv')
        order_items_df = pd.read_csv('data/olist_order_items_dataset.csv')
        products_df = pd.read_csv('data/olist_products_dataset.csv')

        # enosi ton pinakon 
        print("Ένωση (Merging) όλων των πινάκων...")
        merged_df = orders_df.merge(customers_df, on='customer_id', how='inner')
        merged_df = merged_df.merge(payments_df, on='order_id', how='inner')
        merged_df = merged_df.merge(reviews_df, on='order_id', how='inner')
        merged_df = merged_df.merge(order_items_df, on='order_id', how='inner')
        merged_df = merged_df.merge(products_df, on='product_id', how='inner')

        # αντιπροσωπευτικο δειγμα 100 γραμμων
        subset_df = merged_df.head(100)

        unified_records = []

        # τελικο json
        for _, row in subset_df.iterrows():
            
         
            customers_data = {
                "Customer_id": str(row.get('customer_id', '')),
                "customer_fullname": fake.name(),
                "Customer_email": fake.free_email(),                                            #θα ελεγα να κρατησουμε το free_emeil γιατι δίνει διαφορετικες διευθηνσεις περα απο το @example.com που βγαζει μονο το απλο email
                "Customer_afm": f"{random.randint(100000000, 999999999)}",
                "Customer_phone_number": fake.phone_number(),
                "Customer_country": "Greece",                                                   #επισης εδω ισως να βάλουμε
                "Customer_ip": fake.ipv4(),
                "Customer_date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=70).strftime("%Y-%m-%d"),
                "Customer_last_login_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            order_id = str(row.get('order_id', ''))
           
            orders_data = {
                "Customer_id": customers_data["Customer_id"],
                "Order_id": order_id,
                "order_status": str(row.get('order_status', '')),
                "order_purchase_timestamp": str(row.get('order_purchase_timestamp', '')),
                "shipping_country": "Greece",
                "zipcode": str(row.get('customer_zip_code_prefix', '')),
                "shipping_street": fake.street_address()
            }

         
            payments_data = {
                "Order_id": order_id,
                "Credit_card_number": fake.credit_card_number(card_type='visa'),
                "Credit_card_expiry": fake.credit_card_expire(),
                "Iban": fake.iban(),
                "Payment_type": str(row.get('payment_type', '')),
                "Payment_installments": int(row.get('payment_installments', 1)),
                "Payment_value": float(row.get('payment_value', 0.0))
            }

         
            order_items_data = {
                "order_id": order_id,
                "product_id": str(row.get('product_id', '')),
                "shipping_limit_date": str(row.get('shipping_limit_date', '')),
                "price": float(row.get('price', 0.0)),
                "item_discount": 0.00
            }

         
            products_data = {
                "Product_id": order_items_data["product_id"],
                "Product_category": str(row.get('product_category_name', 'general')),
                "product_weight_grams": float(row.get('product_weight_g', 500.0)),
                "product_length_cm": float(row.get('product_length_cm', 10.0)),
                "product_height_cm": float(row.get('product_height_cm', 10.0)),
                "product_width_cm": float(row.get('product_width_cm', 10.0))
            }

       
            reviews_data = {
                "review_id": str(row.get('review_id', '')),
                "order_id": order_id,
                "review_score": int(row.get('review_score', 5)),
                "Review_comment_message": str(row.get('review_comment_message') if pd.notna(row.get('review_comment_message')) else "Πολύ καλό προϊόν!"),
                "Date_review_sent": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "review_language": "el"
            }

            # Ενιαίο πακέτο
            unified_event = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "customers": customers_data,
                "orders": orders_data,
                "payments": payments_data,
                "order_items": order_items_data,
                "products": products_data,
                "reviews": reviews_data
            }

            unified_records.append(unified_event)

        # Αποθήκευση σε σταθερό αρχείο JSON
        output_filename = "final_unified_dataset.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(unified_records, f, indent=4, ensure_ascii=False)

        print(f"Επιτυχία! Το πλήρες dataset αποθηκεύτηκε στο αρχείο: {output_filename}")

    except Exception as e:
        print(f"Σφάλμα κατά τη σύνδεση των αρχείων: {e}")

if __name__ == "__main__":
    build_and_save_dataset()