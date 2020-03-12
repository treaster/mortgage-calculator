#!/usr/bin/env python

# A Python script that may help with mortgage + investment mathing
#
# Instructions:
# 1. Copy to a file in your Python-enabled environment of choice
# 2. Fill in your values in the global vars below
# 3. Run the script


# *** Global Vars ***

# monthly_income is your total mortgage + investments.
# Do not include non-home discretionary spending.
# Income outside mortgage payments is assumed to go in the market immediately
monthly_income = 1000

# What annual rate of return do you expect to get from the stock market?
investment_annual_return = .08

# What tax rate will your mortgage interest deduction go against?
tax_rate = .25

# What tax rate will apply to your investment proceeds?
capital_gains_rate = .20

# What time horizon are you interested? This need not be the mortgage term.
# e.g. Do you want to compare outcomes after 10, 20, or 30 years?
# Loan may still be outstanding.
years_limit = 30

# Specify the scenarios to consider. Elements are:
# (loan_balance, loan_term, interest_rate, monthly_payment)
scenarios = (
    (100000, 30, .035, 1000),
    (100000, 25, .035, 1200),
    (100000, 20, .035, 1500),
    (100000, 15, .030, 2500),
)


# *** Implementation ***

def compute(loan_balance, duration_years, loan_rate, monthly_payment):
    global monthly_income
    global investment_annual_return
    global years_limit

    total_principal_paid = 0
    total_interest_paid = 0
    total_invested = 0
    invest_balance = 0

    # for i in xrange(0, duration_years * 12):
    for i in xrange(0, years_limit * 12):
        monthly_investment = 0

        # Compute loan interest + principal if loan balance is positive
        if loan_balance > 0:
            monthly_interest_paid = loan_balance * loan_rate / 12
            total_interest_paid += monthly_interest_paid

            # Count the tax deduction
            # TODO(treaster): this doesn't consider the 1M or 750k deduction limit
            # TODO(treaster): This should compound annually, not monthly
            monthly_investment += monthly_interest_paid * tax_rate

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


datas = []
for scen in scenarios:
    datas.append(compute(*scen))

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
