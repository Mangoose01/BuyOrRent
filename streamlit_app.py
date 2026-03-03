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

initial_capital = st.sidebar.number_input("Initial Capital Available ($)", min_value=0, value=1000000, step=50000, help="Total starting cash available to either buy the home or invest.")

purchase_price = st.sidebar.number_input("Purchase Price ($)", min_value=0, value=600000, step=10000, help="The total asking price of the property.")
mortgage_balance = st.sidebar.number_input("Mortgage Balance ($)", min_value=0, value=0, step=10000, help="The initial principal amount of the mortgage. Set to 0 for cash purchase.")
monthly_mortgage_payment = st.sidebar.number_input("Monthly Mortgage Payment ($)", min_value=0, value=0, step=100, help="Your total monthly principal and interest payment. Set to 0 if no mortgage.")
mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", min_value=0.0, value=4.0, step=0.1, help="The annual interest rate on the mortgage.") / 100

monthly_rent = st.sidebar.number_input("Monthly Rent ($)", min_value=0, value=2500, step=100, help="The initial monthly cost to rent a comparable property.")
time_horizon = st.sidebar.number_input("Time Horizon (Years)", value=20, min_value=1, max_value=50, step=1, help="How many years you plan to live in the home before selling.")

# Advanced Assumptions in Expanders
with st.sidebar.expander("Growth & Inflation Assumptions"):
    property_appreciation = st.number_input("Property Appreciation (%)", value=2.10, step=0.10, format="%.2f") / 100
    rent_inflation = st.number_input("Rent Inflation (%)", value=2.10, step=0.10, format="%.2f") / 100
    general_inflation = st.number_input("General Inflation (%)", value=2.10, step=0.10, format="%.2f") / 100
    investment_return = st.number_input("Investment Return (%)", value=5.0, step=0.1, help="Expected gross annual return on the invested portfolio.") / 100
    investment_tax_rate = st.number_input("Investment Tax Rate (%)", value=0.0, step=1.0, help="The average tax rate applied to investment growth.") / 100

with st.sidebar.expander("Buying Expenses"):
    acquisition_cost = st.number_input("Acquisition Costs ($)", value=0, step=1000, help="Upfront costs to buy, land transfer tax, legal fees, inspections.")
    disposition_cost_pct = st.number_input("Disposition Costs (%)", value=0.0, step=0.5, help="Costs to sell at the end of the time horizon, realtor commissions, legal fees.") / 100
    buy_property_taxes = st.number_input("Property Taxes ($/yr)", value=0, step=500)
    buy_maintenance = st.number_input("Maintenance ($/yr)", value=0, step=500)
    buy_utilities = st.number_input("Buying Utilities ($/yr)", value=0, step=100)
    buy_insurance = st.number_input("Home Insurance ($/yr)", value=0, step=100)
    buy_other_expenses = st.number_input("Other Buying Expenses ($/yr)", value=0, step=100)

with st.sidebar.expander("Renting Expenses"):
    rent_utilities = st.number_input("Renting Utilities ($/yr)", value=0, step=100)
    rent_insurance = st.number_input("Tenant Insurance ($/yr)", value=0, step=50)
    rent_other_expenses = st.number_input("Other Renting Expenses ($/yr)", value=0, step=100)

# === CALCULATION LOGIC ===
down_payment = purchase_price - mortgage_balance
initial_outlay_buy = down_payment + acquisition_cost

# Safety Check: Does the user have enough capital to buy?
if initial_capital < initial_outlay_buy:
    st.error(f"**Error:** The Initial Capital (\${initial_capital:,.0f}) is not enough to cover the down payment and acquisition costs (\${initial_outlay_buy:,.0f}). Please adjust your inputs.")
    st.stop()

# Initialize Portfolios
buyer_portfolio = initial_capital - initial_outlay_buy
renter_portfolio = initial_capital

# Lists for plotting and data table
years_list = []
buy_net_worth = []
rent_net_worth = []
property_values = []
mortgage_balances = []
buyer_portfolios = []
renter_portfolios = []

