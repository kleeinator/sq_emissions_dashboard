# python code converted to Streamlit + design elements

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

np.random.seed(42)  # ensures reproducible Monte Carlo results
n_simulations = 5000

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
# Styling
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
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Scope 2, 3 Parameters
# ----------------------------
STATE_GRID_INTENSITY = {
    "Texas": 0.4,
    "California": 0.26
}

STATE_ELECTRICITY_COST = {
    "Texas": 0.091,
    "California": 0.2946
}

ELECTRICITY_PRICE_UNCERTAINTY = 0.05

# Industry kWh per $ revenue (baseline intensity)
INDUSTRY_KWH_PER_DOLLAR = {
    "restaurant": 0.15,
    "retail_clothing": 0.10,
    "medical_office": 0.06
}

# Scope 3 factors
INDUSTRY_SCOPE3_FACTORS = {
    "restaurant": 0.194,
    "retail_clothing": 0.138,
    "medical_office": 0.096
}

SCOPE3_UNCERTAINTY_PERCENT = 0.064

# Industry-specific revenue distributions (lognormal)
INDUSTRY_REVENUE_PARAMS = {
    "restaurant": {"mean": 10.36, "sigma": 0.7},
    "retail_clothing": {"mean": 9.03, "sigma": 0.6},
    "medical_office": {"mean": 11.33, "sigma": 0.4}
}

# ----------------------------
# Monte Carlo Model
# ----------------------------
def calculate_total_emissions(monthly_bill=None, monthly_kwh=None, monthly_revenue=None, industry=None, state=None):

    # ---- Scope 3 (Lognormal Sampling) ----
    mean_factor = INDUSTRY_SCOPE3_FACTORS[industry]

    cv = SCOPE3_UNCERTAINTY_PERCENT  # coefficient of variation

    # Convert mean + CV to lognormal parameters
    sigma_ln = np.sqrt(np.log(1 + cv**2))
    mu_ln = np.log(mean_factor) - 0.5 * sigma_ln**2

    sampled_scope3_factors = np.random.lognormal(
        mean=mu_ln,
    sigma=sigma_ln,
    size=n_simulations
)
    scope3_samples = monthly_revenue * sampled_scope3_factors

    # ---- Scope 2 ----
    grid_intensity = STATE_GRID_INTENSITY[state]

    if monthly_kwh is None:
        base_price = STATE_ELECTRICITY_COST[state]
        price_std = base_price * ELECTRICITY_PRICE_UNCERTAINTY

        sampled_prices = np.random.normal(base_price, price_std, n_simulations)
        sampled_prices = np.clip(sampled_prices, 0.0001, None)

        sampled_kwh = monthly_bill / sampled_prices
    else:
        sampled_kwh = np.full(n_simulations, monthly_kwh)

    scope2_samples = sampled_kwh * grid_intensity
    total_samples = scope3_samples + scope2_samples

    return {
        "mean_total": np.mean(total_samples),
        "p5_total": np.percentile(total_samples, 5),
        "p95_total": np.percentile(total_samples, 95),
        "mean_scope3": np.mean(scope3_samples),
        "mean_scope2": np.mean(scope2_samples),
        "mean_kwh": np.mean(sampled_kwh),
        "mean_carbon_intensity": np.mean(total_samples) / monthly_revenue,
        "total_samples": total_samples
    }

# ----------------------------
# Benchmark Dataset (Revenue ↔ Electricity Correlated via Intensity Model)
# ----------------------------

