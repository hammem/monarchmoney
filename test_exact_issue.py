#!/usr/bin/env python3
"""
Test the exact issue reported by user
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_exact_issue():
    """Test the exact scenarios mentioned by user"""
    print("=== Testing Exact User-Reported Issues ===")

    # Load session
    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    # Get categories
    categories = await mm.get_transaction_categories()
    sample_category = (
        categories["categories"][0]["name"]
        if categories.get("categories")
        else "Food & Dining"
    )

    print(f"Using category: {sample_category}")

    # Test 1: Exact amount rule "Amount equals $115.32"
    print("\n1. Testing: Amount equals $115.32...")
    try:
        result = await mm.create_amount_rule(
            amount=115.32,
            operator="eq",
            is_expense=True,
            category_name=sample_category,
            apply_to_existing=True,  # Try with retroactive application
        )
        print("   ✅ SUCCESS - Amount equals rule created")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        # Let's examine the exact error
        if hasattr(e, "args") and e.args:
            print(f"   Full error: {e.args}")

    # Test 2: Combined rule "Airbnb + amount > $200"
    print("\n2. Testing: Airbnb + amount > $200...")
    try:
        result = await mm.create_combined_rule(
            merchant_contains="Airbnb",
            amount=200,
            amount_operator="gt",
            category_name=sample_category,
            apply_to_existing=True,  # Try with retroactive application
        )
        print("   ✅ SUCCESS - Combined rule created")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        if hasattr(e, "args") and e.args:
            print(f"   Full error: {e.args}")

    # Test 3: Apply rules to ALL existing transactions (not limit=1)
    print("\n3. Testing: Apply rules to ALL 18,881 transactions...")
    try:
        result = await mm.apply_rules_to_existing_transactions()  # No limit
        print("   ✅ SUCCESS - Applied rules to existing")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        if hasattr(e, "args") and e.args:
            print(f"   Full error: {e.args}")


if __name__ == "__main__":
    asyncio.run(test_exact_issue())