current_property_value = purchase_price
current_mortgage = mortgage_balance
current_annual_rent = monthly_rent * 12

annual_mortgage_pmt = monthly_mortgage_payment * 12
year_1_buy_cost = annual_mortgage_pmt + buy_property_taxes + buy_maintenance + buy_utilities + buy_insurance + buy_other_expenses
year_1_rent_cost = current_annual_rent + rent_utilities + rent_insurance + rent_other_expenses

for year in range(1, time_horizon + 1):
    years_list.append(year)
    
    # BUY SCENARIO: Mortgage Paydown & Equity
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
    
    # Calculate Total Costs for the Year
    current_buy_cost = annual_mortgage_pmt + buy_property_taxes + buy_maintenance + buy_utilities + buy_insurance + buy_other_expenses
    current_rent_cost = current_annual_rent + rent_utilities + rent_insurance + rent_other_expenses
    
    # Grow Portfolios
    after_tax_return = investment_return * (1 - investment_tax_rate)
    buyer_portfolio *= (1 + after_tax_return)
    renter_portfolio *= (1 + after_tax_return)
    
    # Invest the Cash Flow Difference
    if current_buy_cost > current_rent_cost:
        renter_portfolio += (current_buy_cost - current_rent_cost)
    elif current_rent_cost > current_buy_cost:
        buyer_portfolio += (current_rent_cost - current_buy_cost)
    
    # Calculate Final Liquid Net Worth for the Year
    disposition_fee = current_property_value * disposition_cost_pct
    current_buy_equity = current_property_value - current_mortgage - disposition_fee
    
    # Record values for table and graph
    buy_net_worth.append(current_buy_equity + buyer_portfolio)
    rent_net_worth.append(renter_portfolio)
    property_values.append(current_property_value)
    mortgage_balances.append(current_mortgage)
    buyer_portfolios.append(buyer_portfolio)
    renter_portfolios.append(renter_portfolio)
    
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
    name='Buy (Equity + Portfolio)',
    line=dict(color='#4169E1', width=3),
    marker=dict(size=6),
    hovertemplate="Year %{x}<br>Total Net Worth: $%{y:,.0f}<extra></extra>"
))

# Add Rent Scenario Line
fig.add_trace(go.Scatter(
    x=years_list, 
    y=rent_net_worth, 
    mode='lines+markers',
    name='Rent (Portfolio Value)',
    line=dict(color='#FFD700', width=3),
    marker=dict(size=6),
    hovertemplate="Year %{x}<br>Total Net Worth: $%{y:,.0f}<extra></extra>"
))

