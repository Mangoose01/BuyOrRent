import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Page Configuration for a wide, clean layout
st.set_page_config(page_title="Rent vs Buy Calculator", layout="wide", initial_sidebar_state="expanded")

st.title("Rent vs. Buy Financial Comparison")
st.markdown("A comprehensive cash flow and net worth analysis.")

# === SIDEBAR INPUTS ===
st.sidebar.header("Primary Variables")

purchase_price = st.sidebar.number_input("Purchase Price ($)", min_value=0, value=600000, step=10000, help="The total asking price of the property.")
mortgage_balance = st.sidebar.number_input("Mortgage Balance ($)", min_value=0, value=0, step=10000, help="The initial principal amount of the mortgage. Set to 0 for cash purchase.")
monthly_mortgage_payment = st.sidebar.number_input("Monthly Mortgage Payment ($)", min_value=0, value=0, step=100, help="Your total monthly principal and interest payment. Set to 0 if no mortgage.")
mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", min_value=0.0, value=5.0, step=0.1, help="The annual interest rate on the mortgage.") / 100

monthly_rent = st.sidebar.number_input("Monthly Rent ($)", min_value=0, value=2500, step=100, help="The initial monthly cost to rent a comparable property.")
time_horizon = st.sidebar.number_input("Time Horizon (Years)", value=25, min_value=1, max_value=50, step=1, help="How many years you plan to live in the home before selling.")

# Advanced Assumptions in Expanders
with st.sidebar.expander("Growth & Inflation Assumptions"):
    property_appreciation = st.number_input("Property Appreciation (%)", value=3.0, step=0.1, help="Expected annual increase in property value.") / 100
    rent_inflation = st.number_input("Rent Inflation (%)", value=2.5, step=0.1, help="Expected annual increase in rent.") / 100
    general_inflation = st.number_input("General Inflation (%)", value=2.0, step=0.1, help="Expected annual increase for ongoing expenses.") / 100
    investment_return = st.number_input("Investment Return (%)", value=6.0, step=0.1, help="Expected gross annual return on the renter's invested portfolio.") / 100
    investment_tax_rate = st.number_input("Investment Tax Rate (%)", value=25.0, step=1.0, help="The average tax rate applied to investment growth.") / 100

with st.sidebar.expander("Buying Expenses"):
    acquisition_cost = st.number_input("Acquisition Costs ($)", value=10000, step=1000, help="Upfront costs to buy: land transfer tax, legal fees, inspections.")
    disposition_cost_pct = st.number_input("Disposition Costs (%)", value=5.0, step=0.5, help="Costs to sell at the end of the time horizon: realtor commissions, legal fees.") / 100
    buy_property_taxes = st.number_input("Property Taxes ($/yr)", value=4000, step=500)
    buy_maintenance = st.number_input("Maintenance ($/yr)", value=3000, step=500)
    buy_utilities = st.number_input("Buying Utilities ($/yr)", value=2400, step=100)
    buy_insurance = st.number_input("Home Insurance ($/yr)", value=1200, step=100)
    buy_other_expenses = st.number_input("Other Buying Expenses ($/yr)", value=0, step=100)

with st.sidebar.expander("Renting Expenses"):
    rent_utilities = st.number_input("Renting Utilities ($/yr)", value=1800, step=100)
    rent_insurance = st.number_input("Tenant Insurance ($/yr)", value=300, step=50)
    rent_other_expenses = st.number_input("Other Renting Expenses ($/yr)", value=0, step=100)

# === CALCULATION LOGIC ===
down_payment = purchase_price - mortgage_balance
initial_outlay_buy = down_payment + acquisition_cost
renter_portfolio = initial_outlay_buy

years_list = []
buy_net_worth = []
rent_net_worth = []

current_property_value = purchase_price
current_mortgage = mortgage_balance
current_annual_rent = monthly_rent * 12

annual_mortgage_pmt = monthly_mortgage_payment * 12
year_1_buy_cost = annual_mortgage_pmt + buy_property_taxes + buy_maintenance + buy_utilities + buy_insurance + buy_other_expenses
year_1_rent_cost = current_annual_rent + rent_utilities + rent_insurance + rent_other_expenses

