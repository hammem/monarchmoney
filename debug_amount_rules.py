#!/usr/bin/env python3
"""
Debug the specific amount-based rule creation issues
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def debug_amount_rules():
    """Debug amount-based rule creation specifically"""
    print("=== Debugging Amount-Based Rule Issues ===")

    # Load session
    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    # Verify basic connectivity
    try:
        accounts = await mm.get_accounts()
        print(f"✅ Connection verified: {len(accounts.get('accounts', []))} accounts")

        categories = await mm.get_transaction_categories()
        sample_category = (
            categories["categories"][0]["name"]
            if categories.get("categories")
            else "Food & Dining"
        )
        print(f"✅ Categories loaded: Using '{sample_category}' for testing")
    except Exception as e:
        print(f"❌ Basic connectivity failed: {e}")
        return

    # Test 1: Simple categorization rule (should work)
    print("\n1. Testing simple categorization rule (should work)...")
    try:
        result = await mm.create_categorization_rule(
            "DEBUG Simple Test", sample_category
        )
        print("   ✅ Simple rule creation: SUCCESS")
    except Exception as e:
        print(f"   ❌ Simple rule failed: {e}")

    # Test 2: Amount-based rule (broken)
    print("\n2. Testing amount-based rule (broken)...")
    try:
        result = await mm.create_amount_rule(
            amount=115.32,
            operator="eq",
            is_expense=True,
            category_name=sample_category,
            apply_to_existing=False,
        )
        print("   ✅ Amount rule creation: SUCCESS")
    except Exception as e:
        print(f"   ❌ Amount rule failed: {e}")
        if "Something went wrong while processing" in str(e):
            print("   ^ This is the GraphQL parsing error we need to fix")

    # Test 3: Combined rule (broken)
    print("\n3. Testing combined rule (broken)...")
    try:
        result = await mm.create_combined_rule(
            merchant_contains="DEBUG Test",
            amount=50,
            amount_operator="gt",
            category_name=sample_category,
            apply_to_existing=False,
        )
        print("   ✅ Combined rule creation: SUCCESS")
    except Exception as e:
        print(f"   ❌ Combined rule failed: {e}")
        if "Something went wrong while processing" in str(e):
            print("   ^ This is the GraphQL parsing error we need to fix")

    # Test 4: Apply rules to existing (broken)
    print("\n4. Testing apply rules to existing (broken)...")
    try:
        result = await mm.apply_rules_to_existing_transactions(limit=1)
        print("   ✅ Apply existing rules: SUCCESS")
    except Exception as e:
        print(f"   ❌ Apply existing failed: {e}")
        if "Something went wrong while processing" in str(e):
            print("   ^ This is the GraphQL parsing error we need to fix")

    print("\n=== Analysis ===")
    print("The pattern shows that:")
    print("- Simple merchant-only rules work perfectly")
    print("- Any rule with amount criteria fails with GraphQL parsing error")
    print("- The error 'line: 1, column: 49' suggests specific parsing issue")
    print("- Need to examine the exact GraphQL being sent vs what API expects")


if __name__ == "__main__":
    asyncio.run(debug_amount_rules())