@st.cache_data
def generate_benchmark_dataset(n=3000):

    industries = list(INDUSTRY_SCOPE3_FACTORS.keys())
    states = ["Texas", "California"]
    data = []

    for _ in range(n):

        industry = np.random.choice(industries)
        state = np.random.choice(states)

        # Revenue
        revenue_params = INDUSTRY_REVENUE_PARAMS[industry]
        monthly_revenue = np.random.lognormal(mean=revenue_params["mean"], sigma=revenue_params["sigma"])

        # kWh per revenue intensity
        intensity_mean = INDUSTRY_KWH_PER_DOLLAR[industry]
        kwh_per_dollar = np.random.lognormal(mean=np.log(intensity_mean), sigma=0.45)

        sampled_kwh = monthly_revenue * kwh_per_dollar


        # Run emissions
        emissions = calculate_total_emissions(
        monthly_kwh=sampled_kwh,
        monthly_revenue=monthly_revenue,
        industry=industry,
        state=state
        )

        carbon_intensity = emissions["mean_total"] / monthly_revenue

        data.append({
            "industry": industry,
            "state": state,
            "carbon_intensity": carbon_intensity
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
monthly_electric_bill = st.sidebar.number_input("Monthly Electricity Bill ($)", min_value=0, value=600, step=100)

# ----------------------------
# Title Card
# ----------------------------
title_html = """
<h1 style='text-align:center;'>Estimated Monthly Emissions for Square Client</h1>

<p style='text-align:center;'>
This emissions analytics dashboard uses probabilistic modeling (Monte Carlo) 
to estimate your Scope 2 and Scope 3 emissions, evaluate your performance 
against comparable businesses, and translate your financial activity 
into measurable emissions.
</p>

<p style='text-align:center;'>
For more details behind the assumptions and values used, see 
<a href="https://github.com/kleeinator/sq_emissions_dashboard/blob/main/README.md" target="_blank">this README document</a>.
</p>

<p style='text-align:center;'>
<strong>Not sure what numbers to start with in the "Merchant Inputs" section?<strong>
</p>

<p style='text-align:center;'>
• Average restaurant: $40k/month revenue, $550 electric bill (TX) or $1800 (CA)<br>
• Average clothing store: $10k/month revenue, $100 electric bill (TX) or $300 (CA)<br>
• Average medical office: $90k/month revenue, $500 electric bill (TX) or $1600 (CA)
</p>
"""
card_container(title_html)

# ----------------------------
# Run Model
# ----------------------------
if st.sidebar.button("Calculate Emissions"):

    results = calculate_total_emissions(
    monthly_bill=monthly_electric_bill,
    monthly_revenue=monthly_revenue,
    industry=industry,
    state=state
    )

    merchant_carbon_intensity = results["mean_carbon_intensity"]

    industry_df = benchmark_df[
        (benchmark_df["industry"] == industry) &
        (benchmark_df["state"] == state)
    ]
    percentile = round(((industry_df["carbon_intensity"] < merchant_carbon_intensity).mean()) * 100, 1)

    # ----------------------------
    # Total Emissions Card
    # ----------------------------
    total_emissions_html = f"""
    <h3 style='text-align:center;'>Total Monthly Emissions</h3>
    <div style='text-align:center; font-size:32px; font-weight:700;'>{results['mean_total']:,.0f} kg CO₂e</div>
    <div style='text-align:center; font-size:18px;'>
        Uncertainty Range: {results['p5_total']:,.0f} – {results['p95_total']:,.0f} kg CO₂e
    </div>
    """
    card_container(total_emissions_html)

    # ----------------------------
    # Metrics Card
    # ----------------------------
    metrics_html = f"""
    <div style="display:flex; justify-content:space-around; flex-wrap:wrap;">
        <div style="text-align:center; margin:10px;">
            <div>Estimated Monthly kWh</div>
            <div style='font-size:26px; font-weight:700;'>{results['mean_kwh']:,.0f}</div>
        </div>
        <div style="text-align:center; margin:10px;">
            <div>Scope 2 (kg CO₂e)</div>
            <div style='font-size:26px; font-weight:700;'>{results['mean_scope2']:,.0f}</div>
        </div>
        <div style="text-align:center; margin:10px;">
            <div>Scope 3 (kg CO₂e)</div>
            <div style='font-size:26px; font-weight:700;'>{results['mean_scope3']:,.0f}</div>
        </div>
        <div style="text-align:center; margin:10px;">
            <div>Carbon Intensity (kg CO₂e per $)</div>
            <div style='font-size:26px; font-weight:700;'>{merchant_carbon_intensity:.3f}</div>
        </div>
    </div>
    """
    card_container(metrics_html)

    # ----------------------------
    # Percentile Badge
    # ----------------------------
    if percentile < 33:
        badge_bg = "#E6F4EA"
        badge_text = "#137333"
        badge_label = "Low Carbon Intensity (kg CO2e / $) vs Peers"
    elif percentile < 66:
        badge_bg = "#FFF4E5"
        badge_text = "#8A4B00"
        badge_label = "Average Carbon Intensity (kg CO2e / $) vs Peers"
    else:
        badge_bg = "#FDECEA"
        badge_text = "#A50E0E"
        badge_label = "High Carbon Intensity (kg CO2e / $) vs Peers"

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
    # Donut Chart (Scope 2 vs Scope 3)
    # ----------------------------
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
    card_container("<h3 style='text-align:center;'>Emissions Breakdown</h3>" + donut_html)

    # ----------------------------
    # Monte Carlo Histogram
    # ----------------------------
    fig2, ax2 = plt.subplots(figsize=(6,4))
    ax2.hist(results["total_samples"], bins=40, color="#2ca02c", alpha=0.75)
    ax2.axvline(results["mean_total"], linestyle="dashed", linewidth=2)
    ax2.set_xlabel("Total Emissions (kg CO₂e)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Monte Carlo Distribution of Total Emissions")

    ax2.axvline(results["p5_total"], color='orange', linestyle='dotted', label='5th pct')
    ax2.axvline(results["p95_total"], color='orange', linestyle='dotted', label='95th pct')
    ax2.legend()

    buf2 = io.BytesIO()
    fig2.savefig(buf2, format="png", bbox_inches="tight")
    buf2.seek(0)
    img_b64_2 = base64.b64encode(buf2.read()).decode("utf-8")
    hist_html = f'<img src="data:image/png;base64,{img_b64_2}" style="display:block; margin:auto;">'

    card_container(hist_html)
