import asyncio
import os
import json

from monarchmoney import MonarchMoney

_SESSION_FILE_ = '.mm-session.pickle'

def main() -> None:
    # Use session file
    mm = MonarchMoney(session_file=_SESSION_FILE_)
    asyncio.run(mm.login())

    # Subscription details
    subs = asyncio.run(mm.get_subscription_details())
    print(subs)

    # Accounts
    accounts = asyncio.run(mm.get_accounts())
    with open("data.json", "w") as outfile:
        json.dump(accounts, outfile)

    # Transaction categories
    categories = asyncio.run(mm.get_transaction_categories())
    with open("categories.json", "w") as outfile:
        json.dump(categories, outfile)

    for c in categories.get("categories"):
        print(c.get("group").get("type"), "-", c.get("group").get("name"), "-", c.get("name"), )

    # Cashflow
    cashflow = asyncio.run(mm.get_cashflow_summary())
    with open("cashflow.json", "w") as outfile:
        json.dump(cashflow, outfile)

    for c in cashflow.get("summary"):
        print("Income: ", c.get("summary").get("sumIncome"), ", Expense:", c.get("summary").get("sumExpense"), ", Savings: ", c.get("summary").get("savings"), "(", c.get("summary").get("savingsRate") * 100, "%)")


main()
