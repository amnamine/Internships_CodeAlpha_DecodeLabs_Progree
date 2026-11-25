import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
import os

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Mall Customers Segmentation Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Premium Slate/Glassmorphism Vibe)
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1A365D 0%, #319795 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #718096;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f7fafc;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2B6CB0;
    }
    .metric-label {
        font-size: 0.95rem;
        color: #4a5568;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Load data helper
@st.cache_data
def load_data():
    df = pd.read_csv("Mall_Customers.csv")
    
    # Run K-Means to get stable segments
    X = df[['Annual Income (k$)', 'Spending Score (1-100)']].values
    kmeans = KMeans(n_clusters=5, init='k-means++', random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(X)
    
    # Map to meaningful labels
    centroids = kmeans.cluster_centers_
    cluster_labels = {}
    for i in range(5):
        inc, sp = centroids[i]
        if inc < 40 and sp > 60:
            cluster_labels[i] = "Careless (Low Income, High Spending)"
        elif inc < 40 and sp < 40:
            cluster_labels[i] = "Sensible (Low Income, Low Spending)"
        elif inc > 70 and sp > 60:
            cluster_labels[i] = "Target Group (High Income, High Spending)"
        elif inc > 70 and sp < 40:
            cluster_labels[i] = "Savers (High Income, Low Spending)"
        else:
            cluster_labels[i] = "Average (Medium Income, Medium Spending)"
            
    df['Segment'] = df['Cluster'].map(cluster_labels)
    return df, centroids

df_raw, centroids = load_data()

# ----------------- SIDEBAR FILTER CONTROLS -----------------
st.sidebar.image("https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=300&q=80", use_column_width=True)
st.sidebar.title("🔍 Filter Controls")

# Gender filter
gender_opt = ["All", "Male", "Female"]
gender_select = st.sidebar.selectbox("Gender", gender_opt)

# Age Filter
min_age = int(df_raw['Age'].min())
max_age = int(df_raw['Age'].max())
age_range = st.sidebar.slider("Age Range", min_age, max_age, (min_age, max_age))

# Income Filter
min_income = int(df_raw['Annual Income (k$)'].min())
max_income = int(df_raw['Annual Income (k$)'].max())
income_range = st.sidebar.slider("Annual Income Range (k$)", min_income, max_income, (min_income, max_income))

# Apply Filters
df_filtered = df_raw.copy()
if gender_select != "All":
    df_filtered = df_filtered[df_filtered['Gender'] == gender_select]

df_filtered = df_filtered[
    (df_filtered['Age'] >= age_range[0]) & 
    (df_filtered['Age'] <= age_range[1]) &
    (df_filtered['Annual Income (k$)'] >= income_range[0]) &
    (df_filtered['Annual Income (k$)'] <= income_range[1])
]

# ----------------- MAIN CONTENT -----------------
st.markdown('<div class="main-title">🛍️ Mall Customers Segmentation Insights</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">An interactive visual explorer for customer demographics and behavior patterns</div>', unsafe_allow_html=True)

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Selected Customers</div>
        <div class="metric-value">{len(df_filtered)}</div>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Average Customer Age</div>
        <div class="metric-value">{df_filtered['Age'].mean():.1f} yrs</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Annual Income</div>
        <div class="metric-value">${df_filtered['Annual Income (k$)'].mean():.1f}k</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Spending Score</div>
        <div class="metric-value">{df_filtered['Spending Score (1-100)'].mean():.1f}</div>
    </div>
    """, unsafe_allow_html=True)

st.write(" ")
st.write(" ")

# Layout Tabs
tab1, tab2, tab3 = st.tabs(["🎯 Customer Segmentation Map", "👥 Demographics & Distribution", "📊 Detailed Segment Analysis"])

# --- TAB 1: SEGMENTATION MAP ---
with tab1:
    st.header("K-Means Customer Segments")
    st.write("Visualizing customer clusters based on Annual Income and Spending Score. The red stars represent segment centroids.")
    
    # Plotly Interactive 2D scatter plot
    fig_2d = px.scatter(
        df_filtered,
        x='Annual Income (k$)',
        y='Spending Score (1-100)',
        color='Segment',
        hover_name='CustomerID',
        hover_data=['Gender', 'Age', 'Annual Income (k$)', 'Spending Score (1-100)'],
        color_discrete_sequence=["#319795", "#E53E3E", "#D69E2E", "#1A365D", "#2B6CB0"],
        title="Interactive 2D Customer Segments Map"
    )
    
    # Add centroids to the plot
    fig_2d.add_trace(go.Scatter(
        x=centroids[:, 0],
        y=centroids[:, 1],
        mode='markers',
        marker=dict(symbol='star', size=15, color='#F6E05E', line=dict(width=1.5, color='black')),
        name='Centroids',
        showlegend=True
    ))
    
    fig_2d.update_layout(
        legend_title="Customer Persona",
        xaxis_title="Annual Income (k$)",
        yaxis_title="Spending Score (1-100)",
        height=600,
        hovermode="closest",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    fig_2d.update_xaxes(showgrid=True, gridcolor='#E2E8F0')
    fig_2d.update_yaxes(showgrid=True, gridcolor='#E2E8F0')
    
    st.plotly_chart(fig_2d, use_container_width=True)
    
    # 3D Interactive scatter plot
    st.subheader("3D Customer Segmentation Space")
    st.write("Rotate and zoom to see how the segment separation holds when including **Age** as the third dimension.")
    
    fig_3d = px.scatter_3d(
        df_filtered,
        x='Age',
        y='Annual Income (k$)',
        z='Spending Score (1-100)',
        color='Segment',
        hover_name='CustomerID',
        hover_data=['Gender', 'Age', 'Annual Income (k$)', 'Spending Score (1-100)'],
        color_discrete_sequence=["#319795", "#E53E3E", "#D69E2E", "#1A365D", "#2B6CB0"],
        height=700
    )
    fig_3d.update_layout(
        legend_title="Customer Persona",
        margin=dict(l=0, r=0, b=0, t=40)
    )
    st.plotly_chart(fig_3d, use_container_width=True)

# --- TAB 2: DEMOGRAPHICS ---
with tab2:
    st.header("Customer Demographics Analysis")
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        # Age Distribution
        fig_age = px.histogram(
            df_filtered, 
            x="Age", 
            nbins=15, 
            color_discrete_sequence=["#2B6CB0"],
            title="Distribution of Age",
            marginal="box"
        )
        fig_age.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            xaxis_title="Age", 
            yaxis_title="Count"
        )
        st.plotly_chart(fig_age, use_container_width=True)
        
    with col_d2:
        # Income Distribution
        fig_inc = px.histogram(
            df_filtered, 
            x="Annual Income (k$)", 
            nbins=15, 
            color_discrete_sequence=["#D69E2E"],
            title="Distribution of Annual Income",
            marginal="box"
        )
        fig_inc.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            xaxis_title="Annual Income (k$)", 
            yaxis_title="Count"
        )
        st.plotly_chart(fig_inc, use_container_width=True)
        
    col_d3, col_d4 = st.columns(2)
    
    with col_d3:
        # Spending Score Distribution
        fig_spend = px.histogram(
            df_filtered, 
            x="Spending Score (1-100)", 
            nbins=15, 
            color_discrete_sequence=["#319795"],
            title="Distribution of Spending Score",
            marginal="box"
        )
        fig_spend.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            xaxis_title="Spending Score", 
            yaxis_title="Count"
        )
        st.plotly_chart(fig_spend, use_container_width=True)
        
    with col_d4:
        # Gender split
        fig_gender = px.pie(
            df_filtered, 
            names='Gender', 
            hole=0.4, 
            color_discrete_sequence=["#319795", "#1A365D"],
            title="Gender Distribution Breakdown"
        )
        st.plotly_chart(fig_gender, use_container_width=True)

# --- TAB 3: DETAILED SEGMENT ANALYSIS ---
with tab3:
    st.header("Detailed Segment Analytics")
    
    if len(df_filtered) > 0:
        # Calculate cluster summaries
        summary_df = df_filtered.groupby('Segment').agg(
            Customer_Count=('CustomerID', 'count'),
            Avg_Age=('Age', 'mean'),
            Avg_Annual_Income=('Annual Income (k$)', 'mean'),
            Avg_Spending_Score=('Spending Score (1-100)', 'mean')
        ).reset_index()
        
        # Round numerical values
        summary_df['Avg_Age'] = summary_df['Avg_Age'].round(1)
        summary_df['Avg_Annual_Income'] = summary_df['Avg_Annual_Income'].round(1)
        summary_df['Avg_Spending_Score'] = summary_df['Avg_Spending_Score'].round(1)
        
        st.subheader("Statistical Summary of Segments")
        st.dataframe(summary_df, use_container_width=True)
        
        # Segment Size Breakdown
        fig_bar = px.bar(
            summary_df,
            x='Segment',
            y='Customer_Count',
            color='Segment',
            color_discrete_sequence=["#319795", "#E53E3E", "#D69E2E", "#1A365D", "#2B6CB0"],
            title="Customer Count per Segment"
        )
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Segment characteristics comparison
        st.subheader("Segment Performance Profiling")
        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            fig_box_inc = px.box(
                df_filtered,
                x='Segment',
                y='Annual Income (k$)',
                color='Segment',
                color_discrete_sequence=["#319795", "#E53E3E", "#D69E2E", "#1A365D", "#2B6CB0"],
                title="Annual Income Distributions by Segment"
            )
            fig_box_inc.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig_box_inc, use_container_width=True)
            
        with col_comp2:
            fig_box_spd = px.box(
                df_filtered,
                x='Segment',
                y='Spending Score (1-100)',
                color='Segment',
                color_discrete_sequence=["#319795", "#E53E3E", "#D69E2E", "#1A365D", "#2B6CB0"],
                title="Spending Score Distributions by Segment"
            )
            fig_box_spd.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig_box_spd, use_container_width=True)
            
    else:
        st.warning("No data points match the selected filters. Please adjust the sidebar controls.")