for year in range(1, time_horizon + 1):
    years_list.append(year)
    
    # BUY SCENARIO
    if current_mortgage > 0:
        interest_paid = current_mortgage * mortgage_rate
        principal_paid = annual_mortgage_pmt - interest_paid
        
        if principal_paid > current_mortgage:
            principal_paid = current_mortgage
            annual_mortgage_pmt = interest_paid + principal_paid 
            
        current_mortgage -= principal_paid
    else:
        annual_mortgage_pmt = 0
        
    current_property_value *= (1 + property_appreciation)
    
    disposition_fee = current_property_value * disposition_cost_pct
    current_buy_equity = current_property_value - current_mortgage - disposition_fee
    buy_net_worth.append(current_buy_equity)
    
    # RENT SCENARIO
    current_buy_cost = annual_mortgage_pmt + buy_property_taxes + buy_maintenance + buy_utilities + buy_insurance + buy_other_expenses
    current_rent_cost = current_annual_rent + rent_utilities + rent_insurance + rent_other_expenses
    
    cash_flow_difference = current_buy_cost - current_rent_cost
    
    after_tax_return = investment_return * (1 - investment_tax_rate)
    renter_portfolio *= (1 + after_tax_return)
    renter_portfolio += cash_flow_difference 
    rent_net_worth.append(renter_portfolio)
    
    # Inflate expenses for next year
    current_annual_rent *= (1 + rent_inflation)
    buy_property_taxes *= (1 + general_inflation)
    buy_maintenance *= (1 + general_inflation)
    buy_utilities *= (1 + general_inflation)
    buy_insurance *= (1 + general_inflation)
    buy_other_expenses *= (1 + general_inflation)
    rent_utilities *= (1 + general_inflation)
    rent_insurance *= (1 + general_inflation)
    rent_other_expenses *= (1 + general_inflation)

# === INTERACTIVE VISUALIZATION (Plotly) ===
fig = go.Figure()

# Add Buy Scenario Line
fig.add_trace(go.Scatter(
    x=years_list, 
    y=buy_net_worth, 
    mode='lines+markers',
    name='Buy (Net Equity)',
    line=dict(color='#4169E1', width=3),
    marker=dict(size=6),
    hovertemplate="Year %{x}<br>Net Equity: $%{y:,.0f}<extra></extra>"
))

# Add Rent Scenario Line
fig.add_trace(go.Scatter(
    x=years_list, 
    y=rent_net_worth, 
    mode='lines+markers',
    name='Rent (Portfolio Value)',
    line=dict(color='#FFD700', width=3),
    marker=dict(size=6),
    hovertemplate="Year %{x}<br>Portfolio: $%{y:,.0f}<extra></extra>"
))

# Styling the chart to look modern and clean
fig.update_layout(
    title=dict(text=f"Net Worth Projection Over {time_horizon} Years", font=dict(size=20)),
    xaxis_title="Years",
    yaxis_title="Net Liquid Value ($)",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=60, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# === CASH FLOW SUMMARY (Modern Layout) ===
st.markdown("### Year 1 Cash Flow Summary")

col1, col2 = st.columns(2)

with col1:
    st.info("**BUY OPTION**")
    st.metric(label="Total Annual Buy Cost", value=f"${year_1_buy_cost:,.0f}")
    st.write(f"Mortgage: ${annual_mortgage_pmt:,.0f}")
    st.write(f"Property Taxes: ${buy_property_taxes:,.0f}")
    st.write(f"Maintenance: ${buy_maintenance:,.0f}")
    st.write(f"Utilities: ${buy_utilities:,.0f}")
    st.write(f"Insurance: ${buy_insurance:,.0f}")
    if buy_other_expenses > 0:
        st.write(f"Other: ${buy_other_expenses:,.0f}")

with col2:
    st.warning("**RENT OPTION**")
    st.metric(label="Total Annual Rent Cost", value=f"${year_1_rent_cost:,.0f}")
    st.write(f"Rent: ${monthly_rent * 12:,.0f}")
    st.write(f"Utilities: ${rent_utilities:,.0f}")
    st.write(f"Insurance: ${rent_insurance:,.0f}")
    if rent_other_expenses > 0:
        st.write(f"Other: ${rent_other_expenses:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

if year_1_buy_cost > year_1_rent_cost:
    st.success(f"**Insight:** The Renter has lower monthly costs and invests the cash flow savings of **${(year_1_buy_cost - year_1_rent_cost):,.2f}** into their portfolio in Year 1.")
else:
    st.success(f"**Insight:** The Buyer has lower monthly costs, resulting in a cash flow advantage of **${(year_1_rent_cost - year_1_buy_cost):,.2f}** in Year 1.")
