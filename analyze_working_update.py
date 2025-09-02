#!/usr/bin/env python3
"""
Analyze the working update structure from HAR file
"""
import json

# Working example from HAR file
working_update = {
    "id": "220723814124920059",
    "merchantCriteriaUseOriginalStatement": False,
    "merchantCriteria": [{"operator": "contains", "value": "numberbarn"}],
    "amountCriteria": None,
    "categoryIds": None,
    "accountIds": None,
    "setCategoryAction": "220719326595030610",
    "reviewStatusAction": None,
    "splitTransactionsAction": None,
    "applyToExistingTransactions": True,
}

print("Working update structure from HAR:")
print(json.dumps(working_update, indent=2))
print()
print("Key observations:")
print("- All fields are present, even if None")
print("- setCategoryAction is just a string ID")
print("- amountCriteria can be None or have structure like:")
print("  {'operator': 'gt', 'isExpense': True, 'valueRange': None, 'value': 20}")
print()

# Another example with amount criteria
working_update_with_amount = {
    "id": "220720698715447242",
    "merchantCriteriaUseOriginalStatement": False,
    "merchantCriteria": [{"operator": "contains", "value": "sentris"}],
    "amountCriteria": {
        "operator": "gt",
        "isExpense": True,
        "valueRange": None,
        "value": 20,
    },
    "categoryIds": None,
    "accountIds": None,
    "setCategoryAction": "220719155218914684",
    "reviewStatusAction": None,
    "splitTransactionsAction": None,
    "applyToExistingTransactions": False,
}

print("Example with amount criteria:")
print(json.dumps(working_update_with_amount, indent=2))
