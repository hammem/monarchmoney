import asyncio
import os
import json

from monarchmoney import MonarchMoney

_SESSION_FILE_ = '.mm/mm_session.pickle'

def main() -> None:
    # Use session file
    mm = MonarchMoney(session_file=_SESSION_FILE_)
    asyncio.run(mm.interactive_login())

    # Subscription details
    subs = asyncio.run(mm.get_subscription_details())
    print(subs)

    # Accounts
    accounts = asyncio.run(mm.get_accounts())
    with open("data.json", "w") as outfile:
        json.dump(accounts, outfile)

    # # Transaction categories
    categories = asyncio.run(mm.get_transaction_categories())
    with open("categories.json", "w") as outfile:
        json.dump(categories, outfile)

    income_categories = dict()
    for c in categories.get("categories"):
        if c.get("group").get("type") == "income":
            print(f'{c.get("group").get("type")} - {c.get("group").get("name")} - {c.get("name")}')
            income_categories[c.get("name")] = 0

    expense_category_groups = dict()
    for c in categories.get("categories"):
        if c.get("group").get("type") == "expense":
            print(f'{c.get("group").get("type")} - {c.get("group").get("name")} - {c.get("name")}')
            expense_category_groups[c.get("group").get("name")] = 0

    # Cashflow
    cashflow = asyncio.run(mm.get_cashflow(start_date="2023-10-01", end_date="2023-10-31"))
    with open("cashflow.json", "w") as outfile:
        json.dump(cashflow, outfile)

    for c in cashflow.get("summary"):
        print(
            f'Income: {c.get("summary").get("sumIncome")} '
            f'Expense: {c.get("summary").get("sumExpense")} '
            f'Savings: {c.get("summary").get("savings")} '
            f'({c.get("summary").get("savingsRate"):.0%})'
        )

    for c in cashflow.get("byCategory"):
        if c.get("groupBy").get("category").get("group").get("type") == "income":
            income_categories[c.get("groupBy").get("category").get("name")] += c.get("summary").get("sum")

    print()
    for c in cashflow.get("byCategoryGroup"):
        if c.get("groupBy").get("categoryGroup").get("type") == "expense":
            expense_category_groups[c.get("groupBy").get("categoryGroup").get("name")] += c.get("summary").get("sum")

    print(income_categories)
    print()
    print(expense_category_groups)

main()
