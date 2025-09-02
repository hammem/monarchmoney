#!/usr/bin/env python3
"""
Extract real operations from HAR files more cleanly
"""
import re
import glob

operations = set()

for har_file in glob.glob("/Users/keith/src/monarchmoney-enhanced/*.har"):
    with open(har_file, "r") as f:
        content = f.read()
        # Find operationName in JSON
        matches = re.findall(r'"operationName":"([^"]*)"', content)
        operations.update(matches)

print("=== REAL MonarchMoney Operations ===")
for op in sorted(operations):
    print(f"- {op}")

print(f"\n=== FAILING OPERATIONS IN TEST ===")
failing_ops = [
    "get_recent_account_balances",
    "get_net_worth_history",
    "get_transactions_summary_card",
    "get_goals",
    "get_bills",
    "get_settings",
]

print("\nLet me check what real operations might replace these...")
# Map failing operations to potential real operations
replacements = {
    "get_goals": "GetGoalsV2",  # Found this one!
    "get_bills": "Common_GetAggregatedRecurringItems",  # This looks like bills
    "get_recent_account_balances": "Web_GetFilteredAccounts",  # This has account balances
}

for fake_op, real_op in replacements.items():
    if real_op in operations:
        print(f"✅ {fake_op} -> {real_op} (REAL OPERATION FOUND)")
    else:
        print(f"❌ {fake_op} -> {real_op} (not found)")

print(f"\nOther operations that might be useful:")
useful_ops = [
    op
    for op in operations
    if any(
        keyword in op.lower()
        for keyword in [
            "account",
            "balance",
            "transaction",
            "goal",
            "setting",
            "subscription",
        ]
    )
]
for op in sorted(useful_ops):
    print(f"- {op}")
