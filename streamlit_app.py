import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Page Configuration for a wide, clean layout
st.set_page_config(page_title="Rent vs Buy Calculator", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Apple-style UI and Professional Print Formatting
st.markdown("""
    <style>
    /* Professional Print Styling */
    @media print {
        /* Hide web-only elements */
        header, .stSidebar, .stActionButton, .stButton, .stExpander, [data-testid="stToolbar"], [data-testid="stDecoration"] {
            display: none !important;
        }
        /* Expand the main content area to full page width */
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
        /* Ensure charts don't get cut off between pages */
        .stPlotlyChart {
            page-break-inside: avoid;
        }
        /* Force background colors to show in PDF (important for snapshots) */
        body {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
    }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { font-weight: 300; color: #1f1f1f; }
    h2, h3 { font-weight: 400; color: #333333; }
    </style>
""", unsafe_allow_html=True)

st.title("Rent vs. Buy Financial Comparison")
st.markdown("A comprehensive cash flow and net worth analysis.")

# === SIDEBAR INPUTS ===
st.sidebar.header("Primary Variables")

# Reset Action
if st.sidebar.button("Reset All Variables", type="primary", use_container_width=True):
    if "reset_key" not in st.session_state:
        st.session_state.reset_key = 0
    st.session_state.reset_key += 1
    st.rerun()

st.sidebar.info("💡 **To Save as PDF:** Press **Ctrl+P** (Windows) or **Cmd+P** (Mac). The report will automatically reformat for print.")

if "reset_key" not in st.session_state:
    st.session_state.reset_key = 0
rk = st.session_state.reset_key

initial_capital = st.sidebar.number_input("Initial Capital Available ($)", min_value=0, value=1000000, step=50000, key=f"cap_{rk}")
purchase_price = st.sidebar.number_input("Purchase Price ($)", min_value=0, value=500000, step=10000, key=f"price_{rk}")
mortgage_balance = st.sidebar.number_input("Mortgage Balance ($)", min_value=0, value=0, step=10000, key=f"mort_{rk}")
monthly_mortgage_payment = st.sidebar.number_input("Monthly Mortgage Payment ($)", min_value=0, value=0, step=100, key=f"pmt_{rk}")
mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", min_value=0.0, value=4.0, step=0.1, key=f"rate_{rk}") / 100
monthly_rent = st.sidebar.number_input("Monthly Rent ($)", min_value=0, value=2000, step=100, key=f"rent_{rk}")
time_horizon = st.sidebar.number_input("Time Horizon (Years)", value=20, min_value=1, max_value=50, step=1, key=f"time_{rk}")

with st.sidebar.expander("Growth & Inflation Assumptions"):
    property_appreciation = st.number_input("Property Appreciation (%)", value=2.10, step=0.10, format="%.2f", key=f"app_{rk}") / 100
    rent_inflation = st.number_input("Rent Inflation (%)", value=2.10, step=0.10, format="%.2f", key=f"r_inf_{rk}") / 100
    general_inflation = st.number_input("General Inflation (%)", value=2.10, step=0.10, format="%.2f", key=f"g_inf_{rk}") / 100
    investment_return = st.number_input("Investment Return (%)", value=5.0, step=0.1, key=f"inv_ret_{rk}") / 100
    investment_tax_rate = st.number_input("Investment Tax Rate (%)", value=0.0, step=1.0, key=f"tax_{rk}") / 100

with st.sidebar.expander("Buying Expenses"):
    acquisition_cost = st.number_input("Acquisition Costs ($)", value=0, step=1000, key=f"acq_{rk}")
    disposition_cost_pct = st.number_input("Disposition Costs (%)", value=5.0, step=0.5, key=f"disp_{rk}") / 100
    buy_property_taxes = st.number_input("Property Taxes ($/yr)", value=0, step=500, key=f"b_tax_{rk}")
    buy_maintenance = st.number_input("Maintenance ($/yr)", value=0, step=500, key=f"b_maint_{rk}")
    buy_utilities = st.number_input("Buying Utilities ($/yr)", value=0, step=100, key=f"b_util_{rk}")
    buy_insurance = st.number_input("Home Insurance ($/yr)", value=0, step=100, key=f"b_ins_{rk}")
    buy_other_expenses = st.number_input("Other Buying Expenses ($/yr)", value=0, step=100, key=f"b_oth_{rk}")

with st.sidebar.expander("Renting Expenses"):
    rent_utilities = st.number_input("Renting Utilities ($/yr)", value=0, step=100, key=f"r_util_{rk}")
    rent_insurance = st.number_input("Tenant Insurance ($/yr)", value=0, step=50, key=f"r_ins_{rk}")
    rent_other_expenses = st.number_input("Other Renting Expenses ($/yr)", value=0, step=100, key=f"r_oth_{rk}")

# === CALCULATION LOGIC ===
down_payment = purchase_price - mortgage_balance
initial_outlay_buy = down_payment + acquisition_cost

if initial_capital < initial_outlay_buy:
    st.error(f"**Error:** The Initial Capital (\${initial_capital:,.0f}) is not enough to cover the down payment and acquisition costs (\${initial_outlay_buy:,.0f}).")
    st.stop()

buyer_portfolio = initial_capital - initial_outlay_buy
renter_portfolio = initial_capital

years_list, buy_net_worth, rent_net_worth = [], [], []
property_values, mortgage_balances, buyer_portfolios, renter_portfolios = [], [], [], []
buying_expenses_list, renting_expenses_list, disposition_costs_list = [], [], []

current_property_value, current_mortgage, current_annual_rent = purchase_price, mortgage_balance, monthly_rent * 12
annual_mortgage_pmt = monthly_mortgage_payment * 12
year_1_buy_cost = annual_mortgage_pmt + buy_property_taxes + buy_maintenance + buy_utilities + buy_insurance + buy_other_expenses
year_1_rent_cost = current_annual_rent + rent_utilities + rent_insurance + rent_other_expenses

break_even_year = None

for year in range(1, time_horizon + 1):
    years_list.append(year)
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
    current_buy_cost = annual_mortgage_pmt + buy_property_taxes + buy_maintenance + buy_utilities + buy_insurance + buy_other_expenses
    current_rent_cost = current_annual_rent + rent_utilities + rent_insurance + rent_other_expenses
    after_tax_return = investment_return * (1 - investment_tax_rate)
    buyer_portfolio *= (1 + after_tax_return)
    renter_portfolio *= (1 + after_tax_return)
    if current_buy_cost > current_rent_cost:
        renter_portfolio += (current_buy_cost - current_rent_cost)
    elif current_rent_cost > current_buy_cost:
        buyer_portfolio += (current_rent_cost - current_buy_cost)
    disposition_fee = current_property_value * disposition_cost_pct
    current_buy_equity = current_property_value - current_mortgage - disposition_fee
    total_buy_nw, total_rent_nw = current_buy_equity + buyer_portfolio, renter_portfolio
    buy_net_worth.append(total_buy_nw)
    rent_net_worth.append(total_rent_nw)
    if break_even_year is None and total_buy_nw > total_rent_nw:
        break_even_year = year
    property_values.append(current_property_value)
    mortgage_balances.append(current_mortgage)
    buyer_portfolios.append(buyer_portfolio)
    renter_portfolios.append(renter_portfolio)
    buying_expenses_list.append(current_buy_cost)
    renting_expenses_list.append(current_rent_cost)
    disposition_costs_list.append(disposition_fee)
    current_annual_rent *= (1 + rent_inflation)
    buy_property_taxes *= (1 + general_inflation); buy_maintenance *= (1 + general_inflation)
    buy_utilities *= (1 + general_inflation); buy_insurance *= (1 + general_inflation)
    buy_other_expenses *= (1 + general_inflation); rent_utilities *= (1 + general_inflation)
    rent_insurance *= (1 + general_inflation); rent_other_expenses *= (1 + general_inflation)

# === OUTPUTS ===
fig = go.Figure()
fig.add_trace(go.Scatter(x=years_list, y=buy_net_worth, mode='lines+markers', name='Buy (Equity + Portfolio)', line=dict(color='#4169E1', width=3)))
fig.add_trace(go.Scatter(x=years_list, y=rent_net_worth, mode='lines+markers', name='Rent (Portfolio Value)', line=dict(color='#FFD700', width=3)))
fig.update_layout(title=dict(text="Total Net Worth Projection"), template="plotly_white", margin=dict(l=0, r=0, t=60, b=0))
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Year 1 Snapshot")
c1, c2 = st.columns(2)
c1.info(f"**BUY OPTION**\n\nTotal Cost: \${year_1_buy_cost:,.0f}")
c2.warning(f"**RENT OPTION**\n\nTotal Cost: \${year_1_rent_cost:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)
if year_1_buy_cost > year_1_rent_cost:
    st.success(f"**Insight:** The Renter has lower monthly costs and invests the cash flow savings of **\${(year_1_buy_cost - year_1_rent_cost):,.2f}** into their portfolio in Year 1.")
elif year_1_rent_cost > year_1_buy_cost:
    st.success(f"**Insight:** The Buyer has lower monthly costs and invests the cash flow savings of **\${(year_1_rent_cost - year_1_buy_cost):,.2f}** into their portfolio in Year 1.")

st.markdown("---")
st.markdown(f"### Final Year Snapshot (Year {time_horizon})")
c3, c4 = st.columns(2)
c3.info(f"**BUY NET WORTH**\n\n\${buy_net_worth[-1]:,.0f}")
c4.warning(f"**RENT NET WORTH**\n\n\${rent_net_worth[-1]:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)
if buy_net_worth[-1] > rent_net_worth[-1]:
    st.success(f"**Long-Term Insight:** Over {time_horizon} years, the **Buy** option yields a higher total net worth by **\${(buy_net_worth[-1] - rent_net_worth[-1]):,.0f}**.")
else:
    st.success(f"**Long-Term Insight:** Over {time_horizon} years, the **Rent** option yields a higher total net worth by **\${(rent_net_worth[-1] - buy_net_worth[-1]):,.0f}**.")

if break_even_year: 
    st.info(f"**Break-Even Point:** Buying becomes more advantageous than renting starting in **Year {break_even_year}**.")
else:
    st.info(f"**Break-Even Point:** Within this {time_horizon}-year horizon, the Renting scenario remains more advantageous.")

with st.expander("View Year-by-Year Data breakdown"):
    df = pd.DataFrame({
        "Year": years_list,
        "Property Value ($)": property_values,
        "Mortgage Balance ($)": mortgage_balances,
        "Buyer Portfolio ($)": buyer_portfolios,
        "Annual Buying Costs ($)": buying_expenses_list,
        "Hypothetical Disposition Cost ($)": disposition_costs_list,
        "Buy Scenario Net Worth ($)": buy_net_worth,
        "Annual Renting Costs ($)": renting_expenses_list,
        "Renter Portfolio ($)": renter_portfolios,
        "Rent Scenario Net Worth ($)": rent_net_worth
    })
    styled_df = df.style.format("{:,.0f}", subset=df.columns[1:]) \
        .set_properties(**{'text-align': 'center'}) \
        .set_properties(subset=['Buy Scenario Net Worth ($)'], **{'background-color': '#4169E1', 'color': 'white'}) \
        .set_properties(subset=['Rent Scenario Net Worth ($)'], **{'background-color': '#FFD700', 'color': 'black'})
    st.dataframe(styled_df, use_container_width=True)

st.markdown("---")
with st.expander("How this calculator works & Default Assumptions"):
    st.markdown("""
    **Methodology: Differential Cash Flow**
    This calculator provides a true apples-to-apples comparison by assuming both the renter and the buyer commit the exact same amount of cash to their housing each year.
    * If buying costs more per month, the renter invests the difference into their portfolio.
    * If renting costs more per month, the buyer invests the difference into their portfolio.
    
    **Net Worth Calculation**
    * **Buy Scenario:** Calculates the liquid walk-away money (Estimated property value - mortgage - selling costs + buyer's investment portfolio).
    * **Rent Scenario:** Represents the total value of the renter's investment portfolio.
    """)
