import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

def run_rent_vs_buy_model(params):
    years = params['time_horizon']
    
    # 1. Initial Setup
    down_payment = params['purchase_price'] - params['mortgage_balance']
    initial_outlay_buy = down_payment + params['acquisition_cost']
    
    # Renter starts by investing what the buyer put down
    renter_portfolio = initial_outlay_buy
    
    # Trackers
    buy_net_worth = []
    rent_net_worth = []
    
    current_property_value = params['purchase_price']
    current_mortgage = params['mortgage_balance']
    current_annual_rent = params['monthly_rent'] * 12
    
    # Annual Cost Summaries (First Year)
    annual_mortgage_pmt = params['monthly_mortgage_payment'] * 12
    year_1_buy_cost = annual_mortgage_pmt + params['annual_maintenance'] + params['other_ownership_expenses'] + params['annual_utilities']
    year_1_rent_cost = current_annual_rent + params['annual_utilities']
    
    # 2. Year-by-Year Simulation
    for year in range(1, years + 1):
        # --- BUY SCENARIO ---
        # Calculate mortgage paydown for the year
        interest_paid = current_mortgage * params['mortgage_rate']
        principal_paid = annual_mortgage_pmt - interest_paid
        
        # Ensure we don't overpay the mortgage
        if principal_paid > current_mortgage:
            principal_paid = current_mortgage
            annual_mortgage_pmt = interest_paid + principal_paid # Adjust final payment
            
        current_mortgage -= principal_paid
        
        # Property appreciates
        current_property_value *= (1 + params['property_appreciation'])
        
        # Calculate Buyer Net Worth (if liquidated this year)
        disposition_fee = current_property_value * params['disposition_cost_pct']
        current_buy_equity = current_property_value - current_mortgage - disposition_fee
        buy_net_worth.append(current_buy_equity)
        
        # --- RENT SCENARIO ---
        # Calculate cash flow difference (Buy Cost - Rent Cost for the year)
        current_buy_cost = annual_mortgage_pmt + params['annual_maintenance'] + params['other_ownership_expenses'] + params['annual_utilities']
        current_rent_cost = current_annual_rent + params['annual_utilities']
        
        cash_flow_difference = current_buy_cost - current_rent_cost
        
        # Apply investment growth to renter's portfolio (after-tax)
        after_tax_return = params['investment_return'] * (1 - params['investment_tax_rate'])
        renter_portfolio *= (1 + after_tax_return)
        
        # Add the cash flow savings to the portfolio (if buying costs more, renter invests the difference)
        # If renting costs more, the renter withdraws from the portfolio to cover the shortfall
        renter_portfolio += cash_flow_difference 
        rent_net_worth.append(renter_portfolio)
        
        # Inflate rent and expenses for next year
        current_annual_rent *= (1 + params['rent_inflation'])
        params['annual_maintenance'] *= (1 + params['general_inflation'])
        params['other_ownership_expenses'] *= (1 + params['general_inflation'])
        params['annual_utilities'] *= (1 + params['general_inflation'])

    # 3. Visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Royal Blue (#4169E1) and Gold (#FFD700)
    ax.plot(range(1, years + 1), buy_net_worth, color='#4169E1', linewidth=3, label='Buy Scenario (Net Equity)')
    ax.plot(range(1, years + 1), rent_net_worth, color='#FFD700', linewidth=3, label='Rent Scenario (Portfolio Value)')
    
    ax.set_title(f'Rent vs. Buy Net Worth Over {years} Years', fontsize=14, fontweight='bold')
    ax.set_xlabel('Years', fontsize=12)
    ax.set_ylabel('Net Liquid Value ($)', fontsize=12)
    
    # Format Y-axis as currency
    formatter = ticker.FuncFormatter(lambda x, pos: f'${x:,.0f}')
    ax.yaxis.set_major_formatter(formatter)
    
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(fontsize=12)
    plt.tight_layout()
    plt.show()
    
    # 4. Cash Flow Summary Output
    print("="*40)
    print("FIRST YEAR CASH FLOW SUMMARY")
    print("="*40)
    print(f"BUY OPTION:")
    print(f"  Annual Mortgage Payment: ${annual_mortgage_pmt:,.2f}")
    print(f"  Annual Maintenance:      ${params['annual_maintenance']:,.2f}")
    print(f"  Other Expenses (Taxes):  ${params['other_ownership_expenses']:,.2f}")
    print(f"  Utilities:               ${params['annual_utilities']:,.2f}")
    print(f"  ----------------------------------")
    print(f"  TOTAL ANNUAL BUY COST:   ${year_1_buy_cost:,.2f}")
    print("\n")
    print(f"RENT OPTION:")
    print(f"  Annual Rent:             ${params['monthly_rent'] * 12:,.2f}")
    print(f"  Utilities:               ${params['annual_utilities']:,.2f}")
    print(f"  ----------------------------------")
    print(f"  TOTAL ANNUAL RENT COST:  ${year_1_rent_cost:,.2f}")
    print("\n")
    if year_1_buy_cost > year_1_rent_cost:
        print(f"-> Renter invests the cash flow savings of ${(year_1_buy_cost - year_1_rent_cost):,.2f} in Year 1.")
    else:
        print(f"-> Buyer has a cash flow advantage of ${(year_1_rent_cost - year_1_buy_cost):,.2f} in Year 1.")
    print("="*40)

# Example Dictionary of Variables
variables = {
    'purchase_price': 600000,
    'mortgage_balance': 480000,
    'monthly_mortgage_payment': 2800,
    'mortgage_rate': 0.05,
    'monthly_rent': 2500,
    'property_appreciation': 0.03,
    'rent_inflation': 0.025,
    'general_inflation': 0.02, # For maintenance and utilities
    'investment_return': 0.06,
    'investment_tax_rate': 0.25, # Static non-reg tax rate
    'time_horizon': 25,
    'acquisition_cost': 10000, # Land transfer tax, legal, etc.
    'disposition_cost_pct': 0.05, # 5% realtor/legal fees on sale
    'annual_maintenance': 3000,
    'other_ownership_expenses': 4500, # Property taxes, insurance
    'annual_utilities': 2400
}

run_rent_vs_buy_model(variables)
