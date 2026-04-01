# config.py
"""
Configuration file for Mama Earth Analytics Dashboard
Contains all imports, constants, and configuration settings
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Streamlit page configuration
STREAMLIT_CONFIG = {
    "page_title": "Mama Earth Analytics Dashboard",
    "page_icon": "🌍",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Mama Earth product catalog
PRODUCT_CATALOG = {
    'P001': {'name': 'Ubtan Face Wash', 'category': 'Face Care', 'price': 299, 'cost': 150},
    'P002': {'name': 'Vitamin C Face Serum', 'category': 'Face Care', 'price': 599, 'cost': 300},
    'P003': {'name': 'Onion Hair Oil', 'category': 'Hair Care', 'price': 399, 'cost': 180},
    'P004': {'name': 'Bamboo Hair Shampoo', 'category': 'Hair Care', 'price': 349, 'cost': 160},
    'P005': {'name': 'Coffee Face Scrub', 'category': 'Face Care', 'price': 249, 'cost': 120},
    'P006': {'name': 'Body Lotion', 'category': 'Body Care', 'price': 399, 'cost': 200},
    'P007': {'name': 'Lip Balm', 'category': 'Body Care', 'price': 149, 'cost': 70},
    'P008': {'name': 'Baby Lotion', 'category': 'Baby Care', 'price': 299, 'cost': 140},
    'P009': {'name': 'Baby Shampoo', 'category': 'Baby Care', 'price': 249, 'cost': 120},
    'P010': {'name': 'Face Moisturizer', 'category': 'Face Care', 'price': 449, 'cost': 220}
}

# Geographic and payment configurations
CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 
          'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow']

PAYMENT_METHODS = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'COD']

# Rating weights for realistic review distribution
RATING_WEIGHTS = [0.05, 0.1, 0.15, 0.3, 0.4]  # For ratings 1-5

# Custom CSS for styling
CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(120deg, #f6f9fc 0%, #e6f3e6 100%);
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .section-header {
        font-size: 1.5rem;
        color: #1E3A8A;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #2E7D32;
        padding-left: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
    }
</style>
"""
