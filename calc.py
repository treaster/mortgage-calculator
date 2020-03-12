#!/usr/bin/env python

# A Python script that may help with mortgage + investment mathing
#
# TLDR Instructions:
# 1. Specify your query or scenarios in a JSON file.
# 2. Run the script with the JSON file as a command line argument

# Details:
#
# Specify a JSON file that looks something like this:
#
# years_limit:
#   The time horizon are you interested in estimating for.
#   This need not be the mortgage term.
#   e.g. Do you want to compare outcomes after 10, 20, or 30 years?
#   The loan may not be fully paid off.
#
# monthly_income:
#   Your total take-home mortgage + investments.
#   Assume any income taxes are already applied.
#   Do not include non-home discretionary spending.
#   Income outside mortgage payments is assumed to be invested immediately
#
# income_tax_rate:
#   The tax rate your mortgage interest deduction go against
#
# investment_annual_return:
#   The annual rate of return you expect to get from the stock market
#
# capital_gains_rate:
#   The tax rate you expect to have applied to your investment gains
#
# scenarios:
#   A list of tuples describing a loan option
#   Fields are:
#     (loan_balance, loan_term, interest_rate, monthly_payment)

'''
{
    "years_limit": 30,
    "monthly_income": 1000,
    "income_tax_rate": .25,
    "investment_annual_return": .08,
    "capital_gains_rate": .20,

    "comment": "scenarios fields are (loan_balance, loan_term, interest_rate, monthly_payment)",
    "scenarios": [
        [100000, 30, .035, 1000],
        [100000, 25, .035, 1200],
        [100000, 30, .035, 1500],
        [100000, 15, .030, 2500]
    ]
}
'''

import sys
import json

# *** Implementation ***

def compute(monthly_income,
            years_limit,
            income_tax_rate,
            investment_annual_return,
            capital_gains_rate,
            loan_balance,
            duration_years,
            loan_rate,
            monthly_payment):

    total_principal_paid = 0
    total_interest_paid = 0
    total_invested = 0
    invest_balance = 0

    for i in xrange(0, years_limit * 12):
        monthly_investment = 0

        # Compute loan interest + principal if loan balance is positive
        if loan_balance > 0:
            monthly_interest_paid = loan_balance * loan_rate / 12
            total_interest_paid += monthly_interest_paid

            # Count the tax deduction
            # TODO(treaster): this doesn't consider the 1M or 750k deduction limit
            # TODO(treaster): This should compound annually, not monthly
            monthly_investment += monthly_interest_paid * income_tax_rate

            monthly_principal_paid = (monthly_payment - monthly_interest_paid)
            total_principal_paid += monthly_principal_paid

            # TODO(treaster): will likely overpay in the last month
            loan_balance -= monthly_principal_paid
        else:
            # once the loan is paid off, we make no payments
            monthly_payment = 0

        # Invest the remainder in the market
        monthly_investment += monthly_income - monthly_payment
        total_invested += monthly_investment
        monthly_bump = invest_balance * investment_annual_return / 12.0 + monthly_investment
        invest_balance = invest_balance + monthly_bump

        if False:
            # Print some debugging info
            print(monthly_income, monthly_payment, monthly_income-monthly_payment,monthly_bump, monthly_investment, invest_balance)

        if False:
            print(monthly_income, monthly_payment, monthly_investment, invest_balance, total_invested)

        if False:
            print("{:7d}\t{:4d}\t{:4d}\t{:4d}\t{:4d}".format(
               int(loan_balance),
               int(total_interest_paid),
               int(total_principal_paid),
               int(total_invested),
               int(invest_balance)))

    # Find the part of the investment balance that is gains. Tax that.
    invest_gains = invest_balance - total_invested
    invest_gains_after_tax = invest_gains * (1.0 - capital_gains_rate)

    # Net is investments + home equity - investment taxes
    net = total_invested + invest_gains_after_tax + total_principal_paid # (last is equity)
    return (duration_years, loan_rate * 100, int(net), int(invest_balance), int(total_interest_paid), int(total_principal_paid))


def main():
    args = sys.argv
    if len(args) != 2:
        print("usage: args[0] [json config file]")
        sys.exit(1)
    config_path = args[1]

    data = None
    with open(config_path, 'r') as config_file:
        config_data = config_file.read()
    config = json.loads(config_data)

    monthly_income =           config['monthly_income']
    years_limit =              config['years_limit']
    income_tax_rate =          config['income_tax_rate']
    investment_annual_return = config['investment_annual_return']
    capital_gains_rate =       config['capital_gains_rate']

    datas = []
    for scen in config['scenarios']:
        result = compute(
            monthly_income,
            years_limit,
            income_tax_rate,
            investment_annual_return,
            capital_gains_rate,
            *scen)
        datas.append(result)

    # Sort by net balance after N years
    datas.sort(key=lambda x: -x[2])

    # Verified the total interest paid against other online mortgage calculators.
    # Investment and other calculations could be wrong.
    print("After {:d} years:".format(years_limit))
    for row in datas:
        (duration_years, loan_rate , net, invest_balance, total_interest_paid, total_principal_paid) = row
        print("  {:2d} years @ {:.2f}% -> {:9d} net ({:9d} invest_balance, {:7d} total_interest_paid, {:7d} total_principal_paid)".format(
            duration_years,
            loan_rate,
            net,
            invest_balance,
            total_interest_paid,
            total_principal_paid,
        ))

if __name__ == "__main__":
    main()
