#!/usr/bin/env python3
"""
Debug why helper functions fail when direct GraphQL works
"""
import asyncio
import json
from pathlib import Path
from monarchmoney import MonarchMoney


async def debug_helper_vs_direct():
    """Compare helper function vs direct call"""
    print("=== Loading MCP Session ===")

    mm = MonarchMoney()
    session_file = Path.home() / ".monarchmoney_session"
    mm.load_session(str(session_file))

    # Verify session works
    accounts = await mm.get_accounts()
    print(f"✅ Session valid")

    # Get categories for testing
    categories = await mm.get_transaction_categories()
    test_category_id = categories["categories"][0]["id"]
    test_category_name = categories["categories"][0]["name"]
    print(f"Using test category: {test_category_name} ({test_category_id})")

    # Test 1: Call create_transaction_rule directly (should work)
    print(f"\n=== Test 1: Direct create_transaction_rule ===")
    try:
        result = await mm.create_transaction_rule(
            merchant_criteria=[{"operator": "contains", "value": "Direct Test"}],
            set_category_action=test_category_id,
            apply_to_existing_transactions=False,
        )
        print(f"✅ Direct create_transaction_rule SUCCESS")

    except Exception as e:
        print(f"❌ Direct create_transaction_rule FAILED: {e}")
        return

    # Test 2: Call create_amount_rule (should fail)
    print(f"\n=== Test 2: create_amount_rule Helper ===")
    try:
        result = await mm.create_amount_rule(
            amount=100.00,
            operator="eq",
            is_expense=True,
            set_category_action=test_category_id,
            apply_to_existing=False,
        )
        print(f"✅ create_amount_rule SUCCESS: {result}")

    except Exception as e:
        print(f"❌ create_amount_rule FAILED: {e}")

        # Let's trace what create_amount_rule is trying to do
        print(f"\n=== Tracing create_amount_rule Logic ===")

        # Simulate the logic manually
        amount_criteria = {
            "operator": "eq",
            "isExpense": True,
            "value": 100.00,
        }

        print(f"Amount criteria that would be passed: {amount_criteria}")

        # Try calling create_transaction_rule with the same params create_amount_rule would use
        print(f"Trying create_transaction_rule with amount criteria...")
        try:
            result = await mm.create_transaction_rule(
                amount_criteria=amount_criteria,
                set_category_action=test_category_id,
                apply_to_existing_transactions=False,
            )
            print(f"✅ Manual create_transaction_rule with amount_criteria SUCCESS")
            print(
                f"   So create_amount_rule SHOULD work... there must be a bug in the helper"
            )

        except Exception as e2:
            print(
                f"❌ Manual create_transaction_rule with amount_criteria FAILED: {e2}"
            )
            print(f"   This suggests the issue is with amount_criteria parameter")


async def main():
    await debug_helper_vs_direct()


if __name__ == "__main__":
    asyncio.run(main())
