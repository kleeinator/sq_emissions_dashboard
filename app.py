# python code converted to Streamlit + design elements

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# ----------------------------
# Card Container Function
# ----------------------------
def card_container(content_html):
    st.markdown(
        f"""
        <div style="
            background-color:#f9f9f9;
            padding:20px;
            border-radius:15px;
            margin-bottom:20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        ">
            {content_html}
        
        """,
        unsafe_allow_html=True
    )

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="Square Client Emissions Dashboard",
    layout="centered"
)

# ----------------------------
# Centered Styling
# ----------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

h1, h2 {
    text-align: center;
    font-weight: 600;
}

div[data-testid="metric-container"] {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)



# ----------------------------
# Scope 2 Parameters
# ----------------------------
INDUSTRY_AVG_KWH = {
    "restaurant": 6000,
    "retail_clothing": 4500,
    "medical_office": 2000
}

STATE_GRID_INTENSITY = {
    "Texas": 0.4,
    "California": 0.26
}

KWH_UNCERTAINTY_PERCENT = 0.05

# ----------------------------
# Scope 3 Parameters
# ----------------------------
INDUSTRY_SCOPE3_FACTORS = {
    "restaurant": 0.194,
    "retail_clothing": 0.138,
    "medical_office": 0.096
}

SCOPE3_UNCERTAINTY_PERCENT = 0.064

# ----------------------------
# Monte Carlo Model
# ----------------------------
def calculate_total_emissions(industry, state, monthly_revenue, n_simulations=3000):
    mean_factor = INDUSTRY_SCOPE3_FACTORS[industry]
    std_factor = mean_factor * SCOPE3_UNCERTAINTY_PERCENT
    sampled_scope3_factors = np.random.normal(loc=mean_factor, scale=std_factor, size=n_simulations)
    sampled_scope3_factors = np.clip(sampled_scope3_factors, 0, None)
    scope3_samples = monthly_revenue * sampled_scope3_factors

    avg_kwh = INDUSTRY_AVG_KWH[industry]
    std_kwh = avg_kwh * KWH_UNCERTAINTY_PERCENT
    sampled_kwh = np.random.normal(loc=avg_kwh, scale=std_kwh, size=n_simulations)
    sampled_kwh = np.clip(sampled_kwh, 0, None)
    
    grid_intensity = STATE_GRID_INTENSITY[state]
    scope2_samples = sampled_kwh * grid_intensity
    
    total_samples = scope3_samples + scope2_samples
    
    return {
        "mean_total": np.mean(total_samples),
        "p5_total": np.percentile(total_samples, 5),
        "p95_total": np.percentile(total_samples, 95),
        "mean_scope3": np.mean(scope3_samples),
        "mean_scope2": np.mean(scope2_samples),
        "total_samples": total_samples
    }

# ----------------------------
# Benchmark Dataset
# ----------------------------
@st.cache_data
def generate_benchmark_dataset(n=200):
    industries = list(INDUSTRY_SCOPE3_FACTORS.keys())
    states = ["Texas", "California"]
    data = []
    for _ in range(n):
        industry = np.random.choice(industries)
        state = np.random.choice(states)
        monthly_revenue = np.random.lognormal(mean=10, sigma=0.6)
        emissions = calculate_total_emissions(industry, state, monthly_revenue)
        data.append({
            "industry": industry,
            "state": state,
            "mean_total_emissions": emissions["mean_total"]
        })
    return pd.DataFrame(data)

benchmark_df = generate_benchmark_dataset()

# ----------------------------
# Sidebar Inputs
# ----------------------------
st.sidebar.header("Merchant Inputs")
industry = st.sidebar.selectbox("Industry", list(INDUSTRY_SCOPE3_FACTORS.keys()))
state = st.sidebar.selectbox("State", ["Texas", "California"])
monthly_revenue = st.sidebar.number_input("Monthly Revenue ($)", min_value=1000, value=40000, step=1000)

# ----------------------------
# Page Title Card
# ----------------------------
title_html = """
<h1>Estimated Monthly Emissions for Square Client</h1>
<p style='text-align:center;'> This emissions analytics dashboard uses probabilistic modeling (Monte Carlo) to estimate your 
Scope 2 and Scope 3 emissions, evaluate your performance against comparable businesses, and translate your financial activity 
into measurable emissions. For more details behind the assumptions and values used, see 
the <a href="https://google.com/" target="_blank">this README document</a>.
REMINDER TO LINK MY READ ME DOC!!!!
</p>
"""
card_container(title_html)

