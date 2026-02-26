# Welcome!

Hi! My name is Kayleigh, and I developed this proof-of-concept emissions estimator for Square clients as my AI-assisted work sample for Square’s APM program. I wanted to create a project that capitalized on Square’s treasure trove of merchant data and my environmental sustainability technical background, all while providing valuable sustainability insights for your brick-and-mortar clients. 

## Project Links:

**Github Repo:** https://github.com/kleeinator/sq_emissions_dashboard   
**Deployed App:** https://sqemissionsdashboard-78kx7kdh3b2cxcgfljvkh3.streamlit.app/ 
*(If the app says it’s in sleep mode, wake it up and it’ll be ready to go in about a minute!)*

## How it Works: 

Merchant Inputs (Industry, State, Revenue, Electricity Bill) --> 

Scope 2 and Scope 3 Calculations -->  

Monte Carlo Simulations (n=5000) --> 

Benchmarking Against Synthetic Dataset --> 

Interactive Results Dashboard: Total Emissions, Scope 2 vs. Scope Breakdown, Peer Comparison, and Simulations Histogram

## General Overview:

I’ve worked with environmental and sustainability at small companies, which included tracking and calculating water quality, environmental footprints (carbon, water), greenhouse gas (GHG) emissions, and life-cycle assessments (LCA). It’s almost expected that major companies have sustainability and ESG commitments and reporting, but what about small and medium-sized businesses that want to benchmark their environmental impact? Small businesses often don’t have the time, expertise, or money to develop internal carbon accounting metrics, much less regulatory-grade reporting. 

This project demonstrates how a POS, merchant services platform like Square can use a client’s transaction data and utility payment data to automatically benchmark their emissions. With these insights, small businesses and retailers can have the data they need to both monitor and take actionable steps towards lowering their carbon footprints. 

This model estimates:
- Scope 3 emissions using revenue-based industry emissions 
- Scope 2 emissions using electricity usage and state-specific carbon intensity data 
- Peer benchmarking based on industry and geographical location 

For this project, I drew upon my sustainability estimates background and did my own additional research to develop the framework of this model, which included: researching emissions reporting protocol, sourcing relevant data points, calculating the Scope 2 and Scope 3 intensities, and developing reasonable assumptions. I do have coding experience – mainly data analysis tools like R, MATLAB, and SQL – but little Python experience, so I used AI tools (ChatGPT) to build the Python script and deploy the interactive dashboard in Streamlit.      

This is a proof-of-concept model, and I made many assumptions to help simplify and streamline the emissions calculations. For more details on the specific calculations, sources, and assumptions used, please see additional sections below. 

# Project Details:

## Problem:

- Traditional carbon accounting is expensive, data-intensive, and more accessible for large companies. 

- Smaller retailers and businesses, a core part of Square’s client base, can benefit from automated carbon estimates for their operations, industry benchmarking against comparable peers, and a clear, understandable emissions output.  

- Square is uniquely positioned to provide business-specific emissions estimates because you have access to monthly revenue data, vendor and utility bill payment data, merchant details, and geographical information. 

## Methodological Approach:

There are multiple methods to track a company’s emissions, and a popular protocol is the Greenhouse Gas Protocol (GHGP), which helps businesses better understand where their emissions are coming from (1). In the GHGP, emissions are split into three different sources, called “Scopes”. 

- **Scope 1 Emissions:** Come from direct, on-site sources that are owned by the company, such as company vehicles or cooking equipment  
- **Scope 2 Emissions:** Come from indirect sources that are controlled by the company, most often electricity from a utility provider 
- **Scope 3 Emissions:** Come from indirect sources that are not controlled by the company, but are part of the value chain. This varies by industry, but for retail companies, Scope 3 tends to include emissions from the life cycle of sold goods, transportation, and distribution. (1, 2)    

For this emissions calculator, I chose to focus on Scope 2 and Scope 3 emissions. For Scope 3 emissions, the EPA has publicly accessible data for the supply chain GHG emissions for different US industries on a revenue basis, e.g. kg CO2e emitted per dollar of revenue (3). Square has monthly sales summaries for each client, we can use that revenue number to estimate Scope 3 emissions. Scope 2 emissions for retail businesses can be calculated based on the amount of energy used per month (1). Since businesses can pay vendors, including their utility bills, with Square, we can estimate a business’ monthly electricity use based on their utility payment amount. I excluded Scope 1 emissions in this calculator because they require specific information about a company’s building and operations, such as the type and amount of on-site equipment. A brief survey for Square clients interested in a more robust emissions calculation could allow for Scope 1 emissions in an expanded version of this model. 

