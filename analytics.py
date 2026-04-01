# analytics.py
"""
Analytics Module for Mama Earth
Calculates KPIs and business metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MamaEarthAnalytics:
    """Calculate business metrics and KPIs"""
    
    def __init__(self, data_dict):
        """
        Initialize with cleaned data
        
        Parameters:
        -----------
        data_dict : dict
            Dictionary containing cleaned dataframes
        """
        self.data = data_dict
        
    def calculate_kpis(self, date_range=None):
        """
        Calculate key performance indicators
        
        Parameters:
        -----------
        date_range : tuple, optional
            (start_date, end_date) for filtering
            
        Returns:
        --------
        dict: Dictionary of KPIs
        """
        # Filter by date if provided
        if date_range:
            start_date, end_date = date_range
            mask = (self.data['orders']['order_date'] >= start_date) & \
                   (self.data['orders']['order_date'] <= end_date)
            filtered_orders = self.data['orders'][mask]
            filtered_items = self.data['order_items'][
                self.data['order_items']['order_id'].isin(filtered_orders['order_id'])
            ]
            filtered_customers = self.data['customers'][
                self.data['customers']['customer_id'].isin(filtered_orders['customer_id'])
            ]
        else:
            filtered_orders = self.data['orders']
            filtered_items = self.data['order_items']
            filtered_customers = self.data['customers']
        
        # Revenue metrics
        total_revenue = filtered_orders['total_amount'].sum()
        total_discount = filtered_orders['total_discount'].sum()
        total_profit = filtered_items['profit'].sum() if 'profit' in filtered_items.columns else 0
        
        # Order metrics
        total_orders = len(filtered_orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Customer metrics
        unique_customers = filtered_customers['customer_id'].nunique()
        avg_customer_value = total_revenue / unique_customers if unique_customers > 0 else 0
        
        # Cancellation and return rates
        cancelled_orders = len(filtered_orders[filtered_orders['order_status'] == 'Cancelled'])
        returned_orders = len(filtered_orders[filtered_orders['order_status'] == 'Returned'])
        cancellation_rate = (cancelled_orders / total_orders) * 100 if total_orders > 0 else 0
        return_rate = (returned_orders / total_orders) * 100 if total_orders > 0 else 0
        
        # Payment method distribution
        payment_dist = filtered_orders['payment_method'].value_counts().to_dict()
        
        # Order status distribution
        status_dist = filtered_orders['order_status'].value_counts().to_dict()
        
        return {
            'total_revenue': total_revenue,
            'total_discount': total_discount,
            'total_profit': total_profit,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'unique_customers': unique_customers,
            'avg_customer_value': avg_customer_value,
            'cancellation_rate': cancellation_rate,
            'return_rate': return_rate,
            'payment_distribution': payment_dist,
            'status_distribution': status_dist
        }
    
    def calculate_rfm_scores(self):
        """
        Calculate RFM (Recency, Frequency, Monetary) scores for customers
        
        Returns:
        --------
        pandas.DataFrame: Customer RFM scores
        """
        # Get the latest order date
        latest_date = self.data['orders']['order_date'].max()
        
        # Calculate RFM metrics
        rfm = self.data['orders'].groupby('customer_id').agg({
            'order_date': lambda x: (latest_date - x.max()).days,  # Recency
            'order_id': 'count',  # Frequency
            'total_amount': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        # Create RFM scores (1-5 scale)
        rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
        
        # Combine RFM score
        rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
        
        # Segment customers
        def get_segment(row):
            if row['r_score'] >= 4 and row['f_score'] >= 4 and row['m_score'] >= 4:
                return 'Champions'
            elif row['r_score'] >= 3 and row['f_score'] >= 3:
                return 'Loyal Customers'
            elif row['r_score'] >= 4 and row['f_score'] <= 2:
                return 'New Customers'
            elif row['r_score'] <= 2 and row['f_score'] >= 3:
                return 'At Risk'
            else:
                return 'Others'
        
        rfm['segment'] = rfm.apply(get_segment, axis=1)
        
        return rfm
    
    def calculate_product_metrics(self):
        """
        Calculate product performance metrics
        
        Returns:
        --------
        pandas.DataFrame: Product metrics
        """
        product_metrics = self.data['order_items'].groupby('product_id').agg({
            'product_name': 'first',
            'category': 'first',
            'quantity': 'sum',
            'final_price': 'sum',
            'profit': 'sum' if 'profit' in self.data['order_items'].columns else 'final_price'
        }).reset_index()
        
        product_metrics.columns = ['product_id', 'product_name', 'category', 
                                   'units_sold', 'revenue', 'profit']
        
        # Calculate average selling price
        product_metrics['avg_price'] = product_metrics['revenue'] / product_metrics['units_sold']
        
        # Calculate profit margin
        product_metrics['profit_margin'] = (product_metrics['profit'] / product_metrics['revenue']) * 100
        
        # Add review metrics if available
        if len(self.data['reviews']) > 0:
            review_metrics = self.data['reviews'].groupby('product_id').agg({
                'rating': 'mean',
                'review_id': 'count'
            }).reset_index()
            review_metrics.columns = ['product_id', 'avg_rating', 'review_count']
            product_metrics = product_metrics.merge(review_metrics, on='product_id', how='left')
            product_metrics['avg_rating'] = product_metrics['avg_rating'].fillna(0)
            product_metrics['review_count'] = product_metrics['review_count'].fillna(0)
        
        return product_metrics
    
    def calculate_time_series_metrics(self):
        """
        Calculate time-based metrics for trend analysis
        
        Returns:
        --------
        dict: Dictionary of time series dataframes
        """
        df_orders = self.data['orders'].copy()
        df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
        
        # Daily metrics
        daily = df_orders.groupby(df_orders['order_date'].dt.date).agg({
            'total_amount': 'sum',
            'order_id': 'count',
            'total_discount': 'sum'
        }).reset_index()
        daily.columns = ['date', 'revenue', 'orders', 'discount']
        
        # Monthly metrics
        monthly = df_orders.groupby(df_orders['order_date'].dt.to_period('M')).agg({
            'total_amount': 'sum',
            'order_id': 'count',
            'total_discount': 'sum'
        }).reset_index()
        monthly.columns = ['month', 'revenue', 'orders', 'discount']
        monthly['month'] = monthly['month'].astype(str)
        
        # Weekly metrics
        weekly = df_orders.groupby(df_orders['order_date'].dt.isocalendar().week).agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).reset_index()
        weekly.columns = ['week', 'revenue', 'orders']
        
        return {
            'daily': daily,
            'monthly': monthly,
            'weekly': weekly
        }
    
    def calculate_geographic_metrics(self):
        """
        Calculate geographic performance metrics
        
        Returns:
        --------
        pandas.DataFrame: City-wise metrics
        """
        city_metrics = self.data['orders'].groupby('shipping_city').agg({
            'order_id': 'count',
            'total_amount': 'sum',
            'total_discount': 'sum'
        }).reset_index()
        
        city_metrics.columns = ['city', 'order_count', 'revenue', 'discount']
        
        # Calculate average order value per city
        city_metrics['avg_order_value'] = city_metrics['revenue'] / city_metrics['order_count']
        
        # Add customer count per city
        customers_per_city = self.data['customers'].groupby('city').size().reset_index(name='customer_count')
        city_metrics = city_metrics.merge(customers_per_city, on='city', how='left')
        
        return city_metrics
    