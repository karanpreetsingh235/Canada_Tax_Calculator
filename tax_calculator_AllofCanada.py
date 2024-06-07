import streamlit as st
import numpy as np
import pandas as pd

# Constants for tax rates and deductions
# Federal tax brackets and rates for 2023
FEDERAL_BRACKETS = np.array([50197, 100392, 155625, 221708])
FEDERAL_RATES = np.array([0.15, 0.205, 0.26, 0.29, 0.33])

# Provincial tax brackets and rates for 2023
PROVINCIAL_TAX_INFO = {
    "Alberta": {"brackets": np.array([131220, 157464, 209952, 314928]), "rates": np.array([0.10, 0.12, 0.13, 0.14, 0.15])},
    "British Columbia": {"brackets": np.array([43070, 86141, 98901, 120094, 162832]), "rates": np.array([0.0506, 0.077, 0.105, 0.1229, 0.147, 0.168])},
    "Manitoba": {"brackets": np.array([34670, 73710]), "rates": np.array([0.108, 0.1275, 0.174])},
    "New Brunswick": {"brackets": np.array([45277, 90556, 138491, 160776]), "rates": np.array([0.0968, 0.1482, 0.1652, 0.1784, 0.203])},
    "Newfoundland and Labrador": {"brackets": np.array([39222, 78447, 139780, 200000]), "rates": np.array([0.087, 0.145, 0.158, 0.183, 0.21])},
    "Northwest Territories": {"brackets": np.array([45629, 91259, 147667]), "rates": np.array([0.059, 0.086, 0.122, 0.1405])},
    "Nova Scotia": {"brackets": np.array([29590, 59180, 93000, 150000]), "rates": np.array([0.0879, 0.1495, 0.1667, 0.175, 0.21])},
    "Nunavut": {"brackets": np.array([48229, 96458, 156183]), "rates": np.array([0.04, 0.07, 0.09, 0.115])},
    "Ontario": {"brackets": np.array([46226, 92454, 150000, 220000]), "rates": np.array([0.0505, 0.0915, 0.1116, 0.1216, 0.1316])},
    "Prince Edward Island": {"brackets": np.array([31984, 63969]), "rates": np.array([0.098, 0.138, 0.167])},
    "Quebec": {"brackets": np.array([46295, 92595, 113785, 108390]), "rates": np.array([0.15, 0.20, 0.24, 0.2575])},
    "Saskatchewan": {"brackets": np.array([46677, 133638]), "rates": np.array([0.105, 0.125, 0.145])},
    "Yukon": {"brackets": np.array([51296, 102592, 155625, 500000]), "rates": np.array([0.064, 0.09, 0.109, 0.128, 0.15])}
}

# CPP and EI rates
CPP_RATE = 0.0525
CPP_MAX = 3500  # Maximum CPP contribution per year
EI_RATE = 0.0158
EI_MAX = 889.54  # Maximum EI contribution per year

def calculate_tax(income, brackets, rates):
    """ Calculate tax based on income and provided brackets and rates. """
    tax = 0
    last_bracket = 0
    for bracket, rate in zip(brackets, rates):
        if income > bracket:
            tax += (bracket - last_bracket) * rate
            last_bracket = bracket
        else:
            tax += (income - last_bracket) * rate
            break
    if income > brackets[-1]:
        tax += (income - brackets[-1]) * rates[-1]
    return tax

def main():
    st.title('Canada-Wide Income Tax Calculator')

    # User selects a province
    province = st.selectbox('Select your province:', list(PROVINCIAL_TAX_INFO.keys()))

    # User selects input type (Monthly or Annual)
    income_type = st.radio("Input your gross income on a:", ("Monthly", "Annual"))
    income = st.number_input(f'Enter your {income_type.lower()} gross income:', min_value=0.0, format='%f')
    if income_type == "Monthly":
        income *= 12  # Convert monthly to annual

    # User selects output frequency
    output_frequency = st.radio("Select the output frequency:", ('Biweekly', 'Monthly', 'Yearly'))

    # Checkboxes for deductions to display
    show_federal_tax = st.checkbox("Show Federal Tax", value=True)
    show_prov_tax = st.checkbox("Show Provincial Tax", value=True)
    show_cpp = st.checkbox("Show CPP Contribution", value=True)
    show_ei = st.checkbox("Show EI Contribution", value=True)

    if st.button('Calculate Taxes'):
        # Get the selected province's tax information
        provincial_brackets = PROVINCIAL_TAX_INFO[province]['brackets']
        provincial_rates = PROVINCIAL_TAX_INFO[province]['rates']

        # Calculate federal and provincial taxes
        federal_tax = calculate_tax(income, FEDERAL_BRACKETS, FEDERAL_RATES)
        provincial_tax = calculate_tax(income, provincial_brackets, provincial_rates)

        # Calculate CPP and EI contributions
        cpp = income * CPP_RATE if income * CPP_RATE < CPP_MAX else CPP_MAX
        ei = income * EI_RATE if income * EI_RATE < EI_MAX else EI_MAX

        total_deductions = federal_tax + provincial_tax + cpp + ei
        net_income = income - total_deductions

        frequency_factor = {'Yearly': 1, 'Monthly': 12, 'Biweekly': 26}[output_frequency]
        multiplier = 1 / frequency_factor

        # Display selected deductions
        if show_federal_tax:
            st.write(f"{output_frequency} Federal Tax: ${federal_tax * multiplier:.2f}")
        if show_prov_tax:
            st.write(f"{output_frequency} Provincial Tax ({province}): ${provincial_tax * multiplier:.2f}")
        if show_cpp:
            st.write(f"{output_frequency} CPP Contributions: ${cpp * multiplier:.2f}")
        if show_ei:
            st.write(f"{output_frequency} EI Contributions: ${ei * multiplier:.2f}")
        
        st.write(f"{output_frequency} Net Income in {province}: ${net_income * multiplier:.2f}")
        
        # Show income comparison across provinces
        results = []
        for prov, tax_info in PROVINCIAL_TAX_INFO.items():
            prov_tax = calculate_tax(income, tax_info['brackets'], tax_info['rates'])
            net = income - (federal_tax + prov_tax + cpp + ei)
            results.append({"Province": prov, "Net Income": net * multiplier})

        df = pd.DataFrame(results)
        st.table(df.sort_values(by="Province"))

if __name__ == '__main__':
    main()