This emissions analytics dashboard uses probabilistic modeling (Monte Carlo) to estimate your Scope 2 and Scope 3 emissions, evaluate your performance against comparable businesses, and translate your financial activity into measurable emissions.

## Merchant Inputs Explanation:

If you open up the interactive dashboard, you’ll notice that under “Merchant Inputs”, you can choose from 3 industries (restaurants, retail clothing stores, and medical offices) and from two states (Texas and California). How did I choose these industries and states? Well, I looked all my credit card transactions from the past 2 years, and I catalogued all the purchases I made with a Square POS system (they all started with ‘sq*’ in my raw credit card data). My top 3 merchant industries were restaurants, clothing stores, and doctor’s offices, from two states: California and Texas. 

I thought these industries would be good comparisons for an emissions calculator, because restaurants and medical offices tend to have higher electricity use, but medical office monthly revenue often exceeds a restaurant’s revenue. Clothing stores tend to have less revenue and electricity usage but higher supply chain (Scope 3) emissions. Restaurants tend to have higher supply chain emissions as well. Texas and California are interesting comparison states because they have notably different grid intensities and electricity costs. California has a bigger renewables market, meaning that their electricity usage has a lower carbon output per kWh of energy used. California also has a higher utility cost, about 3x the cost of Texas’ electricity. (4-9) 

See the “Code Walkthrough” section for the exact numbers used in Scope 2 and Scope 3 calculations. 

## Key Assumptions:

All assumptions were made to help produce a simplified, lightweight proof-of-concept model for small business emissions estimates and benchmarking. 

- Scope 2 Grid Intensity: 0.4 kg CO2 / kWh for TX and 0.26 kg CO2 / kWh (8)
- Scope 2 Electricity Usage (kWh): Assumes the entire bill is only electricity charges, and excludes other utility bill charges (e.g. supply charges, delivery charges, tax, fees, etc.) 
- Scope 2 Electricity Pricing: $0.091 / kWh in TX and $0.2946 in CA (9)
- Scope 3 Factor: kg CO2e per $ of revenue based on industry: 0.194 for restaurants, 0.138 for clothing store, and 0.096 for medical office (3)

## Limitations:

- Only 3 industries and 2 states modelled 
- Assumes simplified Scope 2 and Scope 3 calculations
- Peer benchmarked with synthetic data 
- Scope 1 emissions not included    

## Real-World Impact:

If Square clients had automated access to a sustainability calculator like this, they could be better situated to:
- Pinpoint which aspects of their operations contribute most to emissions and improve environmental ROI
- Compare – and maybe even publicize or market! – their carbon intensity (kg CO2e per $ of revenue) with similar businesses in their industry and state, and showcase their commitment to decarbonization and attract environmentally-conscious customers 
- Manage energy costs and optimize operations by tracking their monthly emissions data

With these emissions insights, Square as a company could:
- Enhance value proposition by offering automated insights beyond the transitional scope of POS and merchant services companies, while also attracting environmentally-conscious clients 
- Offer an advanced, monetized version of this dashboard that takes into account even more specific client data
- Leverage this emissions data to create products, services, or marketing strategies that align with sustainability trends across different industries and regions 
- Strengthen Square’s brand as a sustainable and environmentally-forward company 

## Future Enhancements:

Since this is a proof-of-concept model, there are a lot of ways to enhance the capabilities of this emissions calculator!

Some ideas include:
- Adding Scope 1 emissions calculations
- Expanding the states and industries offered
- Address other factors in Scope 2 calculations, such as seasonality and electricity bills and grid intensity by region 
- Expand Scope 3 beyond a revenue-basis 
- Take into account additional operational details, such as square footage, HVAC systems, boilers, etc. 
- Benchmark against actual other companies, instead of a synthetic dataset
- Offer concrete recommendations for a company to lower their lower emissions impact, based on their industry and location 

# Code Walkthrough:

A section-by-section walkthrough of the code: 

Line 10: We get reproducible random results, and later on in the model, we’ll run 5,000 Monte Carlo Simulations per emissions estimate. 

### Line 55: Scope 2, 3 Parameters: 

Texas emits 0.4 kg CO2 per kWh, while California emits 0.26 kg CO2 per kWh, meaning that electricity is cleaner in California. This number is the “grid intensity” for each state. (8)

The average electricity cost in Texas is $0.091 per kWh, and the average electricity cost in California is $0.2946 per kWh. The 5% uncertainty accounts for differing electricity prices within each state. (9)

