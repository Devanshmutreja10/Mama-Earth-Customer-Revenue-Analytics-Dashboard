# visualizations.py
"""
Visualization Module for Mama Earth
Creates all charts and graphs for the dashboard
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class MamaEarthVisualizations:
    """Create interactive visualizations for the dashboard"""
    
    def __init__(self):
        """Initialize the visualization module"""
        self.color_palette = {
            'primary': '#2E7D32',
            'secondary': '#FFA000',
            'accent': '#1976D2',
            'danger': '#D32F2F',
            'success': '#388E3C',
            'warning': '#F57C00'
        }
    
    def plot_revenue_trend(self, df_orders, period='daily'):
        """
        Plot revenue trend over time
        
        Parameters:
        -----------
        df_orders : pandas.DataFrame
            Order data with order_date column
        period : str
            Aggregation period ('daily', 'weekly', 'monthly')
            
        Returns:
        --------
        plotly.graph_objects.Figure
        """
        # Aggregate based on period
        if period == 'daily':
            df_agg = df_orders.groupby(df_orders['order_date'].dt.date)['total_amount'].sum().reset_index()
            df_agg.columns = ['Date', 'Revenue']
            title = 'Daily Revenue Trend'
        elif period == 'weekly':
            df_agg = df_orders.groupby(df_orders['order_date'].dt.isocalendar().week)['total_amount'].sum().reset_index()
            df_agg.columns = ['Week', 'Revenue']
            title = 'Weekly Revenue Trend'
        else:  # monthly
            df_agg = df_orders.groupby(df_orders['order_date'].dt.to_period('M'))['total_amount'].sum().reset_index()
            df_agg['Month'] = df_agg['order_date'].astype(str)
            df_agg.columns = ['Month', 'Revenue']
            title = 'Monthly Revenue Trend'
        
        fig = px.line(df_agg, x=df_agg.columns[0], y='Revenue', 
                      title=title,
                      labels={'Revenue': 'Revenue (₹)'},
                      color_discrete_sequence=[self.color_palette['primary']])
        
        fig.update_layout(
            height=400,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_traces(line=dict(width=2))
        
        return fig
    
    def plot_category_performance(self, df_order_items):
        """
        Plot category-wise performance
        
        Parameters:
        -----------
        df_order_items : pandas.DataFrame
            Order items data with category, final_price, quantity
            
        Returns:
        --------
        plotly.graph_objects.Figure
        """
        category_metrics = df_order_items.groupby('category').agg({
            'final_price': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Revenue by Category', 'Units Sold by Category'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        fig.add_trace(
            go.Bar(x=category_metrics['category'], 
                   y=category_metrics['final_price'],
                   name='Revenue', 
                   marker_color=self.color_palette['primary'],
                   text=category_metrics['final_price'].apply(lambda x: f'₹{x:,.0f}'),
                   textposition='auto'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=category_metrics['category'], 
                   y=category_metrics['quantity'],
                   name='Units Sold', 
                   marker_color=self.color_palette['secondary'],
                   text=category_metrics['quantity'],
                   textposition='auto'),
            row=1, col=2
        )
        
        fig.update_layout(
            height=400, 
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_xaxes(title_text="Category", row=1, col=1)
        fig.update_xaxes(title_text="Category", row=1, col=2)
        fig.update_yaxes(title_text="Revenue (₹)", row=1, col=1)
        fig.update_yaxes(title_text="Units Sold", row=1, col=2)
        
        return fig
    
    def plot_top_products(self, df_order_items, metric='revenue', n=10):
        """
        Plot top performing products
        
        Parameters:
        -----------
        df_order_items : pandas.DataFrame
            Order items data
        metric : str
            Metric to use ('revenue' or 'quantity')
        n : int
            Number of top products to show
            
        Returns:
        --------
        plotly.graph_objects.Figure
        """
        if metric == 'revenue':
            product_metrics = df_order_items.groupby('product_name')['final_price'].sum()
            title = f'Top {n} Products by Revenue'
            x_title = 'Revenue (₹)'
            color = self.color_palette['primary']
        else:
            product_metrics = df_order_items.groupby('product_name')['quantity'].sum()
            title = f'Top {n} Products by Units Sold'
            x_title = 'Units Sold'
            color = self.color_palette['secondary']
        
        product_metrics = product_metrics.sort_values(ascending=False).head(n)
        
        fig = px.bar(x=product_metrics.values, 
                     y=product_metrics.index, 
                     orientation='h', 
                     title=title,
                     labels={'x': x_title, 'y': 'Product Name'},
                     color_discrete_sequence=[color])
        
        fig.update_layout(
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_traces(text=product_metrics.values, textposition='outside')
        
        return fig
    
    def plot_geographic_distribution(self, df_orders, metric='orders'):
        """
        Plot geographic distribution of orders/revenue
        
        Parameters:
        -----------
        df_orders : pandas.DataFrame
            Order data with shipping_city column
        metric : str
            Metric to plot ('orders' or 'revenue')
            
        Returns:
        --------
        plotly.graph_objects.Figure
        """
        if metric == 'orders':
            city_data = df_orders.groupby('shipping_city').size().reset_index(name='value')
            title = 'Order Distribution by City'
            y_title = 'Number of Orders'
            color = self.color_palette['primary']
        else:
            city_data = df_orders.groupby('shipping_city')['total_amount'].sum().reset_index(name='value')
            title = 'Revenue Distribution by City'
            y_title = 'Revenue (₹)'
            color = self.color_palette['secondary']
        
        fig = px.bar(city_data, 
                     x='shipping_city', 
                     y='value',
                     title=title,
                     labels={'shipping_city': 'City', 'value': y_title},
                     color_discrete_sequence=[color])
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    def plot_customer_segments(self, rfm_data):
        """
        Plot customer segmentation based on RFM
        
        Parameters:
        -----------
        rfm_data : pandas.DataFrame
            RFM scores with segment column
            
        Returns:
        --------
        plotly.graph_objects.Figure
        """
        segment_counts = rfm_data['segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Count']
        
        fig = px.pie(segment_counts, 
                     values='Count', 
                     names='Segment', 
                     title='Customer Segmentation by RFM',
                     color_discrete_sequence=px.colors.qualitative.Set3)
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    def plot_rating_distribution(self, df_reviews):
        """
        Plot product rating distribution
        
        Parameters:
        -----------
        df_reviews : pandas.DataFrame
            Review data with rating column
            
        Returns:
        --------
        plotly.graph_objects.Figure
        """
        if len(df_reviews) == 0:
            return None
        
        rating_counts = df_reviews['rating'].value_counts().sort_index().reset_index()
        rating_counts.columns = ['Rating', 'Count']
        
        # Calculate average rating
        avg_rating = df_reviews['rating'].mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=rating_counts['Rating'],
            y=rating_counts['Count'],
            marker_color=self.color_palette['accent'],
            text=rating_counts['Count'],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=f'Product Rating Distribution (Average Rating: {avg_rating:.2f}⭐)',
            xaxis_title='Rating (1-5)',
            yaxis_title='Number of Reviews',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def plot_payment_method_distribution(self, df_orders):
        """
        Plot payment method distribution
        
        Parameters:
        -----------
        df_orders : pandas.DataFrame
            Order data with payment_method column
            
        Returns:
        --------
        plotly.graph_objects.Figure
        """
        payment_counts = df_orders['payment_method'].value_counts().reset_index()
        payment_counts.columns = ['Payment Method', 'Count']
        
        fig = px.pie(payment_counts, 
                     values='Count', 
                     names='Payment Method',
                     title='Payment Method Distribution',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    def plot_order_status_distribution(self, df_orders):
        """
        Plot order status distribution
        
        Parameters:
        -----------
        df_orders : pandas.DataFrame
            Order data with order_status column
            
        Returns:
        --------
        plotly.graph_objects.Figure
        """
        status_counts = df_orders['order_status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        # Define color mapping based on status
        color_map = {
            'Delivered': self.color_palette['success'],
            'Shipped': self.color_palette['primary'],
            'Processing': self.color_palette['warning'],
            'Cancelled': self.color_palette['danger'],
            'Returned': self.color_palette['accent']
        }
        
        colors = [color_map.get(status, '#999999') for status in status_counts['Status']]
        
        fig = px.bar(status_counts, 
                     x='Status', 
                     y='Count',
                     title='Order Status Distribution',
                     labels={'Count': 'Number of Orders'},
                     color='Status',
                     color_discrete_sequence=colors)
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        fig.update_traces(text=status_counts['Count'], textposition='outside')
        
        return fig