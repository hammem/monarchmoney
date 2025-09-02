#!/usr/bin/env python3
"""
Test the other missing functions individually
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_each_function():
    """Test each missing function individually"""
    print("=== Testing Each Missing Function ===")

    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    functions_to_test = [
        (
            "get_net_worth_history",
            lambda: mm.get_net_worth_history("2024-01-01", "2024-12-31"),
        ),
        ("get_transactions_summary_card", lambda: mm.get_transactions_summary_card()),
        ("get_bills", lambda: mm.get_bills()),
        ("get_settings", lambda: mm.get_settings()),
        (
            "preview_transaction_rule",
            lambda: mm.preview_transaction_rule(
                {
                    "merchantCriteria": [{"operator": "contains", "value": "test"}],
                    "setCategoryAction": "56073867267055063",
                }
            ),
        ),
        ("get_insights", lambda: mm.get_insights()),
        ("get_notifications", lambda: mm.get_notifications()),
        ("get_credit_score", lambda: mm.get_credit_score()),
    ]

    working_functions = []
    broken_functions = []

    for func_name, func_call in functions_to_test:
        print(f"\nTesting {func_name}...")
        try:
            result = await func_call()
            print(f"   ✅ SUCCESS! Type: {type(result)}")
            if isinstance(result, dict):
                print(f"   Keys: {list(result.keys())}")
            working_functions.append(func_name)
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ FAILED: {error_msg[:100]}...")
            if "Something went wrong while processing" in error_msg:
                print(f"   ^ Likely fake GraphQL operation")
            broken_functions.append((func_name, error_msg))

    print(f"\n=== SUMMARY ===")
    print(f"✅ Working functions ({len(working_functions)}): {working_functions}")
    print(
        f"❌ Broken functions ({len(broken_functions)}): {[f[0] for f in broken_functions]}"
    )

    return working_functions, broken_functions


if __name__ == "__main__":
    asyncio.run(test_each_function())