# ----------------------------
# Run Model
# ----------------------------
if st.sidebar.button("Calculate Emissions"):

    results = calculate_total_emissions(industry, state, monthly_revenue)

    industry_df = benchmark_df[
        (benchmark_df["industry"] == industry) &
        (benchmark_df["state"] == state)
    ]
    
    percentile = round(((industry_df["mean_total_emissions"] < results["mean_total"]).mean()) * 100, 1)
    carbon_intensity = results["mean_total"] / monthly_revenue

    # ----------------------------
    # Total Monthly Emissions Card
    # ----------------------------
    total_emissions_html = f"""
    <h3 style='text-align:center;'>Total Monthly Emissions</h3>
    <div style='text-align:center; font-size:32px; font-weight:700;'>{results['mean_total']:,.0f} kg CO₂e</div>
    <div style='text-align:center; font-size:18px;'>Uncertainty Range: {results['p5_total']:,.0f} – {results['p95_total']:,.0f} kg CO₂e</div>
    """
    card_container(total_emissions_html)

    # ----------------------------
    # Scope 2 + Scope 3 + Donut Card
    # ----------------------------
    metrics_html = f"""
    <div style="display:flex; justify-content:space-around; margin-bottom:20px;">
        <div style="text-align:center;">
            <div style='font-size:18px;'>Scope 2 (kg CO₂e)</div>
            <div style='font-size:32px; font-weight:700;'>{results['mean_scope2']:,.0f}</div>
        </div>
        <div style="text-align:center;">
            <div style='font-size:18px;'>Scope 3 (kg CO₂e)</div>
            <div style='font-size:32px; font-weight:700;'>{results['mean_scope3']:,.0f}</div>
        </div>
        <div style="text-align:center;">
            <div style='font-size:18px;'>Carbon Intensity (kg CO₂e per $)</div>
            <div style='font-size:32px; font-weight:700;'>{carbon_intensity:.3f}</div>
        </div>
    </div>
    """

    # Donut chart
    scope2 = results["mean_scope2"]
    scope3 = results["mean_scope3"]
    total = scope2 + scope3

    fig, ax = plt.subplots(figsize=(4,4))
    wedges, texts, autotexts = ax.pie(
        [scope2, scope3],
        labels=["Scope 2", "Scope 3"],
        autopct='%1.1f%%',
        startangle=90,
        colors=['#2ca02c', '#1f77b4'],
        wedgeprops={'width':0.4, 'edgecolor':'white'}
    )
    for text in texts:
        text.set_fontsize(20)
        text.set_fontweight('bold')
    for autotext in autotexts:
        autotext.set_fontsize(20)
        autotext.set_fontweight('bold')
    ax.text(0, 0, f"{total:,.0f}\nkg CO₂e",
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=15,
            fontweight='regular',
            color='#333')
    ax.axis('equal')

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    donut_html = f'<img src="data:image/png;base64,{img_b64}" style="display:block; margin:auto;">'

    card_container(metrics_html + donut_html)

    # ----------------------------
    # Green Percentile Badge Card
    # ----------------------------
    if percentile < 33:
        badge_bg = "#E6F4EA"
        badge_text = "#137333"
        badge_label = "Low Emissions vs Peers"
    elif percentile < 66:
        badge_bg = "#FFF4E5"
        badge_text = "#8A4B00"
        badge_label = "Average Emissions vs Peers"
    else:
        badge_bg = "#FDECEA"
        badge_text = "#A50E0E"
        badge_label = "High Emissions vs Peers"

    badge_html = f"""
    <div style="text-align:center;">
        <div style="
            display:inline-block;
            padding:15px;
            border-radius:10px;
            background-color:{badge_bg};
            color:{badge_text};
            font-weight:600;
            font-size:18px;">
            {badge_label}<br>
            Higher than {percentile}% of comparable businesses in {state}
        </div>
    </div>
    """
    card_container(badge_html)

# ----------------------------
# Histogram Card
# ----------------------------
    fig2, ax2 = plt.subplots()

    # Histogram in light green
    ax2.hist(results["total_samples"], bins=40, alpha=0.85, color='#2ca02c')

    # Dashed line for mean
    ax2.axvline(results["mean_total"], linestyle="--", color='black')

    # Labels
    ax2.set_xlabel("Monthly Emissions (kg CO₂e)")
    ax2.set_ylabel("Frequency")

    # Remove top and right spines
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # Convert figure to image
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format="png", bbox_inches="tight")
    buf2.seek(0)
    img2_b64 = base64.b64encode(buf2.read()).decode("utf-8")
    hist_img_html = f'<img src="data:image/png;base64,{img2_b64}" style="display:block; margin:auto;">'

    # Card content including subheader
    hist_card_html = f"""
    <h3 style="text-align:center;">Monte Carlo Emissions Distribution</h3>
    {hist_img_html}
    """

    # Display inside card
    card_container(hist_card_html)