# Styling the chart to look modern and clean
fig.update_layout(
    title=dict(text=f"Total Net Worth Projection Over {time_horizon} Years", font=dict(size=20)),
    xaxis_title="Years",
    yaxis_title="Net Liquid Value ($)",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=60, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# === CASH FLOW SUMMARY (Modern Layout) ===
st.markdown("### Year 1 Snapshot")

col1, col2 = st.columns(2)

with col1:
    st.info("**BUY OPTION**")
    st.metric(label="Starting Investment Portfolio", value=f"${(initial_capital - initial_outlay_buy):,.0f}")
    st.markdown(f"**Total Annual Buy Cost: \${year_1_buy_cost:,.0f}**")
    st.write(f"Mortgage: \${annual_mortgage_pmt:,.0f}")
    st.write(f"Property Taxes: \${buy_property_taxes:,.0f}")
    st.write(f"Maintenance: \${buy_maintenance:,.0f}")
    st.write(f"Utilities: \${buy_utilities:,.0f}")
    st.write(f"Insurance: \${buy_insurance:,.0f}")

with col2:
    st.warning("**RENT OPTION**")
    st.metric(label="Starting Investment Portfolio", value=f"${initial_capital:,.0f}")
    st.markdown(f"**Total Annual Rent Cost: \${year_1_rent_cost:,.0f}**")
    st.write(f"Rent: \${monthly_rent * 12:,.0f}")
    st.write(f"Utilities: \${rent_utilities:,.0f}")
    st.write(f"Insurance: \${rent_insurance:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

if year_1_buy_cost > year_1_rent_cost:
    st.success(f"**Insight:** The Renter has lower monthly costs and invests the cash flow savings of **\${(year_1_buy_cost - year_1_rent_cost):,.2f}** into their portfolio in Year 1.")
elif year_1_rent_cost > year_1_buy_cost:
    st.success(f"**Insight:** The Buyer has lower monthly costs and invests the cash flow savings of **\${(year_1_rent_cost - year_1_buy_cost):,.2f}** into their portfolio in Year 1.")
else:
    st.success("**Insight:** Both options have identical monthly costs in Year 1. No differential cash flow is invested.")

st.markdown("---")

# === FINAL YEAR SNAPSHOT ===
st.markdown(f"### Final Year Snapshot (Year {time_horizon})")

col3, col4 = st.columns(2)

with col3:
    st.info("**BUY OPTION: WALK-AWAY NET WORTH**")
    st.metric(label="Total Buy Net Worth", value=f"${buy_net_worth[-1]:,.0f}")
    st.write(f"Final Property Value: \${property_values[-1]:,.0f}")
    st.write(f"Remaining Mortgage: \${mortgage_balances[-1]:,.0f}")
    st.write(f"Buyer Investment Portfolio: \${buyer_portfolios[-1]:,.0f}")

with col4:
    st.warning("**RENT OPTION: FINAL PORTFOLIO**")
    st.metric(label="Total Rent Net Worth", value=f"${rent_net_worth[-1]:,.0f}")
    st.write(f"Renter Investment Portfolio: \${renter_portfolios[-1]:,.0f}")

st.markdown("---")

# === YEAR-BY-YEAR DATA TABLE ===
with st.expander("View Year-by-Year Data"):
    df = pd.DataFrame({
        "Year": years_list,
        "Property Value ($)": property_values,
        "Mortgage Balance ($)": mortgage_balances,
        "Buyer Portfolio ($)": buyer_portfolios,
        "Buy Scenario Net Worth ($)": buy_net_worth,
        "Renter Portfolio ($)": renter_portfolios,
        "Rent Scenario Net Worth ($)": rent_net_worth
    })
    
    # Format the dataframe to show currency properly
    styled_df = df.style.format({
        "Property Value ($)": "{:,.0f}",
        "Mortgage Balance ($)": "{:,.0f}",
        "Buyer Portfolio ($)": "{:,.0f}",
        "Buy Scenario Net Worth ($)": "{:,.0f}",
        "Renter Portfolio ($)": "{:,.0f}",
        "Rent Scenario Net Worth ($)": "{:,.0f}"
    })
    
    st.dataframe(styled_df, use_container_width=True)

st.markdown("---")

# === DISCLAIMER & METHODOLOGY ===
with st.expander("How this calculator works & Default Assumptions"):
    st.markdown("""
    **Methodology: Differential Cash Flow**
    This calculator provides a true apples-to-apples comparison by assuming both the renter and the buyer commit the exact same amount of cash to their housing each year. 
    * If buying costs more per month, the renter invests the difference into their portfolio. 
    * If renting costs more per month, the buyer invests the difference into their portfolio. 
    
    **Net Worth Calculation**
    * **Buy Scenario:** Calculates the liquid walk-away money. This is the estimated property value, minus the remaining mortgage balance, minus the cost to sell the home, plus whatever is left in the buyer's investment portfolio.
    * **Rent Scenario:** Represents the total value of the renter's investment portfolio.
    
    **Default Assumptions**
    * **Initial Capital (\$1,000,000):** Represents the total cash available before making a housing decision.
    * **Inflation & Appreciation (2.10%):** A baseline assumption for the annual growth of property values, rent prices, and general living expenses.
    * **Investment Return (5.00%):** The assumed gross annual return on any capital kept in the investment portfolios.
    * **Time Horizon (20 Years):** The duration of the simulation before liquidating the property.
    * **Expenses (\$0):** All ongoing maintenance, tax, and utility expenses default to zero to allow for custom inputs based on specific properties.
    """)
