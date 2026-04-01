# app.py
"""
Main Streamlit Application for Mama Earth Analytics Dashboard
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# Import custom modules
from config import STREAMLIT_CONFIG, CUSTOM_CSS
from data_generator import MamaEarthDataGenerator
from data_cleaner import DataCleaner
from analytics import MamaEarthAnalytics
from visualizations import MamaEarthVisualizations

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'data_generated' not in st.session_state:
        st.session_state.data_generated = False
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'date_range': None,
            'category': 'All',
            'city': 'All',
            'payment_method': 'All'
        }

def generate_and_clean_data():
    """Generate synthetic data and clean it"""
    with st.spinner("🌱 Growing Mama Earth data..."):
        # Generate data
        generator = MamaEarthDataGenerator(seed=42)
        raw_data = generator.generate_all_data()
        
        # Clean data
        cleaner = DataCleaner(raw_data)
        cleaned_data = cleaner.clean_all()
        
        st.session_state.data = cleaned_data
        st.session_state.data_generated = True
        
    return cleaned_data

def apply_filters(data, filters):
    """Apply user-selected filters to the data"""
    filtered_data = {}
    
    # Apply date filter to orders
    orders = data['orders'].copy()
    if filters['date_range'] and len(filters['date_range']) == 2:
        start_date, end_date = filters['date_range']
        orders = orders[
            (orders['order_date'] >= pd.to_datetime(start_date)) & 
            (orders['order_date'] <= pd.to_datetime(end_date))
        ]
    
    # Apply category filter
    if filters['category'] != 'All':
        order_items = data['order_items'].copy()
        order_items = order_items[order_items['category'] == filters['category']]
        orders = orders[orders['order_id'].isin(order_items['order_id'])]
    
    # Apply city filter
    if filters['city'] != 'All':
        orders = orders[orders['shipping_city'] == filters['city']]
    
    # Apply payment method filter
    if filters['payment_method'] != 'All':
        orders = orders[orders['payment_method'] == filters['payment_method']]
    
    # Filter all datasets based on filtered orders
    order_ids = orders['order_id'].tolist()
    customer_ids = orders['customer_id'].unique()
    
    filtered_data['orders'] = orders
    filtered_data['order_items'] = data['order_items'][
        data['order_items']['order_id'].isin(order_ids)
    ]
    filtered_data['customers'] = data['customers'][
        data['customers']['customer_id'].isin(customer_ids)
    ]
    filtered_data['products'] = data['products']
    filtered_data['reviews'] = data['reviews'][
        data['reviews']['order_id'].isin(order_ids)
    ] if len(data['reviews']) > 0 else pd.DataFrame()
    
    return filtered_data

def render_sidebar_filters(data):
    """Render sidebar with all filters"""
    st.sidebar.title("🌍 Mama Earth")
    st.sidebar.markdown("---")
    
    # Date range filter
    st.sidebar.subheader("📅 Date Range")
    min_date = data['orders']['order_date'].min().date()
    max_date = data['orders']['order_date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Category filter
    st.sidebar.subheader("🏷️ Category")
    categories = ['All'] + list(data['products']['category'].unique())
    category = st.sidebar.selectbox("Product Category", categories)
    
    # City filter
    st.sidebar.subheader("📍 City")
    cities = ['All'] + list(data['orders']['shipping_city'].unique())
    city = st.sidebar.selectbox("City", cities)
    
    # Payment method filter
    st.sidebar.subheader("💳 Payment Method")
    payment_methods = ['All'] + list(data['orders']['payment_method'].unique())
    payment_method = st.sidebar.selectbox("Payment Method", payment_methods)
    
    # Update filters in session state
    st.session_state.filters = {
        'date_range': date_range,
        'category': category,
        'city': city,
        'payment_method': payment_method
    }
    
    return st.session_state.filters

def render_kpi_cards(analytics, filtered_data):
    """Render KPI metrics in cards"""
    # Calculate KPIs
    kpis = analytics.calculate_kpis()
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>💰 Total Revenue</h3>
            <h2>₹{:,.0f}</h2>
        </div>
        """.format(kpis['total_revenue']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>📊 Total Orders</h3>
            <h2>{:,}</h2>
        </div>
        """.format(kpis['total_orders']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h3>👥 Unique Customers</h3>
            <h2>{:,}</h2>
        </div>
        """.format(kpis['unique_customers']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <h3>💵 Avg Order Value</h3>
            <h2>₹{:,.0f}</h2>
        </div>
        """.format(kpis['avg_order_value']), unsafe_allow_html=True)
    
    # Second row of KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>📈 Total Profit</h3>
            <h2>₹{:,.0f}</h2>
        </div>
        """.format(kpis['total_profit']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>🎁 Total Discount</h3>
            <h2>₹{:,.0f}</h2>
        </div>
        """.format(kpis['total_discount']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h3>❌ Cancellation Rate</h3>
            <h2>{:.1f}%</h2>
        </div>
        """.format(kpis['cancellation_rate']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <h3>👤 Avg Customer Value</h3>
            <h2>₹{:,.0f}</h2>
        </div>
        """.format(kpis['avg_customer_value']), unsafe_allow_html=True)

def render_charts(visualizations, filtered_data):
    """Render all charts and visualizations"""
    st.markdown("---")
    st.markdown("<h2 class='section-header'>📈 Business Analytics</h2>", 
                unsafe_allow_html=True)
    
    # Revenue trend
    st.markdown("<h3 class='section-header'>Revenue Trend</h3>", 
                unsafe_allow_html=True)
    fig_revenue = visualizations.plot_revenue_trend(filtered_data['orders'])
    st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Category performance and top products
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class='section-header'>Category Performance</h3>", 
                   unsafe_allow_html=True)
        fig_category = visualizations.plot_category_performance(filtered_data['order_items'])
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.markdown("<h3 class='section-header'>Top Products</h3>", 
                   unsafe_allow_html=True)
        fig_products = visualizations.plot_top_products(filtered_data['order_items'])
        st.plotly_chart(fig_products, use_container_width=True)
    
    # Geographic and customer segmentation
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class='section-header'>Geographic Distribution</h3>", 
                   unsafe_allow_html=True)
        fig_geo = visualizations.plot_geographic_distribution(filtered_data['orders'])
        st.plotly_chart(fig_geo, use_container_width=True)
    
    with col2:
        st.markdown("<h3 class='section-header'>Payment Methods</h3>", 
                   unsafe_allow_html=True)
        fig_payment = visualizations.plot_payment_method_distribution(filtered_data['orders'])
        st.plotly_chart(fig_payment, use_container_width=True)
    
    # Order status and ratings
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class='section-header'>Order Status</h3>", 
                   unsafe_allow_html=True)
        fig_status = visualizations.plot_order_status_distribution(filtered_data['orders'])
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        if len(filtered_data['reviews']) > 0:
            st.markdown("<h3 class='section-header'>Product Ratings</h3>", 
                       unsafe_allow_html=True)
            fig_ratings = visualizations.plot_rating_distribution(filtered_data['reviews'])
            if fig_ratings:
                st.plotly_chart(fig_ratings, use_container_width=True)
    
    # Customer segmentation
    st.markdown("<h3 class='section-header'>Customer Segmentation</h3>", 
               unsafe_allow_html=True)
    analytics = MamaEarthAnalytics(filtered_data)
    rfm_data = analytics.calculate_rfm_scores()
    fig_segments = visualizations.plot_customer_segments(rfm_data)
    st.plotly_chart(fig_segments, use_container_width=True)

def render_data_tables(filtered_data):
    """Render data tables with download options"""
    st.markdown("---")
    st.markdown("<h2 class='section-header'>📊 Data Explorer</h2>", 
                unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Orders", "Order Items", "Customers", "Products"])
    
    with tab1:
        st.dataframe(filtered_data['orders'].head(100))
        st.caption(f"Showing {len(filtered_data['orders'])} orders")
        
        # Download button
        csv = filtered_data['orders'].to_csv(index=False)
        st.download_button(
            label="📥 Download Orders (CSV)",
            data=csv,
            file_name="mama_earth_orders.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.dataframe(filtered_data['order_items'].head(100))
        st.caption(f"Showing {len(filtered_data['order_items'])} order items")
        
        csv = filtered_data['order_items'].to_csv(index=False)
        st.download_button(
            label="📥 Download Order Items (CSV)",
            data=csv,
            file_name="mama_earth_order_items.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.dataframe(filtered_data['customers'].head(100))
        st.caption(f"Showing {len(filtered_data['customers'])} customers")
        
        csv = filtered_data['customers'].to_csv(index=False)
        st.download_button(
            label="📥 Download Customers (CSV)",
            data=csv,
            file_name="mama_earth_customers.csv",
            mime="text/csv"
        )
    
    with tab4:
        st.dataframe(filtered_data['products'])
        st.caption("Product Catalog")
        
        csv = filtered_data['products'].to_csv(index=False)
        st.download_button(
            label="📥 Download Products (CSV)",
            data=csv,
            file_name="mama_earth_products.csv",
            mime="text/csv"
        )

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("<h1 class='main-header'>🌍 Mama Earth Customer & Revenue Analytics Dashboard</h1>", 
                unsafe_allow_html=True)
    
    # Load or generate data
    if not st.session_state.data_generated:
        data = generate_and_clean_data()
    else:
        data = st.session_state.data
    
    # Render sidebar filters
    filters = render_sidebar_filters(data)
    
    # Apply filters to data
    filtered_data = apply_filters(data, filters)
    
    # Initialize analytics and visualizations
    analytics = MamaEarthAnalytics(filtered_data)
    visualizations = MamaEarthVisualizations()
    
    # Render KPIs
    render_kpi_cards(analytics, filtered_data)
    
    # Render charts
    render_charts(visualizations, filtered_data)
    
    # Render data tables
    render_data_tables(filtered_data)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🌱 Mama Earth Analytics Dashboard | Built with Streamlit & Plotly</p>
        <p>Data last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()