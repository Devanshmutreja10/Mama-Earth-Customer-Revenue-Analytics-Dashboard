# data_cleaner.py
"""
Data Cleaning Module for Mama Earth
Cleans and validates all generated data
"""

import pandas as pd
import numpy as np
from datetime import datetime

class DataCleaner:
    """Clean and validate the generated data"""
    
    def __init__(self, data_dict):
        """
        Initialize with raw data dictionary
        
        Parameters:
        -----------
        data_dict : dict
            Dictionary containing raw dataframes
        """
        self.data = data_dict
        
    def clean_customers(self):
        """Clean and validate customer data"""
        df = self.data['customers'].copy()
        
        # Remove duplicate customers
        initial_count = len(df)
        df = df.drop_duplicates(subset=['customer_id'])
        print(f"Removed {initial_count - len(df)} duplicate customers")
        
        # Handle missing values
        df['age'] = df['age'].fillna(df['age'].median())
        df['loyalty_points'] = df['loyalty_points'].fillna(0)
        
        # Validate and clean data
        df['age'] = df['age'].clip(18, 100)  # Age between 18-100
        df['email'] = df['email'].str.lower().str.strip()  # Standardize email
        
        # Convert signup_date to datetime
        df['signup_date'] = pd.to_datetime(df['signup_date'])
        
        # Add derived columns
        df['customer_tenure_days'] = (datetime.now() - df['signup_date']).dt.days
        df['loyalty_tier'] = pd.cut(df['loyalty_points'], 
                                    bins=[0, 1000, 2500, 5000, float('inf')],
                                    labels=['Bronze', 'Silver', 'Gold', 'Platinum'])
        
        print(f"✅ Cleaned {len(df)} customer records")
        return df
    
    def clean_orders(self):
        """Clean and validate order data"""
        df = self.data['orders'].copy()
        
        # Convert date to datetime
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # Remove duplicate orders
        initial_count = len(df)
        df = df.drop_duplicates(subset=['order_id'])
        print(f"Removed {initial_count - len(df)} duplicate orders")
        
        # Handle negative values
        df['total_amount'] = df['total_amount'].clip(lower=0)
        df['total_discount'] = df['total_discount'].clip(lower=0)
        
        # Validate status combinations
        invalid_status = (df['payment_status'] == 'Failed') & (df['order_status'] == 'Delivered')
        df.loc[invalid_status, 'order_status'] = 'Cancelled'
        
        # Add derived columns for time-based analysis
        df['order_month'] = df['order_date'].dt.to_period('M')
        df['order_year'] = df['order_date'].dt.year
        df['order_quarter'] = df['order_date'].dt.quarter
        df['order_weekday'] = df['order_date'].dt.day_name()
        df['order_hour'] = df['order_date'].dt.hour
        
        # Calculate order value ranges
        df['order_value_tier'] = pd.cut(df['total_amount'],
                                        bins=[0, 500, 1000, 2500, 5000, float('inf')],
                                        labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
        
        print(f"✅ Cleaned {len(df)} order records")
        return df
    
    def clean_order_items(self):
        """Clean and validate order items data"""
        df = self.data['order_items'].copy()
        
        # Remove duplicate items
        initial_count = len(df)
        df = df.drop_duplicates()
        print(f"Removed {initial_count - len(df)} duplicate order items")
        
        # Validate calculations
        calculated_final_price = (df['unit_price'] * df['quantity']) - df['discount_amount']
        df['final_price_calc'] = calculated_final_price
        
        # Check for calculation mismatches
        mismatch = ~np.isclose(df['final_price'], df['final_price_calc'], rtol=0.01)
        if mismatch.any():
            print(f"⚠️ Found {mismatch.sum()} items with price calculation mismatches")
            df.loc[mismatch, 'final_price'] = df.loc[mismatch, 'final_price_calc']
        
        # Calculate profit per item
        df['profit'] = df['final_price'] - (df['cost_price'] * df['quantity'])
        df['profit_margin'] = (df['profit'] / df['final_price']) * 100
        
        # Clean discount percentages
        df['discount_percent'] = df['discount_percent'].clip(0, 100)
        
        print(f"✅ Cleaned {len(df)} order item records")
        return df
    
    def clean_reviews(self):
        """Clean and validate reviews data"""
        df = self.data['reviews'].copy() if len(self.data['reviews']) > 0 else pd.DataFrame()
        
        if len(df) > 0:
            # Remove duplicate reviews
            initial_count = len(df)
            df = df.drop_duplicates(subset=['review_id'])
            print(f"Removed {initial_count - len(df)} duplicate reviews")
            
            # Convert date to datetime
            df['review_date'] = pd.to_datetime(df['review_date'])
            
            # Validate rating range
            df['rating'] = df['rating'].clip(1, 5)
            
            # Add rating categories
            df['rating_category'] = pd.cut(df['rating'],
                                           bins=[0, 2, 3, 4, 5],
                                           labels=['Poor', 'Average', 'Good', 'Excellent'])
            
            print(f"✅ Cleaned {len(df)} review records")
        else:
            print("⚠️ No review data found")
        
        return df
    
    def clean_all(self):
        """Clean all datasets"""
        print("\n🧹 Starting data cleaning process...")
        print("-" * 40)
        
        customers = self.clean_customers()
        orders = self.clean_orders()
        order_items = self.clean_order_items()
        reviews = self.clean_reviews()
        
        print("-" * 40)
        print("✅ Data cleaning complete!")
        
        return {
            'customers': customers,
            'orders': orders,
            'order_items': order_items,
            'products': self.data['products'],  # Products already clean
            'reviews': reviews
        }
    