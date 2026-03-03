import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

# Page Configuration
st.set_page_config(page_title="Rent vs Buy Calculator", layout="wide")

st.title("Rent vs. Buy Financial Comparison")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Scenario Variables")

purchase_price = st.sidebar.number_input("Purchase Price ($)", value=600000, step=10000)
mortgage_balance = st.sidebar.number_input("Mortgage Balance ($)", value=480000, step=10000)
monthly_mortgage_payment = st.sidebar.number_input("Monthly Mortgage Payment ($)", value=2800, step=100)
mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", value=5.0, step=0.1) / 100

monthly_rent = st.sidebar.number_input("Monthly Rent ($)", value=2500, step=100)

property_appreciation = st.sidebar.number_input("Property Appreciation Rate (%)", value=3.0, step=0.1) / 100
rent_inflation = st.sidebar.number_input("Rent Inflation Rate (%)", value=2.5, step=0.1) / 100
general_inflation = st.sidebar.number_input("General Inflation (%)", value=2.0, step=0.1) / 100
investment_return = st.sidebar.number_input("Investment Return (%)", value=6.0, step=0.1) / 100
investment_tax_rate = st.sidebar.number_input("Investment Tax Rate (%)", value=25.0, step=1.0) / 100

time_horizon = st.sidebar.number_input("Time Horizon (Years)", value=25, min_value=1, max_value=50, step=1)

st.sidebar.subheader("Closing & Maintenance Costs")
acquisition_cost = st.sidebar.number_input("Acquisition Costs ($)", value=10000, step=1000)
disposition_cost_pct = st.sidebar.number_input("Disposition Costs (%)", value=5.0, step=0.5) / 100
annual_maintenance = st.sidebar.number_input("Annual Maintenance ($)", value=3000, step=500)
other_ownership_expenses = st.sidebar.number_input("Other Expenses/Property Tax ($)", value=4500, step=500)
annual_utilities = st.sidebar.number_input("Annual Utilities ($)", value=2400, step=100)

# --- CALCULATION LOGIC ---
down_payment = purchase_price - mortgage_balance
initial_outlay_buy = down_payment + acquisition_cost
renter_portfolio = initial_outlay_buy

buy_net_worth = []
rent_net_worth = []

current_property_value = purchase_price
current_mortgage = mortgage_balance
current_annual_rent = monthly_rent * 12

annual_mortgage_pmt = monthly_mortgage_payment * 12
year_1_buy_cost = annual_mortgage_pmt + annual_maintenance + other_ownership_expenses + annual_utilities
year_1_rent_cost = current_annual_rent + annual_utilities

for year in range(1, time_horizon + 1):
    # BUY SCENARIO
    interest_paid = current_mortgage * mortgage_rate
    principal_paid = annual_mortgage_pmt - interest_paid
    
    if principal_paid > current_mortgage:
        principal_paid = current_mortgage
        annual_mortgage_pmt = interest_paid + principal_paid 
        
    current_mortgage -= principal_paid
    current_property_value *= (1 + property_appreciation)
    
    disposition_fee = current_property_value * disposition_cost_pct
    current_buy_equity = current_property_value - current_mortgage - disposition_fee
    buy_net_worth.append(current_buy_equity)
    
    # RENT SCENARIO
    current_buy_cost = annual_mortgage_pmt + annual_maintenance + other_ownership_expenses + annual_utilities
    current_rent_cost = current_annual_rent + annual_utilities
    
    cash_flow_difference = current_buy_cost - current_rent_cost
    
    after_tax_return = investment_return * (1 - investment_tax_rate)
    renter_portfolio *= (1 + after_tax_return)
    renter_portfolio += cash_flow_difference 
    rent_net_worth.append(renter_portfolio)
    
    current_annual_rent *= (1 + rent_inflation)
    annual_maintenance *= (1 + general_inflation)
    other_ownership_expenses *= (1 + general_inflation)
    annual_utilities *= (1 + general_inflation)

# --- VISUALIZATION ---
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(range(1, time_horizon + 1), buy_net_worth, color='#4169E1', linewidth=3, label='Buy Scenario (Net Equity)')
ax.plot(range(1, time_horizon + 1), rent_net_worth, color='#FFD700', linewidth=3, label='Rent Scenario (Portfolio Value)')

ax.set_title(f'Rent vs. Buy Net Worth Over {time_horizon} Years', fontsize=14, fontweight='bold')
ax.set_xlabel('Years', fontsize=12)
ax.set_ylabel('Net Liquid Value ($)', fontsize=12)

formatter = ticker.FuncFormatter(lambda x, pos: f'${x:,.0f}')
ax.yaxis.set_major_formatter(formatter)

ax.grid(True, linestyle='--', alpha=0.7)
ax.legend(fontsize=12)
plt.tight_layout()

# Display the plot in Streamlit
st.pyplot(fig)

# --- CASH FLOW SUMMARY ---
st.markdown("### First Year Cash Flow Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**BUY OPTION**")
    st.text(f"Annual Mortgage Payment: ${annual_mortgage_pmt:,.2f}")
    st.text(f"Annual Maintenance:      ${annual_maintenance:,.2f}")
    st.text(f"Other Expenses (Taxes):  ${other_ownership_expenses:,.2f}")
    st.text(f"Utilities:               ${annual_utilities:,.2f}")
    st.markdown("---")
    st.markdown(f"**TOTAL ANNUAL BUY COST:   ${year_1_buy_cost:,.2f}**")

with col2:
    st.markdown("**RENT OPTION**")
    st.text(f"Annual Rent:             ${monthly_rent * 12:,.2f}")
    st.text(f"Utilities:               ${annual_utilities:,.2f}")
    st.markdown("---")
    st.markdown(f"**TOTAL ANNUAL RENT COST:  ${year_1_rent_cost:,.2f}**")

st.markdown("---")
if year_1_buy_cost > year_1_rent_cost:
    st.success(f"**Insight:** The Renter invests the cash flow savings of ${(year_1_buy_cost - year_1_rent_cost):,.2f} into their portfolio in Year 1.")
else:
    st.info(f"**Insight:** The Buyer has a cash flow advantage of ${(year_1_rent_cost - year_1_buy_cost):,.2f} in Year 1.")
