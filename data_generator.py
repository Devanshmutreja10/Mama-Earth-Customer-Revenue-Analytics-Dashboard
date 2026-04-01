# data_generator.py
"""
Data Generation Module for Mama Earth
Creates synthetic e-commerce data for the dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from config import PRODUCT_CATALOG, CITIES, PAYMENT_METHODS, RATING_WEIGHTS

class MamaEarthDataGenerator:
    """Generate synthetic e-commerce data for Mama Earth brand"""
    
    def __init__(self, seed=42):
        """Initialize the generator with a seed for reproducibility"""
        np.random.seed(seed)
        random.seed(seed)
        self.products = PRODUCT_CATALOG
        self.cities = CITIES
        self.payment_methods = PAYMENT_METHODS
        self.rating_weights = RATING_WEIGHTS
        
    def generate_customers(self, n_customers=1000):
        """
        Generate synthetic customer data
        
        Parameters:
        -----------
        n_customers : int
            Number of customers to generate
            
        Returns:
        --------
        pandas.DataFrame: Customer data
        """
        customers = []
        
        for i in range(1, n_customers + 1):
            # Generate signup date within last 2 years
            signup_date = datetime.now() - timedelta(days=np.random.randint(0, 730))
            
            customer = {
                'customer_id': f'C{str(i).zfill(4)}',
                'name': f'Customer_{i}',
                'email': f'customer{i}@email.com',
                'city': np.random.choice(self.cities),
                'age': np.random.randint(18, 65),
                'gender': np.random.choice(['M', 'F', 'Other'], p=[0.45, 0.5, 0.05]),
                'signup_date': signup_date,
                'loyalty_points': np.random.randint(0, 5000),
                'total_orders': np.random.randint(1, 50)
            }
            customers.append(customer)
        
        return pd.DataFrame(customers)
    
    def generate_orders(self, customers_df, n_orders=5000):
        """
        Generate synthetic order data
        
        Parameters:
        -----------
        customers_df : pandas.DataFrame
            Customer data to associate orders with
        n_orders : int
            Number of orders to generate
            
        Returns:
        --------
        tuple: (orders_df, order_items_df)
        """
        orders = []
        order_items_list = []
        
        for i in range(1, n_orders + 1):
            # Select random customer
            customer = customers_df.sample(1).iloc[0]
            
            # Generate order date within last year
            order_date = datetime.now() - timedelta(days=np.random.randint(0, 365))
            
            # Number of items in this order (1-7 items)
            n_items = np.random.randint(1, 8)
            
            # Calculate order totals
            total_amount = 0
            total_discount = 0
            
            # Generate items for this order
            for _ in range(n_items):
                product_id, product_info = random.choice(list(self.products.items()))
                quantity = np.random.randint(1, 4)
                unit_price = product_info['price']
                
                # Random discount percentage (0-20%)
                discount_percent = np.random.choice([0, 5, 10, 15, 20], 
                                                   p=[0.4, 0.2, 0.2, 0.1, 0.1])
                discount = (unit_price * quantity * discount_percent) / 100
                final_price = (unit_price * quantity) - discount
                
                total_amount += final_price
                total_discount += discount
                
                # Store item details
                order_items_list.append({
                    'order_id': f'ORD{str(i).zfill(5)}',
                    'product_id': product_id,
                    'product_name': product_info['name'],
                    'category': product_info['category'],
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'discount_percent': discount_percent,
                    'discount_amount': discount,
                    'final_price': final_price,
                    'cost_price': product_info['cost']
                })
            
            # Determine order status based on recency
            if order_date > datetime.now() - timedelta(days=30):
                status = np.random.choice(['Delivered', 'Shipped', 'Processing'], 
                                         p=[0.7, 0.2, 0.1])
            else:
                status = np.random.choice(['Delivered', 'Cancelled', 'Returned'], 
                                         p=[0.85, 0.1, 0.05])
            
            # Create order record
            order = {
                'order_id': f'ORD{str(i).zfill(5)}',
                'customer_id': customer['customer_id'],
                'order_date': order_date,
                'total_amount': total_amount,
                'total_discount': total_discount,
                'payment_method': np.random.choice(self.payment_methods),
                'payment_status': np.random.choice(['Completed', 'Pending', 'Failed'], 
                                                  p=[0.85, 0.1, 0.05]),
                'order_status': status,
                'shipping_city': customer['city'],
                'items_count': n_items
            }
            orders.append(order)
        
        orders_df = pd.DataFrame(orders)
        order_items_df = pd.DataFrame(order_items_list)
        
        return orders_df, order_items_df
    
    def generate_reviews(self, orders_df, n_reviews_ratio=0.6):
        """
        Generate synthetic product reviews
        
        Parameters:
        -----------
        orders_df : pandas.DataFrame
            Order data to associate reviews with
        n_reviews_ratio : float
            Ratio of orders that have reviews (0-1)
            
        Returns:
        --------
        pandas.DataFrame: Review data
        """
        reviews = []
        ratings = [1, 2, 3, 4, 5]
        
        for _, order in orders_df.iterrows():
            # Only delivered orders can have reviews
            if order['order_status'] == 'Delivered' and np.random.random() < n_reviews_ratio:
                # Number of reviews for this order (1-2)
                n_reviews = np.random.randint(1, min(3, order['items_count'] + 1))
                
                for _ in range(n_reviews):
                    product_id = random.choice(list(self.products.keys()))
                    product = self.products[product_id]
                    
                    review = {
                        'review_id': f'R{str(np.random.randint(10000, 99999))}',
                        'order_id': order['order_id'],
                        'customer_id': order['customer_id'],
                        'product_id': product_id,
                        'product_name': product['name'],
                        'rating': np.random.choice(ratings, p=self.rating_weights),
                        'review_date': order['order_date'] + timedelta(days=np.random.randint(1, 30)),
                        'helpful_count': np.random.randint(0, 50)
                    }
                    reviews.append(review)
        
        return pd.DataFrame(reviews)
    
    def generate_all_data(self):
        """
        Generate complete dataset for Mama Earth
        
        Returns:
        --------
        dict: Dictionary containing all generated dataframes
        """
        print("🚀 Generating Mama Earth data...")
        print("📊 Generating customer data...")
        customers = self.generate_customers(1000)
        
        print("🛍️ Generating order data...")
        orders, order_items = self.generate_orders(customers, 5000)
        
        print("📦 Creating product catalog...")
        products = pd.DataFrame.from_dict(self.products, orient='index').reset_index()
        products.columns = ['product_id', 'product_name', 'category', 'price', 'cost']
        
        print("⭐ Generating product reviews...")
        reviews = self.generate_reviews(orders)
        
        print("✅ Data generation complete!")
        
        return {
            'customers': customers,
            'orders': orders,
            'order_items': order_items,
            'products': products,
            'reviews': reviews
        }
    