Scope 2 emissions correlate with revenue. For example, if a restaurant increases their revenue, it’s likely that their electricity usage increases as well. The “INDUSTRY_KWH_PER_DOLLAR” variable baselines a business’ electricity usage by estimating how many kWh are used per $1 of revenue. This will be used later on in the peer benchmarking section, where it will calculate how much energy is used (in kWh) for the sampled revenue. 
- These numbers were calculated from the average revenue and electricity bill for industry and state, which is also on the dashboard’s main page, under “ Not sure what numbers to start with in the "Merchant Inputs" section?”.
- For example, an average restaurant in Texas has a $40k/month revenue and a $550 electricity bill (~6000 kWh if electricity cost is \$ 0.091 per kWh). Electricity usage (kWh) / Revenue is ~0.15 kWh per \$.   

The Scope 3 factors are industry-specific, and show the kg CO2e emitted per dollar of revenue. The uncertainty was calculated based on the average margins across US industries. (3)

The industry-specific revenue distributions are simulated with lognormal distribution because most businesses have lower revenue, but a few may have much higher revenue. This also accounts for a restaurant likely having higher seasonal variability than a medical office. 

### Line 93: Monte Carlo Model:

We use lognormal distribution here because this better models real-world economic intensity. The user will input their monthly revenue, and we run 5,000 simulations that multiply the revenue by a range of Scope 3 Factors (kg CO2e emitted per dollar of revenue): Scope3 = Revenue x SampledFactor. 

Next, we calculate Scope 2 emissions using the user’s input or a benchmark merchant’s data. 
- For a user: the monthly electricity bill is converted to kWh usage, assuming that there are no additional charges (distribution, fees, etc.) in order to simplify the model. This is multiplied by the grid intensity, and takes into account the uncertainty in electricity price. In order to further simplify this model, we assume that the grid intensity is fixed because there are actually sources that track real-time grid intensity across the US. (10)  Scope2 = Bill / Electricity Price x GridIntensity
- For a benchmark merchant: Same scenario as a user, but there’s no price uncertainty since we want to compare the user's specific business data to other businesses' emissions data, rather than account for individual variations in electricity pricing. 

The total emissions are calculated by adding Scope 2 and Scope 3 emissions: Total = Scope2 + Scope3. 

### Line 142: Benchmark Dataset:

This generates data for 3,000 fake businesses, so we can compare how our user’s carbon intensity (kg CO2e / $) compares to others in their industry and state. We generate random revenue (lognormal distribution), scale electricity use with revenue, and run it through the previous Monte Carlo function. CarbonIntensity = TotalEmissions / Revenue

### Line 189: Streamlit UI:

After a user inputs their information in the interactive dashboard, they are presented with:
- Total Monthly Emissions (kg CO2e) with an uncertainty range
- Estimated Monthly kWh usage, based on their electricity bill
- Scope 2 and Scope 3 emissions breakdown
- Carbon Intensity (kg CO2e / $) and a comparison to their peers
- Histogram of the Monte Carlo distribution for the user’s total emissions 

For the percentile peer benchmarking feature: low, average, and high carbon intensities represent that a business has a higher carbon intensity than 0 - 32%, 33 - 65%, or 66 - 100% of their peers, respectively.  


# Sources: 

(1) Carbon Neutral - Carbon Accounting Definition (https://www.carbonneutral.com/news/carbon-accounting)

(2) EPA - Greenhouse Gases (https://www.epa.gov/greeningepa/greenhouse-gases-epa)

(3) EPA - Supply Chain Greenhouse Gas Emission Factors for US Industries and Commodities (Scope 3 Emissions) (https://cfpub.epa.gov/si/si_public_record_Report.cfm?dirEntryId=349324&Lab=CESER)

(4) Electric Choice - Industry Electricity Use (https://www.electricchoice.com/business-electricity/) 

(5) Credibly - Restaurant Revenue (https://www.credibly.com/guides/restaurant-average-revenue/) 

(6) Dojo Business - Clothing Store Revenue (https://dojobusiness.com/blogs/news/clothe-shop-monthly-income) 

(7) Weave - Doctor’s Office Revenue (https://www.getweave.com/medical-office-operating-expenses/) 

(8) Drider - State Grid Intensity (https://www.driderescooters.com/blogs/news/us-state-carbon-intensity-rankings-renewable-energy-trends), Note: I converted the grid intensity numbers from lbs CO2e / MWh to units of kg CO2e / kWh

(9) Electric Choice - State Electricity Pricing (https://www.electricchoice.com/electricity-prices-by-state/)  

(10) EIA - US Hourly Electric Grid Monitor (https://www.eia.gov/electricity/gridmonitor/dashboard/electric_overview/US48/US48) 
